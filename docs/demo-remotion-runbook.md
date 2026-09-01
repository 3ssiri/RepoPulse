# RepoPulse WebMCP Demo — Remotion Execution Runbook

Decision date: 2026-09-01

This is the execution playbook for producing the final OpenAI WebMCP Challenge video with **Remotion + Codex/Claude Code**, using the user's existing TTS options (Grok, local TTS models, or Gemini) and without purchasing another video/TTS service.

## Safety boundary

Do **not** build the Remotion project directly on `main` while the production submission is stable.

Preferred setup:

```bash
git fetch origin
git worktree add ../RepoPulse-demo -b chore/demo-video main
cd ../RepoPulse-demo
```

Create the video project inside this worktree. Do not merge it into `main` before submission unless there is a specific reason. This prevents video-production dependencies or assets from triggering unnecessary Vercel changes.

Large recordings and generated audio should remain local and should not be committed.

## What the human must record

Record one truthful native ChatGPT WebMCP session with extra breathing room around every action. It can be longer than the final 2:10 video; Remotion will remove the waiting.

Record this exact sequence:

1. ChatGPT and RepoPulse visible, preferably side by side.
2. WebMCP `scan_repository` on `https://github.com/torvalds/linux`.
3. Keep the completed `69/100`, `Fair`, `scan_truncated: true` result visible for several seconds.
4. WebMCP `get_attention_items` without another scan.
5. Keep the returned order visible: FAIL `github_actions`, then WARN `gitignore`, `tests`, `dependencies`, `security`.
6. WebMCP `get_check_details` for `github_actions`.
7. In the human RepoPulse UI, manually scan `https://github.com/3ssiri/RepoPulse`.
8. Keep the completed `100/100`, `Excellent` dashboard visible.
9. From ChatGPT, call WebMCP `compare_refs` using `v0.3.5` and `v0.3.6` without supplying the repository URL again.
10. Keep the comparison `100/100 → 100/100`, delta `0` visible.
11. End on the live WebMCP-enabled RepoPulse page.

Recording recommendations:

- 1920×1080 or higher
- 16:9
- 30 fps is sufficient
- no intro/title card
- no login/setup footage
- hide unrelated tabs, notifications and sensitive desktop content
- leave 2–4 seconds before and after important state changes; cuts will remove excess time later
- do not worry about narration during capture; silent capture is fine

Save the untouched recording as:

```text
video-demo/public/raw-webmcp-demo.mp4
```

Keep another untouched backup outside the project.

## Generate narration with existing TTS

Do not use `edge-tts` and do not purchase another TTS provider.

Use one of:

1. Grok voice/TTS
2. a local TTS model already available on the machine
3. Gemini TTS/audio generation

First generate the same 10–15 second sample in the candidate voices. Pick the voice with the clearest professional English and the most predictable pacing.

Then generate **one file per scene**, not one long file:

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

WAV is preferred during editing when available; high-quality MP3 is acceptable.

Use the exact narration text from `docs/devpost-submission.md` unless deliberately revised first.

## Create the Remotion project

Inside the `RepoPulse-demo` worktree:

```bash
npx create-video@latest --yes --blank --no-tailwind video-demo
cd video-demo
npm i
npx remotion add @remotion/media
```

Remotion's current agent guidance recommends assets in `public/`, media through `@remotion/media`, preview through `npx remotion studio --no-open`, and rendering through `npx remotion render`.

Do not add web-app dependencies to the root RepoPulse Python project.

## Local-only asset rules

Add these patterns to the video project's `.gitignore`:

```gitignore
public/raw-webmcp-demo.mp4
public/audio/*.wav
public/audio/*.mp3
out/
```

The production recipe/code may be versioned on `chore/demo-video`, but the raw desktop recording and generated narration do not need to be pushed to GitHub.

## Recommended project structure

