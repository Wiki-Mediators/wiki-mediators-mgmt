---
name: "Prior Close Magnet Vol Filter"
tagline: "Trade intraday rotation toward the prior RTH close only in low-to-moderate volatility."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: prior close magnet behavior with volatility filter to avoid trend days."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:00-14:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "mean-reversion"
indicators: ["PriorRTHClose", "ATRZScore(20)", "ChoppinessIndex(14)", "VWAP"]
timeframes_used: ["1-minute", "5-minute", "daily"]

# Execution
brackets: "volatility-adaptive"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: null
implementation: null
related_candidates: ["gap_fill_pressure.md"]

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
  - mean-reversion
  - level-based
  - regime-conditional
---

# Prior Close Magnet Vol Filter

## 1. Thesis

The prior RTH close can act as a reference price when the current day
does not establish strong acceptance away from it. This candidate trades
rotation toward the prior close only when volatility and choppiness say
the session is not a strong trend day.

It is not a gap-fill strategy. It can trigger on any intraday deviation
from prior close, but only after the first 30 minutes.

## 2. Mechanism (what edge it captures)

- Uses prior RTH close as a structural magnet.
- Avoids high ATR z-score regimes where price may be repricing rather
  than rotating.
- Requires price to reject extension away from prior close.
- Uses VWAP only as a sanity check that the trade is not fighting a
  strong accepted trend.

## 3. Signal logic (entry conditions)

**Adaptive elements:**
- Level: prior RTH close.
- Regime gate: ATRZScore(20) between -0.5 and +0.75, and
  ChoppinessIndex(14) >= 50.

**Fixed elements:**
- Long setup: price is below prior close by at least 0.4 x ATR(20),
  then closes back above a 5-minute reversal high.
- Short setup: symmetric above prior close.
- Time window: 10:00-14:00 ET.

## 4. Exit logic (stops, targets, time-based exits)

**Adaptive elements:**
- Stop: beyond the rejection extreme.
- TP1: halfway to prior RTH close.
- TP2: prior RTH close.

**Fixed elements:**
- Time exit after 60 minutes.
- No runner beyond prior close.

## 5. Position sizing

Use fixed dollar risk divided by the distance to the rejection extreme,
capped by Apex limits.

## 6. Required indicators / data

Prior RTH close, ATRZScore(20), ChoppinessIndex(14), VWAP, 1-minute and
5-minute bars, and daily aggregation. Current MNQ data should support
these inputs.

## 7. Differentiation (vs already-tested strategies)

PRJ_3 traded local fractal pullbacks in the direction of a morning
trend. This candidate trades toward a prior-session anchor and only in a
rotational volatility regime. It differs from batch-1 Gap Fill Pressure
because the entry is not tied to the opening gap or first-15-minute
failure; it is a broader intraday prior-close magnet concept.

The adaptive elements are principled because prior close defines the
target and ATRZScore/Choppiness decide whether reversion is plausible.

## 8. Required research before spec drafting

- Define prior RTH close on half-days and holidays.
- Pre-commit ATRZScore and Choppiness bounds.
- Check whether prior-close magnetism is too weak after friction.
- Avoid selection bias from choosing volatility windows that rescue a
  small number of days.

## 9. Source / references

Prior close and settlement magnet concepts from futures trading
practice. No specific research backing is claimed.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch 2 (dynamic adaptive intraday focus). |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.4 R1-first triage applied (Phase A batch).** R1 evidence diagnostic measured mean-reversion-toward-prior-close rate on regime-gated bars (ATR-z ∈ [-0.5, +0.75] AND Choppiness ≥ 50). 88 regime-pass days; 55 qualifying events (27L/28S — balanced); **28 reverted 1R within 30min (50.9%)**, 18 hit stop first, 9 neither. Median 6.2 min to revert. **R1 verdict: NOT MET** at exactly the 50% null hypothesis rate — the mean-reversion-to-prior-close mechanism doesn't produce participant-behavior pattern above random. **First R1 closure at the "mechanism-is-coin-flip" boundary.** Adding a permissive vol regime gate to a generic mean-reversion mechanism does not create edge from nowhere. Candidate CLOSED at R1 gate. Diagnostic: `nb_lib/probe_results/prior_close_magnet_vol_filter_r1_diagnostic.json`. Combined Phase A closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_4_phase_a_closures.md`. |
