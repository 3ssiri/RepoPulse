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


def render_terminal(report: HealthReport, console: Console | None = None) -> None:
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

    if report.recommendations:
        target.print("[bold]Recommendations[/bold]")
        for index, recommendation in enumerate(report.recommendations, start=1):
            target.print(f"{index}. {recommendation}")
