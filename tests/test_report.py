from repopulse.models import CheckResult, HealthReport, RepositoryInfo
from repopulse.report import render_markdown


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
