from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator


class RepoPulseConfig(BaseModel):
    disabled_checks: list[str] = Field(default_factory=list)
    weights: dict[str, int] = Field(default_factory=dict)
    fail_under: int | None = Field(default=None, ge=0, le=100)

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


def load_config(path: Path | None = None) -> RepoPulseConfig:
    config_path = path or Path(".repopulse.yml")
    if not config_path.exists():
        return RepoPulseConfig()

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as error:
        raise ValueError(f"Could not parse config file {config_path}: {error}") from error

    if not isinstance(raw, dict):
        raise ValueError(f"Config file {config_path} must contain a YAML object.")

    try:
        return RepoPulseConfig.model_validate(raw)
    except ValidationError as error:
        raise ValueError(f"Invalid RepoPulse config in {config_path}: {error}") from error


def config_to_public_dict(config: RepoPulseConfig) -> dict[str, Any]:
    data = config.model_dump(exclude_none=True)
    return {key: value for key, value in data.items() if value not in ({}, [])}
