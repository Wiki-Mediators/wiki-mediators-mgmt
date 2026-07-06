---
name: "Lunch Compression Break"
tagline: "Trade post-lunch expansion after volatility compresses."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: volatility contraction and expansion logic related to range-expansion trading concepts."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "11:45-15:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "volatility-expansion"
indicators: ["RealizedRange", "VolumeSMA(20)", "VWAP", "ATR(20) on 5-minute bars"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "volatility-adaptive"
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
  - volatility-expansion
  - midday
  - fixed-risk-dollar
---

# Lunch Compression Break

## 1. Thesis

Midday often compresses range and volume. When volatility contracts
enough, the next directional expansion can be cleaner than the open
because the market has already established session context.

This candidate avoids the noisy opening window entirely and asks whether
post-lunch expansion from a compressed box has better signal quality than
morning breakout attempts.

## 2. Mechanism (what edge it captures)

- Defines a midday compression box from 11:45 to 13:15 ET.
- Requires compression relative to the morning realized range.
- Enters only after a close outside the compressed range.
- Uses volume confirmation to avoid the thinnest false breaks.

## 3. Signal logic (entry conditions)

Compute the realized 1-minute range from 11:45 to 13:15 ET. Require
that range to be below 0.6 x the morning realized range. Long when price
closes above the compression high with volume above the 20-period
1-minute average. Short when price closes below the compression low with
the same volume condition.

Optional research filter: only trade long when price is above VWAP and
short when price is below VWAP.

## 4. Exit logic (stops, targets, time-based exits)

Stop inside the compression box at the opposite side, or at 1.0 x
ATR(20) on 5-minute bars if that is tighter after pre-commitment. TP1 is
1.0 x box height. TP2 is 2.5 x box height. Time exit by 15:30 ET.

## 5. Position sizing

Use fixed dollar risk based on the box-defined stop distance, capped by
Apex contract limits.

## 6. Required indicators / data

MNQ 1-second bars, 1-minute OHLCV and volume, VWAP, 5-minute ATR, and a
morning realized-range calculation. Current MNQ data should support all
inputs.

## 7. Differentiation (vs already-tested strategies)

The tested strategies concentrated on 9:30-11:10 ET and used directional
or breakout-style entries without a compression prerequisite. This
candidate shifts the time window to midday, makes volatility contraction
the setup condition, and sizes risk from the compressed box rather than
fixed 15-contract brackets.

## 8. Required research before spec drafting

- Define morning range and compression range calculations exactly.
- Decide whether VWAP-side filter is mandatory or optional.
- Establish minimum box height to avoid micro-chop entries.
- Verify volume data reliability in the Databento OHLCV store.
- Check signal count before considering OOS use.

## 9. Source / references

Volatility contraction and range expansion concepts, related in spirit
to Toby Crabel-style range ideas. No specific edge claim is made.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | untested-ideation | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch. |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.4 R1-first triage applied (Phase A batch).** R1 evidence diagnostic measured post-compression continuation rate on days where compression range (11:45-13:15 ET) < 0.6 × morning range. 77 compression-pass days; 46 qualifying break events (28L/18S); **only 3 continued 1R within 30min (6.5%)**, 1 stop, **42 neither (91%)**. Median time to continue: 27.4 min. **R1 verdict: NOT MET — strongest lookahead-window mismatch case yet documented.** The compression-break mechanism resolves on a 90+ min timeframe; the 30-min lookahead captures only the leading edge. **Methodology learning**: this is the third candidate exhibiting lookahead bias (after FLRD 31% neither, APTH 25% neither). Per v1.4 HARD-HALT-POST-HOC-TUNING discipline, the 30-min lookahead remains pinned; per-class lookahead specification is documented as v1.5 priority. Candidate CLOSED at R1 gate. Diagnostic: `nb_lib/probe_results/lunch_compression_break_r1_diagnostic.json`. Combined Phase A closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_4_phase_a_closures.md`. |
