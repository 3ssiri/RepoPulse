# RepoPulse WebMCP Demo — Production Tool Recommendations

Research date: 2026-09-01

This document recommends the fastest and safest way to produce the final OpenAI WebMCP Challenge demo video while preserving real evidence of native WebMCP execution.

The core rule is simple: **record the real ChatGPT + RepoPulse interaction first, then use AI to polish the recording. Do not synthesize or recreate the product interaction itself.**

## Recommended stack

### 1. Trupeer Pro — best single-tool option

**Recommendation: primary tool.**

Trupeer is the closest current product to an end-to-end workflow for this demo. It can record a screen/browser session or accept an uploaded recording, generate and polish a narration script, create an AI voiceover, add automatic zooms, captions and annotations, and let the creator edit the video by editing text. Its current product pages also advertise automatic synchronization to voiceover.

Why it fits this demo:

- Screen recording or upload of an existing real recording.
- AI-generated and AI-polished script.
- AI voiceover with many voices/accents.
- Automatic zooms on clicks/actions.
- Text-driven editing.
- Trim, split and skip controls.
- Sync to voiceover.
- MP4 export with captions on Pro.
- The script can be changed without rerecording the whole walkthrough.

Current pricing observed on 2026-09-01:

- Free/trial: limited and watermarked for normal export use.
- Pro: approximately $49/month, or approximately $40/month when billed yearly.
- Pro includes 2,000 AI credits; AI video generation is listed at 100 credits per minute, enough for substantially more than this ~2:10 demo.

Official sources:

- https://www.trupeer.ai/aiscreen-record
- https://www.trupeer.ai/video
- https://www.trupeer.ai/pricing

### Critical caveat for RepoPulse

The competition video must prove that the actual ChatGPT client is using the actual WebMCP Site Tools. Therefore Trupeer should **not** be allowed to invent replacement product screens or create a simulated walkthrough.

Preferred workflow:

1. Capture the real ChatGPT/WebMCP session.
2. Upload that real recording to Trupeer if direct capture is inconvenient.
3. Replace/polish only the narration, timing, captions, zooms and annotations.
4. Preserve the real tool calls and real RepoPulse dashboard output.

If Trupeer can capture the ChatGPT window directly through the available screen picker, use it. If not, use CANVID or another desktop recorder and upload the real recording to Trupeer.

---

### 2. CANVID — best Windows capture layer

**Recommendation: preferred capture fallback on Windows.**

CANVID records desktop/screen content on Windows and Mac and automatically adds zooms, captions and AI voice cleanup. It also allows trimming and adjustment of automatic zooms after recording.

Why it fits:

- Native Windows support.
- Good for recording the actual ChatGPT desktop/in-app browser.
- Automatic click zooms.
- Captions.
- AI microphone cleanup.
- Timeline editing after capture.

Current pricing observed on 2026-09-01:

- $75 one-time Lifetime license, or
- $96/year subscription with cloud AI features/storage.

Official source:

- https://www.canvid.com/

Limitation: CANVID is strongest as a recorder/polisher; it is not the best integrated synthetic narration engine. Pair it with Trupeer, ElevenLabs or Descript when AI narration is required.

---

### 3. ElevenLabs — best voice-quality fallback

**Recommendation: use only if Trupeer's built-in voice does not sound good enough.**

ElevenLabs remains a strong specialized option for synthetic narration and timing-preserving dubbing. Its dubbing workflow explicitly supports synchronizing generated speech to the original video timing.

Best use here:

- Generate a natural English narration from the approved script.
- Use dubbing/timing tools if a scratch narration was recorded during capture.
- Export high-quality audio and bring it into the final editor.

Official sources:

- https://elevenlabs.io/docs/overview/capabilities/dubbing
- https://elevenlabs.io/docs/eleven-creative/services/productions/dubbing

Limitation: ElevenLabs does not edit the screen recording itself, so it should be treated as an audio layer, not the main production tool.

---

### 4. Descript — best precision-editing fallback

**Recommendation: final polish only if precise timing becomes difficult in Trupeer.**

Descript provides screen recording, transcript-based video editing, captions, Studio Sound and AI Speech/Overdub. It is particularly useful when the narration needs exact word-level edits and the video needs to be cut around those edits.

Why it can help:

- Edit video by editing transcript text.
- AI Speech / Overdub.
- Automatic captions.
- Studio Sound.
- Filler-word removal.
- Fine control over cuts and timing.

