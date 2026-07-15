---
request_id: KR-20260715-006
created: 2026-07-15
from: machine/ryry
target: machine/nt8lab
status: ready-for-review
sensitivity: repository-safe
related_request: KR-20260714-005
response_path: _HANDOFFS/knowledge_responses/KR-20260715-006_response.md
---

# Desktop Handoff — Notebook Capture Kit + Verified COLMAP Baseline

The operator is physically transferring a verified notebook package to the
desktop. This message is the repository-safe routing and state receipt; no
binary images, machine-private paths, drive letters, host/share details, or
source EXIF are carried in Git.

## USB package to locate

Top-level folder:

```text
WIKI_MEDIATORS_TO_DESKTOP_20260715/
```

Payload folder:

```text
baseline_south_building_20260715/
```

The package contains `README_FIRST.txt` and `TRANSFER_SHA256.csv`. Notebook-to-
USB verification completed before handoff: **389 files**, **530,377,816
bytes**, and **0 SHA-256 mismatches**.

## Desktop destination and input

Copy the complete payload folder to:

```text
_DIMENSIONS/3d-printing/artifacts/incoming/baseline_south_building_20260715/
```

Use the 128 EXIF-free files under `images/` as reconstruction input.
`originals/` is provenance only. `manifest.csv`, `capture_session.md`, and
`checks/` travel with the images and must remain linked to the session.

## Baseline identity and notebook result

- Source: official COLMAP 3.11.1 South Building dataset, 128 same-camera
  images.
- Download archive SHA-256:
  `D210016BD2DE20936A5F02B87FD38A76BF0440C42D045231218372CF9DB9A7A1`.
- Notebook ingest: **128 accepted, 0 rejected**.
- Source EXIF detected: **128/128**; accepted exports verified EXIF-free:
  **128/128**.
- Blur score range: **122.735–513.685**, average **270.07**.
- The run produced 128 manifest rows, per-frame content hashes, and 128 frame
  receipts plus the session configuration receipt.

## Notebook tool state

The DIY tool source is on `machine/ryry` through commit `6267885`. Current
behavior includes:

- Realtek integrated-camera capture through DirectShow at 1920x1080;
- two alert beeps, a default 10-second setup window, and a long start tone;
- one automatic snapshot every 3 seconds, followed by object rotation;
- blur/exposure checks with the notebook blur baseline calibrated to `20`;
- non-destructive rejection, EXIF-free accepted JPEGs, hashes, manifest rows,
  and JSON receipts;
- Explorer thumbnail review; no custom GUI and no cloud service.

Seven notebook regression tests pass. Real-camera trials established that the
camera path and timing work, while current room captures are materially softer
than the known-good baseline; lighting and rig discipline remain the next
physical variables.

## Desktop actions requested

1. Copy the USB payload to the destination above.
2. Verify the copied payload against `TRANSFER_SHA256.csv` and report counts,
   bytes, and mismatches.
3. Satisfy KR-004 decision D6 before reconstruction: locate and identify the
   authoritative `scan_pipeline.py`, or explicitly declare it absent and bank
   the recovered/authored version. Do not proceed against a dangling script
   reference.
4. Confirm the reconstruction input is the payload's `images/` folder, not
   `originals/`.
5. Report readiness or the precise blocker at
   `_HANDOFFS/knowledge_responses/KR-20260715-006_response.md` on
   `machine/nt8lab`.

This handoff authorizes intake verification and D6 resolution. It does not
silently authorize replacement of the desktop's authoritative reconstruction
pipeline or deletion of prior artifacts.
