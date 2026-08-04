import base64
from urllib.parse import quote

import requests


class GitHubAPIError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str | None = None):
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _get(self, url: str, timeout: int) -> requests.Response:
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
        except requests.RequestException as error:
            raise GitHubAPIError(f"Could not connect to GitHub API: {error}") from error
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            raise GitHubAPIError("GitHub API rate limit exceeded. Provide --token or set GITHUB_TOKEN.")
        if response.status_code == 404:
            raise GitHubAPIError("Repository or file was not found. Check the URL and token permissions.")
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            raise GitHubAPIError(f"GitHub API request failed: {response.status_code} {response.text[:160]}") from error
        return response

    def get_repo(self, owner: str, repo: str) -> dict:
        return self._get(f"{self.base_url}/repos/{owner}/{repo}", timeout=20).json()

    def get_tree(self, owner: str, repo: str, branch: str) -> list[dict]:
        encoded_ref = quote(branch, safe="")
        try:
            data = self._get(
                f"{self.base_url}/repos/{owner}/{repo}/git/trees/{encoded_ref}?recursive=1",
                timeout=30,
            ).json()
        except GitHubAPIError as error:
            raise GitHubAPIError(
                f"Could not load git tree for {owner}/{repo} at ref '{branch}'. {error}"
            ) from error
        return data.get("tree", [])

    def get_file_content(self, owner: str, repo: str, path: str, ref: str | None = None) -> str | None:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        if ref is not None:
            url = f"{url}?ref={quote(ref, safe='')}"
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
        except requests.RequestException as error:
            raise GitHubAPIError(f"Could not connect to GitHub API while reading {path}: {error}") from error
        if response.status_code == 404:
            return None
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            raise GitHubAPIError("GitHub API rate limit exceeded. Provide --token or set GITHUB_TOKEN.")
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            raise GitHubAPIError(f"GitHub API request failed while reading {path}: {response.status_code}") from error
        data = response.json()
        if data.get("encoding") != "base64" or not isinstance(data.get("content"), str):
            return None
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")

    def list_open_issue_titles(self, owner: str, repo: str) -> set[str]:
        """Return titles of open issues (not PRs) for dedupe. Paginates through the API."""
        titles: set[str] = set()
        page = 1
        per_page = 100
        while True:
            url = (
                f"{self.base_url}/repos/{owner}/{repo}/issues"
                f"?state=open&per_page={per_page}&page={page}"
            )
            data = self._get(url, timeout=30).json()
            if not isinstance(data, list) or not data:
                break
            for item in data:
                if not isinstance(item, dict):
                    continue
                # Issues API includes pull requests; skip those.
                if "pull_request" in item:
                    continue
                title = item.get("title")
                if isinstance(title, str) and title:
                    titles.add(title)
            if len(data) < per_page:
                break
            page += 1
            if page > 50:
                # Safety cap: 5000 open issues is enough for dedupe purposes.
                break
        return titles

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> dict:
        """Create a GitHub issue via POST /repos/{owner}/{repo}/issues.

        If GitHub rejects unknown labels (HTTP 422), retries once without labels so
        issue creation still succeeds on repos that have not pre-created label names.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        payload: dict = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels

        def _post(body_payload: dict) -> requests.Response:
            try:
                return requests.post(url, headers=self.headers, json=body_payload, timeout=30)
            except requests.RequestException as error:
                raise GitHubAPIError(
                    f"Could not connect to GitHub API while creating issue: {error}"
                ) from error

        response = _post(payload)
        if (
            response.status_code == 422
            and labels
            and "label" in response.text.lower()
        ):
            # Unknown labels: create the issue without labels rather than failing hard.
            payload_no_labels = {"title": title, "body": body}
            response = _post(payload_no_labels)

        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            raise GitHubAPIError("GitHub API rate limit exceeded. Provide --token or set GITHUB_TOKEN.")
        if response.status_code == 404:
            raise GitHubAPIError(
                "Repository was not found or issues are disabled. Check the URL and token permissions."
            )
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            raise GitHubAPIError(
                f"GitHub API request failed while creating issue: "
                f"{response.status_code} {response.text[:200]}"
            ) from error
        return response.json()
