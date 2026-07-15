---
title: "3D Printing Setup — Outcome: Tuned Machine + First PETG Print"
status: research-input
created: 2026-07-10
dimension: 3d-printing
register: hobby lane — practical, bank-and-log. No infrastructure proposals
  unless the operator asks. Notes enter as raw-intake or research-input per
  Pattern 11; promotion beyond intake is the operator's call. Web-research
  claims are cited to sources; operator machine observations are marked
  operator-reported, not fact.
related:
  - _DIMENSIONS/3d-printing/3d_printing_dimension_seed_20260710.md
  - _DIMENSIONS/3d-printing/3d_printing_firmware_migration_research_input_20260710.md
sources:
  - https://github.com/mriscoc/Ender3V2S1/releases/tag/20260106
  - https://github.com/OrcaSlicer/OrcaSlicer/releases
  - https://www.orcaslicer.com/
---

# 3D Printing Setup — Outcome: Tuned Machine + First PETG Print

## Intake block (provenance)

- **Source identifier:** live setup/tuning session 2026-07-10 (operator +
  assistant), continuing the firmware-migration thread.
- **Domain scope:** 3d-printing / firmware + tuning + slicer. Ender 3 V2 +
  Sprite Pro specific.
- **Claim type:** mostly operator-reported outcomes (what worked on the
  actual machine), plus cited software/download facts.

## Thread (what this closes)

The thread named in the migration note — *"get onto a maintained,
hardware-matched firmware base, then diagnose the actual prints"* — is now
**closed on the machine side.** The machine flashed, tuned, and produced a
clean PETG print. What remains open is **modeling** (creating printable
models), which is really a new sub-thread rather than the tail of this one.

## What got done (operator-reported unless cited)

- **Firmware flashed:** `Ender3V2-422-MM-MPC-20260106.bin` (mriscoc, cited),
  SHA-256 verified byte-for-byte on the card by Codex 5.6, flashed via SD.
  New ProUI came up — flash confirmed successful.
- **e-steps set to 424.9** (Sprite Pro) via the menu; saved.
- **Temperature control:** the build uses **MPC, not PID** — so no PID
  autotune was needed or possible; the `M303` step was correctly dropped.
  Temp held steady at 200 °C in test (MPC working out of the box). (cited:
  mriscoc wiki notes MPC replaces hotend PID.)
- **T13 correction:** the Sprite-Pro thermistor profile (T13) does exist, but
  in mriscoc's Special_Configurations repo, not the main release. It was
  **not needed** — the stock thermistor read accurately at PLA/PETG temps on
  this machine. T13 remains a future option only if high-temp (>260 °C)
  printing or temp drift appears. (cited)
- **Z / first layer:** Z-endstop switch repositioned for the Sprite Pro's
  height (coarse), then paper-set with a heated nozzle. Fine Z dialed live
  during first-layer prints.
- **Bed adhesion:** original failure was traced to (a) an uncleaned glass bed
  and (b) PETG being run at PLA temps. Resolved.

## Proven settings (operator-reported — what actually worked)

These are this machine's working values as of 2026-07-10, from successful
prints — not general truth:

- Material in use: **PETG**.
- **Nozzle 235 °C**, **bed 75 °C** — produced a clean print. (Note: this is
  well below the 255 °C the generic Orca PETG profile defaulted to; 235 is
  the operator's tested value and was trusted over the generic default.)
- **e-steps 424.9.**
- **Retraction ~1 mm** (Sprite Pro direct drive; down from the ~5 mm Bowden
  default). Starting value, not yet calibration-confirmed.
- Nozzle 0.4 mm, filament 1.75 mm.
- First real test (150 mm frame + small center tower, hand-generated gcode)
  printed well after minor live bed/Z tuning. Machine motion reported
  smoother than on the old Jyers build.

## Slicer decision

- **Chosen: OrcaSlicer** (v2.4.2, x64 Windows installer, cited). Rationale:
  actively maintained and its built-in calibration suite (retraction, flow,
  pressure advance) is the strongest fit for a freshly direct-drive-converted
  machine — the tuning payoff Cura would make manual. Cura and PrusaSlicer
  were the considered alternatives (Cura = biggest profile library /
  most beginner-friendly; PrusaSlicer = clean first layers), both viable.
- **Safety note (cited):** only official sources (GitHub / Microsoft Store /
  orcaslicer.com) — several copycat sites serve malicious installers.
- **Orca profile set up:** Ender 3 V2 printer profile (correct as-is; Sprite
  Pro is an extruder change, NOT a separate printer profile), Generic PETG
  filament, nozzle 235/235, bed 75/75, retraction override enabled at 1 mm,
  saved as a "@System - Copy" preset.
- **Not yet done (booked):** run Orca **Calibration → Retraction** and
  **Flow** to replace the 1 mm starting guess with measured values; pressure
  advance left OFF pending calibration.

## Retired

- The `prep_firmware_card.ps1` helper was retired in favor of Codex 5.6 doing
  the verified card copy (recorded in the migration note). Not part of the
  kept toolset.

## Open thread — modeling (NEW sub-thread)

The machine is ready; the operator now wants to create printable models. Open
question captured for the next session: **functional/mechanical parts**
(→ Tinkercad / Fusion / FreeCAD, watertight by construction) vs
**artistic/organic shapes** (→ Blender, needs manifold checking via the 3D
Print Toolbox). Export as STL or 3MF; slice in Orca. Solid-modeling tools
avoid the watertight-repair headache; mesh tools require it. This is the
seed for a future `3d-printing` modeling note.

## Status

Machine + slicer setup COMPLETE and validated on a real PETG print. Modeling
sub-thread OPEN. Calibration (retraction/flow) booked but not run.
