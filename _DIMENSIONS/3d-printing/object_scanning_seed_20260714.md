---
title: "Object Scanning — Seed (scan-to-print / scan-to-compare)"
status: raw-intake
created: 2026-07-14
dimension: 3d-printing
register: hobby lane, bank-and-log weight. Design capture from the
  2026-07-14 operator/Claude conversation. Research claims below marked
  as design-reasoning, not verified benchmarks. No builds authorized.
provenance: operator concept (camera scanning + super-resolution +
  noise-discovery) refined in chat; physics framing from standard
  multi-frame SR / astro-stacking practice. Conversation tape: next
  archive export.
related:
  - 3d_printing_dimension_seed_20260710.md
  - (scanner pipeline / KIRI research note in this dimension)
---

# Object Scanning — scan-to-print and scan-to-compare

## The two goal loops

1. SCAN-TO-PRINT: camera capture → reconstruction (photogrammetry or
   gaussian-splat route) → mesh cleanup → slice → print on the Ender.
2. SCAN-TO-COMPARE (the measurement loop, likely FIRST): print a known
   calibration geometry (cube, tolerance test — baselines already in
   this dimension's test set) → scan the printed object → compare
   measured dimensions/geometry against the known model → quantify the
   printer's dimensional accuracy and drift. This loop has ground truth
   by construction, so it validates the scanning pipeline and the
   printer at the same time.

## Design rules (settled in conversation, 2026-07-14)

- STACKING YES: multi-frame capture from a locked position; true signal
  is consistent across frames, sensor noise is random — averaging N
  frames improves SNR ~sqrt(N). Slow is acceptable; this is the
  astronomy trade. Calibration frames (dark/flat-style) may characterize
  the webcam's systematic noise; the operator's "discover the noise and
  cancel it" concept is exactly this and is sound.
- HALLUCINATION NO: AI single-image super-resolution paints plausible
  detail, not real detail. NEVER feed AI-upscaled frames into
  reconstruction or measurement — invented texture becomes invented
  geometry. Honest blur beats confident fiction for measuring.
- CAPTURE DISCIPLINE > SENSOR QUALITY: coverage, locked positions,
  consistent lighting, many viewpoints. A mediocre webcam with
  discipline beats a good camera waved around.
- OPEN QUESTION: notebook webcam vs phone camera as the sensor. Phone
  is likely the better sensor; notebook is the machine at the printer.
  Decide by trying the compare-loop with both, not by assumption.
- Poor-man's turntable candidate: the Ender build plate (controlled
  rotation via G-code jog) — untested idea, bank as-is.

### Rig refinements (2026-07-14)

(6) Capture rhythm RULED: metronome stills — audio beep paces
move-settle-hold-shoot; interval is a PARAMETER, default 3s (1s risks
mid-move blur; keep-rate data from trial one may argue it down). Session =
~60 keeps across passes.

(7) Rig amendment: object may be HAND-HELD and turned directly (stick
optional); consequence — fingers occlude, so the second pass is mandatory as
a REGRIP pass (different hold points), and the dice moves off-stick: blu-tack
it to the object or use flat grid/ruler in frame as scale reference. Blur risk
rises; the auto-junk checker (variance-of-Laplacian) is the countermeasure,
and keep-rate decides if the stick returns.

(8) Dual camera RULED IN as trial 1b: phone shoots on the same beeps (the
metronome is the sync); reconstruct webcam-only first, then webcam+phone on
the same session — the mesh delta IS the phone's measured fidelity
contribution. Beep metronome is in-scope for the capture MVP (simpler than
camera control; v1 may be beep-only with manual shutter).

## Pipeline shape (design only — nothing built)

capture rig (dumb-tool shaped: lock, burst N frames, timestamp, save to
artifacts/) → stacking step (classical, deterministic — OpenCV-class
tooling) → reconstruction (photogrammetry e.g. Meshroom, or KIRI-style
service — research note exists in this dimension) → EITHER slice-and-
print OR compare-to-baseline measurement report.

## Software / machine reality

The wiki carries KNOWLEDGE (this seed, research notes, procedures); it
does not carry installers. Capture/stacking/reconstruction software is
notebook-local machine state, installed by the notebook agent on its
own machine, guided by notes it reads from its clone. Per the
environment doctrine (5.x track), if this pipeline matures, the
notebook's dependency set gets its own manifest note — banked, not
assumed.

## Machine reality + division of labor (2026-07-14)

Notebook GPU is a smaller AMD Radeon — CUDA-locked tools (Meshroom dense
step, splat training) are off-menu there. Division of labor: NOTEBOOK =
capture rig + honest logging (one capture-session log per scan, written
BEFORE reconstruction: object, purpose, camera, frame count/manifest,
lighting, settings). DESKTOP = reconstruction compute + measurement +
banking results; reconstruction reports must cite their capture log.
Frames are binaries: they travel out-of-band (share/USB) into the desktop's
artifacts/ folder, never through the bridge or correspondence branches.
Scan-to-compare remains CPU-feasible anywhere; the GPU constraint gates only
scan-to-print dense reconstruction.

## Status

Raw intake. First action when the operator is ready: the SCAN-TO-COMPARE
loop on an existing calibration print, phone vs webcam, stacking on/off
— four cheap trials that validate the whole concept before any deeper
build.
