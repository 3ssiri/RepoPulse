# RepoPulse WebMCP Demo — Multi-Agent Handoff

Last updated: 2026-09-01

Purpose: make the demo-video workflow resumable by any capable agent if ChatGPT Work, Codex, Claude Code/Cowork, Grok, Gemini, or another tool stops, hits a quota, or loses context.

## Source of truth

Always read these files before acting:

1. `docs/demo-video-state.md` — current checkpoint and next action.
2. `docs/devpost-submission.md` — approved story/narration and submission copy.
3. `docs/demo-remotion-runbook.md` — editing/render rules.
4. `docs/demo-production-free-stack.md` — tool choices and zero-cost policy.
5. `docs/demo-timeline.schema.json` — required shape of Gemini's edit-plan output.
6. `docs/webmcp-challenge.md` — verified product behavior and WebMCP evidence.

Do not replace these sources with memory, chat history, or guesses.

## Primary production architecture

```text
Native ChatGPT WebMCP capture
        ↓
authentic raw screen recording
        ↓
Gemini Agentic Video Understanding
        ↓
structured `timeline.json` edit plan
        ↓
Grok / local TTS / Gemini narration assets
        ↓
Remotion controlled by Codex or Claude Code
        ↓
programmatic trims + timing + zooms + overlays + optional captions
        ↓
1920×1080 MP4, < 3:00, target ≈ 2:10
        ↓
public YouTube → Devpost
```

## Non-negotiable evidence rule

The raw recording is the only source for ChatGPT, WebMCP, and RepoPulse screens.

Allowed post-production:
- trim/cut real footage
- remove waiting
- modest speed-up of dead time
- crop/zoom real footage
- add narration
- add captions and short labels
- hold on a completed real result

Forbidden:
- generated/recreated ChatGPT screens
- generated/recreated RepoPulse screens
- fake Site Tool calls
- fake cursor activity
- changing a visible result
- presenting a direct API/DOM automation run as native WebMCP

If required evidence is missing, mark the scene `NEEDS_RERECORD` in state and stop fabricating around it.

## Role matrix

| Stage | Preferred tool | Fallback 1 | Fallback 2 | Why |
|---|---|---|---|---|
| Native WebMCP execution | ChatGPT desktop built-in browser / Work or Codex | same built-in browser in another ChatGPT task | human-driven recording while ChatGPT uses Site Tools | Site Tools use WebMCP and share the live page state |
| Raw screen capture | existing local recorder / OS capture | OBS Studio | Screenity / Clipchamp | must preserve authentic UI |
| Video moment detection | Gemini 3.7 Flash with agentic video processing | Gemini 3.6 Flash agentic | manual timestamp pass | best suited to targeted moment retrieval and cut boundaries |
| Structured edit plan | Gemini structured output | Codex/Claude validate/fix JSON | manual JSON edit | deterministic handoff to Remotion |
| Narration | best existing Grok/local/Gemini TTS after sample test | another already-owned TTS | human voice | no new paid provider |
| Remotion implementation | Codex | Claude Code/Cowork | Grok/Antigravity if local repo + command access | repository-local coding and render loop |
| Render/technical validation | same agent that built Remotion | alternate coding agent | local human CLI | deterministic CLI output |
| Final content QA | human + alternate agent | Gemini video review | manual checklist | catches narrative/evidence mismatch |

## Best tool by task

### ChatGPT Work / Codex built-in browser

Best for the native WebMCP evidence step. Site Tools operate on the current live page and current browser state. This stage must not be substituted with ordinary API calls or DOM automation.

### Gemini Agentic Video Understanding

Best for analyzing the raw recording. Ask it to locate only the evidence moments needed by the approved story and return timestamped structured output. It should not generate replacement video.

Preferred model: `gemini-3.7-flash` with video input `processing: "agentic"`.
Fallback: `gemini-3.6-flash` with the same mode.

### Codex

Preferred Remotion implementation agent. It should consume the repository docs, `timeline.json`, raw capture, and narration files, then create/iterate/render the deterministic composition.

### Claude Code / Cowork

Equivalent fallback for local repository editing and command execution. It should use exactly the same state files and acceptance criteria instead of inventing a new workflow.

### Grok / Antigravity

Use as fallback implementation agents only when they can access the same repository/worktree and run Node/Remotion/FFmpeg commands. Grok is also a narration candidate. They are not substitutes for native ChatGPT Site Tools evidence.

## Resume protocol — every agent must do this first

Run/read, in order:

```bash
git status --short
git branch --show-current
git log -5 --oneline
```

Then inspect:

```text
docs/demo-video-state.md
docs/demo-video-handoff.md
docs/demo-remotion-runbook.md
docs/devpost-submission.md
```

If a demo worktree exists, also inspect:

```text
video-demo/timeline.json
video-demo/src/
video-demo/public/audio/
video-demo/out/
```

Never reset, delete, or regenerate existing assets just because the previous agent is unavailable.

## Checkpoint rules

After every meaningful stage, update `docs/demo-video-state.md` with:

- timestamp
- current phase
- status: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, or `DONE`
- exact completed actions
- exact file paths produced
- verification performed
- unresolved issues
- next single action
- assumptions, if any

