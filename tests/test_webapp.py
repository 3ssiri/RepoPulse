"""Tests for the FastAPI web layer (webapp.app).

All GitHub access is mocked at the webapp boundary: GitHubClient and
build_health_report are monkeypatched, following the existing test style.
"""

import pytest

pytest.importorskip("fastapi", reason="web extra not installed")
pytest.importorskip("httpx", reason="web extra not installed")

from fastapi.testclient import TestClient

import webapp.app as webapp
from repopulse import __version__
from repopulse.github_client import GitHubAPIError
from repopulse.models import CheckResult, HealthReport, RepositoryInfo

VALID_URL = "https://github.com/octo/hello"


def sample_report(scan_truncated=False) -> HealthReport:
    return HealthReport(
        repository=RepositoryInfo(
            owner="octo",
            name="hello",
            full_name="octo/hello",
            description="demo",
            url="https://github.com/octo/hello",
            default_branch="main",
            private=False,
            stars=10,
            forks=2,
            open_issues=1,
        ),
        checks=[
            CheckResult(
                key="tests",
                title="Tests",
                status="warn",
                score=5,
                max_score=10,
                message="No CI found.",
                recommendations=["Add a CI workflow."],
            )
        ],
        total_score=80,
        grade="B",
        recommendations=["Add a CI workflow."],
        scan_truncated=scan_truncated,
    )


class FakeClient:
    """Fake GitHubClient; ``private`` controls the pre-scan privacy check."""

    def __init__(self, token=None, private=False):
        self.token = token
        self.private = private

    def get_repo(self, owner, repo):
        return {"private": self.private}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(webapp, "GitHubClient", FakeClient)
    monkeypatch.setattr(webapp, "build_health_report", lambda *a, **k: sample_report())
    return TestClient(webapp.app, raise_server_exceptions=False)


def failing_client(monkeypatch, error):
    def fake_build(*args, **kwargs):
        raise error

    monkeypatch.setattr(webapp, "GitHubClient", FakeClient)
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    return TestClient(webapp.app, raise_server_exceptions=False)


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "repopulse-web",
        "version": __version__,
    }


def test_index_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "RepoPulse" in response.text


def test_security_headers(client):
    response = client.get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_scan_valid(client):
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 200
    body = response.json()
    assert body["schema_version"] == "1.1"
    assert body["repository"]["full_name"] == "octo/hello"
    assert body["total_score"] == 80
    assert body["grade"] == "B"
    assert body["checks"][0]["key"] == "tests"
    assert body["recommendations"] == ["Add a CI workflow."]
    assert body["scan_truncated"] is False


def test_scan_preserves_scan_truncated(monkeypatch):
    monkeypatch.setattr(webapp, "GitHubClient", FakeClient)
    monkeypatch.setattr(
        webapp, "build_health_report", lambda *a, **k: sample_report(scan_truncated=True)
    )
    client = TestClient(webapp.app)
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 200
    assert response.json()["scan_truncated"] is True


