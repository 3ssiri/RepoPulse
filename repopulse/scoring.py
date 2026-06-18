from repopulse.models import CheckResult
from repopulse.settings import RepoPulseConfig


def calculate_total_score(checks: list[CheckResult], max_score: int = 100) -> int:
    return min(max_score, max(0, sum(check.score for check in checks)))


def get_grade(score: int, max_score: int = 100) -> str:
    percentage = round((score / max_score) * 100) if max_score > 0 else 0
    if percentage >= 90:
        return "Excellent"
    if percentage >= 75:
        return "Good"
    if percentage >= 60:
        return "Fair"
    if percentage >= 40:
        return "Weak"
    return "Critical"


def apply_score_config(checks: list[CheckResult], config: RepoPulseConfig) -> list[CheckResult]:
    disabled = set(config.disabled_checks)
    adjusted: list[CheckResult] = []

    for check in checks:
        if check.key.lower() in disabled:
            continue
        weight = config.weights.get(check.key.lower())
        if weight is None or check.max_score == 0:
            adjusted.append(check)
            continue
        ratio = check.score / check.max_score
        adjusted.append(check.model_copy(update={"score": round(ratio * weight), "max_score": weight}))

    return adjusted


def calculate_max_score(checks: list[CheckResult]) -> int:
    return sum(check.max_score for check in checks if check.max_score > 0)
