from repopulse.models import CheckResult, FileItem
from repopulse.utils import find_file

IMPORTANT_PATTERNS = [".env", "node_modules", "dist", "build", "coverage", "__pycache__", ".venv", ".next", ".DS_Store"]


def run_gitignore_check(files: list[FileItem], content: str | None) -> CheckResult:
    if not find_file(files, {".gitignore"}):
        return CheckResult(
            key="gitignore",
            title=".gitignore",
            status="fail",
            score=0,
            max_score=10,
            message="No .gitignore file found.",
            recommendations=["Add a .gitignore with environment, dependency, cache, and build output patterns."],
        )

    lower = (content or "").lower()
    matched = [pattern for pattern in IMPORTANT_PATTERNS if pattern.lower() in lower]
    score = 5 + (5 if len(matched) >= 4 else 3 if len(matched) >= 2 else 0)
    recommendations = [] if score == 10 else ["Add common ignore patterns such as .env, build outputs, caches, and dependencies."]
    return CheckResult(
        key="gitignore",
        title=".gitignore",
        status="pass" if score == 10 else "warn",
        score=score,
        max_score=10,
        message=".gitignore exists and includes common patterns." if score == 10 else ".gitignore exists but misses several common patterns.",
        recommendations=recommendations,
    )
