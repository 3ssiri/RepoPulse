from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem

SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    "credentials.json",
    "service-account.json",
    "firebase-key.json",
    "private-key.pem",
    "id_rsa",
}


def run_sensitive_files_check(files: list[FileItem]) -> CheckResult:
    found = sorted(
        file.path
        for file in files
        if file.type == "blob" and PurePosixPath(file.path).name.lower() in SENSITIVE_NAMES
    )
    if found:
        shown = ", ".join(found[:5])
        return CheckResult(
            key="sensitive_files",
            title="Sensitive Files",
            status="fail",
            score=0,
            max_score=10,
            message=f"Potential sensitive file names detected: {shown}.",
            recommendations=["Remove sensitive files from the repository and rotate any exposed credentials."],
        )
    return CheckResult(
        key="sensitive_files",
        title="Sensitive Files",
        status="pass",
        score=10,
        max_score=10,
        message="No common sensitive file names detected.",
    )
