from typing import Literal

from repopulse.models import CheckResult, FileItem
from repopulse.utils import find_file

README_KEYWORDS = {
    "installation": ["install", "installation", "setup", "getting started", "quickstart", "quick start"],
    "usage": ["usage", "run", "how to use", "example", "examples", "tutorial", "api reference", "documentation"],
    "features": ["features", "what it does", "capabilities", "highlights"],
    # Optional polish — broader phrases so polished READMEs are not nagged unfairly.
    "tech_stack": [
        "tech stack",
        "built with",
        "technologies",
        "requirements",
        "dependencies",
        "requires python",
        "requires node",
        "powered by",
        "stack:",
    ],
}


def run_readme_check(files: list[FileItem], content: str | None) -> CheckResult:
    readme = find_file(files, {"README", "README.md", "README.rst"})
    if not readme:
        return CheckResult(
            key="readme",
            title="README Quality",
            status="fail",
            score=0,
            max_score=20,
            message="No README file found.",
            recommendations=["Add a README with description, installation, and usage examples."],
        )

    text = (content or "").strip()
    lower = text.lower()
    score = 8
    recommendations: list[str] = []

    if len(text) >= 80:
        score += 3
    else:
        recommendations.append("Add a clearer project description to the README.")

    scoring = {"installation": 3, "usage": 3, "features": 2, "tech_stack": 1}
    labels = {
        "installation": "installation instructions",
        "usage": "usage examples",
        "features": "a feature list",
        "tech_stack": "the tech stack",
    }
    found_sections: set[str] = set()
    for key, points in scoring.items():
        if any(keyword in lower for keyword in README_KEYWORDS[key]):
            score += points
            found_sections.add(key)
        else:
            # Skip tech_stack nag when core docs are already present (low-value noise).
            if key == "tech_stack" and {"installation", "usage"}.issubset(found_sections):
                continue
            recommendations.append(f"Document {labels[key]} in the README.")

    status: Literal["pass", "warn"] = "pass" if score >= 16 else "warn"
    return CheckResult(
        key="readme",
        title="README Quality",
        status=status,
        score=min(score, 20),
        max_score=20,
        message="README exists and was evaluated for core documentation sections.",
        recommendations=recommendations,
    )
