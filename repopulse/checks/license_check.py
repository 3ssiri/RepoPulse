from pathlib import PurePosixPath

from repopulse.models import CheckResult, FileItem

# Exact basenames (case-insensitive via lower()).
LICENSE_EXACT = {
    "license",
    "license.md",
    "license.txt",
    "license.rst",
    "licence",
    "licence.md",
    "licence.txt",
    "licence.rst",
    "copying",
    "copying.txt",
    "copying.md",
    "unlicense",
}


def _is_root_license_file(path: str) -> bool:
    """Accept common OSS license filenames at repository root only."""
    pure = PurePosixPath(path)
    if len(pure.parts) != 1:
        return False
    name = pure.name.lower()
    if name in LICENSE_EXACT:
        return True
    # e.g. LICENSE-MIT, LICENSE.APACHE-2.0
    return name.startswith(("license.", "licence.", "license-", "licence-"))


def run_license_check(files: list[FileItem]) -> CheckResult:
    found = next(
        (file.path for file in files if file.type == "blob" and _is_root_license_file(file.path)),
        None,
    )
    if found:
        return CheckResult(
            key="license",
            title="License",
            status="pass",
            score=10,
            max_score=10,
            message=f"License file found ({found}).",
        )
    return CheckResult(
        key="license",
        title="License",
        status="fail",
        score=0,
        max_score=10,
        message="No license file found at repository root.",
        recommendations=[
            "Add a root LICENSE file (LICENSE, LICENSE.md, LICENSE.txt, or COPYING are recognized)."
        ],
    )
