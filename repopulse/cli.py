import os
from pathlib import Path

import typer
from rich.console import Console

from repopulse.analyzer import build_health_report
from repopulse.config import load_environment
from repopulse.github_client import GitHubAPIError, GitHubClient
from repopulse.report import render_json, render_markdown, render_summary, render_terminal
from repopulse.url_parser import parse_github_url

app = typer.Typer(help="Scan GitHub repositories and generate health reports.")
console = Console()

OUTPUT_FORMATS = {"table", "markdown", "json", "summary"}


@app.callback()
def main():
    """RepoPulse command group."""


@app.command()
def scan(
    url: str,
    token: str | None = typer.Option(None, help="GitHub token for private repositories."),
    export: Path | None = typer.Option(None, "--export", help="Export report to a Markdown file."),
    output: Path | None = typer.Option(None, "--output", help="Write the selected output format to a file."),
    output_format: str = typer.Option("table", "--format", help="Output format: table, markdown, json, or summary."),
    json_output: bool = typer.Option(False, "--json", help="Output report as JSON."),
    fail_under: int | None = typer.Option(None, "--fail-under", min=0, max=100, help="Exit with code 2 if score is below this value."),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress progress messages and use compact output."),
    verbose: bool = typer.Option(False, "--verbose", help="Show all recommendations in table output."),
):
    """Scan a GitHub repository and generate a health report."""
    load_environment()
    try:
        owner, repo = parse_github_url(url)
        selected_format = "json" if json_output else output_format.lower()
        if selected_format not in OUTPUT_FORMATS:
            raise ValueError("Invalid output format. Use table, markdown, json, or summary.")
        resolved_token = token or os.getenv("GITHUB_TOKEN")
        if not quiet and selected_format == "table":
            console.print(f"[bold]Scanning repository:[/bold] {owner}/{repo}")
        report = build_health_report(GitHubClient(resolved_token), owner, repo)
        if export:
            export.write_text(render_markdown(report), encoding="utf-8")
            if not quiet and selected_format == "table":
                console.print(f"[green]Markdown report written to:[/green] {export}")
        rendered = render_output(report, selected_format)
        if output:
            output.write_text(rendered + "\n", encoding="utf-8")
            if not quiet and selected_format == "table":
                console.print(f"[green]Report written to:[/green] {output}")
        elif selected_format == "table":
            if quiet:
                console.print(render_summary(report))
            else:
                render_terminal(report, console, verbose=verbose)
        else:
            console.print(rendered)
        if fail_under is not None and report.total_score < fail_under:
            console.print(f"[red]Score {report.total_score} is below required threshold {fail_under}.[/red]")
            raise typer.Exit(code=2)
    except (ValueError, GitHubAPIError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error


def render_output(report, selected_format: str) -> str:
    if selected_format == "json":
        return render_json(report)
    if selected_format == "markdown":
        return render_markdown(report)
    if selected_format == "summary":
        return render_summary(report)
    return render_summary(report)


if __name__ == "__main__":
    app()
