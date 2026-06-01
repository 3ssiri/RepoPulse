from repopulse.models import CheckResult, FileItem

STRUCTURE_DIRS = ("src/", "app/", "lib/", "components/", "docs/")
BUILD_ARTIFACTS = ("dist/", "build/", ".next/", "coverage/")


def run_structure_check(files: list[FileItem]) -> CheckResult:
    paths = [file.path.lower() for file in files]
    root_files = [path for path in paths if "/" not in path]
    has_structure = any(path.startswith(STRUCTURE_DIRS) for path in paths)
    has_artifacts = any(path.startswith(BUILD_ARTIFACTS) for path in paths)

    if has_structure and len(root_files) <= 20 and not has_artifacts:
        score = 5
    elif has_structure or len(root_files) <= 30:
        score = 3
    else:
        score = 1

    return CheckResult(
        key="structure",
        title="Project Structure",
        status="pass" if score == 5 else "warn",
        score=score,
        max_score=5,
        message="Project structure looks organized." if score == 5 else "Project structure could be clearer.",
        recommendations=[] if score == 5 else ["Group source code and docs into clear directories and avoid committing build artifacts."],
    )
