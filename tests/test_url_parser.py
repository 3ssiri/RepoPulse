import pytest

from repopulse.url_parser import parse_github_url


def test_parse_github_url_plain_ref_none():
    owner, repo, ref = parse_github_url("https://github.com/3ssiri/school-attenda")

    assert owner == "3ssiri"
    assert repo == "school-attenda"
    assert ref is None


def test_parse_github_url_strips_git_suffix():
    owner, repo, ref = parse_github_url("https://github.com/owner/repo.git")

    assert owner == "owner"
    assert repo == "repo"
    assert ref is None


def test_parse_github_url_tree_ref():
    owner, repo, ref = parse_github_url("https://github.com/owner/repo/tree/main")

    assert owner == "owner"
    assert repo == "repo"
    assert ref == "main"


def test_parse_github_url_tree_nested_branch():
    owner, repo, ref = parse_github_url("https://github.com/owner/repo/tree/feature/foo")

    assert owner == "owner"
    assert repo == "repo"
    assert ref == "feature/foo"


def test_parse_github_url_tree_deeply_nested_ref():
    owner, repo, ref = parse_github_url("https://github.com/owner/repo/tree/release/2026/08")

    assert owner == "owner"
    assert repo == "repo"
    assert ref == "release/2026/08"


def test_parse_github_url_releases_tag():
    owner, repo, ref = parse_github_url("https://github.com/owner/repo/releases/tag/v1.2.3")

    assert owner == "owner"
    assert repo == "repo"
    assert ref == "v1.2.3"


def test_parse_github_url_releases_tag_with_slash():
    owner, repo, ref = parse_github_url("https://github.com/owner/repo/releases/tag/releases/v2")

    assert owner == "owner"
    assert repo == "repo"
    assert ref == "releases/v2"


def test_parse_github_url_ignores_blob_path():
    """Paths other than tree/releases-tag still yield owner/repo with no ref."""
    owner, repo, ref = parse_github_url("https://github.com/owner/repo/blob/main/README.md")

    assert owner == "owner"
    assert repo == "repo"
    assert ref is None


def test_invalid_url():
    with pytest.raises(ValueError, match="Only github.com URLs are supported"):
        parse_github_url("https://google.com/test")


def test_invalid_tree_missing_ref():
    with pytest.raises(ValueError, match="missing ref"):
        parse_github_url("https://github.com/owner/repo/tree")


def test_invalid_release_missing_tag():
    with pytest.raises(ValueError, match="missing tag"):
        parse_github_url("https://github.com/owner/repo/releases/tag")
