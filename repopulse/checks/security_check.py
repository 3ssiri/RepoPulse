from typing import Literal

from repopulse.models import CheckResult, FileItem
from repopulse.utils import find_file

# Content-light tokens for common security automation (names/workflow text only).
SCAN_TOKENS = (
    "codeql",
    "gitleaks",
    "trivy",
    "snyk",
    "semgrep",
    "bandit",
    "secret-scan",
    "secret scanning",
    "dependency-review",
    "osv-scanner",
)


def run_security_check(files: list[FileItem], workflow_contents: dict[str, str] | None = None) -> CheckResult:
    """Advisory security baseline: policy + Dependabot + scanning signals."""
    status: Literal["pass", "warn", "fail"]
    workflow_contents = workflow_contents or {}
    has_security_policy = find_file(files, {"SECURITY.md"}) is not None
    has_dependabot = find_file(files, {"dependabot.yml", "dependabot.yaml"}) is not None
    # Dependabot may also live under .github/
    if not has_dependabot:
        has_dependabot = any(
            file.path.lower().endswith(("dependabot.yml", "dependabot.yaml")) for file in files if file.type == "blob"
        )

    workflow_text = " ".join(workflow_contents.values()).lower()
    workflow_names = " ".join(
        file.path.lower() for file in files if file.path.lower().startswith(".github/workflows/")
    )
    signal = f"{workflow_names} {workflow_text}"
    has_codeql = "codeql" in signal
    extra_scanners = sorted({token for token in SCAN_TOKENS if token != "codeql" and token in signal})
    has_any_scanner = has_codeql or bool(extra_scanners)

    found: list[str] = []
    if has_security_policy:
        found.append("SECURITY.md")
    if has_dependabot:
        found.append("Dependabot")
    if has_codeql:
        found.append("CodeQL")
    found.extend(extra_scanners)

    missing: list[str] = []
    if not has_security_policy:
        missing.append("Add a SECURITY.md policy describing how to report vulnerabilities.")
    if not has_dependabot:
        missing.append("Enable Dependabot (`.github/dependabot.yml`) for dependency updates.")
    if not has_any_scanner:
        missing.append("Add automated security scanning such as CodeQL, gitleaks, Trivy, or Semgrep in CI.")

    if has_security_policy and has_dependabot and has_any_scanner:
        status = "pass"
        recommendations: list[str] = []
    elif found:
        status = "warn"
        recommendations = missing
    else:
        status = "warn"
        recommendations = missing or [
            "Add SECURITY.md and automated security scanning such as Dependabot or CodeQL."
        ]

    message = (
        "Security signals detected: " + ", ".join(found) + "."
        if found
        else "No baseline security signals detected."
    )
    return CheckResult(
        key="security",
        title="Security Baseline",
        status=status,
        score=0,
        max_score=0,
        message=message,
        recommendations=recommendations,
    )
