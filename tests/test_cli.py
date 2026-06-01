from typer.testing import CliRunner
from pathlib import Path

from repopulse.cli import app
from repopulse.models import CheckResult, HealthReport, RepositoryInfo


def test_scan_command_rejects_non_github_url():
    result = CliRunner().invoke(app, ["scan", "https://google.com/test"])

    assert result.exit_code == 1
    assert "Only github.com URLs are supported" in result.output


def sample_report(score: int = 78) -> HealthReport:
    return HealthReport(
        repository=RepositoryInfo(
            owner="owner",
            name="repo",
            full_name="owner/repo",
            url="https://github.com/owner/repo",
            default_branch="main",
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
    monkeypatch.setattr("repopulse.cli.build_health_report", lambda client, owner, repo: sample_report())
    output = Path("tests/.tmp-report.json")

    result = CliRunner().invoke(app, ["scan", "https://github.com/owner/repo", "--format", "json", "--output", str(output)])

    try:
        assert result.exit_code == 0
        assert '"total_score": 78' in output.read_text(encoding="utf-8")
    finally:
        output.unlink(missing_ok=True)


def test_scan_fail_under_exits_nonzero(monkeypatch):
    monkeypatch.setattr("repopulse.cli.build_health_report", lambda client, owner, repo: sample_report(score=74))

    result = CliRunner().invoke(app, ["scan", "https://github.com/owner/repo", "--fail-under", "75", "--quiet"])

    assert result.exit_code == 2
    assert "below required threshold" in result.output
