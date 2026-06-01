from repopulse.models import CheckResult, FileItem
from repopulse.utils import find_file


def run_license_check(files: list[FileItem]) -> CheckResult:
    if find_file(files, {"LICENSE", "LICENSE.md", "COPYING"}):
        return CheckResult(
            key="license",
            title="License",
            status="pass",
            score=10,
            max_score=10,
            message="License file found.",
        )
    return CheckResult(
        key="license",
        title="License",
        status="fail",
        score=0,
        max_score=10,
        message="No license file found.",
        recommendations=["Add a LICENSE file, commonly MIT or Apache 2.0 for open-source projects."],
    )
