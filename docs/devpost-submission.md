# RepoPulse — Devpost Submission Pack

This file is the submission-ready copy for the OpenAI WebMCP Challenge. It is
written to answer the four questions highlighted in the final Devpost guidance
and to keep the demo focused on real WebMCP execution.

## One-line summary

RepoPulse gives developers and AI agents the same live repository-health
workspace: either side can act, and both see and continue from the same
application state.

## Final Devpost description

### Why is this use case a great fit for WebMCP?

Repository health is already a structured task: select a public GitHub
repository, run deterministic checks, inspect failures and warnings, drill into
one check, and compare two refs before a release. In a normal web UI, an AI
agent would have to infer controls from the page, click through the interface,
and reconstruct state from rendered output. RepoPulse exposes those exact
product actions as explicit WebMCP tools instead.

The important part is that WebMCP is not a separate agent API bolted onto the
product. The tools call the same frontend functions and use the same current
report and comparison state as the human-facing dashboard. The agent gets
structured actions while the developer keeps the normal visual product.

### How does it create a better experience?

A developer can ask ChatGPT to scan a repository with `scan_repository`, and
the result appears immediately in the visible RepoPulse dashboard. Follow-up
tools such as `get_attention_items` and `get_check_details` read the report
already loaded in the page, so they do not trigger another repository scan or
force the agent to rediscover context.

This removes a fragile browser-automation loop. The agent does not need to
scrape score cards, guess selectors, or navigate between controls to answer a
simple question such as "what needs attention?" It receives a typed result,
while the human sees the same score, checks, recommendations, and comparison in
the interface.

### What can people and agents do together now that was difficult or impossible before?

The human and the agent can hand work back and forth without losing context.
A developer can manually scan a repository in the UI, then the agent can use
that currently selected repository to inspect checks or compare refs. The
agent can then scan another repository through WebMCP, and the same dashboard
moves with the agent.

For example, during production verification a human scanned `psf/requests` and
saw a 97/100 report. A WebMCP `scan_repository` call then selected
`3ssiri/RepoPulse`, and the visible dashboard changed to the 100/100 RepoPulse
report. On `torvalds/linux`, `get_attention_items` read the current 69/100
report without rescanning and returned the failing check before all warning
checks. That shared, bidirectional application state is the core product
experience: the agent and developer are working in one session, not in two
disconnected interfaces.

### How did you implement WebMCP?

RepoPulse keeps its existing Python analysis engine unchanged. A small FastAPI
web adapter exposes scan and compare operations, while a vanilla JavaScript
frontend renders the dashboard. The page registers four imperative WebMCP tools
with `document.modelContext.registerTool()`:

- `scan_repository` — scans a public GitHub repository, returns a structured
  summary, and updates the visible dashboard.
- `get_attention_items` — reads FAIL then WARN checks from the current report
  without another GitHub scan.
- `get_check_details` — returns one check from the current report and returns
  the available keys when a requested key does not exist.
- `compare_refs` — compares two refs for the currently selected repository and
  renders the structured comparison in the same dashboard.

All four tools are read-only against GitHub and use the same frontend state as
the human controls. WebMCP is progressive enhancement: the web app still works
normally when `document.modelContext` is unavailable. Repository input is
restricted to public `github.com` URLs, GitHub-derived content is rendered with
safe text APIs rather than raw HTML, and the tools return RepoPulse analysis
rather than raw repository content.

## Suggested short description

RepoPulse is a repository-health analyzer where developers and AI agents share
the same live application state. Four read-only WebMCP tools let an agent scan
public GitHub repositories, inspect failures and warnings, retrieve check
details, and compare refs while every action updates the same dashboard the
human is using.

## Testing instructions

1. Open the live RepoPulse app in a WebMCP-capable ChatGPT browser.
2. Confirm these four Site Tools are exposed: `scan_repository`,
   `get_attention_items`, `get_check_details`, `compare_refs`.
3. Call `scan_repository` with `https://github.com/torvalds/linux` and confirm
   the dashboard updates to the returned report.
4. Call `get_attention_items` without another scan. Confirm it reads the
   current report and places all FAIL items before WARN items.
5. Call `get_check_details` using one returned check key. An unknown key can
   also be used to verify the `available_keys` recovery response.
