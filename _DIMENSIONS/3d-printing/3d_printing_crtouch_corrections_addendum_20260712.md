---
title: "CR Touch Install — Addendum: C29 Config Bug + Final Values"
status: research-input
created: 2026-07-12
dimension: 3d-printing
register: hobby lane — practical, bank-and-log. Corrections to the CR Touch
  install note; operator observations marked operator-reported.
related:
  - _DIMENSIONS/3d-printing/3d_printing_crtouch_install_research_input_20260712.md
---

# Addendum to CR Touch Install note (same day)

## Correction 1 — C29 must NOT be in the master config

The install note's artifact `master_config.gco` included a
`C29 L.. R.. F.. B.. N..` mesh-inset line. **Remove it — superseded.**
C29 corrupted the mesh-area settings BOTH times it ran on this machine
(first the collapsed one-point mesh; later a scrambled grid/changed values
the operator caught on review). The reliable method for the mesh area is
the **menu: Mesh Inset → Maximize Area (→ Center Area)** after setting
physical limits. The corrected artifact is **`master_config_v4.gco`**:
only M92 (e-steps), M851 (probe offset), M500, plus the manual menu
checklist as comments. Config files carry only plain, proven M-codes.

## Correction 2 — final Z-offset is -2.00 (validated on first real print)

Value history: paper test -2.10 → live-tuned -2.54 → transient readings
(-1.67, a "-0.2" that was a relative babystep, not absolute) → settled
**-2.00**, confirmed on screen and validated by a clean first real object
(whistle, functional). -2.00 sits naturally near the paper's -2.10; the
intermediate values are attributed to relative-vs-absolute confusion and
possible bracket settling. **Maintenance flag: if first-layer height
drifts, snug the CR Touch bracket screws (cold) first, then re-tune Z.**

## Maintenance practice (adopted)

- Re-run the **hot-bed (75 °C) mesh** periodically — after bed cleaning,
  moving the machine, or when first layers turn uneven. Stock springs
  settle with heat cycles; normal, not a fault.
- Frequent knob re-tramming (not just re-meshing) = time for yellow
  springs or silicone spacers.
- Config file runs ONCE after flash/reset (M500 persists in EEPROM); it
  is not a boot script.
- Final bed state this session: hot 5×5 mesh, Min -0.02 / Max 0.13,
  saved. 5×5 adopted as standard grid.

## First real print (validation record, operator-reported)

Better_Whistle_V2, PETG 235/75, ~39 min, sliced in OrcaSlicer with the
CR-Touch start G-code. Exterior clean, top surface smooth; interior
bridging messy (normal for an enclosed chamber; suspect damp PETG made
it worse — dry-spool note below). A ridge line on the exterior wall at
~2/3 height, initially suspected as a mechanical layer shift, was
diagnosed as the **internal pea + chamber-roof bridging scar**: sagging
midair bridges at that layer push the surrounding perimeters outward,
asymmetrically (bridges anchor unevenly). Distinguishing test used:
silhouette continuous / top aligned over bottom = no shift; a real shift
offsets everything above the line on every face. **Diagnosis downgraded
to PROVISIONAL** (operator counterexample): several pre-CR-Touch prints
of the same model show NO line — geometry alone can't be the cause.
Candidate variables that changed: Cura→Orca slice (seam/speed/accel),
filament months damper, new firmware, single-Z leadscrew spot, possible
power transient (ranked low). **Experiment booked:** rerun the identical
gcode — line at same height = systematic (slicer diff / Z-mechanical);
no line = transient (moisture pop); different height = filament
moisture. Not a confirmed motion fault either way. **Whistle works**
(pea broken free post-print per the model's design). Honest expectation
set: ABL improves first-layer RELIABILITY, not above-first-layer quality;
surface quality comes from extrusion/temps/cooling tuning (Orca
calibration suite booked, not run).

## Rerun verdict + open watch items (2026-07-13 morning)

- **Ridge-line experiment resolved: ONE-OFF.** Identical gcode rerun
  printed clean — no line. Transient cause (moisture pop or passing
  nozzle blob) confirmed; mesh, config-residue, and Z-screw suspects
  released. Timeline correction for the record: the clean pre-CR-Touch
  whistles were sliced in the SAME Orca profile lineage but printed on
  the hand-configured machine (menu e-steps, wizard Z, manual level, no
  scripts/probe/mesh) — they stand as the **known-good mechanical
  baseline**. Lesson logged: manual era = slow but transparent; scripted
  era = fast but opaque (bad C29 corrupted state invisibly, twice, caught
  only by operator review). Practice: configs carry only plain M-codes;
  verify settings on-screen after any script.
- **Z-OFFSET DRIFT — ACTIVE WATCH ITEM.** Working values by session:
  -2.10 → -2.54 → -2.00 → -2.19. Bouncing around ~-2.2 (±0.3 mm), not
  walking one direction. Healthy setups hold within a few hundredths.
  Action: snug CR Touch bracket screws (cold); then next session start
  at the saved value WITHOUT babystepping — holds = solved; wanders =
  bracket exonerated → stock bed springs (upgrade to yellow springs /
  silicone spacers) and/or re-run M48 (was 0.004 mm at install) to check
  probe repeatability. Quick 5×5 hot mesh before a session: adopted as
  good practice, not a symptom. **Update (2026-07-13): old Z-endstop
  EXONERATED** — hand-click test during a Z-descent showed the firmware
  ignores the switch entirely (safe to leave installed, unplugging
  unnecessary). Operator reports no drift recurrence since the last fix;
  **watch item downgraded to passive** — revisit only if first-layer
  babystepping becomes routine again. **Yellow springs INSTALLED
  2026-07-13** (golden-orange stiff springs — correct part); operator
  elected no further tram/mesh adjustment — springs look settled,
  re-tram + hot-mesh only if symptoms appear. Z-offset unaffected by
  the swap (nozzle-to-probe geometry); saved value stands.

## Open items

- Dry the PETG spool (or fresh spool) — stringing/bridging quality.
- Orca calibrations: flow, pressure advance, retraction fine-tune.
- Spring/spacer upgrade if tram drift appears.
