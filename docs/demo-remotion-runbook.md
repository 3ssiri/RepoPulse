# RepoPulse WebMCP Demo — Execution Runbook

Decision date: 2026-09-01

This is the executable playbook for producing the final OpenAI WebMCP Challenge video with **no additional paid service**.

Primary path:

```text
Native ChatGPT WebMCP capture
        ↓
authentic raw screen recording
        ↓
Gemini Agentic Video Understanding
        ↓
structured `video-demo/timeline.json`
        ↓
Grok / local TTS / Gemini narration assets
        ↓
Remotion + Codex or Claude Code
        ↓
1080p MP4 (<3:00, target ≈2:10)
```

For interruption recovery and model/tool switching, read `docs/demo-video-handoff.md` and `docs/demo-video-state.md` first.

## Safety boundary

Do **not** build video-production code directly on the stable submission branch unless intentionally documenting it.

Preferred local setup:

```bash
git fetch origin
git worktree add ../RepoPulse-demo -b chore/demo-video main
cd ../RepoPulse-demo
```

Raw recordings, generated audio, and rendered output remain local. The production application, Python package, Vercel configuration, and WebMCP behavior must not be changed for video production.

The authentic raw recording is the only source of ChatGPT, WebMCP, and RepoPulse screens. Gemini and Remotion may analyze, trim, zoom, caption, narrate, or hold real footage, but may not regenerate or replace those screens.

## Phase 1 — capture authentic evidence

Record one truthful native ChatGPT Site Tools session with extra breathing room around every action.

Required sequence:

1. ChatGPT and RepoPulse visible, preferably side by side.
2. WebMCP `scan_repository` on `https://github.com/torvalds/linux`.
3. Keep `69/100`, `Fair`, `scan_truncated: true` visible.
4. WebMCP `get_attention_items` without another scan.
5. Keep FAIL `github_actions` followed by WARN `gitignore`, `tests`, `dependencies`, `security` visible.
6. WebMCP `get_check_details` for `github_actions`.
7. In the human RepoPulse UI, manually scan `https://github.com/3ssiri/RepoPulse`.
8. Keep `100/100`, `Excellent` visible.
9. From ChatGPT call WebMCP `compare_refs` with `v0.3.5` and `v0.3.6` without supplying the repository URL again.
10. Keep `100/100 → 100/100`, delta `0` visible.
11. End on the live WebMCP-enabled RepoPulse page.

Recording guidance:

- 1920×1080 or higher
- 16:9
- 30fps is sufficient
- silent capture is fine
- no intro/title card
- no login/setup footage
- hide unrelated tabs, notifications, credentials, and private desktop content
- leave 2–4 seconds before/after important state changes

Save the untouched recording locally as:

```text
video-demo/public/raw-webmcp-demo.mp4
```

Also keep an untouched backup outside the demo project.

### P1 DONE when

- raw MP4 exists
- all required evidence beats are visibly present
- backup exists
- no sensitive data is visible

If an evidence beat is missing, rerecord before post-production.

## Phase 2 — Gemini Agentic Video Understanding

Use Gemini to identify exact evidence moments and cut boundaries before Remotion editing.

Preferred model:

```text
gemini-3.7-flash
```

Use agentic video processing:

```json
{
  "type": "video",
  "uri": "<uploaded-video-uri>",
  "processing": "agentic"
}
```

Fallback: Gemini 3.6 Flash with agentic processing.

Gemini's job is **analysis only**. It must never generate replacement product footage.

Input:

- `raw-webmcp-demo.mp4`
- approved story in `docs/devpost-submission.md`
- schema in `docs/demo-timeline.schema.json`

Required output:

```text
video-demo/timeline.json
```

Use the exact Gemini prompt from `docs/demo-video-handoff.md`.

Gemini must locate:

1. `scan_repository` execution
2. Linux 69/100 result visible
3. `get_attention_items` execution
4. FAIL-before-WARN result visible
5. `get_check_details(github_actions)` execution/result
6. human RepoPulse repository switch
7. RepoPulse 100/100 result
8. `compare_refs(v0.3.5, v0.3.6)` execution without repository reselection
9. delta-0 comparison visible
10. final live product state

The generated JSON must match `docs/demo-timeline.schema.json` and include source start/end, action/result timestamps, evidence text, confidence, safe-cut flag, and dead ranges to cut/speed up.

If Gemini cannot verify a required scene, set `status: "NEEDS_RERECORD"`; do not infer it.

### P2 DONE when

- Gemini agentic analysis actually ran on the raw video
- `video-demo/timeline.json` exists
- JSON validates against the schema
- every required evidence beat is `FOUND` or explicitly `NEEDS_RERECORD`
- no generated UI is used

## Phase 3 — narration with existing TTS

Do not buy another TTS service and do not use `edge-tts`.

Candidates already available:

1. Grok voice/TTS
2. existing local TTS model(s)
3. Gemini TTS/audio generation

Generate the same 10–15 second sample with candidate voices and choose by:

