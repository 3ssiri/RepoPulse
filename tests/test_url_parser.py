import pytest

from repopulse.url_parser import parse_github_url


def test_parse_github_url():
    owner, repo = parse_github_url("https://github.com/3ssiri/school-attenda")

    assert owner == "3ssiri"
    assert repo == "school-attenda"


def test_parse_github_url_strips_git_suffix():
    owner, repo = parse_github_url("https://github.com/owner/repo.git")

    assert owner == "owner"
    assert repo == "repo"


def test_invalid_url():
    with pytest.raises(ValueError, match="Only github.com URLs are supported"):
        parse_github_url("https://google.com/test")
