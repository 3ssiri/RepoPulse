"""RepoPulse web layer (OpenAI WebMCP challenge).

A thin FastAPI adapter over the existing RepoPulse engine. It holds no
business logic of its own: scans go through ``repopulse.analyzer`` and
comparisons through ``repopulse.compare``, exactly like the CLI.

Boundaries:
- Public github.com repositories only (enforced before any tree/file reads).
- Optional ``GITHUB_TOKEN`` is read server-side only; it never reaches
  responses, HTML, or JS.
- Errors are mapped to a stable ``{"detail": {"code", "message"}}`` contract
  without tracebacks, tokens, or raw GitHub payloads.
"""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from repopulse import __version__
from repopulse.analyzer import build_health_report
from repopulse.compare import build_comparison
from repopulse.github_client import GitHubAPIError, GitHubClient
from repopulse.url_parser import parse_github_url

STATIC_DIR = Path(__file__).parent / "static"

MAX_URL_LENGTH = 512
MAX_REF_LENGTH = 256

FIELD_ERROR_CODES = {
    "repository_url": "invalid_repository_url",
    "ref": "invalid_ref",
    "baseline_ref": "invalid_ref",
    "target_ref": "invalid_ref",
}


class ApiError(Exception):
    """Error carrying the public error contract."""

    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class ScanRequest(BaseModel):
    repository_url: str = Field(max_length=MAX_URL_LENGTH)
    ref: str | None = Field(default=None, max_length=MAX_REF_LENGTH)


class CompareRequest(BaseModel):
    repository_url: str = Field(max_length=MAX_URL_LENGTH)
    baseline_ref: str = Field(max_length=MAX_REF_LENGTH)
    target_ref: str = Field(max_length=MAX_REF_LENGTH)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": {"code": code, "message": message}},
    )


def _make_client() -> GitHubClient:
    # Server-side token only; never exposed to the frontend.
    return GitHubClient(os.getenv("GITHUB_TOKEN"))


def _normalize_ref(ref: str | None) -> str | None:
    if ref is None:
        return None
    ref = ref.strip()
    return ref or None


def _checked_ref(ref: str | None, *, required: bool = False) -> str | None:
    normalized = _normalize_ref(ref)
    if normalized is None:
        if required:
            raise ApiError(400, "invalid_ref", "Invalid request parameters.")
        return None
    if len(normalized) > MAX_REF_LENGTH:
        raise ApiError(400, "invalid_ref", "Invalid request parameters.")
    return normalized


def _require_ref(ref: str) -> str:
    checked = _checked_ref(ref, required=True)
    assert checked is not None
    return checked


def _parse_repository(repository_url: str) -> tuple[str, str, str | None]:
    try:
        return parse_github_url(repository_url)
    except ValueError as error:
        raise ApiError(400, "invalid_repository_url", str(error)) from error


def _reject_private(client: GitHubClient, owner: str, repo: str) -> dict:
    """Refuse private repositories before any tree/file content is read."""
    try:
        data = client.get_repo(owner, repo)
    except GitHubAPIError as error:
        raise _map_github_error(error) from error
    if data.get("private"):
        raise ApiError(
            403,
            "private_repository_not_supported",
            "Private repositories are not supported by the web app.",
        )
    return data


def _map_github_error(error: GitHubAPIError) -> ApiError:
    """Translate core GitHubAPIError messages into the public error contract.

    The core client does not expose status codes, so mapping is done on its
    stable message shapes. Raw GitHub response bodies are never forwarded.
    """
    text = str(error)
    if "rate limit exceeded" in text:
        return ApiError(
            429,
            "github_rate_limited",
            "GitHub API rate limit exceeded. Try again later.",
        )
    if "Could not connect" in text:
        return ApiError(
            503,
            "github_unavailable",
            "Could not reach the GitHub API. Try again later.",
        )
    if "was not found" in text:
        if "at ref" in text:
            return ApiError(
                404,
                "ref_not_found",
                "The requested ref was not found in this repository.",
            )
        return ApiError(
            404,
            "repository_not_found",
            "Repository was not found. Only public github.com repositories are supported.",
        )
    return ApiError(
        502,
        "github_unavailable",
        "GitHub API request failed. Try again later.",
    )


def create_app() -> FastAPI:
    app = FastAPI(title="RepoPulse Web", version=__version__)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, error: ApiError) -> JSONResponse:
        return _error_response(error.status_code, error.code, error.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        fields = [
            str(loc)
            for err in error.errors()
            for loc in err.get("loc", ())
            if loc != "body"
        ]
        code = next(
            (FIELD_ERROR_CODES[field] for field in fields if field in FIELD_ERROR_CODES),
            "invalid_request",
        )
        return _error_response(400, code, "Invalid request parameters.")

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, error: Exception) -> JSONResponse:
        return _error_response(500, "internal_error", "Unexpected server error.")

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "service": "repopulse-web", "version": __version__}

    @app.post("/api/scan")
    def scan(payload: ScanRequest) -> dict:
        owner, repo, url_ref = _parse_repository(payload.repository_url)
        body_ref = _checked_ref(payload.ref)
        effective_ref = body_ref if body_ref is not None else _checked_ref(url_ref)
        client = _make_client()
        repo_data = _reject_private(client, owner, repo)
        try:
            report = build_health_report(
                client, owner, repo, ref=effective_ref, repo_data=repo_data
            )
        except GitHubAPIError as error:
            raise _map_github_error(error) from error
        return report.model_dump()

    @app.post("/api/compare")
    def compare(payload: CompareRequest) -> dict:
        owner, repo, _ = _parse_repository(payload.repository_url)
        baseline_ref = _require_ref(payload.baseline_ref)
        target_ref = _require_ref(payload.target_ref)
        client = _make_client()
        repo_data = _reject_private(client, owner, repo)
        try:
            baseline = build_health_report(
                client, owner, repo, ref=baseline_ref, repo_data=repo_data
            )
            target = build_health_report(
                client, owner, repo, ref=target_ref, repo_data=repo_data
            )
        except GitHubAPIError as error:
            raise _map_github_error(error) from error
        comparison = build_comparison(
            baseline,
            target,
            baseline_label=baseline_ref,
            target_label=target_ref,
        )
        return comparison.model_dump()

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()
