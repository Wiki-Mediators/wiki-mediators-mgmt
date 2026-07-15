---
title: "CR Touch Install — Ender 3 V2: Probe Setup, Stuck-Mesh Root Cause, Tramming, Final Config"
status: research-input
created: 2026-07-12
dimension: 3d-printing
register: hobby lane — practical, bank-and-log. No infrastructure proposals
  unless the operator asks. Notes enter as raw-intake or research-input per
  Pattern 11; promotion beyond intake is the operator's call. Web-research
  claims are cited to sources; operator machine observations are marked
  operator-reported, not fact.
related:
  - _DIMENSIONS/3d-printing/3d_printing_dimension_seed_20260710.md
  - _DIMENSIONS/3d-printing/3d_printing_firmware_migration_research_input_20260710.md
  - _DIMENSIONS/3d-printing/3d_printing_setup_outcome_research_input_20260710.md
sources:
  - https://github.com/mriscoc/Ender3V2S1/releases/tag/20260106
  - https://github.com/mriscoc/Ender3V2S1/wiki/3D-BLTouch
  - https://github.com/mriscoc/Ender3V2S1/wiki/Calibration-Guides
  - https://github.com/mriscoc/Ender3V2S1/wiki/Configuration-files
  - https://github.com/mriscoc/Ender3V2S1/wiki/Custom-C-gcodes
  - https://github.com/mriscoc/Ender3V2S1/discussions/1133
  - https://github.com/mriscoc/Ender3V2S1/discussions/883
---

# CR Touch Install — Ender 3 V2 (Sprite Pro, 4.2.2, mriscoc)

## Intake block (provenance)

- **Source identifier:** live install/troubleshooting session 2026-07-12
  (operator + assistant), continuing from the firmware-migration and
  setup-outcome notes.
- **Domain scope:** 3d-printing / auto bed leveling. Ender 3 V2 + Sprite Pro
  + CR Touch + mriscoc BLTUBL specific; the root-cause findings generalize
  to any mriscoc probe setup.
- **Claim type:** mixed — operator-reported machine work and measurements,
  plus firmware behavior findings cited to the mriscoc wiki/discussions.
- **Validation:** closed with a clean end-to-end run — hot-bed mesh, config
  applied, v3 test print completed with no blob, good frame, good center box
  (operator-reported).

## What was installed

- **CR Touch probe** (Creality; metal pin) on the Sprite Pro toolhead, using
  the bracket already on the machine and the Sprite breakout lead (probe
  signal rides the toolhead ribbon cable). Bracket screws go bottom-up.
- **Firmware:** `Ender3V2-422-BLTUBL-MPC-20260106.bin` (mriscoc, cited) —
  the probe + UBL build replacing the MM (manual mesh) build. Same SD-flash
  procedure as before; filename differs so no rename needed.
- **Ordering rule (safety):** wire and mount the probe BEFORE flashing the
  probe firmware. Probe firmware homes on the probe; flashing with no probe
  attached risks a bed crash on first home.

## Probe health check (worth keeping)

- **M48 Probe Test** (Probe Settings menu) probes one point 10× and reports
  deviation. This machine: **0.004062 mm** — excellent (<0.01 is good).
  M48 deliberately stays at ONE point; that is not a fault.
- M48 proved the probe + wiring good, which redirected debugging away from
  hardware — decisive in finding the real bug below.

## THE BUG: mesh probing stuck at one point (root cause + fix)

**Symptom:** bed leveling filled the map with repeated identical values
(e.g. -0.13 everywhere) from ONE physical position; the carriage never
traversed. Probing "completed" but the mesh was garbage. Also: the old
mechanical Z-endstop triggered during some probing moves, and the probe
could not reach the front strip of the bed (bed runs out of Y travel before
the offset probe gets there — inherent to any offset probe).

**Root cause (two compounding config errors):**
1. **Physical settings were oversized:** X max 248, Y max 231, bed size
   230×230 — on a 220×220 machine. The firmware planned probe points across
   a phantom area.
2. **Mesh inset collapsed:** the C29 inset command left Mesh X Min=10,
   X Max=10, Y Min=10, Y Max=10 — a zero-width mesh area. All grid points
   computed to essentially one spot. (A C29 issued with L/R/F/B margins set
   the min/max fields literally; verify the resulting Mesh Inset values on
   screen after any C29.)

**Fix (order matters, per the mriscoc calibration guide, cited):**
1. Set **Physical settings** correct FIRST: X/Y max 220, bed size 220×220
   (Z max 250).
2. Then in **Mesh Inset** menu press **Maximize Area** (then Center Area if
   offered) — the firmware computes the largest valid reachable area from
   physical limits + probe offset. Result here: X 10–189, Y 10–179.
3. Store settings, reboot, re-run leveling.

**Result:** carriage traversed properly, 81-point (9×9) mesh with real
varying values. "Invalid Mesh" + position "-?-" after the fix and before
re-probing is the normal empty-mesh state, not an error.

