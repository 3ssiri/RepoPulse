"""Build GitHub issue payloads from a RepoPulse health report."""

from __future__ import annotations

from repopulse.models import CheckResult, HealthReport
from repopulse.report import format_check_issue_body

DEFAULT_ISSUE_STATUSES: set[str] = {"fail", "warn"}
TITLE_MAX_LEN = 80
BASE_LABELS = ("repopulse", "health-check")


def _truncate_title(title: str, max_len: int = TITLE_MAX_LEN) -> str:
    if len(title) <= max_len:
        return title
    if max_len <= 3:
        return title[:max_len]
    return title[: max_len - 3] + "..."


def issue_title_for_check(check: CheckResult) -> str:
    """Stable issue title; truncated to GitHub-friendly length."""
    return _truncate_title(f"[RepoPulse] {check.title}: {check.status}")


def issue_labels_for_check(check: CheckResult, extra: list[str] | None = None) -> list[str]:
    labels: list[str] = [BASE_LABELS[0], BASE_LABELS[1], check.key]
    if extra:
        for label in extra:
            if label and label not in labels:
                labels.append(label)
    return labels


def issue_payloads_from_report(
    report: HealthReport,
    *,
    labels: list[str] | None = None,
    statuses: set[str] | None = None,
) -> list[dict]:
    """Build one create-issue payload per matching check.

    Status filter is strict on ``check.status`` (default: fail + warn).
    Pure ``pass`` checks are never opened even if they carry recommendations.
    """
    selected = statuses if statuses is not None else set(DEFAULT_ISSUE_STATUSES)
    full_name = report.repository.full_name
    payloads: list[dict] = []
    for check in report.checks:
        if check.status not in selected:
            continue
        payloads.append(
            {
                "title": issue_title_for_check(check),
                "body": format_check_issue_body(check, full_name),
                "labels": issue_labels_for_check(check, labels),
            }
        )
    return payloads
