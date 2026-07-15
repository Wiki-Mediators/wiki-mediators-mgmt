---
request_id: KR-20260714-004
created: 2026-07-14
from: machine/ryry
target: machine/nt8lab
status: ready-for-review
sensitivity: repository-safe
related_dimension: 3d-printing
response_path: _HANDOFFS/knowledge_responses/KR-20260714-004_response.md
---

# Review Request — Notebook Object-Capture Kit

Please review this proposal before any implementation. The operator wants to
use the integrated camera on the RYRY notebook to capture objects, then move
the capture set to the desktop/local machine for reconstruction. The camera is
present, enabled, and operator-tested after opening its physical privacy
shutter. No capture tooling has been built yet.

## Proposed responsibility split

- **Notebook / RYRY:** camera capture, deterministic session-folder creation,
  frame manifest, capture log, and inexpensive preflight quality checks.
- **Desktop / NT8lab:** COLMAP/Open3D reconstruction on the GTX 1080 Ti,
  measurement or mesh cleanup, result banking, and linkage back to the
  notebook capture log.
- **Transport:** binary images/video move out-of-band through an operator-
  selected shared folder or USB. Git, generated `main`, and correspondence
  branches carry only repository-safe manifests, logs, proposals, and results.

This follows the machine split already recorded in
`_DIMENSIONS/3d-printing/object_scanning_seed_20260714.md` and the validated
desktop reconstruction design in
`_DIMENSIONS/3d-printing/3d_printing_scanner_pipeline_research_input_20260714.md`.

## Smallest proposed notebook MVP

1. A PowerShell entry point that creates a uniquely named capture session and
   records object, purpose, camera, lighting, known dimension, and operator
   notes before reconstruction.
2. Camera capture using a Windows-compatible backend, supporting deliberate
   still images first. Video/frame extraction and burst stacking remain later
   options unless the baseline test proves they are needed.
3. A deterministic folder contract:

   ```text
   capture_session/
     capture_session.md
     manifest.csv
     images/
     checks/
   ```

4. Mechanical checks only: readable files, sequential IDs, dimensions,
   timestamps, duplicate detection, blur/exposure warnings, and minimum frame
   and viewpoint prompts. The tool must never invent or enhance pixels.
5. A handoff receipt that identifies the capture session and destination but
   does not place binary frames or machine-private paths in Git.

## Baseline validation proposal

Use scan-to-compare before scan-to-print. Photograph one existing calibration
print with a known source model and measured feature. Run four cheap trials:

1. notebook webcam, ordinary stills;
2. notebook webcam, stacking enabled;
3. phone camera, ordinary stills;
4. phone camera, stacking enabled.

Judge coverage, reconstruction success, dimensional error, and operational
friction. Keep stacking only if it improves measured results. Dense
reconstruction remains desktop-owned.

## Decisions requested from the orchestrator

1. Approve or revise the notebook/desktop responsibility boundary.
2. Name the authoritative out-of-band transfer root and retention policy.
3. Confirm the first calibration object/model and known measurement.
4. Decide whether the MVP should control the integrated camera directly or
   initially ingest photographs saved by the Windows Camera app.
5. Define which capture metadata is repository-safe and which stays beside the
   binary artifacts.
6. Identify the authoritative desktop `scan_pipeline.py` location or confirm
   that it must be recovered/banked before the first handoff.

## Guardrails

- Open the physical camera shutter only for an active capture session.
- Microphone access is unnecessary.
- No AI super-resolution, generative fill, or synthetic detail in measurement
  captures.
- No installers, dependency changes, camera automation, or reconstruction work
  is authorized by this request.

Please answer at
`_HANDOFFS/knowledge_responses/KR-20260714-004_response.md` on
`machine/nt8lab`.
