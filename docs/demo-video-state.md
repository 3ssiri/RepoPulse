# RepoPulse WebMCP Demo — State

Last updated: 2026-09-02T00:30 AST

This file is the single resumable checkpoint for demo-video production. Update it after every meaningful stage and before switching agents.

## Current phase

`P1 — authentic capture`

Status: `P1_COMPLETE — PRIVACY_SAFE_PROXIES_VERIFIED`

Checkpoint (2026-09-02T00:30, Asia/Riyadh):
- 8 NVIDIA clips copied (SHA256-verified) in `video-demo/public/raw/`.
- Raw originals remain untouched and unedited.
- Full manifest at `video-demo/source-clips.json` with `analysis_proxy_path` for all 8 clips.
- Machine-specific local paths stored in untracked `video-demo/source-clips.local.json`.
- 8 complete privacy-safe 1080p proxies generated at `video-demo/public/proxy/clip-01.mp4` .. `clip-08.mp4`.
- Approved production filter: `crop=2560:1360:0:0,scale=1920:1020,pad=1920:1080:0:30:black`.
- Visual inspection and fine-grained scan complete: 100% taskbar-free, 100% clean identity, clear evidence.
- Exact NVIDIA overlay dead ranges documented: `0.0s .. 7.0s` (clip-06: `7.1s`).
- Ready for P2 (Gemini analysis) using strictly `analysis_proxy_path` proxies.

### Source material & Proxy manifest

The previously recorded single-file `video-demo/public/raw-webmcp-demo.mp4`
(234.167s, 1920×1080, 30fps) is **INVALID** and must not be used in the
final video.

The valid source is a collection of **eight NVIDIA ShadowPlay MP4 clips**
mirrored into `video-demo/public/raw/` (machine-specific source folder
recorded in untracked `video-demo/source-clips.local.json`):

| # | Clip ID | Raw Filename | Proxy Path | Duration | SHA256 (first 16) | Overlay Active | Safe Usable After |
|---|---|---|---|---|---|---|---|
| 1 | `clip-01` | `Desktop 2026.09.01 - 23.18.03.02.mp4` | `video-demo/public/proxy/clip-01.mp4` | 97.28s | `8cbc20be002669fd` | 0.0–7.0s | 7.3s |
| 2 | `clip-02` | `Desktop 2026.09.01 - 23.20.09.03.mp4` | `video-demo/public/proxy/clip-02.mp4` | 58.83s | `ecf1f40713cba8c1` | 0.0–7.0s | 7.3s |
| 3 | `clip-03` | `Desktop 2026.09.01 - 23.22.18.04.mp4` | `video-demo/public/proxy/clip-03.mp4` | 37.51s | `b2dc5fe19403d243` | 0.0–7.0s | 7.3s |
| 4 | `clip-04` | `Desktop 2026.09.01 - 23.26.41.06.mp4` | `video-demo/public/proxy/clip-04.mp4` | 32.84s | `64e8de779b385904` | 0.0–7.0s | 7.3s |
| 5 | `clip-05` | `Desktop 2026.09.01 - 23.28.56.07.mp4` | `video-demo/public/proxy/clip-05.mp4` | 21.79s | `02017566feed9cbc` | 0.0–7.0s | 7.3s |
| 6 | `clip-06` | `Desktop 2026.09.01 - 23.29.54.08.mp4` | `video-demo/public/proxy/clip-06.mp4` | 27.32s | `ee5a8e79f7d2c60d` | 0.0–7.1s | 7.4s |
| 7 | `clip-07` | `Desktop 2026.09.01 - 23.31.11.09.mp4` | `video-demo/public/proxy/clip-07.mp4` | 45.35s | `47cf24f48da83c05` | 0.0–7.0s | 7.3s |
| 8 | `clip-08` | `Desktop 2026.09.01 - 23.38.20.10.mp4` | `video-demo/public/proxy/clip-08.mp4` | 31.29s | `ef2bd8f3faf4e19f` | 0.0–7.0s | 7.3s |

