# RepoPulse WebMCP Demo — Zero-Cost Production Stack

Research date: 2026-09-01

Goal: produce the final <3 minute WebMCP demo with **no additional paid subscription**, while preserving real native ChatGPT WebMCP evidence.

## Final recommendation

### Best zero-cost path

**Screenity or Clipchamp capture → Clipchamp AI voice + edit → optional Remotion/auto-editor automation**

This path avoids Trupeer/CANVID/ElevenLabs paid plans entirely.

The non-negotiable rule remains: record the real ChatGPT + RepoPulse WebMCP interaction first. AI may polish the recording, narration, captions, timing, zooms and cuts, but must not recreate or fabricate the product interaction.

## Option A — simplest, no code: Clipchamp only

Microsoft Clipchamp is the strongest single free option for this demo on Windows.

Current verified free capabilities:

- screen recording
- timeline editing
- AI text-to-speech voiceover
- automatic captions/transcript
- automatic pause removal / auto cut
- noise suppression
- 16:9 editing
- MP4 export up to 1080p on the free personal tier

Recommended use:

1. Record the real ChatGPT + RepoPulse interaction.
2. Import the recording into Clipchamp.
3. Paste each approved narration block into Text to Speech.
4. Choose a natural English voice and adjust pace.
5. Cut network waits and dead time.
6. Add the four short on-screen labels from the approved script.
7. Generate captions if useful.
8. Export 1080p MP4.

Official sources:

- https://support.microsoft.com/en-US/Clipchamp/feature-comparison-between-clipchamp-for-work-and-personal-versions
- https://support.microsoft.com/en-us/clipchamp/how-to-use-the-text-to-speech-feature
- https://support.microsoft.com/en-US/Clipchamp/exporting-and-saving-a-video-in-clipchamp
- https://clipchamp.com/en/features/ai-voice-over-generator/

## Option B — best free recorder: Screenity

Screenity is free, open source, has no recording limits, and can record a tab, desktop, application or selected area. It also supports click highlighting, annotations, zoom, trimming/cropping and MP4/WebM/GIF export.

For RepoPulse, use it only as the capture layer if it can record the actual ChatGPT desktop/in-app browser window on the machine. If the browser extension cannot capture the required desktop surface reliably, use Clipchamp or OBS instead.

Repository:

- https://github.com/alyssaxuu/screenity

## Option C — maximum control and reliability: OBS Studio

OBS Studio is free and open source and is suitable for capturing the exact ChatGPT + RepoPulse desktop layout at 1080p. It does not automate narration or editing, so pair it with Clipchamp or the local automation stack below.

Official source:

- https://obsproject.com/

## Free AI voice choices

### Preferred: Clipchamp Text to Speech

The feature is free for Clipchamp users and provides multiple English voices with pace/pitch controls. It is the simplest choice because narration stays in the editing timeline.

### Local/scriptable fallback: edge-tts

`edge-tts` is an open-source Python/CLI wrapper for Microsoft Edge's online TTS service and does not require an API key. It can generate both audio and subtitles.

Example:

```powershell
pipx install edge-tts
edge-tts --voice en-US-AvaNeural --text "Your narration here" --write-media narration.mp3 --write-subtitles narration.srt
```

Repository:

- https://github.com/rany2/edge-tts

Important: this relies on Microsoft's online TTS service even though there is no API key or separate paid plan.

## Agentic / repository-based automation

### Remotion — strongest zero-cost programmable finishing layer

Remotion can construct and render the final MP4 programmatically with React. Its current license explicitly allows free use for individuals and organizations with up to 3 employees, including commercial use.

For this demo, an agent such as Codex/Claude Code can create a small Remotion project that:

- imports the real screen recording
- imports narration audio
- cuts known loading ranges
- adds timed text overlays
- adds zoom/crop animations around the Site Tool call and dashboard
- synchronizes visual sections to the approved 0:00–2:10 script
- renders a deterministic 1080p MP4

This is the best path when the goal is to let a coding agent perform most of the editing work after the real recording exists.

Official project/license:

- https://github.com/remotion-dev/remotion
- https://github.com/remotion-dev/remotion/blob/main/LICENSE.md

### auto-editor — automatic dead-time removal

`auto-editor` is a free CLI that can automatically cut silence or motionless sections and also supports explicit manual ranges. It even publishes an agent skill install command:

```bash
npx skills add WyattBlue/auto-editor
```

Useful role here:

