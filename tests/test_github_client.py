import base64

import requests

from repopulse.github_client import GitHubAPIError, GitHubClient


def test_github_client_wraps_network_errors(monkeypatch):
    def raise_connection_error(*args, **kwargs):
        raise requests.ConnectionError("network blocked")

    monkeypatch.setattr(requests, "get", raise_connection_error)

    try:
        GitHubClient().get_repo("owner", "repo")
    except GitHubAPIError as error:
        assert "Could not connect to GitHub API" in str(error)
    else:
        raise AssertionError("Expected GitHubAPIError")


def test_get_file_content_includes_ref_query(monkeypatch):
    captured: dict = {}

    class FakeResponse:
        status_code = 200
        headers = None

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "encoding": "base64",
                "content": base64.b64encode(b"hello world").decode("ascii"),
            }

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    content = GitHubClient().get_file_content("owner", "repo", "README.md", ref="feature/foo")

    assert content == "hello world"
    assert captured["url"] == "https://api.github.com/repos/owner/repo/contents/README.md?ref=feature%2Ffoo"


def test_get_file_content_omits_ref_query_when_none(monkeypatch):
    captured: dict = {}

    class FakeResponse:
        status_code = 200
        headers = None

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "encoding": "base64",
                "content": base64.b64encode(b"plain").decode("ascii"),
            }

    def fake_get(url, headers=None, timeout=None):
        captured["url"] = url
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    content = GitHubClient().get_file_content("owner", "repo", "README.md")

    assert content == "plain"
    assert captured["url"] == "https://api.github.com/repos/owner/repo/contents/README.md"
    assert "?ref=" not in captured["url"]


def test_get_tree_error_mentions_ref(monkeypatch):
    def fake_get(url, headers=None, timeout=None):
        class FakeResponse:
            status_code = 404
            headers = None
            text = "Not Found"

            def raise_for_status(self):
                raise requests.HTTPError("404")

        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)

    try:
        GitHubClient().get_tree("owner", "repo", "missing-branch")
    except GitHubAPIError as error:
        message = str(error)
        assert "missing-branch" in message
        assert "owner/repo" in message
    else:
        raise AssertionError("Expected GitHubAPIError")


def test_create_issue_posts_payload(monkeypatch):
    captured: dict = {}

    class FakeResponse:
        status_code = 201
        headers = None
        text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return {"html_url": "https://github.com/owner/repo/issues/9", "number": 9}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)

    result = GitHubClient(token="ghs_x").create_issue(
        "owner",
        "repo",
        title="[RepoPulse] License: fail",
        body="body text",
        labels=["repopulse", "health-check", "license"],
    )

    assert result["number"] == 9
    assert captured["url"] == "https://api.github.com/repos/owner/repo/issues"
    assert captured["json"]["title"] == "[RepoPulse] License: fail"
    assert captured["json"]["labels"] == ["repopulse", "health-check", "license"]
    assert captured["headers"]["Authorization"] == "Bearer ghs_x"


def test_create_issue_retries_without_labels_on_422(monkeypatch):
    posts: list[dict] = []

    class FakeResponse:
        def __init__(self, status_code: int, text: str = "", payload: dict | None = None):
            self.status_code = status_code
            self.headers = {}
            self.text = text
            self._payload = payload or {}

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(str(self.status_code))

        def json(self):
            return self._payload

    def fake_post(url, headers=None, json=None, timeout=None):
        posts.append(json or {})
        if "labels" in (json or {}):
            return FakeResponse(422, text='{"message":"Invalid label"}')
        return FakeResponse(201, payload={"number": 3, "html_url": "https://github.com/o/r/issues/3"})

    monkeypatch.setattr(requests, "post", fake_post)

    result = GitHubClient(token="ghs_x").create_issue(
        "o",
        "r",
        title="t",
        body="b",
        labels=["repopulse", "missing-label"],
    )

    assert result["number"] == 3
    assert len(posts) == 2
    assert "labels" in posts[0]
    assert "labels" not in posts[1]
