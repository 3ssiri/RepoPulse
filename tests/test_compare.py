from typer.testing import CliRunner

from repopulse.cli import app
from repopulse.compare import build_comparison, has_regression
from repopulse.models import CheckResult, HealthReport, RepositoryInfo
from repopulse.report import (
    render_comparison_json,
    render_comparison_markdown,
    render_comparison_summary,
)


def _repo(name: str = "repo") -> RepositoryInfo:
    return RepositoryInfo(
        owner="owner",
        name=name,
        full_name=f"owner/{name}",
        url=f"https://github.com/owner/{name}",
        default_branch="main",
        private=False,
        stars=0,
        forks=0,
        open_issues=0,
    )


def _check(
    key: str,
    *,
    status: str = "pass",
    score: int = 10,
    max_score: int = 10,
    title: str | None = None,
) -> CheckResult:
    return CheckResult(
        key=key,
        title=title or key.title(),
        status=status,  # type: ignore[arg-type]
        score=score,
        max_score=max_score,
        message=f"{key} {status}",
    )


def _report(
    *checks: CheckResult,
    score: int | None = None,
    grade: str = "Good",
    name: str = "repo",
) -> HealthReport:
    total = score if score is not None else sum(c.score for c in checks)
    return HealthReport(
        repository=_repo(name),
        checks=list(checks),
        total_score=total,
        grade=grade,
    )


def test_build_comparison_detects_improvement_and_regression():
    baseline = _report(
        _check("readme", status="warn", score=10, max_score=20),
        _check("license", status="pass", score=10, max_score=10),
        _check("tests", status="pass", score=15, max_score=15),
        score=35,
    )
    target = _report(
        _check("readme", status="pass", score=20, max_score=20),
        _check("license", status="fail", score=0, max_score=10),
        _check("tests", status="pass", score=15, max_score=15),
        score=35,
        name="repo-pr",
    )

    comparison = build_comparison(baseline, target, baseline_label="main", target_label="pr")

    assert comparison.baseline_label == "main"
    assert comparison.target_label == "pr"
    assert comparison.score_delta == 0
    assert "readme" in comparison.improved
    assert "license" in comparison.regressed
    assert "tests" in comparison.unchanged
    by_key = {c.key: c for c in comparison.checks}
    assert by_key["readme"].change == "improved"
    assert by_key["readme"].score_delta == 10
    assert by_key["license"].change == "regressed"
    assert by_key["license"].score_delta == -10


def test_has_regression_on_score_drop():
    baseline = _report(_check("readme", score=20, max_score=20), score=80)
    target = _report(_check("readme", score=10, max_score=20, status="warn"), score=70)
    comparison = build_comparison(baseline, target)
    assert comparison.score_delta == -10
    assert has_regression(comparison)


def test_has_regression_on_check_only():
    baseline = _report(
        _check("readme", status="pass", score=20, max_score=20),
        _check("license", status="pass", score=10, max_score=10),
        score=30,
    )
    # Score same overall if we force total, but license regressed
    target = _report(
        _check("readme", status="pass", score=20, max_score=20),
        _check("license", status="fail", score=0, max_score=10),
        score=30,  # forced equal total to isolate check regression path
    )
    comparison = build_comparison(baseline, target)
    assert comparison.score_delta == 0
    assert has_regression(comparison)
    assert "license" in comparison.regressed


def test_render_comparison_formats():
    baseline = _report(_check("readme", status="warn", score=10, max_score=20), score=70, grade="Fair")
    target = _report(_check("readme", status="pass", score=20, max_score=20), score=80, grade="Good")
    comparison = build_comparison(baseline, target, baseline_label="v1", target_label="v2")

    md = render_comparison_markdown(comparison)
    assert "# RepoPulse Comparison Report" in md
    assert "v1" in md and "v2" in md
    assert "improved" in md.lower() or "Improved" in md

    summary = render_comparison_summary(comparison)
    assert "70 → 80" in summary
    assert "+10" in summary

    raw = render_comparison_json(comparison)
    assert '"kind": "comparison"' in raw
    assert '"score_delta": 10' in raw


def test_compare_cli_fail_on_regression(monkeypatch):
    baseline = _report(_check("readme", score=20, max_score=20), score=90)
    target = _report(_check("readme", status="fail", score=0, max_score=20), score=70)

    reports = iter([baseline, target])

    def fake_scan(target, **kwargs):
        return next(reports)

    monkeypatch.setattr("repopulse.cli.scan_target", fake_scan)

    result = CliRunner().invoke(
        app,
        ["compare", "https://github.com/a/b", "https://github.com/a/c", "--fail-on-regression", "--quiet"],
    )
    assert result.exit_code == 2
    assert "Regression detected" in result.output


def test_compare_cli_json(monkeypatch):
    baseline = _report(_check("readme", score=10, max_score=20, status="warn"), score=70)
    target = _report(_check("readme", score=20, max_score=20), score=80)
    reports = iter([baseline, target])
    monkeypatch.setattr("repopulse.cli.scan_target", lambda *a, **k: next(reports))

    result = CliRunner().invoke(
        app,
        [
            "compare",
            "https://github.com/a/b",
            "https://github.com/a/c",
            "--format",
            "json",
            "--baseline-label",
            "main",
            "--target-label",
            "feature",
        ],
    )
    assert result.exit_code == 0
    assert '"baseline_label": "main"' in result.output
    assert '"target_label": "feature"' in result.output
    assert '"score_delta": 10' in result.output
