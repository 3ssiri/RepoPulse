import json

from rich.console import Console
from rich.table import Table

from repopulse.models import HealthReport


def render_markdown(report: HealthReport) -> str:
    repo = report.repository
    private = "Yes" if repo.private else "No"
    updated = repo.last_pushed_at or "Unknown"
    lines = [
        "# RepoPulse Health Report",
        "",
        "## Repository",
        f"- Name: {repo.full_name}",
        f"- URL: {repo.url}",
        f"- Default Branch: {repo.default_branch}",
        f"- Private: {private}",
        f"- Stars: {repo.stars}",
        f"- Forks: {repo.forks}",
        f"- Open Issues: {repo.open_issues}",
        f"- Last Updated: {updated}",
        "",
        "## Final Score",
        f"**{report.total_score} / {report.max_score} - {report.grade}**",
        "",
        "## Checks",
        "| Check | Status | Score | Notes |",
        "|---|---|---:|---|",
    ]
    for check in report.checks:
        lines.append(f"| {check.title} | {check.status.title()} | {check.score}/{check.max_score} | {check.message} |")

    lines.extend(["", "## Recommendations"])
    if report.recommendations:
        lines.extend(f"{index}. {recommendation}" for index, recommendation in enumerate(report.recommendations, start=1))
    else:
        lines.append("No high-priority recommendations.")
    lines.append("")
    return "\n".join(lines)


def render_json(report: HealthReport) -> str:
    return json.dumps(report.model_dump(), indent=2, ensure_ascii=False)


def render_summary(report: HealthReport) -> str:
    lines = [
        f"{report.repository.full_name}: {report.total_score} / {report.max_score} - {report.grade}",
    ]
    if report.recommendations:
        lines.append("Top recommendations:")
        lines.extend(f"- {recommendation}" for recommendation in report.recommendations[:3])
    return "\n".join(lines)


def render_issues(report: HealthReport) -> str:
    """Render GitHub-issue-ready Markdown blocks for fail/warn checks and any with recommendations."""
    repo = report.repository
    full_name = repo.full_name
    lines = [
        f"# RepoPulse recommendations for {full_name}",
        f"Score: {report.total_score}/{report.max_score} — {report.grade}",
        "",
    ]

    actionable = [
        check
        for check in report.checks
        if check.status in {"fail", "warn"} or check.recommendations
    ]

    if not actionable:
        lines.append(
            f"No open recommendations from RepoPulse for {full_name} "
            f"(score {report.total_score}/{report.max_score} — {report.grade})."
        )
        return "\n".join(lines)

    blocks: list[str] = []
    for check in actionable:
        block_lines = [
            f"## [RepoPulse] {check.title}: {check.status}",
            "",
            f"**Repository:** {full_name}",
            f"**Score impact:** {check.score}/{check.max_score}",
            f"**Summary:** {check.message}",
            "",
            "### Action items",
        ]
        if check.recommendations:
            block_lines.extend(f"- {item}" for item in check.recommendations)
        else:
            block_lines.append("- Review this check and improve the repository.")
        block_lines.extend(
            [
                "",
                "### Labels",
                f"`repopulse`, `health-check`, `{check.key}`",
            ]
        )
        blocks.append("\n".join(block_lines))

    lines.append("\n\n---\n\n".join(blocks))
    lines.append("")
    return "\n".join(lines)


def render_terminal(report: HealthReport, console: Console | None = None, verbose: bool = False) -> None:
    target = console or Console()
    repo = report.repository
    target.print(f"[bold]RepoPulse Health Report[/bold] for [cyan]{repo.full_name}[/cyan]")
    target.print(f"Score: [bold]{report.total_score} / {report.max_score}[/bold] - {report.grade}")
    target.print(f"Default branch: {repo.default_branch} | Stars: {repo.stars} | Forks: {repo.forks} | Open issues: {repo.open_issues}")

    table = Table(title="Checks")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Score", justify="right")
    table.add_column("Notes")
    for check in report.checks:
        style = "green" if check.status == "pass" else "yellow" if check.status == "warn" else "red"
        table.add_row(check.title, f"[{style}]{check.status.upper()}[/{style}]", f"{check.score}/{check.max_score}", check.message)
    target.print(table)

    recommendations = report.recommendations if verbose else report.recommendations[:3]
    if recommendations:
        target.print("[bold]Recommendations[/bold]")
        for index, recommendation in enumerate(recommendations, start=1):
            target.print(f"{index}. {recommendation}")
        if not verbose and len(report.recommendations) > 3:
            target.print(f"...and {len(report.recommendations) - 3} more. Use --verbose to show all.")
