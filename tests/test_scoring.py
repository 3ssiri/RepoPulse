from repopulse.models import CheckResult
from repopulse.scoring import calculate_total_score, get_grade


def test_grade_good():
    assert get_grade(80) == "Good"


def test_calculate_total_score_caps_at_100():
    checks = [
        CheckResult(
            key="a",
            title="A",
            status="pass",
            score=80,
            max_score=80,
            message="ok",
        ),
        CheckResult(
            key="b",
            title="B",
            status="pass",
            score=40,
            max_score=40,
            message="ok",
        ),
    ]

    assert calculate_total_score(checks) == 100
