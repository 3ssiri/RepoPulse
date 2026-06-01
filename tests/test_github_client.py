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
