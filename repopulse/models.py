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
    repository: RepositoryInfo
    checks: list[CheckResult]
    total_score: int
    max_score: int = 100
    grade: str
    recommendations: list[str] = Field(default_factory=list)
