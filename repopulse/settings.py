from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator

# Built-in scoring presets. Weights for scored checks sum to ~100.
# Advisory checks (dependencies, security) are not weighted here.
PROFILES: dict[str, dict[str, Any]] = {
    "strict": {
        "fail_under": 85,
        "weights": {
            "readme": 20,
            "license": 10,
            "gitignore": 10,
            "tests": 20,
            "github_actions": 20,
            "activity": 5,
            "sensitive_files": 10,
            "structure": 3,
            "package_scripts": 2,
        },
    },
    "library": {
        "fail_under": 75,
        "weights": {
            "readme": 15,
            "license": 15,
            "gitignore": 10,
            "tests": 25,
            "github_actions": 15,
            "activity": 5,
            "sensitive_files": 10,
            "structure": 5,
            "package_scripts": 0,
        },
    },
    "docs": {
        "fail_under": 70,
        "weights": {
            "readme": 35,
            "license": 10,
            "gitignore": 10,
            "tests": 10,
            "github_actions": 10,
            "activity": 10,
            "sensitive_files": 10,
            "structure": 5,
            "package_scripts": 0,
        },
    },
    # High bar before cutting a release: tests + CI + license first.
    "release": {
        "fail_under": 90,
        "weights": {
            "readme": 15,
            "license": 15,
            "gitignore": 5,
            "tests": 25,
            "github_actions": 20,
            "activity": 5,
            "sensitive_files": 10,
            "structure": 5,
            "package_scripts": 0,
        },
    },
}


class RepoPulseConfig(BaseModel):
    profile: str | None = None
    disabled_checks: list[str] = Field(default_factory=list)
    weights: dict[str, int] = Field(default_factory=dict)
    fail_under: int | None = Field(default=None, ge=0, le=100)

    @field_validator("profile")
    @classmethod
    def normalize_profile(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized:
            return None
        if normalized not in PROFILES:
            allowed = ", ".join(sorted(PROFILES))
            raise ValueError(f"Unknown profile {value!r}. Allowed profiles: {allowed}")
        return normalized

    @field_validator("disabled_checks")
    @classmethod
    def normalize_disabled_checks(cls, value: list[str]) -> list[str]:
        return [item.strip().lower() for item in value if item.strip()]

    @field_validator("weights")
    @classmethod
    def normalize_weights(cls, value: dict[str, int]) -> dict[str, int]:
        invalid = {key: score for key, score in value.items() if score < 0}
        if invalid:
            raise ValueError("weights must be zero or positive integers")
        return {key.strip().lower(): score for key, score in value.items() if key.strip()}


def resolve_config(raw: dict[str, Any]) -> dict[str, Any]:
    """Merge named profile defaults with explicit user fields.

    Merge order:
    1. Empty defaults
    2. Profile base (weights, disabled_checks, fail_under) when ``profile`` is set
    3. Explicit YAML fields overlay:
       - ``weights``: key-by-key merge (user keys win)
       - ``disabled_checks``: user list replaces profile list entirely
       - ``fail_under``: user value overrides profile value

    Configs that omit ``profile`` are returned unchanged (backward compatible).
    """
    data = dict(raw)
    profile_value = data.get("profile")
    if profile_value is None:
        return data

    if not isinstance(profile_value, str):
        raise TypeError("profile must be a string")

    profile_name = profile_value.strip().lower()
    if not profile_name:
        data["profile"] = None
        return data

    if profile_name not in PROFILES:
        allowed = ", ".join(sorted(PROFILES))
        raise ValueError(f"Unknown profile {profile_value!r}. Allowed profiles: {allowed}")

    profile = PROFILES[profile_name]
    data["profile"] = profile_name

    # weights: profile base, then user key-by-key override
    merged_weights = dict(profile.get("weights", {}))
    user_weights = data.get("weights")
    if isinstance(user_weights, dict):
        merged_weights.update(user_weights)
    if user_weights is None or isinstance(user_weights, dict):
        data["weights"] = merged_weights

    # disabled_checks: user list replaces profile list if provided
    if "disabled_checks" not in data and "disabled_checks" in profile:
        data["disabled_checks"] = list(profile["disabled_checks"])

    # fail_under: user value wins when present
    if "fail_under" not in data and "fail_under" in profile:
        data["fail_under"] = profile["fail_under"]

    return data


def load_config(path: Path | None = None) -> RepoPulseConfig:
    config_path = path or Path(".repopulse.yml")
    if not config_path.exists():
        return RepoPulseConfig()

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as error:
        raise ValueError(f"Could not parse config file {config_path}: {error}") from error

    if not isinstance(raw, dict):
        raise TypeError(f"Config file {config_path} must contain a YAML object.")

    try:
        resolved = resolve_config(raw)
        return RepoPulseConfig.model_validate(resolved)
    except (ValueError, ValidationError) as error:
        raise ValueError(f"Invalid RepoPulse config in {config_path}: {error}") from error


def config_to_public_dict(config: RepoPulseConfig) -> dict[str, Any]:
    data = config.model_dump(exclude_none=True)
    return {key: value for key, value in data.items() if value not in ({}, [])}