Do this before switching tools or ending a session.

## Local-only assets

These are expected to remain local and uncommitted:

```text
video-demo/public/raw-webmcp-demo.mp4
video-demo/public/audio/*.wav
video-demo/public/audio/*.mp3
video-demo/out/
```

`video-demo/timeline.json` SHOULD be tracked when it contains only timestamps/labels and no private information. It is the key machine-readable handoff between Gemini and Remotion.

## Gemini analysis input

Input:
- authentic `raw-webmcp-demo.mp4`
- approved story from `docs/devpost-submission.md`
- JSON schema from `docs/demo-timeline.schema.json`

Gemini must find these evidence beats:

1. `scan_repository` executed for `torvalds/linux`
2. Linux result becomes visible (`69/100`, Fair, `scan_truncated: true`)
3. `get_attention_items` executed without a new scan
4. FAIL `github_actions` appears before WARN items
5. `get_check_details(github_actions)` executed and details visible
6. human manually changes RepoPulse UI to `3ssiri/RepoPulse`
7. RepoPulse result becomes visible (`100/100`, Excellent)
8. `compare_refs(v0.3.5, v0.3.6)` executed without re-supplying repository URL
9. comparison becomes visible (`100/100 → 100/100`, delta 0)
10. final live WebMCP-enabled product state

### Gemini prompt

```text
Analyze this authentic screen recording of the RepoPulse WebMCP demo.

Goal: create a precise edit plan for Remotion. Do not summarize broadly and do not propose generated/recreated UI. The original recording is the sole visual evidence source.

Find only the required evidence beats listed in the supplied story. For each beat, identify the tightest safe source-video range that preserves the real action and enough context to prove what happened.

Return JSON matching the supplied schema exactly.

For every scene include:
- source start/end in seconds
- action time if visible
- result-visible time if visible
- evidence description
- confidence 0..1
- whether the scene is safe to cut directly
- any hold range that can remain on screen during narration
- any dead/wait ranges that can be removed or accelerated
- NEEDS_RERECORD if the claimed evidence is not actually visible

Be conservative. Never infer that a tool was used when the recording does not visibly support it.
```

## Codex / Claude Code resume prompt

```text
Resume the RepoPulse WebMCP demo-video project from repository state. Do not start over.

Read first:
- docs/demo-video-state.md
- docs/demo-video-handoff.md
- docs/demo-remotion-runbook.md
- docs/devpost-submission.md
- docs/demo-timeline.schema.json

Then inspect git status and any existing `video-demo/` worktree/project.

Use `video-demo/timeline.json` as the source-video edit plan if it exists and validates against the schema. Use the authentic raw recording only; never synthesize application screens.

Continue only the next incomplete phase recorded in `docs/demo-video-state.md`.

For Remotion:
- 1920x1080, 30fps
- composition id `RepoPulseWebMCPDemo`
- non-destructive trims of raw recording
- narration from existing Grok/local/Gemini audio assets
- frame-driven zooms/overlays only
- no title card, avatar, fake UI, fake cursor, or background music
- final duration <3:00, target ≈2:10

Run real verification before marking a phase DONE. Update `docs/demo-video-state.md` before ending the session or switching tools.
```

## Grok / Antigravity resume prompt

```text
Continue the existing RepoPulse demo-video work; do not redesign it.

Read docs/demo-video-state.md and docs/demo-video-handoff.md first. Follow the same Remotion project, timeline.json, evidence rules, and DONE criteria used by Codex/Claude Code.

If you cannot access the local raw recording, narration assets, repository files, or command runner, do not claim completion. Report the missing capability and leave state unchanged except for a precise BLOCKED note.
```

## Phase DONE criteria

### P0 — documentation
DONE when:
- handoff docs exist
- state file exists
- timeline schema exists
- local media ignore rules exist

### P1 — authentic capture
DONE when:
- untouched raw MP4 exists locally
- all required WebMCP beats are visibly present
- backup copy exists
- no sensitive desktop data is visible

### P2 — Gemini analysis
DONE when:
- agentic video analysis completed
- `timeline.json` validates against schema
- every required evidence beat has timestamps or `NEEDS_RERECORD`
- no scene relies on generated UI

### P3 — narration
DONE when:
- one TTS source selected by actual sample comparison
- seven scene audio files exist
- wording matches approved script

### P4 — Remotion assembly
DONE when:
- composition renders in Studio
- all scenes consume real source ranges from timeline
- audio is synchronized
- approved overlays/zooms implemented

### P5 — final render
DONE when:
- final MP4 is 1920×1080
- duration <180 seconds
- audio is clean
- evidence remains readable
- no fabricated UI or private information

### P6 — submission
DONE when:
- final video watched with audio and muted
- uploaded publicly to YouTube
- YouTube URL added to Devpost
- final Devpost fields checked

## Failure / quota policy

If any tool hits quota/session limits:

1. stop only that tool
2. update `docs/demo-video-state.md`
3. preserve all local files and current git changes
4. move to the next fallback in the role matrix
5. give the new agent the resume prompt, not the entire historical chat

No stage should depend on a single model retaining conversational memory.