All raw clips: 2560×1440, 59.94fps, H.264 High, AAC LC stereo 48kHz.
All proxies: 1920×1080, 59.94fps, H.264, AAC stereo.
Combined duration: **352.21s**.
The raw originals must be preserved exactly — never moved, renamed, edited,
overwritten, trimmed, transcoded, or deleted.

### Privacy review summary

Document: `video-demo/privacy-review.md`

**Approved Filter:** `crop=2560:1360:0:0,scale=1920:1020,pad=1920:1080:0:30:black`
- Removes the entire 80px bottom region containing the Windows taskbar (`y >= 1360`, taskbar starts at `y = 1378`).
- Zero taskbar or personal app icon pixels remain in any proxy.
- Letterbox padding: top 30px, bottom 30px.
- ChatGPT right panel and RepoPulse left panel are completely sharp and readable.
- NVIDIA recording indicator appears during `0.0s .. 7.0s` (clip-06: `7.1s`) across clips; recommended dead ranges are `0.0s .. 7.3s` (clip-06: `7.4s`) with action `CUT`.

## Completed

### P0 — documentation and resilient handoff
- [x] RepoPulse WebMCP production behavior verified in ChatGPT native Site Tools.
- [x] Final product verdict: READY FOR SUBMISSION.
- [x] Devpost description and approved ~2:10 story exist in `docs/devpost-submission.md`.
- [x] Zero-additional-cost architecture documented as:
  `native capture → Gemini agentic video analysis → timeline.json → narration → Remotion → final MP4`.
- [x] Multi-agent handoff protocol exists in `docs/demo-video-handoff.md`.
- [x] Execution runbook updated in `docs/demo-remotion-runbook.md`.
- [x] `docs/demo-timeline.schema.json` updated and validated for multi-clip timelines.
- [x] `.gitignore` excludes raw capture, proxies, previews, narration audio, and rendered output while leaving `video-demo/timeline.json` and manifests trackable.

### P1 — authentic capture & privacy verification
- [x] Record raw WebMCP demo from real ChatGPT Site Tools execution (8 NVIDIA clips).
- [x] Verify all required evidence beats are present through native tool results, live page state, and sampled capture frames.
- [x] Save untouched originals (preserved in NVIDIA Desktop directory).
- [x] Eight-clip inventory inspected via ffprobe: all 8 valid, 352.21s combined, 2560×1440/59.94fps.
- [x] Copy clips to workspace: `video-demo/public/raw/` (SHA256-verified).
- [x] Create manifest: `video-demo/source-clips.json` (8 clips, all metadata, `analysis_proxy_path`).
- [x] Generate 8 complete privacy-safe proxies under `video-demo/public/proxy/` using approved 1360px crop.
- [x] Verify all 8 full proxies (1920x1080, 59.94fps, audio, expected duration, zero taskbar pixels).
- [x] Fine-grained timestamp scan for NVIDIA overlays (documented dead ranges).
- [x] Complete privacy review document: `video-demo/privacy-review.md`.

## Not started

### P2 — Gemini analysis
- [ ] Pass privacy-safe proxies (`video-demo/public/proxy/clip-*.mp4` via `analysis_proxy_path`) to Gemini 3.7 Flash with `processing: agentic`.
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

None. P1 is complete and all full proxies are verified. Ready for Gemini P2 analysis.

## Next single action

**Execute Gemini P2 Analysis.**
Pass the 8 verified proxy clips (`video-demo/public/proxy/clip-01.mp4` .. `clip-08.mp4`) specified in `video-demo/source-clips.json` to Gemini to produce `video-demo/timeline.json`, and validate against `docs/demo-timeline.schema.json`.

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

P1 full proxy generation and verification completed 2026-09-02T00:30 AST.
All 8 clips transcoded to 1080p privacy proxies with `crop=2560:1360:0:0,scale=1920:1020,pad=1920:1080:0:30:black`.
Verified: 1920×1080 resolution, 59.94fps, audio present, durations matching, zero taskbar pixels, overlay ranges logged. Status: `P1_COMPLETE — PRIVACY_SAFE_PROXIES_VERIFIED`.
