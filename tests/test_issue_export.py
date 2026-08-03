from repopulse.issue_export import (
    DEFAULT_ISSUE_STATUSES,
    issue_payloads_from_report,
    issue_title_for_check,
)
from repopulse.models import CheckResult, HealthReport, RepositoryInfo


def _report_with_checks(checks: list[CheckResult]) -> HealthReport:
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
        checks=checks,
        total_score=50,
        grade="Fair",
        recommendations=[],
    )


def test_default_statuses_are_fail_and_warn():
    assert DEFAULT_ISSUE_STATUSES == {"fail", "warn"}


def test_issue_payloads_one_per_fail_or_warn():
    report = _report_with_checks(
        [
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
                message="ok",
                recommendations=[],
            ),
            CheckResult(
                key="tests",
                title="Tests",
                status="warn",
                score=8,
                max_score=15,
                message="Limited tests.",
                recommendations=[],
            ),
        ]
    )

    payloads = issue_payloads_from_report(report)

    assert len(payloads) == 2
    titles = [p["title"] for p in payloads]
    assert titles == ["[RepoPulse] License: fail", "[RepoPulse] Tests: warn"]
    assert payloads[0]["labels"] == ["repopulse", "health-check", "license"]
    assert payloads[1]["labels"] == ["repopulse", "health-check", "tests"]
    assert "Add a LICENSE file." in payloads[0]["body"]
    assert "Review this check and improve the repository." in payloads[1]["body"]
    assert "**Repository:** owner/repo" in payloads[0]["body"]


def test_pass_with_recommendations_excluded_by_default():
    report = _report_with_checks(
        [
            CheckResult(
                key="security",
                title="Security",
                status="pass",
                score=10,
                max_score=10,
                message="Baseline security present.",
                recommendations=["Consider enabling Dependabot."],
            ),
        ]
    )

    assert issue_payloads_from_report(report) == []


def test_status_filter_and_extra_labels():
    report = _report_with_checks(
        [
            CheckResult(
                key="license",
                title="License",
                status="fail",
                score=0,
                max_score=10,
                message="missing",
                recommendations=["Add LICENSE"],
            ),
            CheckResult(
                key="tests",
                title="Tests",
                status="warn",
                score=5,
                max_score=15,
                message="weak",
            ),
            CheckResult(
                key="readme",
                title="README Quality",
                status="pass",
                score=20,
                max_score=20,
                message="ok",
            ),
        ]
    )

    payloads = issue_payloads_from_report(
        report,
        labels=["team-x", "repopulse"],
        statuses={"fail"},
    )

    assert len(payloads) == 1
    assert payloads[0]["title"] == "[RepoPulse] License: fail"
    assert payloads[0]["labels"] == ["repopulse", "health-check", "license", "team-x"]


def test_title_truncation():
    check = CheckResult(
        key="long",
        title="A" * 100,
        status="fail",
        score=0,
        max_score=10,
        message="x",
    )
    title = issue_title_for_check(check)
    assert len(title) == 80
    assert title.endswith("...")
    assert title.startswith("[RepoPulse] ")
