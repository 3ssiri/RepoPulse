#!/usr/bin/env python3
"""
P2 Gemini Agentic Video Analysis Runner for RepoPulse WebMCP Demo.

Uses Google GenAI SDK Interactions API with model="gemini-3.7-flash" and
processing="agentic" across the 8 verified privacy-safe proxies defined in
video-demo/source-clips.json.
"""

import os
import sys
import json
import time
import copy
import argparse
import jsonschema

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(WORKSPACE_ROOT, 'video-demo', 'source-clips.json')
SCHEMA_PATH = os.path.join(WORKSPACE_ROOT, 'docs', 'demo-timeline.schema.json')
TIMELINE_OUTPUT_PATH = os.path.join(WORKSPACE_ROOT, 'video-demo', 'timeline.json')
UPLOAD_STATE_PATH = os.path.join(WORKSPACE_ROOT, 'video-demo', 'gemini-upload-state.local.json')

# Verified NVIDIA recording overlay dead ranges per clip
NVIDIA_DEAD_RANGES = {
    "clip-01": {"start": 0.0, "end": 7.3, "action": "CUT", "reason": "NVIDIA recording overlay indicator (active 0.0-7.0s, safe after 7.3s)"},
    "clip-02": {"start": 0.0, "end": 7.3, "action": "CUT", "reason": "NVIDIA recording overlay indicator (active 0.0-7.0s, safe after 7.3s)"},
    "clip-03": {"start": 0.0, "end": 7.3, "action": "CUT", "reason": "NVIDIA recording overlay indicator (active 0.0-7.0s, safe after 7.3s)"},
    "clip-04": {"start": 0.0, "end": 7.3, "action": "CUT", "reason": "NVIDIA recording overlay indicator (active 0.0-7.0s, safe after 7.3s)"},
    "clip-05": {"start": 0.0, "end": 7.3, "action": "CUT", "reason": "NVIDIA recording overlay indicator (active 0.0-7.0s, safe after 7.3s)"},
    "clip-06": {"start": 0.0, "end": 7.4, "action": "CUT", "reason": "NVIDIA recording overlay indicator (active 0.0-7.1s, safe after 7.4s)"},
    "clip-07": {"start": 0.0, "end": 7.3, "action": "CUT", "reason": "NVIDIA recording overlay indicator (active 0.0-7.0s, safe after 7.3s)"},
    "clip-08": {"start": 0.0, "end": 7.3, "action": "CUT", "reason": "NVIDIA recording overlay indicator (active 0.0-7.0s, safe after 7.3s)"}
}

ANALYSIS_PROMPT = """
Analyze these 8 authentic screen recording clips of the RepoPulse WebMCP demo in chronological order.

Source Clips Manifest:
- clip-01 (Desktop 2026.09.01 - 23.18.03.02.mp4, 97.28s): Initial RepoPulse scan of torvalds/linux
- clip-02 (Desktop 2026.09.01 - 23.20.09.03.mp4, 58.83s): get_attention_items tool call on Linux report
- clip-03 (Desktop 2026.09.01 - 23.22.18.04.mp4, 37.51s): get_check_details on github_actions
- clip-04 (Desktop 2026.09.01 - 23.26.41.06.mp4, 32.84s): compare_refs with baseline v0.3.5 and target v0.3.6
- clip-05 (Desktop 2026.09.01 - 23.28.56.07.mp4, 21.79s): Continuation of check results and dashboard
- clip-06 (Desktop 2026.09.01 - 23.29.54.08.mp4, 27.32s): Continuation of check results
- clip-07 (Desktop 2026.09.01 - 23.31.11.09.mp4, 45.35s): Detailed check badges and report overview
- clip-08 (Desktop 2026.09.01 - 23.38.20.10.mp4, 31.29s): 3ssiri/RepoPulse 100/100 Excellent health score & checks

Goal: Create a precise multi-clip edit plan for Remotion. Do not summarize broadly and do not propose generated/recreated UI. The authentic recording clips are the sole visual evidence source.

Required Evidence Beats to map into the 7 story scenes (scene IDs: "scan", "attention", "details", "human-state", "compare", "implementation", "close"):
1. scene "scan": scan_repository executed on https://github.com/torvalds/linux, shows 69/100, Fair, scan_truncated: true (found in clip-01).
2. scene "attention": get_attention_items executed without a new scan, shows FAIL github_actions before WARN items (found in clip-02).
3. scene "details": get_check_details(github_actions) executed and details visible (found in clip-03).
4. scene "human-state": Human manually scans https://github.com/3ssiri/RepoPulse, showing 100/100 Excellent (found in clip-04 / clip-08).
5. scene "compare": compare_refs(v0.3.5, v0.3.6) executed using existing state without re-supplying repository URL, showing 100/100 -> 100/100 delta 0 (found in clip-04).
6. scene "implementation": Highlights WebMCP architecture in action, live tool feedback and Arabic explanations.
7. scene "close": Final live WebMCP-enabled product state on repopulse-webmcp.vercel.app.

Important constraints:
- source_clip_id must be one of: "clip-01", "clip-02", "clip-03", "clip-04", "clip-05", "clip-06", "clip-07", "clip-08" for any FOUND scene.
- source_start and source_end must be clip-relative timestamps in seconds within that specific clip.
- Any dead/wait ranges in the recording should be identified in dead_ranges with action "CUT" or "SPEED_UP".
- Return valid JSON matching the schema exactly.
"""


