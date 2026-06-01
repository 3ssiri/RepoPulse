from repopulse.models import CheckResult


def calculate_total_score(checks: list[CheckResult]) -> int:
    return min(100, max(0, sum(check.score for check in checks)))


def get_grade(score: int) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Fair"
    if score >= 40:
        return "Weak"
    return "Critical"
