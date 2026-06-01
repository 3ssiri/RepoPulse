import base64

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
        data = self._get(
            f"{self.base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
            timeout=30,
        ).json()
        return data.get("tree", [])

    def get_file_content(self, owner: str, repo: str, path: str) -> str | None:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
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