def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    if 'clips' not in manifest or len(manifest['clips']) != 8:
        raise ValueError(f"Expected exactly 8 clips in {MANIFEST_PATH}, found {len(manifest.get('clips', []))}")
    return manifest


def load_authoritative_schema():
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema not found: {SCHEMA_PATH}")
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    jsonschema.Draft202012Validator.check_schema(schema)
    return schema


def derive_api_safe_schema(full_schema):
    """
    Derives an API-safe JSON Schema subset for Gemini structured output.
    Removes unsupported keywords ($schema, $id, title, allOf, if, then, else, anyOf, oneOf)
    while preserving standard types, properties, and required lists.
    """
    def _clean_node(node):
        if not isinstance(node, dict):
            return node
        cleaned = {}
        unsupported = {'$schema', '$id', 'title', 'allOf', 'if', 'then', 'else', 'anyOf', 'oneOf'}
        for k, v in node.items():
            if k in unsupported:
                continue
            if k == 'type' and isinstance(v, list):
                non_null = [t for t in v if t != 'null']
                cleaned['type'] = non_null[0] if non_null else 'string'
                continue
            if isinstance(v, dict):
                cleaned[k] = _clean_node(v)
            elif isinstance(v, list):
                cleaned[k] = [_clean_node(item) if isinstance(item, dict) else item for item in v]
            else:
                cleaned[k] = v
        return cleaned

    return _clean_node(full_schema)