6. Manually scan `https://github.com/3ssiri/RepoPulse` in the UI.
7. Call `compare_refs` with baseline `v0.3.5` and target `v0.3.6`. Confirm the
   comparison appears in the same dashboard.

GitHub's unauthenticated API rate limit can return HTTP 429 after repeated
scans. If that happens, it is a GitHub rate-limit condition rather than a
WebMCP tool-registration failure.

## Submission metadata

- Live app: `https://repopulse-webmcp.vercel.app`
- Source repository: `https://github.com/3ssiri/RepoPulse`
- License: MIT
- Authentication: none; public GitHub repositories only

## Demo video — target 2:00–2:20

Do not use a title card. Begin with the live application and ChatGPT already
open. Cut all loading time and paste prompts instead of typing them.

### 0:00–0:15 — WebMCP action from the first second

**Screen:** RepoPulse and ChatGPT visible. Immediately execute
`scan_repository` on `https://github.com/torvalds/linux`. Cut directly to the
completed result and the 69/100 dashboard.

**Narration:**

> I am scanning the Linux repository from ChatGPT using RepoPulse's WebMCP
> `scan_repository` tool. The agent receives structured repository-health
> data, and the same action updates the dashboard I am looking at.

**On-screen text:** `WebMCP action → same visible dashboard`

### 0:15–0:35 — Read current state, no rescan

**Screen:** Execute `get_attention_items`. Show the returned order: one FAIL
followed by WARN items. Briefly keep the dashboard in view.

**Narration:**

> Now I ask for only the checks that need attention. This tool reads the
> report already loaded in the page; it does not scan GitHub again. Here the
> failing GitHub Actions check comes first, followed by the warnings.

**On-screen text:** `Current state · no repository rescan`

### 0:35–0:50 — Drill into one check

**Screen:** Execute `get_check_details` for `github_actions`; show the
structured status, message, and recommendations.

**Narration:**

> I can drill into one check directly. There is no DOM scraping and no need to
> rediscover which repository or report we are discussing.

### 0:50–1:10 — Human changes the shared state

**Screen:** In the normal RepoPulse UI, paste
`https://github.com/3ssiri/RepoPulse` and click Scan. Cut to the completed
100/100 dashboard.

**Narration:**

> The state works in the other direction too. I switch the repository myself
> in the normal interface. The agent and I are still working in the same
> application state.

**On-screen text:** `Human action → shared agent state`

### 1:10–1:30 — Agent continues from the human-selected repository

**Screen:** In ChatGPT call `compare_refs` with `v0.3.5` and `v0.3.6`. Do not
supply a repository URL. Show the returned comparison and the same dashboard
rendering `100/100 → 100/100` with delta 0.

**Narration:**

> Without selecting the repository again, the agent compares version 0.3.5
> with 0.3.6. `compare_refs` uses the repository I selected and renders the
> comparison back into the same dashboard.

### 1:30–1:55 — Explain the implementation while showing the product

**Screen:** Keep the live product visible. Briefly show a compact overlay with
the four tool names; do not switch to code unless the overlay is unavailable.

**Narration:**

> RepoPulse exposes four read-only WebMCP tools: scan a repository, read the
> current attention items, inspect one check, and compare refs. They call the
> same frontend functions as the human controls, so there is no separate
> agent-only state. The existing RepoPulse analysis engine stays unchanged.

### 1:55–2:10 — Close on the product value

**Screen:** Show the completed RepoPulse comparison and WebMCP-enabled page.

**Narration:**

> RepoPulse turns repository health from a page an agent has to operate into a
> shared workspace where the developer and the agent can hand the task back
> and forth. That shared state is what WebMCP adds to the product.

**On-screen text:** `One product · one state · human + agent`

## Recording rules for this demo

- Keep the final edit under 3 minutes; target 2:00–2:20.
- Start after all logins and setup are complete.
- Use the real production site and real WebMCP Site Tools.
- Cut or speed up network waits; never imply that a cut result was fabricated.
- Paste prompts; do not type long prompts on camera.
- Use one continuous product story rather than repeating the same capability.
- Keep architecture, build history, CI, and team background out of the video.
- English narration may be recorded by the creator or generated with an AI
  voice; the narration must accurately describe what is visibly running.
- Upload the final video publicly to YouTube and place the strongest working
  interaction in the first 10–15 seconds.
