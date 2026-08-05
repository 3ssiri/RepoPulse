from pathlib import Path, PurePosixPath

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
from repopulse.local_source import (
    iter_local_files,
    read_local_text,
    repository_info_from_path,
)
from repopulse.models import FileItem, HealthReport, RepositoryInfo
from repopulse.scoring import (
    apply_score_config,
    calculate_max_score,
    calculate_total_score,
    get_grade,
)
from repopulse.settings import RepoPulseConfig, config_to_public_dict
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


def build_health_report_from_inputs(
    repository: RepositoryInfo,
    files: list[FileItem],
    *,
    readme_content: str | None,
    gitignore_content: str | None,
    package_content: str | None,
    pyproject_content: str | None,
    workflow_contents: dict[str, str],
    config: RepoPulseConfig | None = None,
) -> HealthReport:
    """Run the shared check pipeline and build a HealthReport."""
    config = config or RepoPulseConfig()
    checks = [
        run_readme_check(files, readme_content),
        run_license_check(files),
        run_gitignore_check(files, gitignore_content),
        run_tests_check(files, package_content, pyproject_content, workflow_contents),
        run_actions_check(files, workflow_contents),
        run_activity_check(repository.last_pushed_at),
        run_sensitive_files_check(files),
        run_structure_check(files),
        run_package_check(files, package_content, pyproject_content),
        run_dependencies_check(files),
        run_security_check(files, workflow_contents),
    ]
    checks = apply_score_config(checks, config)
    max_score = calculate_max_score(checks)
    total_score = calculate_total_score(checks, max_score)
    recommendations = [item for check in checks for item in check.recommendations]
    return HealthReport(
        repository=repository,
        checks=checks,
        total_score=total_score,
        max_score=max_score,
        grade=get_grade(total_score, max_score),
        recommendations=recommendations,
        config=config_to_public_dict(config),
    )


def _load_content_inputs(
    files: list[FileItem],
    content_loader,
) -> tuple[str | None, str | None, str | None, str | None, dict[str, str]]:
    """Resolve standard content files via a path -> content callable."""
    readme_file = find_file(files, {"README", "README.md", "README.rst"})
    gitignore_file = find_file(files, {".gitignore"})
    package_json = find_file(files, {"package.json"})
    pyproject = find_file(files, {"pyproject.toml"})
    workflows = [file for file in files if file.type == "blob" and file.path.lower().startswith(".github/workflows/")]

    readme_content = content_loader(readme_file.path) if readme_file else None
    gitignore_content = content_loader(gitignore_file.path) if gitignore_file else None
    package_content = content_loader(package_json.path) if package_json else None
    pyproject_content = content_loader(pyproject.path) if pyproject else None
    workflow_contents = {
        workflow.path: content
        for workflow in workflows
        if (content := content_loader(workflow.path)) is not None
    }
    return readme_content, gitignore_content, package_content, pyproject_content, workflow_contents


def build_health_report(
    client: GitHubClient,
    owner: str,
    repo: str,
    config: RepoPulseConfig | None = None,
    ref: str | None = None,
) -> HealthReport:
    config = config or RepoPulseConfig()
    repo_data = client.get_repo(owner, repo)
    repository = repo_info_from_api(owner, repo, repo_data)
    # Tree + content loads use the explicit ref when given, otherwise the API default branch.
    tree_ref = ref or repository.default_branch
    # When an explicit ref is scanned, surface it as default_branch so reports/labels show which ref was used.
    if ref is not None:
        repository.default_branch = ref
    files = file_items_from_tree(client.get_tree(owner, repo, tree_ref))

    def load(path: str) -> str | None:
        return client.get_file_content(owner, repo, path, ref=tree_ref)

    readme_content, gitignore_content, package_content, pyproject_content, workflow_contents = _load_content_inputs(
        files, load
    )
    return build_health_report_from_inputs(
        repository,
        files,
        readme_content=readme_content,
        gitignore_content=gitignore_content,
        package_content=package_content,
        pyproject_content=pyproject_content,
        workflow_contents=workflow_contents,
        config=config,
    )


def build_local_health_report(root: Path, config: RepoPulseConfig | None = None) -> HealthReport:
    """Scan a local directory without calling the GitHub API."""
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    config = config or RepoPulseConfig()
    files = iter_local_files(root)
    repository = repository_info_from_path(root)

    def load(path: str) -> str | None:
        return read_local_text(root, path)

    readme_content, gitignore_content, package_content, pyproject_content, workflow_contents = _load_content_inputs(
        files, load
    )
    return build_health_report_from_inputs(
        repository,
        files,
        readme_content=readme_content,
        gitignore_content=gitignore_content,
        package_content=package_content,
        pyproject_content=pyproject_content,
        workflow_contents=workflow_contents,
        config=config,
    )
