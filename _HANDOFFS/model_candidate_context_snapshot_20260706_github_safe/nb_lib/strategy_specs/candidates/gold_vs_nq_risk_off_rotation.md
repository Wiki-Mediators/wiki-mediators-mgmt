---
name: "Gold-vs-NQ Risk-Off Rotation"
tagline: "Trade NQ only when gold confirms risk-off or risk-on pressure."
status: "untested-ideation"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: intermarket analysis and macro risk-rotation frameworks."

# Market and timing
markets: ["MNQ", "MGC"]
session: "RTH"
time_of_day: "10:00-14:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "cross-asset-confirmation"
indicators: ["VWAP", "ATR(20) on 5-minute bars", "ThirtyMinuteHighLow"]
timeframes_used: ["1-minute", "5-minute"]

# Execution
brackets: "atr-scaled"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: null
implementation: null
related_candidates: []

# Test status (only populated when status >= tested-*)
test_results:
  in_sample_n: null
  in_sample_pnl_dollars: null
  in_sample_pf: null
  in_sample_win_rate: null
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: null

# Tags for organization (recommended controlled vocabulary in README)
tags:
  - rth-only
  - intraday
  - cross-asset
  - macro
  - data-acquisition-required
---

# Gold-vs-NQ Risk-Off Rotation

## 1. Thesis

Equity index futures sometimes respond to macro risk appetite. Gold can
act as a cross-asset confirmation input during risk-off or risk-on
episodes. Instead of using NQ alone, this candidate waits for MGC to
confirm the macro direction.

The strategy trades MNQ only; MGC is an input, not a hedging leg.

## 2. Mechanism (what edge it captures)

- Uses gold as a macro confirmation filter.
- Avoids isolated MNQ moves that lack cross-asset confirmation.
- Looks for MNQ breakdowns with gold strength or MNQ strength with gold
  weakness.
- Exits if cross-asset confirmation disappears.

## 3. Signal logic (entry conditions)

Use MNQ and MGC 5-minute bars. Risk-off short MNQ: MNQ below VWAP, MGC
above VWAP, MGC making a 30-minute high, and MNQ breaking a 30-minute
low. Risk-on long MNQ is the reverse condition.

Trade only from 10:00 to 14:30 ET to avoid the noisiest open and the
late close.

## 4. Exit logic (stops, targets, time-based exits)

Stop is 1.0 x ATR(20) on MNQ 5-minute bars. TP1 is 1.0 x ATR. TP2 is
2.0 x ATR. Exit early if the cross-asset confirmation disappears by the
pre-committed definition.

## 5. Position sizing

Use fixed MNQ dollar risk based on the MNQ stop distance, capped by Apex
contract limits. No gold position is opened.

## 6. Required indicators / data

MNQ and MGC 1-minute or 5-minute bars, VWAP for both instruments,
30-minute highs/lows, and MNQ ATR. MGC data is not currently in the
project store and requires acquisition before testing.

## 7. Differentiation (vs already-tested strategies)

The tested strategies were MNQ-only and used only MNQ intraday
structure. This candidate requires independent cross-asset confirmation
from gold and is meant to trade macro-rotation days rather than ordinary
MNQ morning breakouts or pullbacks.

## 8. Required research before spec drafting

- **GC data status (updated 2026-05-12):** GC daily data IS
  present at `databento/GC/ohlcv-1d/` (468 daily rows,
  2024-07-31 → 2026-04-13). Daily resolution only — intraday
  GC NOT in store. The store contains full-size `GC.c.0`, not
  `MGC` (micro gold); usable as a proxy with tick-size
  differences accounted for in execution modeling.
- **Implication:** if the strategy's edge can be expressed at
  daily resolution (e.g., end-of-day gold-rotation signals),
  proceed without further data acquisition. If intraday gold
  behavior matters (e.g., morning rotation reactions), Stage 0
  prerequisite: acquire intraday GC or MGC data via Databento.
- **Library blocker:** no `load_gc_1d()` helper exists in nb_lib.
  Strategy-local loader required at minimum.
- Define what counts as confirmation disappearing.
- Test whether gold-equity relationship is stable enough over the
  research window.
- Decide whether inflation-shock days where gold and equities move
  together should be excluded or handled separately.

## 9. Source / references

Intermarket analysis and macro risk-rotation frameworks. The gold-equity
relationship is unstable, so this is a hypothesis, not a proven edge.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | untested-ideation | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch. |
| 2026-05-12 | untested-ideation | 2026-05-12: GC daily data confirmed present; intraday GC still blocked. Operator decision needed on whether daily resolution is sufficient for the strategy. |