- English clarity
- neutral professional delivery
- natural cadence
- stable/predictable duration
- clean audio

Then generate one file per scene:

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

Use exact approved narration from `docs/devpost-submission.md` unless deliberately revised first.

### P3 DONE when

- one voice was selected by an actual sample comparison
- all seven narration files exist
- wording matches approved script

## Phase 4 — create the Remotion project

Inside the demo worktree:

```bash
npx create-video@latest --yes --blank --no-tailwind video-demo
cd video-demo
npm i
npx remotion add @remotion/media
```

Recommended structure:

```text
video-demo/
  package.json
  remotion.config.ts
  timeline.json
  src/
    Root.tsx
    RepoPulseDemo.tsx
    scenes.ts
    components/
      ScreenRecording.tsx
      ZoomWindow.tsx
      OverlayLabel.tsx
  public/
    raw-webmcp-demo.mp4
    audio/
      01-scan.wav
      02-attention.wav
      03-details.wav
      04-human-state.wav
      05-compare.wav
      06-implementation.wav
      07-close.wav
  out/
```

Composition:

```text
id: RepoPulseWebMCPDemo
width: 1920
height: 1080
fps: 30
```

The source-video edit plan comes from `timeline.json`; narration duration determines final pacing.

## Phase 5 — Remotion editing model

Codex is the preferred implementation agent; Claude Code/Cowork is the first fallback. Grok/Antigravity may continue the same project only if they can access the same repository/worktree and run Node/Remotion/FFmpeg commands.

Before editing, the agent must read:

```text
docs/demo-video-state.md
docs/demo-video-handoff.md
docs/demo-remotion-runbook.md
docs/devpost-submission.md
video-demo/timeline.json
```

Use non-destructive source trims. For each scene define:

- source trim start/end from `timeline.json`
- output scene start
- narration asset
- optional hold range
- optional dead range removal or speed-up
- optional crop/zoom
- optional approved overlay

Use `<Video>` and `<Audio>` from `@remotion/media`, `staticFile()` for local assets, and frame-based timing with `useCurrentFrame()`, `interpolate()`, or `spring()`.

Do not use CSS transitions/animations for rendered timing.

Allowed visual treatment:

- hard cuts over waiting
- modest speed-up only on unimportant waiting
- hold on completed real results
- 1.08×–1.22× restrained zooms on Site Tool actions/results
- 1.08×–1.18× dashboard zooms on score/comparison changes
- short approved overlays
- optional captions if they do not obscure evidence

Forbidden:

- title card
- AI avatar
- generated/recreated application screens
- fake cursor activity
- decorative filler
- background music

Approved overlays:

```text
WebMCP action → same visible dashboard
Current state · no repository rescan
Human action → shared agent state
One product · one state · human + agent
```

### Synchronization rule

The factual raw footage is the evidence source; narration is the pacing source.

For each scene:

1. measure narration duration
2. take the exact raw range from `timeline.json`
3. remove dead waits
4. align the state change with the sentence describing it
5. hold on the completed real result if narration is longer
6. speed only non-evidence waiting if the raw scene is slightly long
7. regenerate one TTS scene or adjust trim rather than distorting narration heavily

### P4 DONE when

- composition opens in Remotion Studio
- all seven scenes use real raw footage ranges
- narration is synchronized
- approved zooms/labels are implemented
- no scene relies on synthetic UI

## Preview

```bash
npx remotion studio --no-open
```

If Codex hits a file-watcher limit:

```bash
npx remotion studio --no-open --webpack-poll 1000
```

Review first:

- first 15 seconds immediately show native WebMCP value
- attention order is readable
- human repository switch is unmistakable
- compare uses the current human-selected repository
- ending claim matches the visible product

## Phase 5 — final render

After preview approval:

```bash
npx remotion render RepoPulseWebMCPDemo out/repopulse-webmcp-demo.mp4
```

Verify:

- 1920×1080
- 16:9
- clean audio
- duration <180s, target ≈130s
- no clipped UI/text
- no private notifications/secrets
- every WebMCP claim maps to a real visible action
- shared state is understandable with audio muted

### P5 DONE when

All checks above pass on the rendered MP4.

## Phase 6 — submission

1. watch final MP4 with audio
2. watch it muted
3. upload publicly to YouTube
4. add YouTube URL to Devpost
5. recheck live URL, testing instructions, repo, MIT license, description, team fields

## Interruption / quota recovery

Do not depend on chat memory.

Every agent must:

1. read `docs/demo-video-state.md`
2. read `docs/demo-video-handoff.md`
3. inspect Git/worktree state
4. continue only the next incomplete phase
5. update the state file before ending or switching tools

If a model hits quota, preserve files and move to the next fallback. Never reset or regenerate completed work only because the previous model is unavailable.

## Exact implementation handoff

Use the resume prompt in `docs/demo-video-handoff.md`. It is intentionally tool-neutral so Codex, Claude Code/Cowork, Grok, or another capable coding agent can continue the same Remotion project without historical chat context.