Official sources:

- https://www.descript.com/video-editing
- https://www.descript.com/price

Caution: recent community reports in 2026 describe reliability and AI-credit-consumption frustrations for fully automated end-to-end editing. For this reason, it is not the first choice for this challenge video; use it for targeted fixes rather than asking it to create the whole demo automatically.

---

### 5. Guidde — strong automated tutorial alternative

**Recommendation: backup if Trupeer is unavailable.**

Guidde can capture workflows using a browser extension or desktop app, automatically generate a structured script, add AI-generated voiceover, captions and highlights, and export finished videos on paid tiers.

Strengths:

- Fast workflow capture.
- Automated storyboarding/script generation.
- AI voiceover.
- Captions and highlights.
- Browser and desktop capture options.

Official sources:

- https://www.guidde.com/
- https://help.guidde.com/en/articles/6360996-install-the-guidde-browser-extension
- https://www.guidde.com/pricing

Limitation for this competition: Guidde is optimized for step-by-step documentation and may make the result feel more like a tutorial than a live product demonstration. Preserve continuous real WebMCP evidence if using it.

---

### 6. HeyGen — useful for narration/presenter, not for the core evidence

**Recommendation: optional only.**

HeyGen can build product-demo videos from scripts, add AI voiceover, captions and real product screens, and supports video generation and voice control. It can also be accessed through the connected HeyGen tools available in ChatGPT.

Official product-demo source:

- https://www.heygen.com/tool/product-demo-video-generator

Good uses:

- Generate an alternate English narration.
- Add captions or a narrator if absolutely desired.
- Produce supporting promotional material after submission.

Do **not** use an AI avatar or reconstructed/synthetic product screens as the main competition demo. The strongest evidence is the real ChatGPT WebMCP tool execution visible beside the real RepoPulse dashboard.

---

## Tool ranking for this exact demo

| Rank | Tool | Best role | Automation | Risk to real WebMCP evidence |
|---|---|---|---|---|
| 1 | Trupeer Pro | End-to-end polish + AI voice + sync | Very high | Low if real recording is preserved |
| 2 | CANVID | Real Windows screen capture | High | Very low |
| 3 | ElevenLabs | Highest-quality voice fallback | High for audio | None if used only for audio |
| 4 | Descript | Precise transcript/timing repair | High | Low |
| 5 | Guidde | Automated tutorial generation | Very high | Medium; can over-structure the live flow |
| 6 | HeyGen | Narration/presenter/supporting demo | Very high | Medium/high if it replaces real screens |

## Final recommendation

### Fastest single-tool path

**Trupeer Pro**.

Record the real interaction, paste the approved narration into the script editor, choose an English AI voice, use Sync to Voiceover, keep Auto Zoom enabled, remove waits, add the approved on-screen labels, and export 1080p MP4.

### Safest competition path

**CANVID capture → Trupeer Pro finish**.

This separates the part that must be unquestionably authentic — native WebMCP execution — from the part AI is best at automating — narration, timing, zooms, captions and cleanup.

### Highest voice-quality path

**CANVID capture → ElevenLabs narration → Trupeer or Descript final sync**.

Use this only if the built-in Trupeer voice is noticeably weaker. The integrated Trupeer voice workflow is simpler and should be tried first.

## Exact production workflow

1. Set the screen to 16:9 and record at 1080p or higher.
2. Open ChatGPT and RepoPulse before recording; no login/setup footage.
3. Record the real flow below. A single clean continuous recording is acceptable; idle/loading sections will be removed later.
4. Capture these real actions:
   - `scan_repository` on `torvalds/linux`.
   - `get_attention_items` without another scan.
   - `get_check_details` for `github_actions`.
   - human manually scans `3ssiri/RepoPulse` in the visible UI.
   - `compare_refs` for `v0.3.5` vs `v0.3.6` without passing the repository again.
5. Upload the raw recording to Trupeer if it was captured elsewhere.
6. Replace the generated narration with the exact approved script below.
7. Select a natural English AI voice. Prefer neutral US/International English, moderate pace, no exaggerated promotional delivery.
8. Use voiceover synchronization so visual actions align with the corresponding narration.
9. Keep automatic zooms only when they help identify the WebMCP call/result or RepoPulse dashboard change.
10. Remove all network waiting and dead time with cuts; do not alter the actual result shown.
11. Add only the specified short on-screen labels.
12. Do not add an intro card.
13. Do not add an avatar over the product.
14. Avoid background music unless it is very quiet and clearly licensed; silence under narration is safer.
15. Export 1080p MP4, 16:9.
16. Verify final duration is comfortably below 3:00; target about 2:10.
17. Watch the final export once with audio and once muted to make sure the WebMCP evidence is still understandable visually.
18. Upload publicly to YouTube.

