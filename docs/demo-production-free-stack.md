# RepoPulse WebMCP Demo — Zero-Cost Production Stack

Research/decision date: 2026-09-01

Goal: produce the final <3 minute WebMCP demo with **no additional paid subscription**, while preserving real native ChatGPT WebMCP evidence.

## Final recommendation

### Primary path — recommended

**Real WebMCP recording → Remotion + Codex/Claude Code → existing TTS (Grok / local TTS / Gemini) → 1080p MP4**

This is now the preferred production path because it offers the highest automation potential, deterministic timing, precise synchronization, repeatable rendering, and no need to buy a separate video SaaS.

The non-negotiable rule remains: **record the real ChatGPT + RepoPulse WebMCP interaction first.** The post-production pipeline may cut, zoom, caption, narrate, synchronize, or annotate that recording, but it must not recreate or fabricate the product interaction itself.

## Why Remotion + Codex/Claude Code is the best fit

Remotion turns the demo into a small reproducible video project rather than a manually edited timeline. A coding agent can control almost every production detail from source code and configuration:

- import the real WebMCP screen recording
- split it into the approved story beats
- cut or compress loading/waiting intervals
- place narration audio at deterministic timestamps
- synchronize visual actions to narration
- add timed zoom/crop animations around Site Tool calls and dashboard updates
- add captions and the approved short on-screen labels
- keep a consistent 16:9 / 1920x1080 composition
- render the final MP4 repeatedly after small timing changes
- keep the whole production recipe version-controlled alongside RepoPulse

This is preferable to a SaaS editor for this submission because the approved sequence is already known and only ~2:10 long. Once the real recording and narration files exist, most iteration should be changing timing constants rather than re-editing manually.

Official Remotion project/license:

- https://github.com/remotion-dev/remotion
- https://github.com/remotion-dev/remotion/blob/main/LICENSE.md

## Agent responsibilities

### Codex — preferred implementation agent

Use Codex to:

1. scaffold a small Remotion composition for this demo
2. ingest the raw screen recording and narration assets
3. implement the approved 0:00–2:10 timeline
4. create deterministic cuts, zooms, overlays and transitions
5. run Remotion/FFmpeg commands
6. render preview and final 1080p MP4 outputs
7. inspect duration and technical output
8. iterate by adjusting timing constants only where possible

### Claude Code / Cowork — equivalent implementation path

Use Claude Code/Cowork for the same repository-local post-production work if it has access to the recording and command execution environment:

- Remotion source edits
- Node/FFmpeg commands
- asset placement
- timing synchronization
- render/preview iterations

### Antigravity / other coding agents

They may implement or refine the same local Remotion pipeline when they can edit the repository and run Node/FFmpeg tooling. They are post-production agents, not a substitute for the native ChatGPT WebMCP capture.

### OpenAI Work / ChatGPT browser

Use Work/ChatGPT to execute and capture the **real native WebMCP flow**. Its role is evidence capture, not final editing.

## Narration — use existing TTS, no new provider

**Do not use edge-tts and do not buy a new TTS subscription for this demo.**

Available narration sources already in the user's toolchain are sufficient:

1. **Grok TTS / voice generation** — candidate for the final English narration if its selected voice sounds natural and gives predictable pacing.
2. **Existing local TTS models** — preferred when they provide natural English output with clean audio and reproducible generation; zero marginal cost and can be fully automated locally.
3. **Gemini TTS / audio generation** — strong alternate source already available to the user; use when it gives the best voice quality or pacing for this script.

Selection criterion is not vendor preference. Generate the same short 10–15 second narration sample with the available sources and choose the one with:

- clearest English pronunciation
- neutral professional delivery
- minimal synthetic cadence
- predictable duration
- clean audio with no background artifacts

Then generate the approved narration as separate scene audio files rather than one monolithic track. Scene-level files make Remotion synchronization and rerecording much easier.

Suggested asset structure:

```text
video-demo/
  public/
    raw-webmcp-demo.mp4
    audio/
      01-scan.mp3
      02-attention.mp3
      03-details.mp3
      04-human-state.mp3
      05-compare.mp3
      06-implementation.mp3
      07-close.mp3
```

## Capture options — all zero additional cost

The capture layer only needs to produce a truthful, readable screen recording of the actual WebMCP execution.

### 1. Existing ChatGPT/Work recording path

Preferred when it can capture the native browser session cleanly. Keep ChatGPT and RepoPulse visible side by side where practical.

### 2. OBS Studio

Free/open source and a reliable Windows desktop capture fallback.

- https://obsproject.com/

### 3. Screenity

Free/open source browser/desktop capture option with annotations, click highlighting, zoom and export features.

- https://github.com/alyssaxuu/screenity

### 4. Clipchamp

Useful as a free Windows capture or emergency manual-edit fallback. It is no longer the preferred production editor; Remotion is the primary finishing layer.

## Optional open-source helpers

### auto-editor

