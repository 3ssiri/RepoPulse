from pathlib import Path
from unittest.mock import MagicMock

from typer.testing import CliRunner

from repopulse.analyzer import build_health_report
from repopulse.cli import app, scan_target
from repopulse.models import CheckResult, HealthReport, RepositoryInfo
from repopulse.settings import RepoPulseConfig


def test_scan_command_rejects_non_github_url():
    result = CliRunner().invoke(app, ["scan", "https://google.com/test"])

    assert result.exit_code == 1
    assert "Only github.com URLs are supported" in result.output


def sample_report(score: int = 78, default_branch: str = "main") -> HealthReport:
    return HealthReport(
        repository=RepositoryInfo(
            owner="owner",
            name="repo",
            full_name="owner/repo",
            url="https://github.com/owner/repo",
            default_branch=default_branch,
            private=False,
            stars=1,
            forks=0,
            open_issues=0,
            last_pushed_at="2026-06-01T00:00:00Z",
        ),
        checks=[
            CheckResult(
                key="readme",
                title="README Quality",
                status="pass",
                score=20,
                max_score=20,
                message="ok",
            )
        ],
        total_score=score,
        grade="Good",
    )


def test_scan_writes_json_output_file(monkeypatch):
    monkeypatch.setattr(
        "repopulse.cli.build_health_report",
        lambda client, owner, repo, config, ref=None: sample_report(),
    )
    output = Path("tests/.tmp-report.json")

    result = CliRunner().invoke(app, ["scan", "https://github.com/owner/repo", "--format", "json", "--output", str(output)])

    try:
        assert result.exit_code == 0
        assert '"total_score": 78' in output.read_text(encoding="utf-8")
    finally:
        output.unlink(missing_ok=True)


def test_scan_fail_under_exits_nonzero(monkeypatch):
    monkeypatch.setattr(
        "repopulse.cli.build_health_report",
        lambda client, owner, repo, config, ref=None: sample_report(score=74),
    )

    result = CliRunner().invoke(app, ["scan", "https://github.com/owner/repo", "--fail-under", "75", "--quiet"])

    assert result.exit_code == 2
    assert "below required threshold" in result.output


def test_scan_passes_url_ref_to_build_health_report(monkeypatch):
    captured: dict = {}

    def fake_build(client, owner, repo, config, ref=None):
        captured["owner"] = owner
        captured["repo"] = repo
        captured["ref"] = ref
        return sample_report(default_branch=ref or "main")

    monkeypatch.setattr("repopulse.cli.build_health_report", fake_build)

    result = CliRunner().invoke(
        app,
        ["scan", "https://github.com/owner/repo/tree/feature/foo", "--format", "json", "--quiet"],
    )

    assert result.exit_code == 0
    assert captured["owner"] == "owner"
    assert captured["repo"] == "repo"
    assert captured["ref"] == "feature/foo"