## Probe offsets (this machine, operator-confirmed)

- **M851 X-31 Y-41** (CR Touch left of and behind nozzle on the Sprite Pro
  front-housing mount; matches community values for this exact setup, cited
  discussions #1133/#883).
- **HS mode OFF**, **Multiple Probing 2** (community-flagged reliability
  settings; HS-off matters for UBL dense grids).

## Mesh-driven manual tramming (the method that worked)

Instead of the corner wizard, read the full mesh map and turn knobs from it:
- Operator naming convention: front-right = driver front, front-left =
  passenger front, back-left = passenger rear, back-right = driver rear.
  Screen grid orientation matched the physical bed intuitively (verified by
  watching probing order).
- Mesh value positive = bed HIGH there = knob toward "down"; negative = bed
  LOW = knob toward "up". The aftermarket labeled knobs ("up"/"down" printed
  on the wheel) beat any CW/CCW description — perspective under the bed
  flips rotation intuitions. Verify direction by watching the corner move.
- Quarter-turns; the worst corner gets slightly more. Re-map between rounds.
- Progression: 0.38 mm total spread → 0.30 → **0.18 mm (Min -0.05 /
  Max +0.13)** across three small rounds. Stopped there: under ~0.25 mm
  total, ABL compensates fully; further tramming is chasing noise on stock
  springs. (One small front-left high spot ~+0.13 remains; ABL handles it.
  If it ever matters: tiny "down" on passenger-front.)
- **Stock spring note:** tired stock springs drift; yellow springs or
  silicone spacers are the standard upgrade if re-tramming becomes frequent.

## Z-offset (the number and how it was found)

- Probe Z offset is a NEW reference vs the old endstop system — the old MM
  firmware's 0.18 offset is meaningless after the probe flash. Expect a
  large negative value.
- Path taken: Z Probe Wizard paper test gave **-2.10**; started prints at
  **-2.00** (fail-high principle: err high, never low, approach the bed by
  babystepping DOWN during a live first layer).
- **Earlier live-tuned value on real PETG plastic: Z-2.54** (at 235 °C nozzle
  / 75 °C bed). A newer operator-reported adjustment, **Z-2.48**, seems to
  produce a better first layer and is the current working value. Paper
  undershoots; plastic is truth.

## Print-start lessons (PETG)

- **Center blob:** a hot idle nozzle drools PETG during homing/probing.
  Fix: anti-ooze start sequence — nozzle at **175 °C during home + probe**,
  full 235 °C only after parking at the corner, then purge. Designed into
  the test gcode.
- **Old gcode is invalid after the probe flash** — files from the MM era
  neither load the mesh (`M420 S1 Z2`) nor use the anti-ooze sequence.
  Regenerate; don't reuse.
- **Purge:** short purge was insufficient; v3 uses a double 175 mm purge
  line plus a +0.8 mm re-prime after the long travel to the center object
  (ooze during travel starves the next feature otherwise).
- **Nozzle-wipe habit:** heat, wipe the tip (brass brush / paper towel),
  then print — PETG clings a booger to the nozzle otherwise and deposits it
  mid-print.
- **Mesh at print temperature:** re-probed with the bed at **75 °C** (print
  temp) rather than 50 °C — the bed moves slightly with heat, so a hot mesh
  matches print conditions. Adopted as standard practice.

## Artifacts (banked alongside this note)

- **`master_config.gco`** — one-shot machine restore (C10 config file, run
  from Print menu): e-steps 424.9, M851 X-31 Y-41 Z-2.48, mesh area/grid,
  M500. Deliberately does NOT restore a mesh — mesh is physical measurement
  data; re-probe (hot) and Save after running the config.
- **`petg_test_v3_CRTOUCH_150mm.gcode`** — validation print: double purge,
  mesh-loading, anti-ooze sequence, 150 mm 2-lap frame, 20 mm box × 15
  layers with travel re-prime. This is the file that produced the clean
  end-to-end run.

## Final state (operator-reported, validated by clean print)

Ender 3 V2 / 4.2.2 / Sprite Pro / CR Touch / mriscoc BLTUBL-MPC-20260106.
E-steps 424.9. Probe X-31 Y-41 Z-2.48. HS off, multi-probe 2. Physical
220/220/250, bed 220×220. Mesh area ~X10–189/Y10–179 (Maximize Area). Bed
trammed to ~0.18 mm. Hot-bed (75 °C) mesh saved. PETG 235/75. Clean test
print with no blob: frame even, center box starts clean.

## Open threads

- Front-left (+~0.13) high spot — cosmetic; optional tiny "down" turn later.
- 5×5 vs 9×9 grid — hot re-mesh ran 5×5 (grid setting reverted or config
  N-value applied); either is adequate on a 0.18 mm bed; N is set in Mesh
  Inset if 9×9 is wanted back.
- Spring/spacer upgrade if tram drift appears.
- Modeling sub-thread (from the setup-outcome note) still open: functional
  vs artistic first CAD project.
