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
import hashlib
import argparse
import jsonschema

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(WORKSPACE_ROOT, 'video-demo', 'source-clips.json')
SCHEMA_PATH = os.path.join(WORKSPACE_ROOT, 'docs', 'demo-timeline.schema.json')
TIMELINE_OUTPUT_PATH = os.path.join(WORKSPACE_ROOT, 'video-demo', 'timeline.json')
UPLOAD_STATE_PATH = os.path.join(WORKSPACE_ROOT, 'video-demo', 'gemini-upload-state.local.json')

REQUIRED_SCENE_IDS = [
    "scan",
    "attention",
    "details",
    "human-state",
    "compare",
    "implementation",
    "close"
]

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
- If any required evidence beat is not visible, mark status="NEEDS_RERECORD" with null source_clip_id, source_start, and source_end.
- Return valid JSON matching the schema exactly.
"""


def get_file_sha256(filepath):
    """Computes SHA256 hash of a local file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest():
    """Loads and validates source-clips.json."""
    if not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    if 'clips' not in manifest or len(manifest['clips']) != 8:
        raise ValueError(f"Expected exactly 8 clips in {MANIFEST_PATH}, found {len(manifest.get('clips', []))}")
    return manifest


def validate_and_resolve_proxy_path(clip, workspace_root):
    """
    Hardened validation for proxy files:
    - Must be within video-demo/public/proxy/
    - Filename must match clip-XX.mp4
    - Rejects path traversal, raw directories, and raw-webmcp-demo.mp4
    """
    cid = clip['clip_id']
    proxy_rel = clip.get('analysis_proxy_path', '')

    if not proxy_rel:
        raise ValueError(f"Clip {cid} is missing analysis_proxy_path")

    # Reject forbidden substrings
    forbidden = ['raw/', 'raw\\', 'raw-webmcp-demo']
    if any(fb in proxy_rel.lower() for fb in forbidden):
        raise ValueError(f"Forbidden raw or unapproved path in analysis_proxy_path for {cid}: {proxy_rel}")

    # Expected filename check
    expected_filename = f"{cid}.mp4"
    if os.path.basename(proxy_rel) != expected_filename:
        raise ValueError(f"Proxy filename mismatch for {cid}: expected {expected_filename}, got {os.path.basename(proxy_rel)}")

    # Resolve and boundary check inside video-demo/public/proxy
    proxy_full = os.path.normpath(os.path.abspath(os.path.join(workspace_root, proxy_rel.replace('/', os.sep))))
    allowed_dir = os.path.normpath(os.path.abspath(os.path.join(workspace_root, 'video-demo', 'public', 'proxy')))

    try:
        common = os.path.commonpath([proxy_full, allowed_dir])
    except ValueError:
        raise ValueError(f"Path traversal detected across drives: {proxy_rel}")

    if common != allowed_dir:
        raise ValueError(f"Path traversal detected: {proxy_rel} is outside {allowed_dir}")

    if not os.path.exists(proxy_full):
        raise FileNotFoundError(f"Proxy file not found: {proxy_full}")

    return proxy_full


