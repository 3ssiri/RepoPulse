from typing import Literal

from pydantic import BaseModel, Field


class RepositoryInfo(BaseModel):
    owner: str
    name: str
    full_name: str
    description: str | None = None
    url: str
    default_branch: str
    private: bool
    stars: int
    forks: int
    open_issues: int
    last_pushed_at: str | None = None


class FileItem(BaseModel):
    path: str
    name: str
    type: str
    size: int | None = None


class CheckResult(BaseModel):
    key: str
    title: str
    status: Literal["pass", "warn", "fail"]
    score: int
    max_score: int
    message: str
    recommendations: list[str] = Field(default_factory=list)


class HealthReport(BaseModel):
    schema_version: str = "1.0"
    repository: RepositoryInfo
    checks: list[CheckResult]
    total_score: int
    max_score: int = 100
    grade: str
    recommendations: list[str] = Field(default_factory=list)
    config: dict = Field(default_factory=dict)
    # True when the file listing was cut short (local max-files cap or GitHub
    # tree API truncation): checks ran on a partial file list.
    scan_truncated: bool = False


class CheckDelta(BaseModel):
    """Per-check difference between two health reports."""

    key: str
    title: str
    baseline_status: str | None = None
    target_status: str | None = None
    baseline_score: int | None = None
    target_score: int | None = None
    score_delta: int = 0
    change: Literal["improved", "regressed", "unchanged", "added", "removed"]


class ComparisonReport(BaseModel):
    """Side-by-side comparison of two health scans (branches, tags, paths, or repos)."""

    schema_version: str = "1.0"
    kind: Literal["comparison"] = "comparison"
    baseline_label: str
    target_label: str
    baseline_repository: str
    target_repository: str
    baseline_score: int
    target_score: int
    baseline_max_score: int
    target_max_score: int
    score_delta: int
    baseline_grade: str
    target_grade: str
    checks: list[CheckDelta] = Field(default_factory=list)
    improved: list[str] = Field(default_factory=list)
    regressed: list[str] = Field(default_factory=list)
    unchanged: list[str] = Field(default_factory=list)
    config: dict = Field(default_factory=dict)