```text
video-demo/
  package.json
  remotion.config.ts
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

## Composition specification

Create one composition:

```text
id: RepoPulseWebMCPDemo
width: 1920
height: 1080
fps: 30
```

Initial target duration: 130 seconds / 3900 frames.

The final duration should be calculated from the real scene durations and narration, and must remain under 180 seconds.

## Scene manifest

Use a single typed manifest as the source of truth for timing. Initial targets:

```ts
export const scenes = [
  {id: 'scan', from: 0, duration: 15, audio: 'audio/01-scan.wav'},
  {id: 'attention', from: 15, duration: 20, audio: 'audio/02-attention.wav'},
  {id: 'details', from: 35, duration: 15, audio: 'audio/03-details.wav'},
  {id: 'human-state', from: 50, duration: 20, audio: 'audio/04-human-state.wav'},
  {id: 'compare', from: 70, duration: 20, audio: 'audio/05-compare.wav'},
  {id: 'implementation', from: 90, duration: 25, audio: 'audio/06-implementation.wav'},
  {id: 'close', from: 115, duration: 15, audio: 'audio/07-close.wav'},
] as const;
```

These are starting targets only. The agent should measure each narration file and adjust the visual segment to the real audio duration.

## Editing model

Do not physically rewrite the source screen recording unless necessary. Use Remotion to build a virtual edit from the raw recording.

For each scene define:

- source video trim start
- source video trim end
- output scene start
- narration audio
- optional playback-rate for a waiting interval
- optional zoom rectangle / scale
- optional overlay text

Use `<Video>` and `<Audio>` from `@remotion/media`, `staticFile()` for local assets, and Remotion frame-based timing. Use `trimBefore`/`durationInFrames` or `<Sequence>` for non-destructive cuts.

Animations must be frame-driven (`useCurrentFrame()`, `interpolate()`, `spring()`), not CSS transitions/animations.

## Visual treatment

Keep styling restrained and evidence-first.

Allowed:

- hard cuts over loading
- short crossfade only when it does not hide state changes
- 1.08×–1.22× zooms on the active ChatGPT Site Tool call/result
- 1.08×–1.18× zoom on RepoPulse score/comparison when it changes
- short overlay labels
- optional captions in safe lower-third space

Do not use:

- title card
- AI avatar
- synthetic/recreated application screens
- decorative transitions that obscure the real interface
- fake mouse/tool activity

Approved overlay labels:

```text
WebMCP action → same visible dashboard
Current state · no repository rescan
Human action → shared agent state
One product · one state · human + agent
```

## Synchronization strategy

The audio is the pacing source of truth after the factual screen capture.

For each scene:

1. measure narration duration
2. identify the exact raw-video range containing the required action/result
3. remove dead waiting before/after the result
4. if the useful visual action is shorter than the narration, hold on the completed real result instead of inventing footage
5. if the raw interaction is slightly longer than narration, speed only unimportant waiting portions; keep actual clicks/tool calls/results at natural speed
6. align the key visible state change within the sentence that describes it

Do not stretch or speed the synthetic narration just to fit a bad visual cut unless the adjustment is very small. Regenerate that scene's TTS or change its source-video trim instead.

## Preview loop

Start Remotion Studio:

```bash
npx remotion studio --no-open
```

If running through Codex and the watcher hits an `EMFILE` limit:

```bash
npx remotion studio --no-open --webpack-poll 1000
```

Review these points first:

- first 15 seconds: WebMCP action and dashboard update are immediately understandable
- attention scene: FAIL-before-WARN order is readable
- human-state scene: it is obvious the human selected RepoPulse manually
- compare scene: the agent uses the currently selected repository and the same dashboard updates
- ending: final claim matches what is visibly on screen

## Render

After the preview is approved:

```bash
npx remotion render RepoPulseWebMCPDemo out/repopulse-webmcp-demo.mp4
```

Verify:

- 1920×1080
- 16:9
- audio present and clean
- duration < 3:00
- target ≈ 2:10
- no clipped UI/text
- no private notifications or secrets
- all WebMCP claims correspond to real visible actions

## Exact Codex / Claude Code handoff prompt

Use the following instruction in the coding agent after the raw video and scene audio files are present:

```text
Work in the RepoPulse demo worktree only. Do not modify the production web app, Python package, Vercel configuration, or main branch.

Build a small Remotion project in `video-demo/` for the OpenAI WebMCP Challenge demo.

Source of truth:
- `docs/devpost-submission.md` for the approved narration/story.
- `docs/demo-remotion-runbook.md` for the production rules.
- `video-demo/public/raw-webmcp-demo.mp4` is the authentic native ChatGPT WebMCP screen recording. Never recreate or replace its application screens.
- narration assets are in `video-demo/public/audio/`.

Requirements:
1. Scaffold/use a blank Remotion project with no Tailwind.
2. Use 1920x1080, 30fps, composition id `RepoPulseWebMCPDemo`.
3. Use `@remotion/media` Video/Audio and non-destructive trims of the raw recording.
4. Implement the seven approved scenes using one typed timing manifest.
5. Measure the real narration durations and make them the pacing source of truth.
6. Cut network waits aggressively while preserving all real tool calls/results.
7. Add restrained frame-driven zooms around WebMCP actions and RepoPulse state changes.
8. Add only the approved short overlay labels.
9. No title card, avatar, fabricated UI, fake cursor activity, decorative filler, or background music.
10. Keep raw recording/audio/output files ignored by Git.
11. Start `npx remotion studio --no-open` and inspect the composition.
12. Fix timing/readability issues iteratively, changing timing constants rather than overcomplicating the component structure.
13. Render `out/repopulse-webmcp-demo.mp4` only after the preview is coherent.
14. Verify the final video is under 3 minutes, ideally around 2:10, and report exact duration plus any assumptions/cuts made.

Do not claim a scene is verified unless it is actually visible in the source recording. If an expected action is missing from the recording, stop editing that scene and report exactly which source footage needs to be rerecorded.
```

## Division of labor

### Human

Only needs to:

1. capture the authentic WebMCP session
2. choose the preferred Grok/local/Gemini voice
3. generate or provide the seven narration files
4. approve the preview/final render

### Codex / Claude Code

Should handle:

- project scaffolding
- media ingestion
- source-video trims
- timeline timing
- audio synchronization
- zooms/overlays
- render commands
- technical validation
- iteration

## Final execution order

```text
1. Capture real WebMCP footage
2. Generate 7 TTS scene files (Grok/local/Gemini)
3. Create RepoPulse-demo worktree
4. Run the handoff prompt in Codex or Claude Code
5. Agent builds Remotion composition
6. Preview in Remotion Studio
7. Adjust timing constants
8. Render 1080p MP4
9. Watch once with audio and once muted
10. Upload publicly to YouTube
11. Put YouTube link into Devpost
```
