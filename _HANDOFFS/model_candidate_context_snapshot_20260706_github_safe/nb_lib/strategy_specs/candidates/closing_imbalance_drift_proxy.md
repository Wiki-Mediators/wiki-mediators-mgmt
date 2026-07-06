---
name: "Closing Imbalance Drift Proxy"
tagline: "Capture late-day continuation when institutions press into the close."
status: "untested-ideation"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: common institutional flow and late-day positioning concept; no actual imbalance feed used."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "14:00-15:58 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "momentum"
indicators: ["VWAP", "ATR(20) on 5-minute bars", "FiveMinuteSwingStructure"]
timeframes_used: ["1-second", "5-minute"]

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
  - late-day
  - momentum
  - atr-scaled
---

# Closing Imbalance Drift Proxy

## 1. Thesis

Late-day flows can be dominated by positioning, hedging, and closing
auction preparation. If the market trends steadily from 14:00 or 14:30
with shallow pullbacks, the final 30-60 minutes may continue in the same
direction.

This is only a proxy for closing imbalance behavior. It does not use
actual imbalance, order-flow, or auction data.

## 2. Mechanism (what edge it captures)

- Avoids early-session noise and focuses on late-day positioning.
- Requires price to hold on one side of VWAP.
- Requires measurable cumulative return before entry.
- Uses shallow-pullback structure to avoid late fades.

## 3. Signal logic (entry conditions)

From 14:00 to 15:15 ET, require price to stay above VWAP for longs or
below VWAP for shorts. Require cumulative return from 14:00 to 15:15 to
exceed 0.5 x ATR(20) on 5-minute bars. Require no 5-minute close through
VWAP during the trend qualification window.

Enter between 15:15 and 15:25 on a continuation break in the trend
direction.

## 4. Exit logic (stops, targets, time-based exits)

Stop behind the most recent 5-minute swing. TP is 1.0 x ATR(20) on
5-minute bars. Mandatory flat by the Apex EOD deadline, 15:58:30 ET.

## 5. Position sizing

Use fixed dollar risk. Initial research should likely use smaller risk
than morning systems because late-day reversals can be fast and the time
to recover is short.

## 6. Required indicators / data

MNQ 1-second bars, 5-minute bars, VWAP, 5-minute swing structure, and
ATR(20). All are available from the current MNQ store.

## 7. Differentiation (vs already-tested strategies)

The tested strategies entered between 9:30 and 11:10 and were mostly
morning direction or pullback concepts. This candidate shifts the edge
hypothesis to late-day participant behavior and forces flat by the Apex
deadline, with ATR-scaled targets instead of fixed brackets.

## 8. Required research before spec drafting

- Define swing structure mechanically and avoid discretionary pivots.
- Decide whether 14:00 or 14:30 is the start of the trend qualification
  window.
- Check half-day handling because close timing changes.
- Verify whether actual imbalance-free proxy has enough signal quality.
- Pre-commit behavior on catalyst afternoons and FOMC days.

## 9. Source / references

Institutional flow and late-day positioning concepts commonly discussed
by discretionary futures traders. No proprietary closing-imbalance feed
is assumed.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | untested-ideation | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch. |
| 2026-05-14 | `untested-ideation` | Phase 0 admissibility check: **INADMISSIBLE**. R2 (Apex survival), R3 (management lifecycle), R4 (signal-frequency tolerance) not met; R1 (edge thesis), R5 (direction handling) partially met. Candidate does not progress to Phase 1 in current form. Third of 3 inadmissible candidates in this Phase 0 batch (all rejected). See `nb_lib_phase0_closing_imbalance_drift_proxy.md`. |
