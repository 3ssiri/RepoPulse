import os
from pathlib import Path

import typer
from rich.console import Console

from repopulse.analyzer import build_health_report, build_local_health_report
from repopulse.compare import build_comparison, has_regression
from repopulse.config import load_environment
from repopulse.github_client import GitHubAPIError, GitHubClient
from repopulse.issue_export import (
    filter_payloads_against_open_titles,
    issue_payloads_from_report,
)
from repopulse.local_source import repository_info_from_path
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

# Formats that must not be interpreted as Rich markup (brackets in JSON/Markdown).
_PLAIN_OUTPUT_FORMATS = frozenset({"json", "markdown", "issues", "summary"})


def _print_plain(text: str) -> None:
    """Print user/report text without Rich markup or syntax highlighting."""
    console.print(text, markup=False, highlight=False)


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
    ref: str | None = None,
) -> HealthReport:
    """Scan a local directory or GitHub URL and return a HealthReport."""
    target_path = Path(target)
    if target_path.exists() and target_path.is_dir():
        if ref is not None and not quiet:
            console.print(
                "[yellow]Warning:[/yellow] --ref is ignored for local directory scans "
                "(refs apply only to GitHub URLs)."
            )
        resolved = target_path.resolve()
        if not quiet and progress_label:
            console.print(f"[bold]{progress_label}:[/bold] {resolved}")
        return build_local_health_report(resolved, scan_config)

    owner, repo, url_ref = parse_github_url(target)
    # CLI --ref overrides a ref embedded in the URL when both are set.
    resolved_ref = ref if ref is not None else url_ref
    resolved_token = token or os.getenv("GITHUB_TOKEN")
    if not quiet and progress_label:
        display = f"{owner}/{repo}@{resolved_ref}" if resolved_ref else f"{owner}/{repo}"
        console.print(f"[bold]{progress_label}:[/bold] {display}")
    return build_health_report(GitHubClient(resolved_token), owner, repo, scan_config, ref=resolved_ref)


