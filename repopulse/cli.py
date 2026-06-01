import os
from pathlib import Path

import typer
from rich.console import Console

from repopulse.analyzer import build_health_report
from repopulse.config import load_environment
from repopulse.github_client import GitHubAPIError, GitHubClient
from repopulse.report import render_markdown, render_terminal
from repopulse.url_parser import parse_github_url

app = typer.Typer(help="Scan GitHub repositories and generate health reports.")
console = Console()


@app.callback()
def main():
    """RepoPulse command group."""


@app.command()
def scan(
    url: str,
    token: str | None = typer.Option(None, help="GitHub token for private repositories."),
    export: Path | None = typer.Option(None, "--export", help="Export report to a Markdown file."),
    json_output: bool = typer.Option(False, "--json", help="Output report as JSON."),
):
    """Scan a GitHub repository and generate a health report."""
    load_environment()
    try:
        owner, repo = parse_github_url(url)
        resolved_token = token or os.getenv("GITHUB_TOKEN")
        if not json_output:
            console.print(f"[bold]Scanning repository:[/bold] {owner}/{repo}")
        report = build_health_report(GitHubClient(resolved_token), owner, repo)
        if export:
            export.write_text(render_markdown(report), encoding="utf-8")
            if not json_output:
                console.print(f"[green]Markdown report written to:[/green] {export}")
        if json_output:
            console.print_json(report.model_dump_json())
        else:
            render_terminal(report, console)
    except (ValueError, GitHubAPIError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error


if __name__ == "__main__":
    app()
