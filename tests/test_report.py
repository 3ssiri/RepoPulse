from repopulse.models import CheckResult, HealthReport, RepositoryInfo
from repopulse.report import render_issues, render_json, render_markdown, render_summary


def test_render_markdown_contains_score_and_recommendations():
    report = HealthReport(
        repository=RepositoryInfo(
            owner="3ssiri",
            name="school-attenda",
            full_name="3ssiri/school-attenda",
            description="Demo",
            url="https://github.com/3ssiri/school-attenda",
            default_branch="main",
            private=False,
            stars=0,
            forks=0,
            open_issues=2,
            last_pushed_at="2026-06-01T00:00:00Z",
        ),
        checks=[
            CheckResult(
                key="license",
                title="License",
                status="fail",
                score=0,
                max_score=10,
                message="No license file found.",
                recommendations=["Add a LICENSE file."],
            )
        ],
        total_score=78,
        grade="Good",
        recommendations=["Add a LICENSE file."],
    )

    markdown = render_markdown(report)

    assert "# RepoPulse Health Report" in markdown
    assert "**78 / 100 (78%) - Good**" in markdown
    assert "Add a LICENSE file." in markdown
    assert "## Attention needed" in markdown
    assert "schema `1.0`" in markdown


def test_render_json_is_pretty_json():
    report = HealthReport(
        repository=RepositoryInfo(
            owner="3ssiri",
            name="school-attenda",
            full_name="3ssiri/school-attenda",
            url="https://github.com/3ssiri/school-attenda",
            default_branch="main",
            private=False,
            stars=0,
            forks=0,
            open_issues=0,
        ),
        checks=[],
        total_score=91,
        grade="Excellent",
    )

    rendered = render_json(report)

    assert rendered.startswith("{\n")
    assert '"schema_version": "1.0"' in rendered
    assert '"grade": "Excellent"' in rendered


def test_render_summary_highlights_top_recommendations():
    report = HealthReport(
        repository=RepositoryInfo(
            owner="3ssiri",
            name="school-attenda",
            full_name="3ssiri/school-attenda",
            url="https://github.com/3ssiri/school-attenda",
            default_branch="main",
            private=False,
            stars=0,
            forks=0,
            open_issues=0,
        ),
        checks=[],
        total_score=70,
        grade="Fair",
        recommendations=["Add CI.", "Add tests.", "Add security policy.", "Add lockfile."],
    )

    summary = render_summary(report)

    assert "70 / 100 - Fair" in summary
    assert "Add CI." in summary
    assert "Add lockfile." not in summary


def test_render_issues_includes_fail_and_skips_clean_pass():
    report = HealthReport(
        repository=RepositoryInfo(
            owner="3ssiri",
            name="school-attenda",
            full_name="3ssiri/school-attenda",
            url="https://github.com/3ssiri/school-attenda",
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
                message="No license file found.",
                recommendations=["Add a LICENSE file."],
            ),
            CheckResult(
                key="readme",
                title="README Quality",
                status="pass",
                score=20,
                max_score=20,
                message="README looks solid.",
                recommendations=[],
            ),
            CheckResult(
                key="tests",
                title="Tests",
                status="warn",
                score=8,
                max_score=15,
                message="Limited test coverage signals.",
                recommendations=[],
            ),
        ],
        total_score=78,
        grade="Good",
        recommendations=["Add a LICENSE file."],
    )

    issues = render_issues(report)

    assert "# RepoPulse recommendations for 3ssiri/school-attenda" in issues
    assert "Score: 78/100 — Good" in issues
    assert "## [RepoPulse] License: fail" in issues
    assert "**Repository:** 3ssiri/school-attenda" in issues
    assert "**Score impact:** 0/10" in issues
    assert "- Add a LICENSE file." in issues
    assert "`repopulse`, `health-check`, `license`" in issues
    assert "## [RepoPulse] Tests: warn" in issues
    assert "- Review this check and improve the repository." in issues
    assert "`repopulse`, `health-check`, `tests`" in issues
    assert "---" in issues
    assert "README Quality" not in issues


def test_render_issues_includes_pass_with_recommendations():
    report = HealthReport(
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
                key="security",
                title="Security",
                status="pass",
                score=10,
                max_score=10,
                message="Baseline security present.",
                recommendations=["Consider enabling Dependabot."],
            ),
        ],
        total_score=100,
        grade="Excellent",
    )

    issues = render_issues(report)

    assert "## [RepoPulse] Security: pass" in issues
    assert "- Consider enabling Dependabot." in issues
    assert "`repopulse`, `health-check`, `security`" in issues


def test_render_issues_empty_when_all_pass_clean():
    report = HealthReport(
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
                key="readme",
                title="README Quality",
                status="pass",
                score=20,
                max_score=20,
                message="ok",
            )
        ],
        total_score=100,
        grade="Excellent",
    )

    issues = render_issues(report)

    assert "# RepoPulse recommendations for owner/repo" in issues
    assert "Score: 100/100 — Excellent" in issues
    assert "No open recommendations from RepoPulse for owner/repo (score 100/100 — Excellent)." in issues
    assert "### Action items" not in issues
