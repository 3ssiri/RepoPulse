# JSON report contract

RepoPulse JSON output (`--format json` / `--json`) is intended for automation.

## Stability rules

- Top-level field `schema_version` identifies the document shape.
- Current value: **`1.0`**.
- Additive fields may appear without a version bump.
- Removing or renaming fields, or changing meaning of existing fields, requires a new `schema_version`.

## Top-level fields (`schema_version` 1.0)

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | Document version (`1.0`). |
| `repository` | object | Repository metadata (see below). |
| `checks` | array | Ordered check results. |
| `total_score` | integer | Sum of check scores after config. |
| `max_score` | integer | Sum of check max scores (usually 100). |
| `grade` | string | Excellent / Good / Fair / Weak / Critical. |
| `recommendations` | array of string | Flattened action items. |
| `config` | object | Applied config subset (may be empty). |

## `repository` object

| Field | Type |
|---|---|
| `owner` | string |
| `name` | string |
| `full_name` | string |
| `description` | string or null |
| `url` | string |
| `default_branch` | string |
| `private` | boolean |
| `stars` | integer |
| `forks` | integer |
| `open_issues` | integer |
| `last_pushed_at` | string or null (ISO-8601 when present) |

## `checks[]` object

| Field | Type |
|---|---|
| `key` | string (stable id, e.g. `readme`, `tests`) |
| `title` | string |
| `status` | `pass` \| `warn` \| `fail` |
| `score` | integer |
| `max_score` | integer (0 for advisory checks) |
| `message` | string |
| `recommendations` | array of string |

## Notes

- Object key order in JSON is **sorted** for stable diffs in automation.
- Local scans set `repository.full_name` from git remote when possible (e.g. `owner/repo`); otherwise `local/<dirname>`.
- Do not parse free-text `message` fields for control flow — use `key`, `status`, and scores.

## Comparison JSON (`repopulse compare --format json`)

Top-level `kind` is always `"comparison"`. Current `schema_version`: **`1.0`**.

| Field | Type | Description |
|---|---|---|
| `schema_version` | string | Document version (`1.0`). |
| `kind` | string | Always `comparison`. |
| `baseline_label` / `target_label` | string | Display labels. |
| `baseline_repository` / `target_repository` | string | `full_name` from each scan. |
| `baseline_score` / `target_score` | integer | Totals. |
| `baseline_max_score` / `target_max_score` | integer | Max totals. |
| `score_delta` | integer | `target_score - baseline_score`. |
| `baseline_grade` / `target_grade` | string | Grades. |
| `checks` | array | Per-check deltas (see below). |
| `improved` / `regressed` / `unchanged` | array of string | Check keys. |
| `config` | object | `{ "baseline": {...}, "target": {...} }`. |

### `checks[]` delta object

| Field | Type |
|---|---|
| `key` | string |
| `title` | string |
| `baseline_status` / `target_status` | `pass` \| `warn` \| `fail` \| null |
| `baseline_score` / `target_score` | integer or null |
| `score_delta` | integer |
| `change` | `improved` \| `regressed` \| `unchanged` \| `added` \| `removed` |