def test_scan_rejects_non_github_url(client):
    response = client.post("/api/scan", json={"repository_url": "https://example.com/foo"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_repository_url"


def test_scan_rejects_gitlab_host(client):
    response = client.post(
        "/api/scan", json={"repository_url": "https://gitlab.com/octo/hello"}
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_repository_url"


def test_scan_rejects_overlong_url(client):
    response = client.post("/api/scan", json={"repository_url": "https://github.com/" + "a" * 600})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_repository_url"


def test_scan_rejects_overlong_ref(client):
    response = client.post(
        "/api/scan", json={"repository_url": VALID_URL, "ref": "a" * 300}
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_ref"


def test_scan_body_ref_takes_precedence_over_url_ref(monkeypatch):
    captured = {}

    def fake_build(client_obj, owner, repo, config=None, ref=None, **kwargs):
        captured["ref"] = ref
        return sample_report()

    monkeypatch.setattr(webapp, "GitHubClient", FakeClient)
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app)
    response = client.post(
        "/api/scan",
        json={"repository_url": VALID_URL + "/tree/url-ref", "ref": "body-ref"},
    )
    assert response.status_code == 200
    assert captured["ref"] == "body-ref"


def test_scan_url_ref_used_when_body_ref_missing(monkeypatch):
    captured = {}

    def fake_build(client_obj, owner, repo, config=None, ref=None, **kwargs):
        captured["ref"] = ref
        return sample_report()

    monkeypatch.setattr(webapp, "GitHubClient", FakeClient)
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app)
    response = client.post("/api/scan", json={"repository_url": VALID_URL + "/tree/dev"})
    assert response.status_code == 200
    assert captured["ref"] == "dev"


def test_scan_empty_body_ref_falls_back_to_url_ref(monkeypatch):
    captured = {}

    def fake_build(client_obj, owner, repo, config=None, ref=None, **kwargs):
        captured["ref"] = ref
        return sample_report()

    monkeypatch.setattr(webapp, "GitHubClient", FakeClient)
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app)
    response = client.post(
        "/api/scan", json={"repository_url": VALID_URL + "/tree/dev", "ref": "  "}
    )
    assert response.status_code == 200
    assert captured["ref"] == "dev"


def test_scan_repository_not_found(monkeypatch):
    client = failing_client(
        monkeypatch,
        GitHubAPIError("Repository or file was not found. Check the URL and token permissions."),
    )
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "repository_not_found"


def test_scan_ref_not_found(monkeypatch):
    client = failing_client(
        monkeypatch,
        GitHubAPIError(
            "Could not load git tree for octo/hello at ref 'nope'. "
            "Repository or file was not found. Check the URL and token permissions."
        ),
    )
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "ref_not_found"


def test_scan_rate_limited(monkeypatch):
    client = failing_client(
        monkeypatch,
        GitHubAPIError("GitHub API rate limit exceeded. Provide --token or set GITHUB_TOKEN."),
    )
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 429
    detail = response.json()["detail"]
    assert detail["code"] == "github_rate_limited"
    assert "GITHUB_TOKEN" not in detail["message"]


def test_scan_network_failure(monkeypatch):
    client = failing_client(
        monkeypatch, GitHubAPIError("Could not connect to GitHub API: boom")
    )
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "github_unavailable"


def test_scan_other_github_failure(monkeypatch):
    client = failing_client(
        monkeypatch, GitHubAPIError("GitHub API request failed: 500 raw-body-here")
    )
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail["code"] == "github_unavailable"
    assert "raw-body-here" not in detail["message"]


def test_scan_private_repo_rejected(monkeypatch):
    called = {"build": False}

    def fake_build(*args, **kwargs):
        called["build"] = True
        return sample_report()

    monkeypatch.setattr(
        webapp, "GitHubClient", lambda token=None: FakeClient(token, private=True)
    )
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app)
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "private_repository_not_supported"
    assert called["build"] is False  # no tree/file reads happen for private repos


def test_scan_uses_server_side_token(monkeypatch):
    captured = {}

    class TokenCapturingClient(FakeClient):
        def __init__(self, token=None):
            super().__init__(token)
            captured["token"] = token

    monkeypatch.setattr(webapp, "GitHubClient", TokenCapturingClient)
    monkeypatch.setattr(webapp, "build_health_report", lambda *a, **k: sample_report())
    monkeypatch.setenv("GITHUB_TOKEN", "secret-token-123")
    client = TestClient(webapp.app)
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 200
    assert captured["token"] == "secret-token-123"
    assert "secret-token-123" not in response.text


def test_errors_do_not_leak_token_or_traceback(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "secret-token-123")

    def fake_build(*args, **kwargs):
        raise RuntimeError("internal boom with secret-token-123 inside")

    monkeypatch.setattr(
        webapp, "GitHubClient", lambda token=None: FakeClient(token)
    )
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app, raise_server_exceptions=False)
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail["code"] == "internal_error"
    assert "secret-token-123" not in response.text
    assert "Traceback" not in response.text
    assert "internal boom" not in response.text