# Approved demo script

Target length: approximately 2:10.

## 0:00–0:15 — Start with WebMCP working

**Screen**

RepoPulse and ChatGPT are already visible side by side.

Immediately execute `scan_repository` on:

`https://github.com/torvalds/linux`

Cut the loading time and go directly to the completed result and the visible 69/100 dashboard.

**Narration**

> I'm scanning the Linux repository from ChatGPT using RepoPulse's WebMCP `scan_repository` tool.
>
> The agent receives structured repository-health data, and the same action updates the dashboard I'm looking at.

**On-screen text**

`WebMCP action → same visible dashboard`

## 0:15–0:35 — Read the current state without another scan

**Screen**

Execute `get_attention_items`.

Show the result:

- FAIL — `github_actions`
- WARN — `gitignore`
- WARN — `tests`
- WARN — `dependencies`
- WARN — `security`

Keep part of the RepoPulse dashboard visible.

**Narration**

> Now I ask for only the checks that need attention.
>
> This tool reads the report already loaded in the page. It does not scan GitHub again.
>
> Here, the failing GitHub Actions check comes first, followed by the warnings.

**On-screen text**

`Current state · no repository rescan`

## 0:35–0:50 — Drill into a real problem

**Screen**

Execute `get_check_details` for `github_actions`.

Show the structured status, message, and recommendations.

**Narration**

> I can drill directly into one check.
>
> There's no DOM scraping and no need to rediscover which repository or report we're discussing.

## 0:50–1:10 — The human changes the shared state

**Screen**

Move to the normal RepoPulse interface yourself.

Paste:

`https://github.com/3ssiri/RepoPulse`

Click Scan.

Cut the wait and show the completed 100/100 dashboard.

**Narration**

> The state works in the other direction too.
>
> I switch the repository myself in the normal interface.
>
> The agent and I are still working in the same application state.

**On-screen text**

`Human action → shared agent state`

## 1:10–1:30 — The agent continues from the human-selected state

**Screen**

Return to ChatGPT.

Execute `compare_refs` with:

- `baseline_ref: v0.3.5`
- `target_ref: v0.3.6`

Do not provide the repository URL again.

Show both the structured WebMCP result and the visible dashboard comparison:

`100/100 → 100/100`

`delta 0`

**Narration**

> Without selecting the repository again, the agent compares version 0.3.5 with 0.3.6.
>
> `compare_refs` uses the repository I selected and renders the comparison back into the same dashboard.

## 1:30–1:55 — Explain what is actually implemented

**Screen**

Keep the live product visible.

Use a small overlay showing:

- `scan_repository`
- `get_attention_items`
- `get_check_details`
- `compare_refs`

Do not switch to a terminal or spend time showing source code.

**Narration**

> RepoPulse exposes four read-only WebMCP tools: scan a repository, read the current attention items, inspect one check, and compare refs.
>
> They call the same frontend functions as the human controls, so there is no separate agent-only state.
>
> The existing RepoPulse analysis engine stays unchanged.

## 1:55–2:10 — Close on the WebMCP value

**Screen**

End on the completed RepoPulse comparison with the WebMCP-enabled page visible.

**Narration**

> RepoPulse turns repository health from a page an agent has to operate into a shared workspace where the developer and the agent can hand the task back and forth.
>
> That shared state is what WebMCP adds to the product.

**On-screen text**

`One product · one state · human + agent`

## Final choice

Use this order unless a tool fails during production:

1. **Try Trupeer Pro first** with a real recorded WebMCP session.
2. If direct recording is awkward, **capture with CANVID and upload to Trupeer**.
3. If the voice is not strong enough, generate narration with **ElevenLabs** and finish in Trupeer/Descript.
4. Use **Descript** only when manual timing/transcript repair is needed.
5. Use **Guidde** only as a backup automated tutorial workflow.
6. Use **HeyGen** only for narration/supporting assets; do not replace the live WebMCP evidence with generated product screens or an avatar-led demo.
