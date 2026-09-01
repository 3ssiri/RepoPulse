# RepoPulse WebMCP Demo — Zero-Cost Production Stack

Research/decision date: 2026-09-01

Goal: produce the final <3 minute WebMCP demo with **no additional paid subscription**, while preserving real native ChatGPT WebMCP evidence.

## Final recommendation

### Primary path — recommended

**Native ChatGPT WebMCP capture → Gemini Agentic Video Understanding → structured `timeline.json` → Remotion + Codex/Claude Code → existing TTS (Grok / local TTS / Gemini) → 1080p MP4**

This is the preferred production architecture because each tool is assigned to the task it is strongest at:

- ChatGPT built-in browser / Site Tools: authentic WebMCP execution on the live page.
- Gemini Agentic Video Understanding: precise moment retrieval and cut-boundary discovery from the raw recording.
- Codex / Claude Code: deterministic repository-local Remotion implementation and render loop.
- Grok / local TTS / Gemini: narration from resources already available; no new paid TTS provider.

The non-negotiable rule: **the raw ChatGPT + RepoPulse recording is the sole source for application screens.** AI may analyze and edit the real recording, but it may not recreate product interactions.

## Why Gemini belongs before Remotion

A coding agent should not manually guess timestamps in a 4–5 minute raw capture when Gemini can first create a structured edit plan.

Gemini Agentic Video Understanding should:

- search for the exact WebMCP evidence moments required by the approved story
- inspect relevant frames/audio/transcript selectively
- return tight source ranges and sub-second action/result timestamps
- identify dead/wait ranges that can be cut or accelerated
- mark missing evidence as `NEEDS_RERECORD`
- emit JSON matching `docs/demo-timeline.schema.json`

This makes `video-demo/timeline.json` the machine-readable handoff from video analysis to Remotion.

Preferred analysis model: `gemini-3.7-flash` with `processing: "agentic"`.
Fallback: `gemini-3.6-flash` with the same mode.

## Why Remotion + Codex/Claude Code remains the best finishing layer

Once `timeline.json` and narration files exist, Remotion turns the demo into a reproducible programmatic edit rather than a manually maintained timeline.

A coding agent can:

- import the authentic raw recording
- consume Gemini's source ranges
- cut/compress waiting
- place narration at deterministic timestamps
- align state changes to spoken claims
- add restrained zooms around Site Tool actions and dashboard updates
- add short overlays/captions
- render repeatedly after changing timing constants
- verify exact final duration and output properties

## Tool responsibilities and fallback order

| Task | Preferred | Fallback |
|---|---|---|
| Native WebMCP evidence | ChatGPT desktop built-in browser / Work or Codex | same browser in another ChatGPT session |
| Raw capture | existing recorder / OS capture | OBS → Screenity/Clipchamp |
| Video analysis | Gemini 3.7 Flash Agentic Video | Gemini 3.6 Flash → manual timestamp pass |
| Edit-plan JSON | Gemini structured output | Codex/Claude validation/fix |
| Narration | best existing Grok/local/Gemini TTS sample | another already-owned voice |
| Remotion build | Codex | Claude Code/Cowork → Grok/Antigravity if local command access exists |
| Final QA | human + alternate agent | Gemini video review + checklist |

Full interruption/fallback rules: `docs/demo-video-handoff.md`.
Current checkpoint: `docs/demo-video-state.md`.

## Narration — no new provider

Do not use `edge-tts` and do not buy a new TTS subscription.

Candidates:

1. Grok voice/TTS
2. existing local TTS models
3. Gemini TTS/audio generation

Generate the same 10–15 second sample and choose by:

- English pronunciation
- neutral professional delivery
- minimal synthetic cadence
- predictable duration
- clean output

Then generate seven scene files, not one monolithic track:

```text
video-demo/public/audio/
  01-scan.wav
  02-attention.wav
  03-details.wav
  04-human-state.wav
  05-compare.wav
  06-implementation.wav
  07-close.wav
```

## Local-only asset policy

Keep these uncommitted:

```text
video-demo/public/raw-webmcp-demo.mp4
video-demo/public/audio/*.wav
video-demo/public/audio/*.mp3
video-demo/out/
```

Track `video-demo/timeline.json` when it contains only timestamps/labels/evidence metadata. This file is intentionally not ignored because it enables model-independent resumption.

## Execution order

### P0 — documentation and handoff

- `docs/demo-video-handoff.md`
- `docs/demo-video-state.md`
- `docs/demo-timeline.schema.json`
- `docs/demo-remotion-runbook.md`
- local-media `.gitignore` rules

### P1 — authentic capture

Record the exact native WebMCP sequence from `docs/demo-video-state.md` and save the untouched recording.

### P2 — Gemini analysis

Run agentic video analysis using the prompt in `docs/demo-video-handoff.md`; save and validate `video-demo/timeline.json`.

### P3 — narration

Choose the best already-owned TTS by sample test and generate seven scene audio files.

### P4 — Remotion assembly

Codex or Claude Code consumes raw recording + `timeline.json` + narration and builds `RepoPulseWebMCPDemo` at 1920×1080/30fps.

### P5 — final render

Render MP4; verify <3:00, target ≈2:10, authentic evidence, clean audio, readable shared-state handoff.

### P6 — submission

Watch with audio and muted, upload public YouTube video, add URL to Devpost, and check all fields.

## Decision

Do **not** purchase Trupeer, CANVID, ElevenLabs, Descript, or another TTS service for this submission.

Do **not** use generated/recreated product screens.

Use the following resilient architecture:

```text
real WebMCP capture
   → Gemini agentic analysis
   → tracked timeline.json
   → existing narration source
   → Remotion + interchangeable coding agent
   → final MP4
```

No single model's conversational memory is required to finish the work.
