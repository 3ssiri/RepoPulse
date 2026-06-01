# Security Policy

## Supported Versions

RepoPulse is currently in its initial `0.x` release line. Security fixes target the latest release.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately through GitHub security advisories when available. Do not include secrets or private repository data in public issues.

RepoPulse only inspects sensitive file names and must not print secret file contents.

## Security Notes

- Do not paste private tokens into issues or public discussions.
- Use `GITHUB_TOKEN` or `--token` only in trusted local or CI environments.
- If RepoPulse reports a sensitive file name in a repository, review the repository history and rotate credentials when exposure is possible.
- RepoPulse is a repository quality checker, not a full secret scanner or vulnerability scanner.