def load_authoritative_schema():
    """Loads authoritative Draft 2020-12 schema from docs/demo-timeline.schema.json."""
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
    while strictly preserving nullable type arrays (e.g. ['string', 'null'], ['number', 'null']).
    """
    def _clean_node(node):
        if not isinstance(node, dict):
            return node
        cleaned = {}
        unsupported = {'$schema', '$id', 'title', 'allOf', 'if', 'then', 'else', 'anyOf', 'oneOf'}
        for k, v in node.items():
            if k in unsupported:
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
    """Loads resumable upload state from local untracked file."""
    if os.path.exists(UPLOAD_STATE_PATH):
        try:
            with open(UPLOAD_STATE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_upload_state(state):
    """Atomically saves resumable upload state."""
    tmp_state = UPLOAD_STATE_PATH + '.tmp'
    with open(tmp_state, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    os.replace(tmp_state, UPLOAD_STATE_PATH)


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


def validate_semantic_timeline(timeline, manifest):
    """
    Validates semantic requirements on the timeline:
    - Exactly the 7 scene IDs, each exactly once
    - For FOUND: 0 <= source_start < source_end <= clip duration
    - action_time, result_visible_time, hold_start, hold_end inside clip when non-null
    - dead_ranges: 0 <= start < end <= clip duration
    - NEEDS_RERECORD must use null source_clip_id/start/end
    """
    clip_duration_map = {c['clip_id']: c['duration_seconds'] for c in manifest['clips']}
    scenes = timeline.get('scenes', [])

    if not isinstance(scenes, list):
        raise ValueError("Timeline 'scenes' property must be a list.")

    scene_ids = [s.get('id') for s in scenes]
    if len(scene_ids) != len(REQUIRED_SCENE_IDS) or set(scene_ids) != set(REQUIRED_SCENE_IDS):
        raise ValueError(f"Timeline must contain exactly the 7 required scene IDs each once {REQUIRED_SCENE_IDS}, got: {scene_ids}")

    for scene in scenes:
        sid = scene.get('id')
        status = scene.get('status')

        if status == 'NEEDS_RERECORD':
            if scene.get('source_clip_id') is not None:
                raise ValueError(f"Scene {sid} with NEEDS_RERECORD must have source_clip_id=null, got: {scene.get('source_clip_id')}")
            if scene.get('source_start') is not None:
                raise ValueError(f"Scene {sid} with NEEDS_RERECORD must have source_start=null, got: {scene.get('source_start')}")
            if scene.get('source_end') is not None:
                raise ValueError(f"Scene {sid} with NEEDS_RERECORD must have source_end=null, got: {scene.get('source_end')}")
        elif status == 'FOUND':
            cid = scene.get('source_clip_id')
            if cid not in clip_duration_map:
                raise ValueError(f"Scene {sid} has invalid source_clip_id: {cid}")

            dur = clip_duration_map[cid]
            start = scene.get('source_start')
            end = scene.get('source_end')

            if start is None or end is None:
                raise ValueError(f"FOUND scene {sid} must have non-null source_start and source_end")
            if not (0.0 <= start < end <= (dur + 0.5)):
                raise ValueError(f"Scene {sid} invalid time range: 0 <= start ({start}) < end ({end}) <= clip duration ({dur:.2f})")

            # Validate optional timing fields
            for tf in ['action_time', 'result_visible_time', 'hold_start', 'hold_end']:
                tv = scene.get(tf)
                if tv is not None:
                    if not (0.0 <= tv <= (dur + 0.5)):
                        raise ValueError(f"Scene {sid} timing field {tf} ({tv}) is outside clip duration ({dur:.2f})")

            # Validate dead ranges
            for dr in scene.get('dead_ranges', []):
                dr_start = dr.get('start')
                dr_end = dr.get('end')
                if dr_start is None or dr_end is None:
                    raise ValueError(f"Scene {sid} dead range missing start or end: {dr}")
                if not (0.0 <= dr_start < dr_end <= (dur + 0.5)):
                    raise ValueError(f"Scene {sid} invalid dead range: 0 <= {dr_start} < {dr_end} <= clip duration ({dur:.2f})")
        else:
            raise ValueError(f"Scene {sid} has unknown status: {status}")


def validate_and_finalize_timeline(raw_output_text, authoritative_schema, manifest, destination_path=TIMELINE_OUTPUT_PATH):
    """
    Validates model output against schema and semantic rules, injects known dead ranges,
    and writes atomically via temporary file and os.replace without deleting prior files.
    """
    try:
        timeline = json.loads(raw_output_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Interaction output is not valid JSON: {e}")

    # Ensure source_manifest is set
    timeline['source_manifest'] = 'video-demo/source-clips.json'

    # Inject NVIDIA dead ranges into FOUND scenes if missing
    for scene in timeline.get('scenes', []):
        if scene.get('status') == 'FOUND':
            cid = scene.get('source_clip_id')
            dr_list = scene.get('dead_ranges', [])
            has_overlay = any(dr.get('start', -1) == 0.0 and dr.get('end', 0) >= 7.0 for dr in dr_list)
            if not has_overlay and cid in NVIDIA_DEAD_RANGES:
                dr_list.insert(0, copy.deepcopy(NVIDIA_DEAD_RANGES[cid]))
            scene['dead_ranges'] = dr_list

    # 1. Authoritative JSON Schema validation (Draft 2020-12)
    jsonschema.validate(instance=timeline, schema=authoritative_schema)

    # 2. Semantic validation
    validate_semantic_timeline(timeline, manifest)

    # 3. Atomic write via os.replace
    tmp_output = destination_path + '.tmp'
    with open(tmp_output, 'w', encoding='utf-8') as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)
    os.replace(tmp_output, destination_path)

    return timeline


def run_dry_run():
    print("=" * 68)
    print("RUNNING DRY-RUN VALIDATION (NO API KEY / ZERO NETWORK CALLS)")
    print("=" * 68)

    # 1. Validate manifest
    manifest = load_manifest()
    print(f"✓ Manifest loaded: {len(manifest['clips'])} clips from {MANIFEST_PATH}")

    # 2. Validate hardened proxy selection
    for clip in manifest['clips']:
        cid = clip['clip_id']
        proxy_full = validate_and_resolve_proxy_path(clip, WORKSPACE_ROOT)
        proxy_sha = get_file_sha256(proxy_full)
        sz = os.path.getsize(proxy_full)
        print(f"  ✓ {cid}: {clip['analysis_proxy_path']} ({sz:,} bytes | SHA256: {proxy_sha[:16]}...)")

    # 3. Validate authoritative schema
    auth_schema = load_authoritative_schema()
    print("✓ Authoritative schema (docs/demo-timeline.schema.json): Valid Draft 2020-12")

    # 4. Validate API-safe schema derivation and assert nullable types
    api_schema = derive_api_safe_schema(auth_schema)
    api_props = api_schema['properties']['scenes']['items']['properties']

    cid_type = api_props['source_clip_id']['type']
    start_type = api_props['source_start']['type']
    end_type = api_props['source_end']['type']

    print(f"✓ API-safe schema derived:")
    print(f"  - source_clip_id type: {cid_type}")
    print(f"  - source_start type:   {start_type}")
    print(f"  - source_end type:     {end_type}")

    assert isinstance(cid_type, list) and "null" in cid_type, "source_clip_id must include 'null' type"
    assert isinstance(start_type, list) and "null" in start_type, "source_start must include 'null' type"
    assert isinstance(end_type, list) and "null" in end_type, "source_end must include 'null' type"
    print("✓ Nullable type preservation assertions PASSED.")

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
    print("✓ Output target: video-demo/timeline.json (via atomic os.replace)")
    print("✓ Zero raw recordings or raw-webmcp-demo.mp4 referenced")

    # 6. In-memory synthetic validation test
    print("\n" + "-" * 68)
    print("IN-MEMORY SYNTHETIC TIMELINE VALIDATION (FOUND + NEEDS_RERECORD)")
    print("-" * 68)

    synthetic_timeline = {
        "source_manifest": "video-demo/source-clips.json",
        "analysis_model": "gemini-3.7-flash",
        "combined_duration_seconds": 352.21,
        "notes": ["Synthetic test timeline for dry-run verification"],
        "scenes": [
            {
                "id": "scan",
                "status": "FOUND",
                "source_clip_id": "clip-01",
                "source_start": 8.0,
                "source_end": 45.0,
                "action_time": 10.0,
                "result_visible_time": 42.0,
                "hold_start": 42.0,
                "hold_end": 45.0,
                "evidence": "scan_repository on torvalds/linux visible",
                "confidence": 0.99,
                "safe_direct_cut": True,
                "dead_ranges": [{"start": 0.0, "end": 7.3, "action": "CUT", "reason": "NVIDIA overlay"}],
                "notes": ["Synthetic FOUND scene"]
            },
            {
                "id": "attention",
                "status": "FOUND",
                "source_clip_id": "clip-02",
                "source_start": 8.0,
                "source_end": 35.0,
                "action_time": 10.0,
                "result_visible_time": 30.0,
                "hold_start": None,
                "hold_end": None,
                "evidence": "get_attention_items tool execution",
                "confidence": 0.98,
                "safe_direct_cut": True,
                "dead_ranges": [],
                "notes": []
            },
            {
                "id": "details",
                "status": "FOUND",
                "source_clip_id": "clip-03",
                "source_start": 8.0,
                "source_end": 30.0,
                "action_time": 9.5,
                "result_visible_time": 28.0,
                "hold_start": None,
                "hold_end": None,
                "evidence": "get_check_details on github_actions",
                "confidence": 0.98,
                "safe_direct_cut": True,
                "dead_ranges": [],
                "notes": []
            },
            {
                "id": "human-state",
                "status": "FOUND",
                "source_clip_id": "clip-04",
                "source_start": 8.0,
                "source_end": 28.0,
                "action_time": None,
                "result_visible_time": None,
                "hold_start": None,
                "hold_end": None,
                "evidence": "human scan 3ssiri/RepoPulse",
                "confidence": 0.95,
                "safe_direct_cut": True,
                "dead_ranges": [],
                "notes": []
            },
            {
                "id": "compare",
                "status": "FOUND",
                "source_clip_id": "clip-04",
                "source_start": 10.0,
                "source_end": 30.0,
                "action_time": 12.0,
                "result_visible_time": 25.0,
                "hold_start": None,
                "hold_end": None,
                "evidence": "compare_refs execution",
                "confidence": 0.97,
                "safe_direct_cut": True,
                "dead_ranges": [],
                "notes": []
            },
            {
                "id": "implementation",
                "status": "FOUND",
                "source_clip_id": "clip-07",
                "source_start": 8.0,
                "source_end": 40.0,
                "action_time": None,
                "result_visible_time": None,
                "hold_start": None,
                "hold_end": None,
                "evidence": "live badges and implementation",
                "confidence": 0.95,
                "safe_direct_cut": True,
                "dead_ranges": [],
                "notes": []
            },
            {
                "id": "close",
                "status": "NEEDS_RERECORD",
                "source_clip_id": None,
                "source_start": None,
                "source_end": None,
                "action_time": None,
                "result_visible_time": None,
                "hold_start": None,
                "hold_end": None,
                "evidence": "Synthetic NEEDS_RERECORD validation",
                "confidence": 0.0,
                "safe_direct_cut": False,
                "dead_ranges": [],
                "notes": ["Synthetic NEEDS_RERECORD scene"]
            }
        ]
    }

    # Test synthetic validation
    synthetic_json_str = json.dumps(synthetic_timeline)
    tmp_test_dest = os.path.join(WORKSPACE_ROOT, 'video-demo', '.synthetic_test_timeline.json.tmp')
    try:
        val_res = validate_and_finalize_timeline(synthetic_json_str, auth_schema, manifest, destination_path=tmp_test_dest)
        print("✓ Synthetic timeline validation passed (authoritative schema + semantic validation).")
        print(f"  - 6 FOUND scenes validated with boundary checks [0 <= start < end <= duration]")
        print(f"  - 1 NEEDS_RERECORD scene validated with null source_clip_id/start/end")
    finally:
        if os.path.exists(tmp_test_dest):
            os.remove(tmp_test_dest)

    print("\n" + "=" * 68)
    print("ALL DRY-RUN AND SYNTHETIC VALIDATION CHECKS PASSED.")
    print("=" * 68)


def run_live(resume=True):
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable is not set.")
        print("Setup instructions:")
        print("  In PowerShell:")
        print("    $env:GEMINI_API_KEY = 'your_gemini_api_key_here'")
        print("    python video-demo/analyze_video_gemini.py")
        sys.exit(1)

    try:
        from google import genai
    except ImportError:
        print("ERROR: google-genai library not installed. Install with: pip install google-genai==1.74.0")
        sys.exit(1)

    manifest = load_manifest()
    auth_schema = load_authoritative_schema()
    api_schema = derive_api_safe_schema(auth_schema)
    upload_state = load_upload_state() if resume else {}

    client = genai.Client(api_key=api_key)

    print("=" * 68)
    print("P2: UPLOADING / VERIFYING PROXY CLIPS (BOUNDED PROCESSING & SHA256 RESUME)")
    print("=" * 68)

    file_uri_map = {}
    MAX_WAIT_PER_FILE_SECONDS = 180
    POLL_INTERVAL_SECONDS = 2

    for clip in manifest['clips']:
        cid = clip['clip_id']
        proxy_full = validate_and_resolve_proxy_path(clip, WORKSPACE_ROOT)
        current_sha256 = get_file_sha256(proxy_full)

        # Check resumable state with SHA256 validation
        cached = upload_state.get(cid)
        reused = False
        if cached and cached.get('file_name') and cached.get('proxy_sha256') == current_sha256:
            try:
                remote_file = client.files.get(name=cached['file_name'])
                if remote_file.state.name == "ACTIVE":
                    file_uri_map[cid] = remote_file.uri
                    reused = True
                    print(f"✓ Reusing active upload for {cid} (SHA256 verified): {remote_file.name}")
            except Exception:
                reused = False

        if not reused:
            print(f"Uploading {cid} ({clip['analysis_proxy_path']})...")
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
                "proxy_sha256": current_sha256,
                "timestamp": time.time()
            }
            save_upload_state(upload_state)
            print(f"  ✓ {cid} active: {current_file.name} (SHA256: {current_sha256[:16]}...)")

    print(f"\nAll {len(file_uri_map)} proxies active on Gemini Files API.")

    # Construct interaction payload
    inputs = build_interaction_inputs(manifest, file_uri_map)

    print("\n" + "=" * 68)
    print("CALLING GEMINI INTERACTIONS API (model='gemini-3.7-flash', processing='agentic')")
    print("=" * 68)

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
        if hasattr(interaction, 'text'):
            output_text = interaction.text
        elif hasattr(interaction, 'outputs') and interaction.outputs:
            output_text = interaction.outputs[0].text
        else:
            raise ValueError("Could not extract output_text from Interaction response")

    print("✓ Received Interaction response.")

    # Validate and atomically save timeline.json
    timeline = validate_and_finalize_timeline(output_text, auth_schema, manifest)
    print(f"✓ Validated and saved timeline to {TIMELINE_OUTPUT_PATH}")
    print(f"  Total scenes: {len(timeline.get('scenes', []))}")
    for sc in timeline.get('scenes', []):
        print(f"    - [{sc.get('id')}] status={sc.get('status')}, clip={sc.get('source_clip_id')}, time={sc.get('source_start')}s..{sc.get('source_end')}s")


def main():
    parser = argparse.ArgumentParser(description="P2 Gemini Agentic Video Analysis for RepoPulse WebMCP Demo")
    parser.add_argument('--dry-run', action='store_true', help="Run local validation without API calls or network requests")
    parser.add_argument('--resume', action='store_true', default=True, help="Resume from previously uploaded file references if active (default: True)")
    parser.add_argument('--no-resume', action='store_false', dest='resume', help="Force re-upload of all proxy clips")
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
            run_live(resume=args.resume)


if __name__ == '__main__':
    main()
