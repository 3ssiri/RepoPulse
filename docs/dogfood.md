# Dogfood notes

Informal scans of public repositories to catch false positives. Scores are approximate and change with check updates.

**Last run:** 2026-08-04 against RepoPulse `main` (post-0.3.3 / tests-check deepen).

## Score snapshot

| Repository | Score | Grade |
|---|---:|---|
| `3ssiri/RepoPulse` | 100 | Excellent |
| `tiangolo/fastapi` | 100 | Excellent |
| `psf/requests` | 97 | Excellent |
| `encode/httpx` | 95 | Excellent |
| `pallets/flask` | 93 | Excellent |
| `pypa/pip` | 92 | Excellent |
| `cli/cli` (Go) | 75 | Good |

## Themes

- **Python libraries** with standard layout score high after license/Actions/fixture fixes.
- **Go / other ecosystems** score lower: heuristics are still Python/JS-weighted (expected; see scope notes in reports).
- Residual risks after 0.3.x trust pass: unusual CI without runner tokens; monorepos with nonstandard roots still may warn on structure.

## How to re-run

```bash
pip install -U repopulse-cli
repopulse scan https://github.com/psf/requests --format summary --quiet
```

Report unfair findings: [CONTRIBUTING.md](../CONTRIBUTING.md#reporting-false-positives).
