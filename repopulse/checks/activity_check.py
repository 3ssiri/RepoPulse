from datetime import UTC, datetime

from repopulse.models import CheckResult


def run_activity_check(last_pushed_at: str | None, now: datetime | None = None) -> CheckResult:
    if not last_pushed_at:
        return CheckResult(
            key="activity",
            title="Recent Activity",
            status="fail",
            score=0,
            max_score=10,
            message="Repository push date is unavailable.",
            recommendations=["Ensure repository metadata exposes recent activity."],
        )

    current = now or datetime.now(UTC)
    try:
        pushed = datetime.fromisoformat(last_pushed_at.replace("Z", "+00:00"))
    except ValueError:
        return CheckResult(
            key="activity",
            title="Recent Activity",
            status="fail",
            score=0,
            max_score=10,
            message="Repository push date could not be parsed.",
            recommendations=["Check the repository pushed_at metadata."],
        )

    days = (current - pushed).days
    if days <= 30:
        score = 10
    elif days <= 183:
        score = 7
    elif days <= 365:
        score = 4
    else:
        score = 1

    return CheckResult(
        key="activity",
        title="Recent Activity",
        status="pass" if score >= 7 else "warn" if score >= 4 else "fail",
        score=score,
        max_score=10,
        message=f"Last push was about {max(days, 0)} days ago.",
        recommendations=[] if score >= 7 else ["Update the repository or archive it if it is no longer maintained."],
    )
