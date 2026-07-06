---
name: "Opening Range Liquidity Sweep Reversal"
tagline: "Fade failed sweeps of the opening range after reclaim/rejection with volume expansion."
status: "phase-0-inadmissible-closed"
created: 2026-05-21
updated: 2026-05-21
source: "Operator request 2026-05-21 to build three liquidity-sweep strategies from True Zone transcript plus project lessons."

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-12:00 ET"
hold_duration: "intraday"

signal_type: "liquidity-sweep-reversal"
indicators: ["opening range high", "opening range low", "volume MA(20)", "VWAP optional"]
timeframes_used: ["1-second source", "1-minute derived"]

brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
  - "true_zone_liquidity_sweep_reference"
  - "pdh_pdl_liquidity_sweep_reversal"
  - "opening_range_width_switch"
  - "round_number_vwap_liquidity_sweep_reversal"

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

tags:
  - rth-only
  - intraday
  - liquidity-sweep
  - opening-range
  - volume-confirmation
  - ohclv-testable
---

# Opening Range Liquidity Sweep Reversal

## 0. Role In The Three-Strategy Liquidity-Sweep Batch

This is Strategy 2 of the OHLCV-first liquidity-sweep batch. It uses the opening range as the objective zone instead of prior-day levels. The project has learned that broad zone frameworks become too discretionary, while opening-range mechanics can be counted cleanly and compared across months.

The opening range is also a good test of the transcript's central point: the obvious level is not the entry; the failed sweep and volume-confirmed reclaim/rejection is the entry.

## 1. Thesis

Opening range high and low are obvious intraday levels. Breakout traders chase them, and short-term traders place stops just beyond them. This candidate waits for price to sweep an opening-range extreme, fail to hold beyond it, then enter in the reversal direction only if volume confirms the failed break.

Long thesis: a sweep below opening range low followed by a reclaim on elevated volume may indicate that sellers were trapped and the stop run is complete.

Short thesis: a sweep above opening range high followed by rejection on elevated volume may indicate that buyers were trapped and the stop run is complete.

Counter-hypothesis: opening range sweeps are continuation events on trend days. Fading them may reproduce the failed wide-reversal pattern unless the volume/reclaim filter is strong.

## 2. Mechanism

- The first 15 minutes establish an obvious intraday range.
- Breakout traders and stops cluster just beyond ORH/ORL.
- A sweep through the range edge triggers liquidity.
- Reclaim/rejection back inside the range shows the breakout failed.
- Volume expansion confirms the response is more than passive drift.

## 3. Entry Logic

Use 1-minute bars derived from the 1-second OHLCV store.

Opening range definition:

- OR window: 09:30:00-09:45:00 ET.
- `ORH = max(high)` over the window.
- `ORL = min(low)` over the window.
- Entries begin only after the OR window is complete.

Long ORL sweep:

- Price trades below ORL by at least 2 ticks.
- Sweep depth is no more than a pre-committed maximum, likely 20 ticks.
- The same or later 1-minute bar closes back above ORL.
- Reclaim candle closes in the upper half of its range.
- Reclaim candle volume >= `1.5 * SMA(volume, 20)`.
- Entry stop is reclaim candle high + 1 tick.
- Stop is sweep low - 1 tick.

Short ORH sweep:

- Price trades above ORH by at least 2 ticks.
- Sweep depth is no more than a pre-committed maximum, likely 20 ticks.
- The same or later 1-minute bar closes back below ORH.
- Rejection candle closes in the lower half of its range.
- Rejection candle volume >= `1.5 * SMA(volume, 20)`.
- Entry stop is rejection candle low - 1 tick.
- Stop is sweep high + 1 tick.

Pre-commit one trade per side per day, maximum two trades per day.

## 4. Exit Logic

First spec should choose one simple baseline before P&L:

- Fixed 2R target.
- OR midpoint target.
- VWAP target.

The likely first test is fixed 2R because it avoids target-shape overfitting and lets the sweep entry stand or fall on its own.

## 5. Position Sizing And Apex Survival Rationale

Use fixed-risk-dollar sizing. Likely starting risk is $300 per trade with a 12-contract cap and stop-band guard. Because opening-range sweeps can cluster on noisy days, a daily realized-loss cap of two is part of the candidate identity.

Stop-band lesson from recent work: use `[5, 50]` only if actual R4 stop distribution needs it. If OR sweeps are tighter, prefer `[5, 35]` to avoid wide-bar Apex damage.

## 6. Required Indicators / Data

This candidate is OHLCV-testable:

- MNQ 1-second OHLCV.
- Derived 1-minute OHLCV.
- Opening range high/low.
- 1-minute volume SMA(20).
- Optional later VWAP filter.

No footprint data is required for the first version.

## 7. Differentiation

This differs from `opening_range_width_switch`, which tested the range width as a regime switch. Here, opening range is a liquidity level, not a volatility classifier.

It differs from `pdh_pdl_liquidity_sweep_reversal` because it uses intraday levels that every session creates. That likely increases signal frequency, but also raises overtrading risk.

## 8. Required Research Before Spec Drafting

- R4 v1.2 probe for ORH/ORL sweeps, reclaim/rejection events, and volume-confirmed entries.
- Stop-distance distribution and fill drift.
- Signal density by day; reject if it becomes round-number-style overactive.
- Compare 5-minute OR, 15-minute OR, and 30-minute OR only if pre-authorized; default is 15-minute OR.

## 9. Source / References

Source is the operator's True Zone liquidity-sweep transcript synthesis plus project lessons from chop-fade sparsity, round-number overactivity, and wide-state Apex failures.

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-21 | untested-ideation | Strategy 2 of three OHLCV-first liquidity-sweep candidates. Objective opening-range level, sweep/reclaim, volume confirmation. Awaiting R4 probe before spec drafting. |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.4 R1-first triage applied (first post-formalization application).** R1 evidence diagnostic over 127 in-sample days measured OR sweep-and-reclaim-with-volume reversion rate. **225 raw ORL sweeps + 225 ORH sweeps; 19 qualified after sweep-depth + reclaim + volume×1.5 filters (4.2% pass rate); 10 reverted 1R within 30min = 52.6% — NOT MET.** Direction: long 63.6% (7/11), short 37.5% (3/8); 0% neither (fast resolution, median 2.2min). **Striking finding: 26.9pp BELOW ORWS R1 (79.5%) — the sweep+reclaim+volume filters REDUCED empirical edge instead of improving it.** The wiki's own counter-hypothesis ("volume/reclaim filter is strong unless OR sweeps are continuation events on trend days") is empirically vindicated: volume spike on OR-reclaim likely correlates with continuation participation, not exhaustion. **Candidate CLOSED at R1 gate** — no R4 probe, no FINAL spec, no implementation. v1.4 R1-first triage saved ~6-10h downstream pipeline. 14-pattern update; third consecutive R1-gate closure. **Methodology learning**: filter-augmented variants of working mechanisms can have WORSE empirical edge than the base. Liquidity-sweep family (pdh_pdl R4-sparse, opening_range R1-NOT-MET) hypothesis needs revision before round_number_vwap variant is pursued. Diagnostic: `nb_lib/probe_results/opening_range_liquidity_sweep_reversal_r1_diagnostic.json`. Closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_4_opening_range_liquidity_sweep_reversal_closure.md`. |
