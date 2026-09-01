# RepoPulse WebMCP Demo — State

Last updated: 2026-09-01

This file is the single resumable checkpoint for demo-video production. Update it after every meaningful stage and before switching agents.

## Current phase

`P0 — documentation`

Status: `IN_PROGRESS`

## Completed

- RepoPulse WebMCP production behavior verified in ChatGPT native Site Tools.
- Final product verdict: READY FOR SUBMISSION.
- Devpost description and approved ~2:10 story exist in `docs/devpost-submission.md`.
- Zero-additional-cost production decision: Remotion + coding agent, existing Grok/local/Gemini TTS only.
- Multi-agent handoff protocol created in `docs/demo-video-handoff.md`.

## In progress

- Move production architecture to:
  `native capture → Gemini agentic video analysis → timeline.json → narration → Remotion → final MP4`.
- Add/verify tracked timeline schema and local media ignore rules.

## Not started

### P1 — authentic capture
- [ ] Record `raw-webmcp-demo.mp4` from real ChatGPT Site Tools execution.
- [ ] Verify all required evidence beats are present.
- [ ] Save an untouched backup outside the video project.

### P2 — Gemini analysis
- [ ] Upload/pass raw recording to Gemini 3.7 Flash with `processing: agentic`.
- [ ] Run the prompt in `docs/demo-video-handoff.md`.
- [ ] Save result as `video-demo/timeline.json`.
- [ ] Validate against `docs/demo-timeline.schema.json`.

### P3 — narration
- [ ] Generate one 10–15s comparison sample using available Grok/local/Gemini TTS.
- [ ] Select best voice based on clarity, natural delivery, and stable duration.
- [ ] Generate seven scene audio files.

### P4 — Remotion assembly
- [ ] Create/use isolated demo worktree/branch.
- [ ] Scaffold `video-demo/` Remotion project.
- [ ] Build `RepoPulseWebMCPDemo` from raw footage + timeline + narration.
- [ ] Preview and adjust timing constants.

### P5 — final render
- [ ] Render 1920×1080 MP4.
- [ ] Confirm duration <3:00, target ≈2:10.
- [ ] Verify evidence/narration synchronization and privacy.

### P6 — submission
- [ ] Watch final export with audio.
- [ ] Watch final export muted.
- [ ] Upload public YouTube video.
- [ ] Add video URL to Devpost and recheck all fields.

## Blockers

None currently documented.

## Next single action

**Capture the authentic native ChatGPT WebMCP session as `raw-webmcp-demo.mp4`.**

Do not generate narration or build the final Remotion timeline before the raw evidence recording exists.

## Required capture sequence

1. `scan_repository` on `https://github.com/torvalds/linux`
2. show `69/100`, Fair, `scan_truncated: true`
3. `get_attention_items` without another scan
4. show FAIL `github_actions` before WARN items
5. `get_check_details(github_actions)`
6. human manually scans `https://github.com/3ssiri/RepoPulse`
7. show `100/100`, Excellent
8. `compare_refs` with `v0.3.5` and `v0.3.6` without re-supplying repository URL
9. show `100/100 → 100/100`, delta 0
10. end on live WebMCP-enabled RepoPulse

## Last verification performed

Documentation-level only. No new recording, Gemini analysis, narration generation, Remotion preview, or render has been completed in this state file yet.
