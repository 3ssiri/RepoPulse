from pathlib import PurePosixPath

from repopulse.checks import (
    run_actions_check,
    run_activity_check,
    run_dependencies_check,
    run_gitignore_check,
    run_license_check,
    run_package_check,
    run_readme_check,
    run_security_check,
    run_sensitive_files_check,
    run_structure_check,
    run_tests_check,
)
from repopulse.github_client import GitHubClient
from repopulse.models import FileItem, HealthReport, RepositoryInfo
from repopulse.scoring import calculate_total_score, get_grade
from repopulse.utils import find_file


def repo_info_from_api(owner: str, repo: str, data: dict) -> RepositoryInfo:
    return RepositoryInfo(
        owner=owner,
        name=data.get("name", repo),
        full_name=data.get("full_name", f"{owner}/{repo}"),
        description=data.get("description"),
        url=data.get("html_url", f"https://github.com/{owner}/{repo}"),
        default_branch=data.get("default_branch", "main"),
        private=bool(data.get("private", False)),
        stars=int(data.get("stargazers_count", 0)),
        forks=int(data.get("forks_count", 0)),
        open_issues=int(data.get("open_issues_count", 0)),
        last_pushed_at=data.get("pushed_at"),
    )


def file_items_from_tree(tree: list[dict]) -> list[FileItem]:
    files: list[FileItem] = []
    for item in tree:
        path = item.get("path")
        if not path:
            continue
        files.append(
            FileItem(
                path=path,
                name=PurePosixPath(path).name,
                type=item.get("type", "blob"),
                size=item.get("size"),
            )
        )
    return files


def build_health_report(client: GitHubClient, owner: str, repo: str) -> HealthReport:
    repo_data = client.get_repo(owner, repo)
    repository = repo_info_from_api(owner, repo, repo_data)
    files = file_items_from_tree(client.get_tree(owner, repo, repository.default_branch))

    readme_file = find_file(files, {"README", "README.md", "README.rst"})
    gitignore_file = find_file(files, {".gitignore"})
    package_json = find_file(files, {"package.json"})
    pyproject = find_file(files, {"pyproject.toml"})
    workflows = [file for file in files if file.type == "blob" and file.path.lower().startswith(".github/workflows/")]

    readme_content = client.get_file_content(owner, repo, readme_file.path) if readme_file else None
    gitignore_content = client.get_file_content(owner, repo, gitignore_file.path) if gitignore_file else None
    package_content = client.get_file_content(owner, repo, package_json.path) if package_json else None
    pyproject_content = client.get_file_content(owner, repo, pyproject.path) if pyproject else None
    workflow_contents = {
        workflow.path: content
        for workflow in workflows
        if (content := client.get_file_content(owner, repo, workflow.path)) is not None
    }

    checks = [
        run_readme_check(files, readme_content),
        run_license_check(files),
        run_gitignore_check(files, gitignore_content),
        run_tests_check(files, package_content, pyproject_content),
        run_actions_check(files, workflow_contents),
        run_activity_check(repository.last_pushed_at),
        run_sensitive_files_check(files),
        run_structure_check(files),
        run_package_check(files, package_content, pyproject_content),
        run_dependencies_check(files),
        run_security_check(files, workflow_contents),
    ]
    total_score = calculate_total_score(checks)
    recommendations = [item for check in checks for item in check.recommendations]
    return HealthReport(
        repository=repository,
        checks=checks,
        total_score=total_score,
        grade=get_grade(total_score),
        recommendations=recommendations,
    )
