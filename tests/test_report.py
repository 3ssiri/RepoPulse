from repopulse.models import CheckResult, HealthReport, RepositoryInfo
from repopulse.report import render_json, render_markdown, render_summary


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
    assert "**78 / 100 - Good**" in markdown
    assert "Add a LICENSE file." in markdown


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
