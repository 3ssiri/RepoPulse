# Privacy Review — RepoPulse WebMCP Demo Clips

> **Reviewer:** Automated Agent (Antigravity)
> **Date:** 2026-09-02
> **Status:** P1_COMPLETE — PRIVACY_SAFE_PROXIES_VERIFIED
> **Clips reviewed:** 8 full proxy videos generated and verified
> **Approved Production Filter:** `crop=2560:1360:0:0,scale=1920:1020,pad=1920:1080:0:30:black`
> **Source resolution:** 2560×1440 (WQHD) → **Proxy output:** 1920×1080 (16:9), 59.94fps, H.264 + AAC stereo

---

## Screen Layout (Consistent Across All Clips)

```
┌──────────────────────────────────────────────────────────────────┐
│ [Top Black Pad: 30px (y = 0 .. 29)]                              │
├──────────────────────────────────────────────────────────────────┤
│ [Arc browser title bar + tab "RepoPulse – Re…"]                  │
│ [URL: repopulse-webmcp.vercel.app]                               │
├────────────────────────────┬─────────────────────────────────────┤
│                            │                                     │
│   LEFT PANEL (~50%)        │   RIGHT PANEL (~50%)                │
│   RepoPulse dashboard      │   ChatGPT "العمل" (Work) mode      │
│   - Scan a repository      │   - WebMCP tool instructions       │
│   - Report / Checks        │   - Arabic conversation text       │
│   - Compare refs           │   - Thinking/Details indicators    │
│                            │                                     │
├────────────────────────────┴─────────────────────────────────────┤
│ [Bottom Black Pad: 30px (y = 1050 .. 1079)]                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Complete Proxy Verification Results

All 8 complete proxies were generated under `video-demo/public/proxy/` and verified:

| Proxy File | Source Clip | Resolution | FPS | Duration | Audio | Taskbar Absent | Evidence Clear |
|---|---|---|---|---|---|---|---|
| `video-demo/public/proxy/clip-01.mp4` | `clip-01` | 1920×1080 | 59.94 | 97.30s | AAC stereo | ✅ 100% Absent | ✅ Crisp & Legible |
| `video-demo/public/proxy/clip-02.mp4` | `clip-02` | 1920×1080 | 59.94 | 58.84s | AAC stereo | ✅ 100% Absent | ✅ Crisp & Legible |
| `video-demo/public/proxy/clip-03.mp4` | `clip-03` | 1920×1080 | 59.94 | 37.52s | AAC stereo | ✅ 100% Absent | ✅ Crisp & Legible |
| `video-demo/public/proxy/clip-04.mp4` | `clip-04` | 1920×1080 | 59.94 | 32.85s | AAC stereo | ✅ 100% Absent | ✅ Crisp & Legible |
| `video-demo/public/proxy/clip-05.mp4` | `clip-05` | 1920×1080 | 59.94 | 21.80s | AAC stereo | ✅ 100% Absent | ✅ Crisp & Legible |
| `video-demo/public/proxy/clip-06.mp4` | `clip-06` | 1920×1080 | 59.94 | 27.34s | AAC stereo | ✅ 100% Absent | ✅ Crisp & Legible |
| `video-demo/public/proxy/clip-07.mp4` | `clip-07` | 1920×1080 | 59.94 | 45.38s | AAC stereo | ✅ 100% Absent | ✅ Crisp & Legible |
| `video-demo/public/proxy/clip-08.mp4` | `clip-08` | 1920×1080 | 59.94 | 31.31s | AAC stereo | ✅ 100% Absent | ✅ Crisp & Legible |

---

## Detailed Privacy & Visual Audit

### 1. Windows Taskbar (100% Clean)
- **Approved crop height (1360px):** Removes the entire `y = 1360 .. 1440` bottom portion (80px total cropped).
- **Verification:** The Windows taskbar (which starts at `y = 1378`) is completely absent in every frame across all 8 clips. No system tray, clock, open apps, or icon slivers are visible.
- **Letterbox padding:** Top 30px (`y=0..29`) and bottom 30px (`y=1050..1079`) are centered black letterbox bars.

### 2. Personal Identity & Conversations (100% Clean)
- **Account Identity:** No user email, username, avatar, or personal identifier appears.
- **Side Conversations:** The ChatGPT panel contains only the active WebMCP task conversation. No history sidebar or private chat threads are visible.
- **System Paths:** No machine-specific filesystem paths appear on screen.
- **Public Repositories Only:** Only `torvalds/linux` and `3ssiri/RepoPulse` are referenced.

### 3. Application UI & Evidence Readability
- The RepoPulse dashboard (health scores, pass/warn/fail badges, ref comparison diff) is sharp, high-contrast, and completely legible.
- The ChatGPT WebMCP tool invocations (`scan_repository`, `get_attention_items`, `get_check_details`, `compare_refs`) and live Arabic response explanations are completely readable.

---

## NVIDIA ShadowPlay Overlay & Dead Ranges

Fine-grained empirical scanning (0.1s step resolution) identified the exact presence of the NVIDIA top-right indicator across all 8 clips:

| Clip ID | Overlay Active Range | Safe Usable After | Recommended Dead Range (to CUT) |
|---|---|---|---|
| `clip-01` | 0.0s – 7.0s | **7.3s** | `[0.0s .. 7.3s]` |
| `clip-02` | 0.0s – 7.0s | **7.3s** | `[0.0s .. 7.3s]` |
| `clip-03` | 0.0s – 7.0s | **7.3s** | `[0.0s .. 7.3s]` |
| `clip-04` | 0.0s – 7.0s | **7.3s** | `[0.0s .. 7.3s]` |
| `clip-05` | 0.0s – 7.0s | **7.3s** | `[0.0s .. 7.3s]` |
| `clip-06` | 0.0s – 7.1s | **7.4s** | `[0.0s .. 7.4s]` |
| `clip-07` | 0.0s – 7.0s | **7.3s** | `[0.0s .. 7.3s]` |
| `clip-08` | 0.0s – 7.0s | **7.3s** | `[0.0s .. 7.3s]` |

**Rules for Timeline & Remotion Edit:**
- These are dead ranges for the final edit. Do not mask or reconstruct the overlay.
- Mark these intervals as dead ranges with action `CUT`.
- All actual WebMCP tool triggers and live dashboard updates occur well after the safe timestamps in every clip.

---

## Verdict

> **ALL EIGHT FULL PROXIES ARE VERIFIED 100% PRIVACY-SAFE AND READY FOR GEMINI ANALYSIS (P2).**
> **Gemini analysis must operate exclusively on the proxy files referenced by `analysis_proxy_path` in `video-demo/source-clips.json`.**
