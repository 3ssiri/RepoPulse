import os
from pathlib import Path

import typer
from rich.console import Console

from repopulse.analyzer import build_health_report, build_local_health_report
from repopulse.compare import build_comparison, has_regression
from repopulse.config import load_environment
from repopulse.github_client import GitHubAPIError, GitHubClient
from repopulse.models import HealthReport
from repopulse.report import (
    render_comparison_json,
    render_comparison_markdown,
    render_comparison_summary,
    render_comparison_terminal,
    render_issues,
    render_json,
    render_markdown,
    render_summary,
    render_terminal,
)
from repopulse.settings import RepoPulseConfig, load_config
from repopulse.url_parser import parse_github_url

app = typer.Typer(help="Scan GitHub repositories and generate health reports.")
console = Console()

OUTPUT_FORMATS = {"table", "markdown", "json", "summary", "issues"}
COMPARE_FORMATS = {"table", "markdown", "json", "summary"}


@app.callback()
def main():
    """RepoPulse command group."""


def scan_target(
    target: str,
    *,
    token: str | None,
    scan_config: RepoPulseConfig,
    quiet: bool,
    progress_label: str | None = None,
) -> HealthReport:
    """Scan a local directory or GitHub URL and return a HealthReport."""
    target_path = Path(target)
    if target_path.exists() and target_path.is_dir():
        resolved = target_path.resolve()
        if not quiet and progress_label:
            console.print(f"[bold]{progress_label}:[/bold] {resolved}")
        return build_local_health_report(resolved, scan_config)

    owner, repo = parse_github_url(target)
    resolved_token = token or os.getenv("GITHUB_TOKEN")
    if not quiet and progress_label:
        console.print(f"[bold]{progress_label}:[/bold] {owner}/{repo}")
    return build_health_report(GitHubClient(resolved_token), owner, repo, scan_config)


@app.command()
def scan(
    url: str = typer.Argument(..., help="GitHub repository URL or local directory path."),
    token: str | None = typer.Option(None, help="GitHub token for private repositories."),
    export: Path | None = typer.Option(None, "--export", help="Export report to a Markdown file."),
    output: Path | None = typer.Option(None, "--output", help="Write the selected output format to a file."),
    output_format: str = typer.Option(
        "table",
        "--format",
        help="Output format: table, markdown, json, summary, or issues.",
    ),
    config: Path | None = typer.Option(None, "--config", help="Path to a RepoPulse YAML config file."),
    json_output: bool = typer.Option(False, "--json", help="Output report as JSON."),
    fail_under: int | None = typer.Option(
        None,
        "--fail-under",
        min=0,
        max=100,
        help="Exit with code 2 if score is below this value.",
    ),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress progress messages and use compact output."),
    verbose: bool = typer.Option(False, "--verbose", help="Show all recommendations in table output."),
):
    """Scan a GitHub repository or local directory and generate a health report."""
    load_environment()
    try:
        selected_format = "json" if json_output else output_format.lower()
        if selected_format not in OUTPUT_FORMATS:
            raise ValueError("Invalid output format. Use table, markdown, json, summary, or issues.")
        scan_config = load_config(config)
        report = scan_target(
            url,
            token=token,
            scan_config=scan_config,
            quiet=quiet,
            progress_label="Scanning" if selected_format == "table" else None,
        )

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
        threshold = fail_under if fail_under is not None else scan_config.fail_under
        if threshold is not None and score_percentage(report.total_score, report.max_score) < threshold:
            console.print(
                f"[red]Score {report.total_score}/{report.max_score} is below required threshold {threshold}%.[/red]"
            )
            raise typer.Exit(code=2)
    except (ValueError, GitHubAPIError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error


@app.command("compare")
def compare_cmd(
    baseline: str = typer.Argument(..., help="Baseline GitHub URL or local directory path."),
    target: str = typer.Argument(..., help="Target GitHub URL or local directory path."),
    token: str | None = typer.Option(None, help="GitHub token for private repositories."),
    output: Path | None = typer.Option(None, "--output", help="Write the selected output format to a file."),
    output_format: str = typer.Option(
        "table",
        "--format",
        help="Output format: table, markdown, json, or summary.",
    ),
    config: Path | None = typer.Option(None, "--config", help="Path to a RepoPulse YAML config file."),
    json_output: bool = typer.Option(False, "--json", help="Output comparison as JSON."),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress progress messages and use compact output."),
    fail_on_regression: bool = typer.Option(
        False,
        "--fail-on-regression",
        help="Exit with code 2 if the score dropped or any check regressed.",
    ),
    baseline_label: str | None = typer.Option(
        None,
        "--baseline-label",
        help="Display label for the baseline (default: repository full name).",
    ),
    target_label: str | None = typer.Option(
        None,
        "--target-label",
        help="Display label for the target (default: repository full name).",
    ),
):
    """Compare two scans (e.g. main vs PR branch checkouts, or two repositories)."""
    load_environment()
    try:
        selected_format = "json" if json_output else output_format.lower()
        if selected_format not in COMPARE_FORMATS:
            raise ValueError("Invalid output format. Use table, markdown, json, or summary.")
        scan_config = load_config(config)
        show_progress = not quiet and selected_format == "table"
        baseline_report = scan_target(
            baseline,
            token=token,
            scan_config=scan_config,
            quiet=quiet,
            progress_label="Scanning baseline" if show_progress else None,
        )
        target_report = scan_target(
            target,
            token=token,
            scan_config=scan_config,
            quiet=quiet,
            progress_label="Scanning target" if show_progress else None,
        )
        comparison = build_comparison(
            baseline_report,
            target_report,
            baseline_label=baseline_label,
            target_label=target_label,
        )

        rendered = render_comparison_output(comparison, selected_format)
        if output:
            output.write_text(rendered + "\n", encoding="utf-8")
            if show_progress:
                console.print(f"[green]Comparison written to:[/green] {output}")
        elif selected_format == "table":
            if quiet:
                console.print(render_comparison_summary(comparison))
            else:
                render_comparison_terminal(comparison, console)
        else:
            console.print(rendered)

        if fail_on_regression and has_regression(comparison):
            console.print(
                f"[red]Regression detected:[/red] score delta {comparison.score_delta}, "
                f"regressed checks: {', '.join(comparison.regressed) or 'score drop only'}."
            )
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
    if selected_format == "issues":
        return render_issues(report)
    return render_summary(report)


def render_comparison_output(comparison, selected_format: str) -> str:
    if selected_format == "json":
        return render_comparison_json(comparison)
    if selected_format == "markdown":
        return render_comparison_markdown(comparison)
    if selected_format == "summary":
        return render_comparison_summary(comparison)
    return render_comparison_summary(comparison)


def score_percentage(score: int, max_score: int) -> int:
    return round((score / max_score) * 100) if max_score > 0 else 0


if __name__ == "__main__":
    app()
