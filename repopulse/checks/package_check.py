from repopulse.models import CheckResult, FileItem
from repopulse.utils import find_file, parse_json_content


def run_package_check(files: list[FileItem], package_json_content: str | None = None) -> CheckResult:
    package = parse_json_content(package_json_content)
    scripts = package.get("scripts", {}) if isinstance(package.get("scripts"), dict) else {}
    script_keys = {key for key in ("dev", "build", "test", "lint") if key in scripts and str(scripts[key]).strip()}

    has_pyproject = find_file(files, {"pyproject.toml"}) is not None
    has_requirements = find_file(files, {"requirements.txt"}) is not None
    has_package_json = find_file(files, {"package.json"}) is not None

    if has_package_json and len(script_keys) >= 3:
        score = 5
    elif has_package_json and script_keys:
        score = 3
    elif has_pyproject or has_requirements:
        score = 3
    else:
        score = 0

    return CheckResult(
        key="package_scripts",
        title="Package Scripts",
        status="pass" if score == 5 else "warn" if score else "fail",
        score=score,
        max_score=5,
        message="Package or project commands are documented." if score else "No package scripts or Python project config detected.",
        recommendations=[] if score == 5 else ["Add clear dev, build, test, or lint commands in package metadata."],
    )