def test_scan_ref_option_overrides_url_ref(monkeypatch):
    captured: dict = {}

    def fake_build(client, owner, repo, config, ref=None):
        captured["ref"] = ref
        return sample_report(default_branch=ref or "main")

    monkeypatch.setattr("repopulse.cli.build_health_report", fake_build)

    result = CliRunner().invoke(
        app,
        [
            "scan",
            "https://github.com/owner/repo/tree/from-url",
            "--ref",
            "from-cli",
            "--format",
            "json",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert captured["ref"] == "from-cli"


def test_scan_progress_shows_owner_repo_at_ref(monkeypatch):
    monkeypatch.setattr(
        "repopulse.cli.build_health_report",
        lambda client, owner, repo, config, ref=None: sample_report(default_branch=ref or "main"),
    )

    result = CliRunner().invoke(
        app,
        ["scan", "https://github.com/owner/repo/tree/develop"],
    )

    assert result.exit_code == 0
    assert "owner/repo@develop" in result.output


def test_scan_target_ref_kwarg_and_url(monkeypatch):
    captured: dict = {}

    def fake_build(client, owner, repo, config, ref=None):
        captured["ref"] = ref
        return sample_report()

    monkeypatch.setattr("repopulse.cli.build_health_report", fake_build)

    scan_target(
        "https://github.com/owner/repo/releases/tag/v1.0.0",
        token=None,
        scan_config=RepoPulseConfig(),
        quiet=True,
        ref=None,
    )
    assert captured["ref"] == "v1.0.0"

    scan_target(
        "https://github.com/owner/repo/releases/tag/v1.0.0",
        token=None,
        scan_config=RepoPulseConfig(),
        quiet=True,
        ref="override",
    )
    assert captured["ref"] == "override"


def test_build_health_report_uses_ref_for_tree_and_content():
    """Analyzer passes tree_ref to get_tree and get_file_content; explicit ref labels default_branch."""
    client = MagicMock()
    client.get_repo.return_value = {
        "name": "repo",
        "full_name": "owner/repo",
        "html_url": "https://github.com/owner/repo",
        "default_branch": "main",
        "private": False,
        "stargazers_count": 0,
        "forks_count": 0,
        "open_issues_count": 0,
        "pushed_at": "2026-06-01T00:00:00Z",
        "description": None,
    }
    client.get_tree.return_value = (
        [{"path": "README.md", "type": "blob", "size": 10}],
        False,
    )
    client.get_file_content.return_value = "# Hello\n\nA decent readme body for scoring."

    report = build_health_report(client, "owner", "repo", ref="feature/bar")

    client.get_tree.assert_called_once_with("owner", "repo", "feature/bar")
    assert client.get_file_content.call_count >= 1
    for call in client.get_file_content.call_args_list:
        assert call.kwargs.get("ref") == "feature/bar" or (len(call.args) >= 4 and call.args[3] == "feature/bar")
    assert report.repository.default_branch == "feature/bar"


def test_build_health_report_without_ref_uses_default_branch():
    client = MagicMock()
    client.get_repo.return_value = {
        "name": "repo",
        "full_name": "owner/repo",
        "html_url": "https://github.com/owner/repo",
        "default_branch": "develop",
        "private": False,
        "stargazers_count": 0,
        "forks_count": 0,
        "open_issues_count": 0,
        "pushed_at": "2026-06-01T00:00:00Z",
        "description": None,
    }
    client.get_tree.return_value = ([], False)
    client.get_file_content.return_value = None

    report = build_health_report(client, "owner", "repo")

    client.get_tree.assert_called_once_with("owner", "repo", "develop")
    assert report.repository.default_branch == "develop"


def _report_with_fail() -> HealthReport:
    return HealthReport(
        repository=RepositoryInfo(
            owner="owner",
            name="repo",
            full_name="owner/repo",
            url="https://github.com/owner/repo",
            default_branch="main",
            private=False,
            stars=0,
            forks=0,
            open_issues=0,
        ),
        checks=[
            CheckResult(
                key="license",
                title="License",
                status="fail",
                score=0,
                max_score=10,
                message="No license",
                recommendations=["Add LICENSE"],
            ),
            CheckResult(
                key="readme",
                title="README Quality",
                status="pass",
                score=20,
                max_score=20,
                message="ok",
            ),
        ],
        total_score=50,
        grade="Fair",
    )


def test_create_issues_requires_dry_run_or_yes(monkeypatch):
    monkeypatch.setattr(
        "repopulse.cli.scan_target",
        lambda *args, **kwargs: _report_with_fail(),
    )
    result = CliRunner().invoke(app, ["create-issues", "https://github.com/owner/repo"])
    assert result.exit_code == 1
    assert "--dry-run" in result.output or "--yes" in result.output


def test_create_issues_dry_run(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(
        "repopulse.cli.scan_target",
        lambda *args, **kwargs: _report_with_fail(),
    )
    result = CliRunner().invoke(
        app,
        ["create-issues", "https://github.com/owner/repo", "--dry-run", "--quiet"],
    )
    assert result.exit_code == 0
    assert "[RepoPulse] License: fail" in result.output
    assert "Add LICENSE" in result.output


def test_create_issues_yes_calls_api(monkeypatch):
    calls: list[dict] = []

    class FakeClient:
        def __init__(self, token=None):
            self.token = token

        def list_open_issue_titles(self, owner, repo):
            return set()

        def create_issue(self, owner, repo, title, body, labels=None):
            calls.append(
                {
                    "owner": owner,
                    "repo": repo,
                    "title": title,
                    "body": body,
                    "labels": labels,
                }
            )
            return {"html_url": f"https://github.com/{owner}/{repo}/issues/1"}

    monkeypatch.setattr(
        "repopulse.cli.scan_target",
        lambda *args, **kwargs: _report_with_fail(),
    )
    monkeypatch.setattr("repopulse.cli.GitHubClient", FakeClient)

    result = CliRunner().invoke(
        app,
        [
            "create-issues",
            "https://github.com/owner/repo",
            "--yes",
            "--token",
            "ghs_test",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0]["owner"] == "owner"
    assert calls[0]["repo"] == "repo"
    assert calls[0]["title"] == "[RepoPulse] License: fail"
    assert "repopulse" in calls[0]["labels"]


def test_create_issues_dedupes_open_titles(monkeypatch):
    create_calls: list[str] = []

    class FakeClient:
        def __init__(self, token=None):
            pass

        def list_open_issue_titles(self, owner, repo):
            return {"[RepoPulse] License: fail"}

        def create_issue(self, owner, repo, title, body, labels=None):
            create_calls.append(title)
            return {"html_url": f"https://github.com/{owner}/{repo}/issues/2"}

    monkeypatch.setattr(
        "repopulse.cli.scan_target",
        lambda *args, **kwargs: _report_with_fail(),
    )
    monkeypatch.setattr("repopulse.cli.GitHubClient", FakeClient)

    result = CliRunner().invoke(
        app,
        [
            "create-issues",
            "https://github.com/owner/repo",
            "--yes",
            "--token",
            "ghs_test",
        ],
    )

    assert result.exit_code == 0
    assert create_calls == []
    assert "Skip" in result.output or "already open" in result.output


def test_create_issues_no_dedupe_forces_create(monkeypatch):
    create_calls: list[str] = []

    class FakeClient:
        def __init__(self, token=None):
            pass

        def list_open_issue_titles(self, owner, repo):
            raise AssertionError("list_open_issue_titles should not be called with --no-dedupe")

        def create_issue(self, owner, repo, title, body, labels=None):
            create_calls.append(title)
            return {"html_url": f"https://github.com/{owner}/{repo}/issues/3"}

    monkeypatch.setattr(
        "repopulse.cli.scan_target",
        lambda *args, **kwargs: _report_with_fail(),
    )
    monkeypatch.setattr("repopulse.cli.GitHubClient", FakeClient)

    result = CliRunner().invoke(
        app,
        [
            "create-issues",
            "https://github.com/owner/repo",
            "--yes",
            "--token",
            "ghs_test",
            "--no-dedupe",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert create_calls == ["[RepoPulse] License: fail"]


def test_create_issues_local_yes_without_github_remote_errors(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "repopulse.cli.scan_target",
        lambda *args, **kwargs: _report_with_fail(),
    )
    result = CliRunner().invoke(
        app,
        ["create-issues", str(tmp_path), "--yes", "--token", "ghs_test"],
    )
    assert result.exit_code == 1
    assert "GitHub" in result.output


def test_compare_passes_per_side_refs(monkeypatch):
    calls: list[dict] = []

    def fake_scan(target, **kwargs):
        calls.append({"target": target, "ref": kwargs.get("ref")})
        return sample_report()

    monkeypatch.setattr("repopulse.cli.scan_target", fake_scan)

    result = CliRunner().invoke(
        app,
        [
            "compare",
            "https://github.com/owner/repo",
            "https://github.com/owner/repo",
            "--baseline-ref",
            "main",
            "--target-ref",
            "feature/x",
            "--format",
            "summary",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert len(calls) == 2
    assert calls[0]["ref"] == "main"
    assert calls[1]["ref"] == "feature/x"


def test_create_issues_yes_requires_token_before_scan(monkeypatch):
    scanned = {"called": False}

    def boom(*args, **kwargs):
        scanned["called"] = True
        return _report_with_fail()

    monkeypatch.setattr("repopulse.cli.scan_target", boom)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    result = CliRunner().invoke(
        app,
        ["create-issues", "https://github.com/owner/repo", "--yes"],
    )
    assert result.exit_code == 1
    assert "token" in result.output.lower()
    assert scanned["called"] is False
