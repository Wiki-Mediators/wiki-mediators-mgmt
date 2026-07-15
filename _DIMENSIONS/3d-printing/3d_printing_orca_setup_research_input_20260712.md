---
title: "OrcaSlicer Setup — Ender 3 V2 (Sprite Pro + CR Touch) Profile & Start G-code"
status: research-input
created: 2026-07-12
dimension: 3d-printing
register: hobby lane — practical, bank-and-log. Operator-confirmed slicer
  configuration; validated by the first real object print.
related:
  - _DIMENSIONS/3d-printing/3d_printing_crtouch_install_research_input_20260712.md
  - _DIMENSIONS/3d-printing/3d_printing_setup_outcome_research_input_20260712.md
---

# OrcaSlicer Setup — Ender 3 V2 (Sprite Pro + CR Touch)

Validated end-to-end 2026-07-12: sliced Better_Whistle_V2 with this
profile, exported gcode verified in Notepad (M420 present), printed
clean, whistle functional.

## Profile (OrcaSlicer v2.4.2, x64)

- **Printer:** Creality Ender-3 V2, 0.4 nozzle (stock profile as base;
  saved as a "- Copy" preset after edits). Sprite Pro is NOT a separate
  printer profile — it is settings changes on the stock profile.
- **Printer > Extruder:** Retraction Length **1 mm** (direct-drive value;
  stock Bowden default ~5 mm causes stringing on the Sprite).
  Z-hop 0.4 left at default.
- **Filament:** "Generic PETG @System - Copy": nozzle **235/235**, bed
  **75/75** (operator-proven temps; ignore the generic 255 default and
  the 227-233 recommended range - trust the tested value).
  Pressure advance OFF until calibrated.
- **Process:** 0.20mm Standard @Creality Ender3V2 (stock, fine as-is).

## Machine start G-code (the critical piece)

Printer settings → toggle **Advanced** (top-right slider) → **Machine
G-code** tab → replace Machine start G-code with:

```
G90 ; absolute coordinates
M83 ; extruder relative mode
M140 S[bed_temperature_initial_layer_single] ; start bed heating
M104 S175 ; nozzle no-ooze temp for homing/probing
M190 S[bed_temperature_initial_layer_single] ; wait for bed
M109 S175 ; wait for nozzle at 175
G28 ; home all (probe defines Z)
M420 S1 Z2 ; LOAD SAVED MESH, fade 2mm
G0 X15 Y15 F3000 ; park front-left corner
M104 S[nozzle_temperature_initial_layer] ; full print temp
M109 S[nozzle_temperature_initial_layer] ; wait for it
G92 E0
G1 Z0.28 F600
G1 X20 Y18 F3000
G1 X195 Y18 E12 F1000 ; purge line out
G1 X195 Y18.6 F1000
G1 X20 Y18.6 E12 F1000 ; purge line back
G1 E-1 F1800
G92 E0
```

Why: stock Orca Ender 3 V2 start gcode does NOT load the mesh (no M420)
- prints would ignore all CR Touch leveling. This block also holds the
nozzle at 175 °C during home/probe (PETG oozes a center blob if heated
fully first) and runs the proven double purge. Placeholders resolve from
the active filament profile automatically (whistle gcode showed S75/S235
correctly).

## Workflow habits (validated)

- Slice → **verify before printing**: open the exported .gcode (Notepad)
  and confirm `M420 S1 Z2` appears in the first ~20 lines.
- Export to SD card root; print from the printer's SD slot (machine is
  SD-only).
- Z-offset (-2.00) lives in printer EEPROM, not the slicer — nothing to
  set in Orca for it.
- Division of labor: Orca GUI settings = operator (per this note);
  file/vault/SD work = Codex. Editing Orca profile JSONs by agent is
  possible but not worth the risk for one-time GUI settings.

## Booked, not done

- Orca Calibration menu: retraction test, flow rate, pressure advance —
  the payoff features that motivated choosing Orca; run when print
  quality tuning begins in earnest.
- PETG spool drying (interior bridging/stringing on the whistle suggests
  moisture).