def test_compare_valid(monkeypatch):
    def fake_build(client_obj, owner, repo, config=None, ref=None, **kwargs):
        return sample_report()

    monkeypatch.setattr(webapp, "GitHubClient", FakeClient)
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app)
    response = client.post(
        "/api/compare",
        json={
            "repository_url": VALID_URL,
            "baseline_ref": "v0.3.5",
            "target_ref": "v0.3.6",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["schema_version"] == "1.0"
    assert body["kind"] == "comparison"
    assert body["baseline_label"] == "v0.3.5"
    assert body["target_label"] == "v0.3.6"
    assert body["baseline_score"] == 80
    assert body["target_score"] == 80
    assert body["score_delta"] == 0
    assert "checks" in body
    assert "improved" in body
    assert "regressed" in body
    assert "unchanged" in body


def test_compare_requires_baseline_ref(client):
    response = client.post(
        "/api/compare", json={"repository_url": VALID_URL, "target_ref": "main"}
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_ref"


def test_compare_requires_target_ref(client):
    response = client.post(
        "/api/compare", json={"repository_url": VALID_URL, "baseline_ref": "main"}
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_ref"


def test_compare_rejects_overlong_ref(client):
    response = client.post(
        "/api/compare",
        json={
            "repository_url": VALID_URL,
            "baseline_ref": "a" * 300,
            "target_ref": "main",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_ref"


def test_compare_rejects_non_github_url(client):
    response = client.post(
        "/api/compare",
        json={
            "repository_url": "https://example.com/foo",
            "baseline_ref": "a",
            "target_ref": "b",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_repository_url"


def test_compare_propagates_github_errors(monkeypatch):
    client = failing_client(
        monkeypatch,
        GitHubAPIError("GitHub API rate limit exceeded. Provide --token or set GITHUB_TOKEN."),
    )
    response = client.post(
        "/api/compare",
        json={"repository_url": VALID_URL, "baseline_ref": "a", "target_ref": "b"},
    )
    assert response.status_code == 429
    assert response.json()["detail"]["code"] == "github_rate_limited"


def test_compare_rejects_private_repo(monkeypatch):
    monkeypatch.setattr(
        webapp, "GitHubClient", lambda token=None: FakeClient(token, private=True)
    )
    monkeypatch.setattr(webapp, "build_health_report", lambda *a, **k: sample_report())
    client = TestClient(webapp.app)
    response = client.post(
        "/api/compare",
        json={"repository_url": VALID_URL, "baseline_ref": "a", "target_ref": "b"},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "private_repository_not_supported"


def test_compare_strips_whitespace_refs(monkeypatch):
    captured = []

    def fake_build(client_obj, owner, repo, config=None, ref=None, **kwargs):
        captured.append(ref)
        return sample_report()

    monkeypatch.setattr(webapp, "GitHubClient", FakeClient)
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app)
    response = client.post(
        "/api/compare",
        json={
            "repository_url": VALID_URL,
            "baseline_ref": "  v0.3.5  ",
            "target_ref": "\tv0.3.6\n",
        },
    )
    assert response.status_code == 200
    assert captured == ["v0.3.5", "v0.3.6"]
    assert response.json()["baseline_label"] == "v0.3.5"
    assert response.json()["target_label"] == "v0.3.6"


def test_compare_rejects_blank_refs(client):
    response = client.post(
        "/api/compare",
        json={"repository_url": VALID_URL, "baseline_ref": "   ", "target_ref": "main"},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_ref"


def test_frontend_commits_repository_only_after_scan_success():
    """Failed scans must not overwrite the selected repository (dashboard/agent share state)."""
    from pathlib import Path

    source = (Path(__file__).resolve().parents[1] / "webapp" / "static" / "app.js").read_text(
        encoding="utf-8"
    )
    function = source.split("async function scanRepository", 1)[1].split(
        "async function compareRefs", 1
    )[0]
    before_try, after_try = function.split("try {", 1)
    assert "state.repositoryUrl = repositoryUrl" not in before_try
    assert "state.repositoryUrl = repositoryUrl" in after_try.split("} catch", 1)[0]


def test_frontend_compare_error_is_human_readable():
    from pathlib import Path

    source = (Path(__file__).resolve().parents[1] / "webapp" / "static" / "app.js").read_text(
        encoding="utf-8"
    )
    function = source.split("async function compareRefs", 1)[1].split(
        "/* All GitHub-derived data", 1
    )[0]
    assert "scan_repository" not in function
    assert "Scan a repository first" in function


FRONTEND_JS = (
    __import__("pathlib").Path(__file__).resolve().parents[1] / "webapp" / "static" / "app.js"
)


def _frontend_source() -> str:
    return FRONTEND_JS.read_text(encoding="utf-8")


def test_frontend_compare_without_scan_goes_through_seterror():
    """Compare-before-scan must hit the catch that calls setError, not throw first."""
    function = _frontend_source().split("async function compareRefs", 1)[1].split(
        "/* All GitHub-derived data", 1
    )[0]
    before_try, rest = function.split("try {", 1)
    assert "No repository is selected" not in before_try
    try_body, catch_body = rest.split("} catch", 1)
    assert "No repository is selected" in try_body
    assert "setError" in catch_body


def test_scan_rejects_overlong_url_derived_ref(client):
    long_ref = "a" * 300
    url = f"{VALID_URL}/tree/{long_ref}"
    assert len(url) <= 512
    response = client.post("/api/scan", json={"repository_url": url})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_ref"


def test_scan_url_ref_at_max_length_is_accepted(monkeypatch):
    captured = {}

    def fake_build(client_obj, owner, repo, config=None, ref=None, **kwargs):
        captured["ref"] = ref
        return sample_report()

    monkeypatch.setattr(webapp, "GitHubClient", FakeClient)
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app)
    ref = "b" * 256
    response = client.post("/api/scan", json={"repository_url": f"{VALID_URL}/tree/{ref}"})
    assert response.status_code == 200
    assert captured["ref"] == ref


def test_scan_passes_privacy_metadata_into_build(monkeypatch):
    captured = {}

    class CountingClient(FakeClient):
        def __init__(self, token=None):
            super().__init__(token)
            self.calls = 0

        def get_repo(self, owner, repo):
            self.calls += 1
            captured["client"] = self
            return {"private": False, "full_name": "octo/hello"}

    def fake_build(client_obj, owner, repo, config=None, ref=None, repo_data=None, **kwargs):
        captured["repo_data"] = repo_data
        return sample_report()

    monkeypatch.setattr(webapp, "GitHubClient", CountingClient)
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app)
    response = client.post("/api/scan", json={"repository_url": VALID_URL})
    assert response.status_code == 200
    assert captured["client"].calls == 1
    assert captured["repo_data"] == {"private": False, "full_name": "octo/hello"}


def test_compare_reuses_privacy_metadata_for_both_scans(monkeypatch):
    captured = {"repo_data": [], "get_repo": 0}

    class CountingClient(FakeClient):
        def get_repo(self, owner, repo):
            captured["get_repo"] += 1
            return {"private": False}

    def fake_build(client_obj, owner, repo, config=None, ref=None, repo_data=None, **kwargs):
        captured["repo_data"].append(repo_data)
        return sample_report()

    monkeypatch.setattr(webapp, "GitHubClient", CountingClient)
    monkeypatch.setattr(webapp, "build_health_report", fake_build)
    client = TestClient(webapp.app)
    response = client.post(
        "/api/compare",
        json={"repository_url": VALID_URL, "baseline_ref": "a", "target_ref": "b"},
    )
    assert response.status_code == 200
    assert captured["get_repo"] == 1
    assert captured["repo_data"] == [{"private": False}, {"private": False}]


def test_frontend_aborts_partial_webmcp_registration():
    source = _frontend_source()
    block = source.split("Promise.all", 1)[1]
    catch = block.split(".catch", 1)[1]
    abort_at = catch.find("registration.abort()")
    unavailable_at = catch.find("webmcpAvailable = false")
    assert abort_at != -1
    assert unavailable_at != -1
    assert abort_at < unavailable_at


def test_stale_compare_is_discarded_after_newer_scan():
    """Compare for repo A must not commit after a newer scan of repo B."""
    import json
    import re
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node is required to execute the stale-result predicate")

    source = _frontend_source()
    match = re.search(
        r"function isStaleResult\([^)]*\) \{\s*return [^;]+;\s*\}",
        source,
    )
    assert match is not None, "isStaleResult helper is missing"
    script = (
        match.group(0)
        + """
        const stale = isStaleResult(1, 2, 'https://github.com/a/a', 'https://github.com/b/b');
        const same = isStaleResult(2, 2, 'https://github.com/b/b', 'https://github.com/b/b');
        const olderScan = isStaleResult(1, 2, 'https://github.com/b/b', 'https://github.com/b/b');
        console.log(JSON.stringify({stale, same, olderScan}));
        """
    )
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    assert payload["stale"] is True
    assert payload["same"] is False
    assert payload["olderScan"] is True


def test_frontend_scan_and_compare_ignore_stale_results():
    source = _frontend_source()
    scan = source.split("async function scanRepository", 1)[1].split(
        "async function compareRefs", 1
    )[0]
    compare = source.split("async function compareRefs", 1)[1].split(
        "/* All GitHub-derived data", 1
    )[0]
    for body in (scan, compare):
        assert "isStaleResult(" in body
        commit_at = body.find("state.current")
        stale_at = body.find("isStaleResult(")
        assert stale_at != -1
        assert stale_at < commit_at or "if (isStaleResult" in body