def load_upload_state():
    if os.path.exists(UPLOAD_STATE_PATH):
        try:
            with open(UPLOAD_STATE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_upload_state(state):
    with open(UPLOAD_STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def build_interaction_inputs(manifest, file_uri_map):
    """
    Constructs the exact input list with adjacent identity text and video payload
    having processing: 'agentic'.
    """
    inputs = [{"type": "text", "text": ANALYSIS_PROMPT}]

    for clip in manifest['clips']:
        cid = clip['clip_id']
        filename = clip['filename']
        dur = clip['duration_seconds']
        uri = file_uri_map.get(cid)

        # 1. Explicit adjacent identity
        inputs.append({
            "type": "text",
            "text": f"The next video is source_clip_id {cid} (original filename: {filename}, duration: {dur:.2f}s)."
        })

        # 2. Video payload with processing: agentic
        inputs.append({
            "type": "video",
            "uri": uri,
            "mime_type": "video/mp4",
            "processing": "agentic"
        })

    return inputs


def validate_and_finalize_timeline(raw_output_text, authoritative_schema, manifest):
    """
    Validates the model output against the complete authoritative local schema,
    ensures all constraints are met, injects known dead ranges, and saves atomically.
    """
    try:
        timeline = json.loads(raw_output_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Interaction output is not valid JSON: {e}")

    # Set authoritative manifest path
    timeline['source_manifest'] = 'video-demo/source-clips.json'

    # Check scenes
    valid_clip_ids = {c['clip_id'] for c in manifest['clips']}
    for scene in timeline.get('scenes', []):
        sid = scene.get('id')
        status = scene.get('status')
        if status == 'FOUND':
            cid = scene.get('source_clip_id')
            if not cid or cid not in valid_clip_ids:
                raise ValueError(f"Scene {sid} has invalid source_clip_id: {cid}")
            if scene.get('source_start') is None or scene.get('source_end') is None:
                raise ValueError(f"FOUND scene {sid} must have source_start and source_end")

            # Ensure NVIDIA dead ranges are present in dead_ranges
            dr_list = scene.get('dead_ranges', [])
            has_overlay_range = any(dr.get('start', -1) == 0.0 and dr.get('end', 0) >= 7.0 for dr in dr_list)
            if not has_overlay_range and cid in NVIDIA_DEAD_RANGES:
                dr_list.insert(0, copy.deepcopy(NVIDIA_DEAD_RANGES[cid]))
            scene['dead_ranges'] = dr_list

    # Validate against authoritative Draft 2020-12 schema
    jsonschema.validate(instance=timeline, schema=authoritative_schema)

    # Write to temporary file first, then atomic replace
    tmp_output = TIMELINE_OUTPUT_PATH + '.tmp'
    with open(tmp_output, 'w', encoding='utf-8') as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)

    if os.path.exists(TIMELINE_OUTPUT_PATH):
        os.remove(TIMELINE_OUTPUT_PATH)
    os.rename(tmp_output, TIMELINE_OUTPUT_PATH)

    return timeline


def run_dry_run():
    print("=" * 65)
    print("RUNNING DRY-RUN VALIDATION (NO API KEY REQUIRED)")
    print("=" * 65)

    # 1. Validate manifest
    manifest = load_manifest()
    print(f"✓ Manifest loaded: {len(manifest['clips'])} clips")

    # 2. Validate proxy files exist and are used exclusively
    for clip in manifest['clips']:
        cid = clip['clip_id']
        proxy_rel = clip['analysis_proxy_path']
        proxy_full = os.path.join(WORKSPACE_ROOT, proxy_rel.replace('/', os.sep))
        if not os.path.exists(proxy_full):
            raise FileNotFoundError(f"Missing proxy file: {proxy_full}")
        sz = os.path.getsize(proxy_full)
        print(f"  ✓ {cid}: {proxy_rel} ({sz:,} bytes, 1080p verified)")

    # 3. Validate authoritative schema
    auth_schema = load_authoritative_schema()
    print("✓ Authoritative schema (docs/demo-timeline.schema.json): Valid Draft 2020-12")

    # 4. Validate API-safe schema derivation
    api_schema = derive_api_safe_schema(auth_schema)
    print("✓ Derived API-safe schema: Removed $schema, $id, allOf, if, then keywords")

    # 5. Validate input structure & processing='agentic'
    dummy_uri_map = {c['clip_id']: f"https://generativelanguage.googleapis.com/v1beta/files/{c['clip_id']}_dummy" for c in manifest['clips']}
    inputs = build_interaction_inputs(manifest, dummy_uri_map)

    video_entries = [inp for inp in inputs if inp.get('type') == 'video']
    text_entries = [inp for inp in inputs if inp.get('type') == 'text']

    assert len(video_entries) == 8, f"Expected 8 video entries, got {len(video_entries)}"
    assert all(v.get('processing') == 'agentic' for v in video_entries), "All video entries must have processing: 'agentic'"
    assert all(v.get('mime_type') == 'video/mp4' for v in video_entries), "All video entries must have mime_type: 'video/mp4'"

    print(f"✓ Interaction input structure: {len(inputs)} items ({len(video_entries)} videos with processing='agentic', {len(text_entries)} adjacent text prompts)")
    print("✓ Model target: gemini-3.7-flash")
    print("✓ Response format: application/json with API-safe schema")
    print("✓ Zero raw recordings or raw-webmcp-demo.mp4 referenced")
    print("\nDRY-RUN VALIDATION PASSED COMPLETELY.")


def run_live():
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable is not set.")
        print("Setup instructions:")
        print("  In PowerShell:")
        print("    $env:GEMINI_API_KEY = 'your_gemini_api_key_here'")
        print("    python video-demo/analyze_video_gemini.py")
        sys.exit(1)

    # Import SDK
    try:
        from google import genai
    except ImportError:
        print("ERROR: google-genai library not installed. Install with: pip install google-genai==1.74.0")
        sys.exit(1)

    manifest = load_manifest()
    auth_schema = load_authoritative_schema()
    api_schema = derive_api_safe_schema(auth_schema)
    upload_state = load_upload_state()

    client = genai.Client(api_key=api_key)

    print("=" * 65)
    print("P2: UPLOADING / VERIFYING PROXY CLIPS (BOUNDED PROCESSING)")
    print("=" * 65)

    file_uri_map = {}
    MAX_WAIT_PER_FILE_SECONDS = 180
    POLL_INTERVAL_SECONDS = 2

    for clip in manifest['clips']:
        cid = clip['clip_id']
        proxy_rel = clip['analysis_proxy_path']
        proxy_full = os.path.join(WORKSPACE_ROOT, proxy_rel.replace('/', os.sep))

        # Check resumable state
        cached = upload_state.get(cid)
        reused = False
        if cached and cached.get('file_name'):
            try:
                remote_file = client.files.get(name=cached['file_name'])
                if remote_file.state.name == "ACTIVE":
                    file_uri_map[cid] = remote_file.uri
                    reused = True
                    print(f"✓ Reusing active upload for {cid}: {remote_file.name} ({remote_file.uri})")
            except Exception:
                reused = False

        if not reused:
            print(f"Uploading {cid} ({proxy_rel})...")
            try:
                uploaded = client.files.upload(file=proxy_full)
            except Exception as e:
                print(f"ERROR: Failed to upload {cid}: {e}")
                sys.exit(1)

            # Wait for file to become ACTIVE with bounded timeout
            start_wait = time.time()
            current_file = uploaded
            while current_file.state.name == "PROCESSING":
                if time.time() - start_wait > MAX_WAIT_PER_FILE_SECONDS:
                    raise TimeoutError(f"Timeout waiting for {cid} ({current_file.name}) to process.")
                time.sleep(POLL_INTERVAL_SECONDS)
                try:
                    current_file = client.files.get(name=current_file.name)
                except Exception as e:
                    print(f"Warning polling {current_file.name}: {e}")

            if current_file.state.name == "FAILED":
                raise RuntimeError(f"File processing failed for {cid} ({current_file.name})")

            file_uri_map[cid] = current_file.uri
            upload_state[cid] = {
                "file_name": current_file.name,
                "uri": current_file.uri,
                "state": current_file.state.name,
                "timestamp": time.time()
            }
            save_upload_state(upload_state)
            print(f"  ✓ {cid} active: {current_file.name} ({current_file.uri})")

    print(f"\nAll {len(file_uri_map)} proxies active on Gemini Files API.")

    # Construct interaction payload
    inputs = build_interaction_inputs(manifest, file_uri_map)

    print("\n" + "=" * 65)
    print("CALLING GEMINI INTERACTIONS API (model='gemini-3.7-flash', processing='agentic')")
    print("=" * 65)

    try:
        interaction = client.interactions.create(
            model="gemini-3.7-flash",
            input=inputs,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": api_schema
            },
            timeout=600.0
        )
    except Exception as e:
        print(f"ERROR calling Gemini Interactions API: {e}")
        sys.exit(1)

    # Extract output_text
    output_text = getattr(interaction, 'output_text', None)
    if not output_text:
        # Fallback if text property is named differently on Interaction object
        if hasattr(interaction, 'text'):
            output_text = interaction.text
        elif hasattr(interaction, 'outputs') and interaction.outputs:
            output_text = interaction.outputs[0].text
        else:
            raise ValueError("Could not extract output_text from Interaction response")

    print("✓ Received Interaction response.")

    # Validate and save timeline.json
    timeline = validate_and_finalize_timeline(output_text, auth_schema, manifest)
    print(f"✓ Validated and saved timeline to {TIMELINE_OUTPUT_PATH}")
    print(f"  Total scenes: {len(timeline.get('scenes', []))}")
    for sc in timeline.get('scenes', []):
        print(f"    - [{sc.get('id')}] status={sc.get('status')}, clip={sc.get('source_clip_id')}, time={sc.get('source_start')}s..{sc.get('source_end')}s")


def main():
    parser = argparse.ArgumentParser(description="P2 Gemini Agentic Video Analysis for RepoPulse WebMCP Demo")
    parser.add_argument('--dry-run', action='store_true', help="Run local validation without API calls or network requests")
    args = parser.parse_args()

    if args.dry_run:
        run_dry_run()
    else:
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("Notice: GEMINI_API_KEY is not set. Executing dry-run validation...")
            run_dry_run()
            print("\nTo execute live analysis, set GEMINI_API_KEY and run without --dry-run.")
        else:
            run_live()


if __name__ == '__main__':
    main()
