from repopulse.models import CheckResult
from repopulse.scoring import apply_score_config, calculate_max_score, calculate_total_score, get_grade
from repopulse.settings import RepoPulseConfig, load_config


def test_load_config_reads_yaml(tmp_path):
    config_path = tmp_path / ".repopulse.yml"
    config_path.write_text(
        """
disabled_checks:
  - activity
weights:
  readme: 30
fail_under: 85
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.disabled_checks == ["activity"]
    assert config.weights == {"readme": 30}
    assert config.fail_under == 85


def test_score_config_disables_checks_and_reweights():
    checks = [
        CheckResult(
            key="readme",
            title="README",
            status="pass",
            score=10,
            max_score=20,
            message="ok",
        ),
        CheckResult(
            key="activity",
            title="Activity",
            status="pass",
            score=10,
            max_score=10,
            message="ok",
        ),
    ]
    config = RepoPulseConfig(disabled_checks=["activity"], weights={"readme": 40})

    adjusted = apply_score_config(checks, config)

    assert [check.key for check in adjusted] == ["readme"]
    assert adjusted[0].score == 20
    assert adjusted[0].max_score == 40
    assert calculate_max_score(adjusted) == 40
    assert calculate_total_score(adjusted, 40) == 20
    assert get_grade(20, 40) == "Weak"