Free CLI for automatic removal/speed-up of obvious dead time. Use only as a preprocessing helper when it clearly saves effort; Remotion should remain the source of truth for the final timeline.

Repository:

- https://github.com/WyattBlue/auto-editor

Agent skill install documented by the project:

```bash
npx skills add WyattBlue/auto-editor
```

### LosslessCut

Free/open-source emergency trimming tool for extracting or removing raw recording sections before they enter the Remotion pipeline.

- https://github.com/mifi/lossless-cut

## Recommended repository workflow

### Phase 1 — capture evidence

Record the real flow once, preferably with extra breathing room before/after each action:

1. `scan_repository` on `torvalds/linux`
2. visible `69/100`, Fair result
3. `get_attention_items` without another scan
4. visible FAIL then WARN order
5. `get_check_details(github_actions)`
6. human UI scan of `3ssiri/RepoPulse`
7. visible `100/100` result
8. `compare_refs(v0.3.5, v0.3.6)` without re-supplying the repository
9. visible `100/100 → 100/100`, delta 0
10. final visible WebMCP-enabled product state

Save the original untouched recording separately.

### Phase 2 — generate narration assets

Use Grok, a local TTS model, or Gemini. Generate one audio file per script section. Do not change factual wording unless the approved script is deliberately revised first.

### Phase 3 — build the Remotion composition

Codex/Claude Code should create a small isolated video project that consumes:

- raw screen capture
- scene narration files
- scene timing manifest
- approved overlays

Recommended data model:

```ts
const scenes = [
  {id: 'scan', start: 0, end: 15, audio: 'audio/01-scan.mp3'},
  {id: 'attention', start: 15, end: 35, audio: 'audio/02-attention.mp3'},
  {id: 'details', start: 35, end: 50, audio: 'audio/03-details.mp3'},
  {id: 'human-state', start: 50, end: 70, audio: 'audio/04-human-state.mp3'},
  {id: 'compare', start: 70, end: 90, audio: 'audio/05-compare.mp3'},
  {id: 'implementation', start: 90, end: 115, audio: 'audio/06-implementation.mp3'},
  {id: 'close', start: 115, end: 130, audio: 'audio/07-close.mp3'},
];
```

Treat these times as initial targets, not rigid truth. The final visual timing should follow the actual narration duration while remaining comfortably under 3:00.

### Phase 4 — automated polish

Implement in Remotion:

- hard cuts over network waits
- restrained zooms around the active WebMCP call/result
- dashboard zoom when its visible state changes
- short text overlays only where specified
- no title card
- no avatar
- no decorative transitions that hide the real interface
- optional captions if they remain readable without obscuring evidence

### Phase 5 — render and verify

Render:

- 1920×1080
- 16:9
- MP4
- target duration about 2:10
- absolute maximum <3:00

Verification checklist:

- every claimed WebMCP action is visibly real
- narration matches the visual state
- no fabricated/reconstructed product screen
- loading cuts do not imply a different result
- Site Tool names remain readable when relevant
- shared-state handoff is understandable even with audio muted
- no sensitive desktop data appears

## Approved story sequence

Reuse the exact approved narration/content from `docs/devpost-submission.md`:

1. WebMCP `scan_repository` from the first seconds
2. `get_attention_items` from current state with no rescan
3. `get_check_details(github_actions)`
4. human changes the shared state to `3ssiri/RepoPulse`
5. agent continues with `compare_refs(v0.3.5, v0.3.6)` without another repository selection
6. briefly explain the four read-only tools
7. close on one product / one state / human + agent

## Final zero-cost ranking

| Rank | Tool / stack | Cost | Best role |
|---|---|---:|---|
| 1 | **Remotion + Codex/Claude Code** | No additional cost | Primary editing, synchronization, zooms, overlays and deterministic rendering |
| 2 | **Grok / local TTS / Gemini** | Already available | Narration generation; choose by actual voice-quality test |
| 3 | OBS Studio | Free / open source | Reliable raw desktop capture |
| 4 | Screenity | Free / open source | Lightweight screen capture + annotations |
| 5 | Clipchamp | Free tier | Capture/manual emergency fallback |
| 6 | auto-editor | Free / open source | Optional dead-time preprocessing |
| 7 | LosslessCut | Free / open source | Emergency raw trimming |

## Decision

**Primary production architecture:**

```text
Native ChatGPT WebMCP capture
        ↓
real raw screen recording
        ↓
Grok / local TTS / Gemini narration assets
        ↓
Remotion project controlled by Codex or Claude Code
        ↓
programmatic cuts + timing + zooms + overlays + captions
        ↓
1080p MP4 (<3:00, target ≈2:10)
        ↓
public YouTube upload
```

Do not purchase Trupeer, CANVID, ElevenLabs, Descript, or another TTS service for this submission. Do not use `edge-tts`. The preferred path is now **Remotion + Codex/Claude Code**, using the TTS resources already available to the user.