- preview/cut long idle sections
- speed up or remove silent/loading intervals
- hand the shortened recording to Remotion or Clipchamp

Do not rely blindly on automatic cuts around spoken narration; preview the result first.

Repository:

- https://github.com/WyattBlue/auto-editor

### LosslessCut — free manual emergency cutter

LosslessCut is free and open source and is useful for fast lossless trimming/splitting if one segment needs to be removed without a full re-encode.

Repository:

- https://github.com/mifi/lossless-cut

## Recommended zero-cost workflow for this exact submission

### Path 1 — fastest and easiest

**Clipchamp only**

1. Capture the real WebMCP demo.
2. Generate the approved English narration using Clipchamp Text to Speech.
3. Place each narration block over the matching screen section.
4. Cut all loading/waiting sections.
5. Add captions and the approved short labels.
6. Export 1080p MP4.

Use this first if the timeline is easy to align manually.

### Path 2 — best agent-assisted workflow

**Real recording → Remotion + edge-tts → MP4**

1. Capture one clean real WebMCP recording using Clipchamp/OBS/Screenity.
2. Save it as `raw-webmcp-demo.mp4`.
3. Have Codex/Claude Code create a dedicated Remotion composition from the approved script.
4. Generate English narration blocks with Clipchamp or `edge-tts`.
5. Put each narration block and corresponding video segment at deterministic timestamps.
6. Add zooms and overlays in code.
7. Render to 1920x1080 MP4.
8. Review the output once and adjust only the timestamp constants.

This path has the highest automation potential with no external paid editor.

### Path 3 — hybrid with automatic cutting

**OBS/Screenity → auto-editor → Clipchamp**

Use `auto-editor` to remove obvious dead space, then use Clipchamp for AI voice, captions, overlays and final 1080p export.

## Which existing agent environment should do what?

### OpenAI Work / Cloud Browser

Use it to execute and capture the **real WebMCP workflow** when ChatGPT Site Tools are required. It is not the final video editor.

### Codex

Best role: build a local Remotion/FFmpeg pipeline, generate timing code, run renders, inspect the rendered file, and iterate on deterministic edits.

### Claude Code / Cowork

Best role: same class of local repository work if it has access to the recording and local commands: build/edit a Remotion project, run `edge-tts`, `auto-editor`, FFmpeg and render commands. Do not use browser simulation as a substitute for the already-recorded native WebMCP evidence.

### Antigravity / other coding agents

Treat them as implementation agents for the same local pipeline, not as the source of WebMCP evidence. If they can edit/run the repo and invoke FFmpeg/Node/Python, they can automate the post-production steps.

## Existing-tool note

Previous project work has already used Remotion/Playwright-style video automation and FFmpeg-class local pipelines. That makes a repository-driven Remotion workflow a particularly sensible zero-cost option here, but the exact list of currently installed desktop applications/extensions on the machine must be checked locally rather than inferred from repository history.

## Approved demo content

Reuse the exact approved 0:00–2:10 script in `docs/devpost-submission.md`. Do not change the factual sequence:

1. `scan_repository` on `torvalds/linux`
2. `get_attention_items` with no rescan
3. `get_check_details(github_actions)`
4. human UI scan of `3ssiri/RepoPulse`
5. `compare_refs(v0.3.5, v0.3.6)` from the shared state
6. close on the four read-only tools and shared human-agent state

## Final zero-cost ranking

| Rank | Tool / stack | Cost | Best role |
|---|---|---:|---|
| 1 | Clipchamp | Free tier | Capture + AI voice + edit + captions + 1080p export |
| 2 | Remotion + coding agent | Free for eligible individual use | Maximum programmable automation and precise sync |
| 3 | Screenity | Free / open source | Lightweight real screen capture + annotations |
| 4 | OBS Studio | Free / open source | Most reliable raw desktop capture |
| 5 | edge-tts | Free / open source client | Scriptable English AI narration |
| 6 | auto-editor | Free / open source | Automatic removal/speed-up of dead time |
| 7 | LosslessCut | Free / open source | Fast emergency cuts without quality loss |

## Decision

Do **not** purchase Trupeer, CANVID, ElevenLabs or Descript for this submission.

Start with **Clipchamp**, because it already covers recording, free AI voice, captions, pause removal and 1080p export. If synchronization becomes tedious, move the same real recording into a **Remotion project controlled by Codex/Claude Code**, using Clipchamp or `edge-tts` for narration. This remains a zero-additional-cost workflow and gives full control over the 2:10 submission video.
