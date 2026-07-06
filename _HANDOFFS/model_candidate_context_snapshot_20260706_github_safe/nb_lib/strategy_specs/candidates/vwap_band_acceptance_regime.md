---
name: "VWAP Band Acceptance Regime"
tagline: "Continue only when price accepts outside a VWAP band in a trending volatility regime."
status: "untested-ideation"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: VWAP band acceptance combined with volatility-regime filtering."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:00-14:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "level-acceptance"
indicators: ["VWAP", "SessionStdev", "ATRPercentile(60 sessions)", "ChoppinessIndex(14)"]
timeframes_used: ["1-minute", "5-minute"]

# Execution
brackets: "atr-scaled"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: null
implementation: null
related_candidates: ["vwap_stretch_snapback.md"]

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
  - trend-continuation
  - vwap-anchored
  - regime-conditional
---

# VWAP Band Acceptance Regime

## 1. Thesis

VWAP bands can either mark stretched mean-reversion zones or accepted
trend territory. This candidate tests the second interpretation: when a
directional volatility regime is present, acceptance outside the 1.5
stdev VWAP band may signal continuation rather than snapback.

It combines a level reference (VWAP band) with a volatility-regime gate
so the strategy does not blindly buy high or sell low in rotational
sessions.

## 2. Mechanism (what edge it captures)

- Uses VWAP plus session stdev as an adaptive intraday level.
- Requires acceptance outside the band, not just a wick through it.
- Filters for movement capacity and trend structure before treating the
  band as continuation.
- Uses ATR-scaled exits because band width and ATR may diverge intraday.

## 3. Signal logic (entry conditions)

**Adaptive elements:**
- Level: VWAP +/- 1.5 x rolling session stdev.
- Regime gate: ATRPercentile(60 sessions) >= 0.60 and
  ChoppinessIndex(14) < 40.

**Fixed elements:**
- Long entry: two consecutive 5-minute closes above the upper VWAP band,
  followed by a 1-minute pullback that holds above the band.
- Short entry: symmetric below the lower VWAP band.
- Time window: 10:00-14:30 ET.

## 4. Exit logic (stops, targets, time-based exits)

**Adaptive elements:**
- Stop: back inside the VWAP band by 2 ticks.
- TP1: 1.0 x ATR(20) on 5-minute bars.
- TP2: 2.0 x ATR(20) on 5-minute bars.

**Fixed elements:**
- BE arm after TP1.
- EOD flat.

## 5. Position sizing

Use fixed dollar risk based on the distance from entry to the band
invalidation stop, capped by Apex limits.

## 6. Required indicators / data

VWAP, rolling session stdev, ATRPercentile over 60 sessions,
ChoppinessIndex(14), ATR(20), 1-minute and 5-minute bars. Current MNQ
data and nb_lib indicators should support this.

## 7. Differentiation (vs already-tested strategies)

PRJ_3 used fractal pullback levels and entered after proximity to a
local swing. This candidate uses VWAP bands and requires acceptance
outside the band under a specific volatility regime. It also differs
from batch-1 VWAP Stretch Snapback: that candidate fades stretched
price back to VWAP, while this one follows accepted movement away from
VWAP only when volatility and choppiness support trend.

The adaptive elements are principled: VWAP bands define structural
acceptance, while ATRPercentile and Choppiness decide whether acceptance
should be interpreted as continuation rather than exhaustion.

## 8. Required research before spec drafting

- Pre-commit VWAP band width and stdev calculation.
- Check whether the regime gate leaves enough samples.
- Decide whether band invalidation stop is too tight in fast regimes.
- Guard against curve-fit risk from combining both band and regime
  thresholds.

## 9. Source / references

VWAP band acceptance and volatility-regime filtering from common
intraday trading practice. No specific performance claim is made.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch 2 (dynamic adaptive intraday focus). |
| 2026-05-14 | `phase-0-inadmissible` | Phase 0 admissibility check completed. Verdict: INADMISSIBLE. R2 (Apex survival thesis) and R4 (signal-frequency tolerance) are NOT MET; R1 (edge thesis), R3 (management lifecycle compatibility), and R5 (direction handling) are PARTIALLY MET. Two principal gaps: (a) wiki does not address why the closest relative vwap_stretch_snapback Apex failure (account FAILED in-sample 2024-10-14) would not recur on the same VWAP-band scaffolding, and Section 8 explicitly defers band-invalidation stop sizing in fast regimes; (b) wiki defers signal-frequency expectation to Section 8 research with no committed count range. Candidate remains `untested-ideation`; no Phase 1 preflight, no spec drafting. Report at `C:/VMShare/NT8lab/nb_lib_phase0_vwap_band_acceptance_regime.md`. Joins the four-Phase-0-INADMISSIBLE pattern (mnq_news_like, closing_imbalance, mhw, this) where R4 fails in every case and R2 fails in three of four. |
