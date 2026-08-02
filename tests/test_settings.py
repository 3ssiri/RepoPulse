import pytest

from repopulse.models import CheckResult
from repopulse.scoring import (
    apply_score_config,
    calculate_max_score,
    calculate_total_score,
    get_grade,
)
from repopulse.settings import (
    PROFILES,
    RepoPulseConfig,
    config_to_public_dict,
    load_config,
    resolve_config,
)


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
    assert config.profile is None


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


def test_profile_strict_loads_expected_defaults(tmp_path):
    config_path = tmp_path / ".repopulse.yml"
    config_path.write_text("profile: strict\n", encoding="utf-8")

    config = load_config(config_path)

    assert config.profile == "strict"
    assert config.fail_under == 85
    assert config.disabled_checks == []
    assert config.weights == PROFILES["strict"]["weights"]
    assert config.weights["readme"] == 20
    assert config.weights["tests"] == 20
    assert config.weights["github_actions"] == 20


def test_profile_user_weight_override_merges(tmp_path):
    config_path = tmp_path / ".repopulse.yml"
    config_path.write_text(
        """
profile: strict
weights:
  readme: 50
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.profile == "strict"
    assert config.weights["readme"] == 50
    # other strict weights remain
    assert config.weights["license"] == 10
    assert config.weights["tests"] == 20
    assert config.weights["github_actions"] == 20
    assert config.fail_under == 85


def test_unknown_profile_raises(tmp_path):
    config_path = tmp_path / ".repopulse.yml"
    config_path.write_text("profile: enterprise\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Unknown profile"):
        load_config(config_path)


def test_profile_release_loads_high_threshold(tmp_path):
    config_path = tmp_path / ".repopulse.yml"
    config_path.write_text("profile: release\n", encoding="utf-8")

    config = load_config(config_path)

    assert config.profile == "release"
    assert config.fail_under == 90
    assert config.weights["tests"] == 25
    assert config.weights["github_actions"] == 20
    assert sum(config.weights.values()) == 100


def test_no_profile_identical_empty_defaults(tmp_path):
    missing = load_config(tmp_path / "missing.yml")
    empty_file = tmp_path / ".repopulse.yml"
    empty_file.write_text("{}\n", encoding="utf-8")
    empty_config = load_config(empty_file)

    assert missing == RepoPulseConfig()
    assert empty_config == RepoPulseConfig()
    assert missing.profile is None
    assert missing.weights == {}
    assert missing.disabled_checks == []
    assert missing.fail_under is None


def test_apply_score_config_with_resolved_profile(tmp_path):
    config_path = tmp_path / ".repopulse.yml"
    config_path.write_text("profile: library\n", encoding="utf-8")
    config = load_config(config_path)

    checks = [
        CheckResult(
            key="tests",
            title="Tests",
            status="pass",
            score=15,
            max_score=15,
            message="ok",
        ),
        CheckResult(
            key="package_scripts",
            title="Package Scripts",
            status="pass",
            score=5,
            max_score=5,
            message="ok",
        ),
    ]

    adjusted = apply_score_config(checks, config)

    tests_check = next(c for c in adjusted if c.key == "tests")
    package_check = next(c for c in adjusted if c.key == "package_scripts")
    assert tests_check.max_score == 25
    assert tests_check.score == 25
    # weight 0 zeros contribution
    assert package_check.max_score == 0
    assert package_check.score == 0


def test_profile_disabled_checks_user_replaces(tmp_path):
    config_path = tmp_path / ".repopulse.yml"
    config_path.write_text(
        """
profile: docs
disabled_checks:
  - activity
fail_under: 60
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.profile == "docs"
    assert config.disabled_checks == ["activity"]
    assert config.fail_under == 60
    assert config.weights["readme"] == 35


def test_config_to_public_dict_includes_profile():
    config = RepoPulseConfig.model_validate(resolve_config({"profile": "strict"}))
    public = config_to_public_dict(config)

    assert public["profile"] == "strict"
    assert public["fail_under"] == 85
    assert "weights" in public


def test_profile_name_normalized_case(tmp_path):
    config_path = tmp_path / ".repopulse.yml"
    config_path.write_text("profile: STRICT\n", encoding="utf-8")

    config = load_config(config_path)
    assert config.profile == "strict"