@app.command()
def scan(
    url: str = typer.Argument(..., help="GitHub repository URL or local directory path."),
    token: str | None = typer.Option(None, help="GitHub token for private repositories."),
    ref: str | None = typer.Option(
        None,
        "--ref",
        help="Git branch, tag, or commit SHA to scan (overrides ref in the URL if both are set).",
    ),
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
            ref=ref,
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
                _print_plain(render_summary(report))
            else:
                render_terminal(report, console, verbose=verbose)
        elif selected_format in _PLAIN_OUTPUT_FORMATS:
            _print_plain(rendered)
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
    baseline_ref: str | None = typer.Option(
        None,
        "--baseline-ref",
        help="Git ref for the baseline (overrides ref in the baseline URL).",
    ),
    target_ref: str | None = typer.Option(
        None,
        "--target-ref",
        help="Git ref for the target (overrides ref in the target URL).",
    ),
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
    """Compare two scans (e.g. main vs feature via /tree/ refs, or two local checkouts)."""
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
            ref=baseline_ref,
        )
        target_report = scan_target(
            target,
            token=token,
            scan_config=scan_config,
            quiet=quiet,
            progress_label="Scanning target" if show_progress else None,
            ref=target_ref,
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
                _print_plain(render_comparison_summary(comparison))
            else:
                render_comparison_terminal(comparison, console)
        elif selected_format in _PLAIN_OUTPUT_FORMATS:
            _print_plain(rendered)
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


def _resolve_github_owner_repo(target: str) -> tuple[str, str]:
    """Resolve owner/repo from a GitHub URL or a local clone with github.com remote."""
    path = Path(target)
    if path.exists() and path.is_dir():
        info = repository_info_from_path(path.resolve())
        if info.owner == "local" or not info.url or "github.com" not in info.url:
            raise ValueError(
                "Creating issues requires a GitHub repository. "
                "Pass a github.com URL, or run from a local clone with a github.com remote. "
                "Use --dry-run to preview issue text without creating anything."
            )
        return info.owner, info.name
    owner, repo, _ref = parse_github_url(target)
    return owner, repo


def _parse_status_set(raw: str) -> set[str]:
    statuses = {part.strip().lower() for part in raw.split(",") if part.strip()}
    if not statuses:
        raise ValueError("At least one status is required (e.g. fail,warn).")
    allowed = {"pass", "warn", "fail"}
    unknown = statuses - allowed
    if unknown:
        raise ValueError(f"Unknown statuses: {', '.join(sorted(unknown))}. Use pass, warn, or fail.")
    return statuses


@app.command("create-issues")
def create_issues_cmd(
    target: str = typer.Argument(..., help="GitHub repository URL or local directory path."),
    token: str | None = typer.Option(None, help="GitHub token with issues:write (required unless --dry-run)."),
    config: Path | None = typer.Option(None, "--config", help="Path to a RepoPulse YAML config file."),
    ref: str | None = typer.Option(None, "--ref", help="Git ref to scan (branch, tag, or SHA)."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print issue titles and bodies; create nothing."),
    yes: bool = typer.Option(False, "--yes", help="Actually create issues on GitHub (requires token)."),
    label: list[str] | None = typer.Option(
        None,
        "--label",
        help="Extra label to apply (repeatable).",
    ),
    statuses: str = typer.Option(
        "fail,warn",
        "--statuses",
        help="Comma-separated check statuses to open issues for (default: fail,warn).",
    ),
    no_dedupe: bool = typer.Option(
        False,
        "--no-dedupe",
        help="Create issues even when an open issue with the same title already exists.",
    ),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress non-essential messages."),
):
    """Create GitHub issues from fail/warn health-check recommendations.

    By default, skips titles that already match an open GitHub issue (exact title match).
    """
    load_environment()
    try:
        if dry_run and yes:
            raise ValueError("Use either --dry-run or --yes, not both.")
        if not dry_run and not yes:
            raise ValueError("Specify --dry-run to preview or --yes to create issues.")

        resolved_token = token or os.getenv("GITHUB_TOKEN")
        if yes and not resolved_token:
            raise ValueError("A GitHub token is required to create issues. Pass --token or set GITHUB_TOKEN.")

        scan_config = load_config(config)
        status_set = _parse_status_set(statuses)
        report = scan_target(
            target,
            token=token,
            scan_config=scan_config,
            quiet=quiet,
            progress_label="Scanning" if not quiet else None,
            ref=ref,
        )
        payloads = issue_payloads_from_report(
            report,
            labels=list(label) if label else None,
            statuses=status_set,
        )

        if not payloads:
            if not quiet:
                console.print("[green]No matching checks to open issues for.[/green]")
            return

        skipped: list[dict] = []
        # Dedupe when we can resolve a GitHub repo and have a token (create path always;
        # dry-run when token is available so preview matches what --yes would do).
        if not no_dedupe:
            try:
                owner, repo = _resolve_github_owner_repo(target)
            except ValueError:
                owner, repo = None, None
            if owner and repo and resolved_token:
                client = GitHubClient(resolved_token)
                try:
                    open_titles = client.list_open_issue_titles(owner, repo)
                except GitHubAPIError as error:
                    if dry_run:
                        if not quiet:
                            console.print(
                                f"[yellow]Dedupe skipped (could not list open issues):[/yellow] {error}"
                            )
                        open_titles = set()
                    else:
                        raise
                payloads, skipped = filter_payloads_against_open_titles(payloads, open_titles)
                if skipped and not quiet:
                    for payload in skipped:
                        console.print(
                            f"[yellow]Skip (open issue exists):[/yellow] {payload['title']}"
                        )

        if not payloads:
            if not quiet:
                if skipped:
                    console.print(
                        f"[green]Nothing to create:[/green] {len(skipped)} issue(s) already open."
                    )
                else:
                    console.print("[green]No matching checks to open issues for.[/green]")
            return

        if dry_run:
            for index, payload in enumerate(payloads, start=1):
                console.print(f"[bold]--- Issue {index}/{len(payloads)} ---[/bold]")
                # Plain text: titles contain [brackets]; Rich markup/highlight must not touch them.
                _print_plain(f"Title: {payload['title']}")
                _print_plain(f"Labels: {', '.join(payload['labels'])}")
                _print_plain(str(payload["body"]))
                console.print()
            if not quiet:
                extra = f" ({len(skipped)} skipped as already open)" if skipped else ""
                console.print(
                    f"[green]Dry run:[/green] {len(payloads)} issue(s) would be created{extra}."
                )
            return

        owner, repo = _resolve_github_owner_repo(target)
        client = GitHubClient(resolved_token)
        created_urls: list[str] = []
        try:
            for payload in payloads:
                issue = client.create_issue(
                    owner,
                    repo,
                    title=payload["title"],
                    body=payload["body"],
                    labels=payload["labels"],
                )
                html_url = issue.get("html_url", "")
                if html_url:
                    created_urls.append(html_url)
                if not quiet:
                    created_line = f"Created: {payload['title']}" + (
                        f" → {html_url}" if html_url else ""
                    )
                    _print_plain(created_line)
        except GitHubAPIError:
            if created_urls and not quiet:
                console.print(
                    f"[yellow]Partial success:[/yellow] created {len(created_urls)}/{len(payloads)} issue(s):"
                )
                for url in created_urls:
                    console.print(f"  {url}")
            raise
        if not quiet:
            extra = f" ({len(skipped)} skipped as already open)" if skipped else ""
            console.print(
                f"[green]Created {len(created_urls)} issue(s) on {owner}/{repo}{extra}.[/green]"
            )
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
