---
title: "Firmware Migration — Ender 3 V2 to mriscoc Marlin (Sprite Pro, 4.2.2)"
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
sources:
  - https://github.com/mriscoc/Ender3V2S1/releases/tag/20260106
  - https://marlin.crc.id.au/
  - https://the3dprinterbee.com/creality-sprite-pro-review/
  - https://3dprintbeginner.com/creality-sprite-pro-extruder-review/
  - https://www.crealityexperts.com/sprite-extruder-upgrade-buying-guide
  - https://www.3djake.com/creality-3d-printers-spare-parts/sprite-extruder-pro
---

# Firmware Migration — Ender 3 V2 → mriscoc Marlin (Sprite Pro, 4.2.2)

## Intake block (provenance)

- **Source identifier:** live troubleshooting session 2026-07-10 (operator +
  assistant), plus the web sources listed in frontmatter.
- **Domain scope:** 3d-printing / firmware + extruder hardware. Ender 3 V2
  specific; does not generalize to other printers.
- **Claim type:** mixed — external process/evidence (cited) and operator
  machine observations (marked operator-reported). Seed-level, not promoted.

## Thread (what this is, why it exists)

The operator set out to (a) leave the stale Jyers firmware for something
maintained and (b) eventually diagnose print-quality issues originally
suspected to be Z-related (single Z, no ABL). This note banks the firmware
half of that thread. The print-symptom diagnosis is **still open** — see the
last section. Naming the thread so it can be picked up: *"get onto a
maintained, hardware-matched firmware base, then diagnose the actual
prints."*

## Machine state (operator-reported)

Marked operator-reported; not independently verified. This is one machine at
one date, not general truth.

- Printer: Creality Ender 3 V2.
- Mainboard: **4.2.2** — read off the board silkscreen by the operator after
  opening the base enclosure. (Serial number does not reliably map to board
  version; a physical look was the correct check.)
- Extruder: **Creality Sprite Pro** direct-drive — identified by metal
  (all-metal) body, single part-cooling fan with a stainless shield, and a
  single flat ribbon cable to a breakout board on the toolhead. This is the
  Pro's signature versus the plastic-body, existing-hotend extruder-only
  Sprite.
- Probe: BLTouch firmware-capable but **no probe physically installed** yet
  (planned later).
- Prior firmware: Jyers v2.0.1 (community Marlin fork; UI-focused). Whether
  the running build was the correct 4.2.2 variant was never confirmed — made
  moot by reflashing a known-4.2.2 build.
- Slicer: Cura.

## Findings (web-research, cited)

- **Jyers is stale.** It is a Marlin fork whose appeal was its custom
  touchscreen UI; active development largely stopped, which is the staleness
  the operator was reacting to. Leaving it is sound.
- **Klipper without a Raspberry Pi is possible but still needs a host.**
  Klipper splits into a Linux *host* (does motion planning) plus lightweight
  MCU firmware on the printer board. The host does not have to be a Pi — a
  spare laptop/PC, a mini PC, or an Android box can run it (commonly via the
  KIAUH installer). But *something* must be powered on and USB-connected to
  the printer for every print; the 4.2.2 board cannot host itself. Payoff is
  speed (input shaping, ~150–200 mm/s vs ~50–60 on stock Marlin). Source:
  general Klipper community guidance.
- **Decision: no Pi, no dedicated host machine on hand → Marlin, not
  Klipper.** Klipper's payoff exists only because of the host doing the math;
  without a host there is no Klipper, and stock-frame hobby printing does not
  need those speeds. Klipper stays available later if a host (e.g. an Android
  TV box) turns up.
- **mriscoc "Professional Firmware" is the chosen build.** Actively
  maintained, purpose-built for the Ender 3 V2/S1, ships pre-compiled `.bin`
  files (no self-compiling), and carries forward the enhanced Jyers-style UI
  the operator liked. Free. This is effectively where the Jyers lineage
  continued. Release used: `20260106`.
- **Board vs firmware must match.** 4.2.2 and 4.2.7 boards use different
  stepper drivers; firmware is not interchangeable. Only `422` builds are
  correct for this machine.
- **Chosen file:** `Ender3V2-422-MM-MPC-20260106.bin` (187 KB). Decode:
  `Ender3V2` printer, `422` board, `MM` manual mesh (correct for no-probe),
  `MPC` model-predictive temp control. The release did **not** ship a
  separate `T13` (Sprite-Pro-thermistor) binary despite the release-notes
  text; so temperature accuracy must be verified after flashing rather than
  assumed. `BLTUBL` variants are the BLTouch builds — the operator's *later*
  file once the probe is installed. SHA-256 leading chars on GitHub:
  `0dc34cf5…`.
- **Sprite Pro e-steps = ~424.9** (vs stock Bowden ~93). Documented value;
  must be set after flashing via menu or `M92 E424.9` + `M500`. Wrong e-steps
  after a direct-drive conversion cause under/over-extrusion that looks like
  generic "bad prints." Source: Sprite Pro install writeups.
- **Direct-drive retraction ≈ 1–2 mm** (vs Bowden ~5–6 mm). Cura profile must
  be updated or stringing/blobbing results.

## Card prep (procedure, and delegation decision)

- SD card: 8 GB reader showed a ~1.97 GB usable volume (likely a leftover
  small partition; irrelevant for a <200 KB firmware file). Formatted
  **FAT32, 4096-byte allocation**, label `V2`. A write-protect error traced
  to a daisy-chained double USB adapter; resolved by using a single adapter.
- Old card contents (obsolete Jyers `.bin`/`.cur` and old `.gcode` sliced for
  the pre-Sprite Bowden setup) treated as disposable — the old gcode is
  unsafe to reuse on the direct-drive machine anyway.
- **Delegation decision (2026-07-10):** a PowerShell helper
  (`prep_firmware_card.ps1`) was drafted to verify-hash-copy-eject, then
  **retired** in favor of handing the card copy to **Codex 5.6** as the local
  actor. Rationale: Codex already runs locally and fits the produce →
  download → local-agent workflow; hand-running a PS1 is the less efficient
  path. The PS1 is not part of the kept toolset.

## Current state

- Firmware `.bin` selected and downloaded; card formatted and ready.
- Not yet flashed at time of banking.

## Next actions (booked, not done)

1. Codex 5.6 copies `Ender3V2-422-MM-MPC-20260106.bin` to the card root
   (verify SHA-256 leading `0dc34cf5…`, single `.bin` in root, safe eject).
2. Flash: card into printer (power off first), power on, wait ~15 s for the
   mriscoc UI to confirm the flash took.
3. **Temp sanity check** — heat nozzle to 200 °C, confirm sane reading / no
   thermistor error. Stand-in for the absent T13 profile; the Sprite Pro
   thermistor may or may not match the stock profile.
4. Set **e-steps 424.9** (`M92 E424.9`, then `M500`).
5. Cura **retraction → ~1–2 mm** for direct drive.

## Open thread — the actual diagnosis (NOT yet started)

The original reason for all this — **print-quality symptoms** — has not been
examined. No symptom description or photo captured yet. The single-Z / no-ABL
hypothesis is now only one of several suspects; the Sprite Pro conversion
introduced two strong rivals: **wrong e-steps** (under/over-extrusion) and
**Bowden-length retraction** left in the Cura profile. Diagnosis should start
from observed symptoms once the firmware base is clean, not from the Z
assumption. Capture as new raw-intake in this dimension when it happens.
