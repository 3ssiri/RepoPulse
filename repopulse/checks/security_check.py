from repopulse.models import CheckResult, FileItem
from repopulse.utils import find_file


def run_security_check(files: list[FileItem], workflow_contents: dict[str, str] | None = None) -> CheckResult:
    workflow_contents = workflow_contents or {}
    has_security_policy = find_file(files, {"SECURITY.md"}) is not None
    has_dependabot = find_file(files, {"dependabot.yml", "dependabot.yaml"}) is not None
    workflow_text = " ".join(workflow_contents.values()).lower()
    workflow_names = " ".join(file.path.lower() for file in files if file.path.lower().startswith(".github/workflows/"))
    has_codeql = "codeql" in workflow_text or "codeql" in workflow_names

    found = []
    if has_security_policy:
        found.append("SECURITY.md")
    if has_dependabot:
        found.append("Dependabot")
    if has_codeql:
        found.append("CodeQL")

    if len(found) >= 3:
        status = "pass"
        recommendations: list[str] = []
    elif found:
        status = "warn"
        recommendations = ["Add SECURITY.md, Dependabot, and CodeQL for stronger baseline security."]
    else:
        status = "warn"
        recommendations = ["Add SECURITY.md and automated security scanning such as Dependabot or CodeQL."]

    message = "Security signals detected: " + ", ".join(found) + "." if found else "No baseline security signals detected."
    return CheckResult(
        key="security",
        title="Security Baseline",
        status=status,
        score=0,
        max_score=0,
        message=message,
        recommendations=recommendations,
    )
