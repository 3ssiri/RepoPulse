# Supported Checks

RepoPulse produces a 100-point score from core checks and adds advisory recommendations from supplemental checks.

## Core Scored Checks

| Check | Points | What It Looks For |
|---|---:|---|
| README Quality | 20 | README file, clear description, installation, usage, features, and tech stack. |
| License | 10 | `LICENSE`, `LICENSE.md`, or `COPYING`. |
| .gitignore | 10 | `.gitignore` plus common patterns such as `.env`, caches, dependencies, and build outputs. |
| Tests | 15 | Test directories, test files, and package test command. |
| GitHub Actions | 15 | Workflows for CI, tests, linting, or builds. |
| Recent Activity | 10 | Recent `pushed_at` timestamp from GitHub. |
| Sensitive Files | 10 | Common sensitive file names such as `.env`, `credentials.json`, `private-key.pem`, and `id_rsa`. |
| Project Structure | 5 | Organized source/docs directories and limited root clutter. |
| Package Scripts | 5 | Node scripts or Python project/tooling configuration. |

## Advisory Checks

Advisory checks currently use `max_score=0`. They do not change the 100-point score, but they add recommendations.

| Check | What It Looks For |
|---|---|
| Dependencies | Dependency manifest, lockfile, and Dependabot configuration. |
| Security Baseline | `SECURITY.md`, Dependabot, and CodeQL workflow. |

## Sensitive File Safety

RepoPulse checks sensitive file names only. It does not print sensitive file contents.

If a sensitive file name is detected, the recommendation is to remove the file from the repository history when needed and rotate any exposed credentials.

## README Quality Scoring

| Signal | Points |
|---|---:|
| README exists | 8 |
| Clear description | 3 |
| Installation section | 3 |
| Usage section | 3 |
| Features section | 2 |
| Tech stack section | 1 |

## Activity Scoring

| Last Push | Points |
|---|---:|
| Last 30 days | 10 |
| Last 6 months | 7 |
| Last year | 4 |
| More than a year | 1 |
| Unknown | 0 |
