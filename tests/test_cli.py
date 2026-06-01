from typer.testing import CliRunner

from repopulse.cli import app


def test_scan_command_rejects_non_github_url():
    result = CliRunner().invoke(app, ["scan", "https://google.com/test"])

    assert result.exit_code == 1
    assert "Only github.com URLs are supported" in result.output
