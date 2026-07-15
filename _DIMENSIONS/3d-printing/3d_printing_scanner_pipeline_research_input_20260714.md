---
title: "Homemade 3D Scanner — Photogrammetry Pipeline (Video/Photos → Watertight STL)"
status: research-input
created: 2026-07-14
dimension: 3d-printing
register: hobby lane — practical, bank-and-log. Web-research claims cited;
  operator/local-agent machine findings marked as such. Pipeline validated
  on a known baseline dataset before first real capture.
related:
  - _DIMENSIONS/3d-printing/3d_printing_setup_outcome_research_input_20260712.md
sources:
  - https://colmap.github.io/datasets.html
  - https://github.com/colmap/colmap/releases
  - https://openscan.eu/ and https://openscan-org.github.io/OpenScan-Doc/
  - https://www.kiriengine.app/blog/3DGSvsPhotogrammetryvsLiDAR
---

# Homemade 3D Scanner — Photogrammetry Pipeline

## What this is

A scanner built from software: phone video or photo set → **ffmpeg**
(frame extraction) → **COLMAP automatic_reconstructor** (dense CUDA
reconstruction on the local GTX 1080 Ti) → **Open3D** (Poisson
reconstruction → density trim → component filter → STL). One command:
`python scan_pipeline.py <video|image_folder> [name]`. Artifact:
**`scan_pipeline.py`** (knobs at top: extract FPS, COLMAP quality,
Poisson depth, density %, KEEP_LARGEST_ONLY).

## Baseline validation (2026-07-14, Codex-executed)

Known-good dataset: official COLMAP **South Building** (128 images).
Result: **3,403,511-point dense cloud → 185,291-triangle STL**; the
building is clearly recognizable in Orca (facade, windows, portico,
roofline). Pipeline VALIDATED on known data before any own-capture —
this separates pipeline bugs from capture-technique problems.

## Hard-won findings (bank-worthy)

1. **GTX 1080 Ti (Pascal, compute 6.1) requires COLMAP ≤3.11.1 CUDA
   build.** COLMAP 4.1.0's CUDA build fails initialization on Pascal
   (cudacc.cc:59). Fix: official 3.11.1 CUDA release. (Codex-diagnosed.)
2. **Open3D STL export writes a ZERO-BYTE file if triangle normals are
   missing.** Fix in pipeline: `compute_triangle_normals()` before
   `write_triangle_mesh`. (Codex-caught; script patched.)
3. **A failed COLMAP run leaves a poisoned workspace database** — a
   later run cannot reuse it. Archive/rename the scan_work folder and
   start clean.
4. **Building/scene datasets are inherently non-watertight** (no
   bottom/top coverage); object orbits with two heights close far
   better. Density trim also trades watertightness for faithfulness —
   slicer auto-repair closes the remainder.
5. **Background chunks (trees etc.) survive a min-triangle floater
   filter** because they are large connected components. For
   single-object scans, KEEP_LARGEST_ONLY=True is the right filter.

## Capture rules (for own scans)

- **Orbit the object; do NOT use a turntable** with a normal background:
  COLMAP solves camera pose from ALL frame features, and a static
  background contradicts a rotating object → ghost reconstruction.
  Turntables only work with a featureless backdrop + controlled light
  (the OpenScan rig approach, cited). A cluttered static background
  actually HELPS handheld capture.
- **Light: diffuse and even beats bright.** No hard shadows (baked in as
  fake geometry), no specular hotspots (features that "teleport"), no
  flash, consistent exposure across the orbit (lock exposure/focus).
- Slow orbit, two loops at different heights (~level and ~30–45° above),
  object filling the frame, everything sharp. ~2 fps extraction from a
  30 s orbit ≈ 60 frames; <20 images is too few.
- **Matte, textured surfaces reconstruct best**; chalk-dust or matting
  spray on shiny objects.
- **Photogrammetry has NO SCALE** — include a ruler/known dimension in
  the capture and scale the STL in the slicer to a measured feature.

## The two AIs (policy for this vault)

- **Faithful repair** (Poisson closure, density trim, slicer/Fix-Wizard
  repair): measurement-preserving. The ONLY type trusted for fitting
  parts.
- **Generative completion** (Hunyuan3D, TRELLIS image-to-3D): invents
  plausible geometry from learned priors — excellent for decorative
  objects from a single photo, HALLUCINATION for engineering fits.
  Rule: *generative for looks, Poisson for fits.*

## Capability ladder (2026, cited in sources)

Phone apps w/ cloud (Scaniverse/KIRI, free, casual) → this local
pipeline (free, scriptable, private, GPU-bound) → RealityScan (free
personal GUI) → structured-light scanner (~$500 POP 3 Plus class) →
prosumer blue-laser hybrids (~$1,200 Raptor class, shiny metal).
Calipers + parametric FreeCAD still beat all of the above for
geometric fitting parts.

## Status / next

Pipeline validated on baseline; patched script is authoritative
(normals fix + KEEP_LARGEST_ONLY). NEXT: first real capture per the
rules above, judged against the baseline. OpenScan printed rig filed as
a future build for routine small-object scanning.
