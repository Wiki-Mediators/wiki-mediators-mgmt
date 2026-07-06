---
name: "PDH/PDL Liquidity Sweep Reversal"
tagline: "Fade previous-day high/low stop sweeps only after reclaim/rejection with volume expansion."
status: "untested-ideation"
created: 2026-05-21
updated: 2026-05-21
source: "Operator-provided True Zone liquidity sweep transcript synthesis, 2026-05-21."

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-15:30 ET"
hold_duration: "intraday"

signal_type: "liquidity-sweep-reversal"
indicators: ["previous day high", "previous day low", "volume MA(20)", "VWAP optional"]
timeframes_used: ["1-second source", "1-minute derived"]

brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
  - "true_zone_liquidity_sweep_reference"
  - "opening_range_liquidity_sweep_reversal"
  - "round_number_vwap_liquidity_sweep_reversal"
  - "footprint_confirmed_supply_demand_reaction"
  - "wide_state_absorption_reversal"

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
  - support-resistance
  - previous-day-levels
  - volume-confirmation
  - ohclv-testable
---

# PDH/PDL Liquidity Sweep Reversal

## 0. Role In The Three-Strategy Liquidity-Sweep Batch

This is Strategy 1 of the OHLCV-first liquidity-sweep batch. It is the cleanest and most objective branch: previous day high and previous day low are externally visible levels, not fitted zones. The reason to test this first is methodological discipline, not preference. It minimizes discretionary zone marking and gives the R4 probe a simple question: do prior-day liquidity sweeps with volume-confirmed reclaim/rejection occur often enough to trade?

## 1. Thesis

Previous day high and previous day low are obvious liquidity levels. Traders place breakout orders around them and protective stops beyond them. This candidate does not buy PDL support or short PDH resistance immediately. It waits for price to sweep the obvious liquidity, reclaim/reject the level, and confirm the reversal with volume expansion.

Long thesis: if price sweeps below previous day low, then closes back above it on elevated volume, the stop hunt may be complete and buyers may be absorbing the forced selling.

Short thesis: if price sweeps above previous day high, then closes back below it on elevated volume, the stop hunt may be complete and sellers may be absorbing the forced buying.

Counter-hypothesis: MNQ often sweeps PDH/PDL as continuation, not reversal. The volume spike may identify continuation participation rather than exhaustion.

## 2. Mechanism

- PDH/PDL are objective, widely watched levels.
- Stops and breakout orders cluster around those levels.
- A sweep forces liquidity into the market.
- Reclaim/rejection indicates the breakout did not hold.
- Volume expansion on the reclaim/rejection is the confirmation that the response has real participation.

## 3. Entry Logic

Use 1-minute bars derived from the 1-second OHLCV store. The setup is two-sided.

Long at previous day low:

- Compute previous regular-session high/low from the prior trading day.
- Current 1-minute bar trades below PDL by at least 2 ticks.
- Sweep depth is no more than a pre-committed maximum, likely 20 ticks, to avoid catching runaway breakdowns.
- The bar closes back above PDL.
- The reclaim bar is bullish or closes in the upper half of its range.
- Reclaim bar volume is at least `1.5 * SMA(volume, 20)` on 1-minute bars.
- Entry is a stop-market at reclaim bar high plus one tick, armed after bar close.
- Stop is sweep low minus one tick.

Short at previous day high:

- Current 1-minute bar trades above PDH by at least 2 ticks.
- Sweep depth is no more than a pre-committed maximum, likely 20 ticks.
- The bar closes back below PDH.
- The rejection bar is bearish or closes in the lower half of its range.
- Rejection bar volume is at least `1.5 * SMA(volume, 20)`.
- Entry is a stop-market at rejection bar low minus one tick, armed after bar close.
- Stop is sweep high plus one tick.

One trade per level per day. Maximum two trades per day.

## 4. Exit Logic

Initial test candidates:

- Fixed 2R target.
- VWAP target.
- Previous day midpoint target.

The first FINAL spec should choose one baseline, probably fixed 2R, before any P&L test. Adaptive management and footprint upgrades are later variants.

## 5. Position Sizing And Apex Survival Rationale

Use fixed-risk-dollar sizing. The likely starting risk is $300 per trade with a contract cap. Stop distance is structural: entry to sweep wick plus one tick. A stop-band guard is required because deep sweeps can create oversized risk.

The Apex concern is cluster loss around trend days. If PDH/PDL sweeps frequently continue, this strategy can lose twice per day and fail quickly. The first R4 probe should log sweep counts, reclaim counts, volume-confirmed counts, stop distances, and same-day clustering before any FINAL spec.

## 6. Required Indicators / Data

This candidate is OHLCV-testable.

Required:

- MNQ 1-second OHLCV.
- Derived 1-minute OHLCV.
- Prior trading day's RTH high and low.
- 1-minute volume SMA(20).
- Optional later additions: VWAP, opening range, round numbers, footprint delta.

No real footprint data is required for the first version.

## 7. Differentiation

This differs from `footprint_confirmed_supply_demand_reaction` because it uses one objective level family, PDH/PDL, and basic volume confirmation. It is intentionally narrower and more testable.

It differs from generic support/resistance by requiring a sweep first. The point is not "price touched support"; the point is "price swept the obvious stops and failed to continue."

It differs from `wide_state_bvc_proxy_divergence_reversal` because it uses explicit market structure levels and real OHLCV volume, not BVC participation estimates.

## 8. Required Research Before Spec Drafting

- R4 v1.2 probe: count PDH/PDL sweeps, reclaim/rejection events, and volume-confirmed entries over 20 trading days.
- Stop-distance distribution: does the sweep-wick stop fit Apex sizing?
- Time-of-day distribution: are signals concentrated near the open or later retests?
- Direction balance: are PDH shorts and PDL longs both present?
- Continuation failure mode: how often does price reclaim/reject and then immediately resume through the swept level?

## 9. Source / References

Source is the operator's 2026-05-21 transcript synthesis. The idea is trader-art liquidity sweep logic made testable by restricting the first version to objective previous-day high/low levels and OHLCV volume confirmation.

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-21 | untested-ideation | Candidate authored from True Zone liquidity sweep transcript. First recommended version is PDH/PDL sweep + reclaim/rejection + volume spike, because it is objective and OHLCV-testable. |
| 2026-05-21 | untested-ideation | Assigned as Strategy 1 of three OHLCV-first liquidity-sweep candidates. Siblings: opening-range sweep and round-number/VWAP confluence sweep. |
| 2026-05-24 | untested-ideation | R4 v1.2 probe completed: 5 structural signals, 3 valid fill-guard-passing entries over 23 trading days; sparse classification. Report: `C:/VMShare/NT8lab/nb_lib_pdh_pdl_liquidity_sweep_reversal_r4_probe_report.md`. JSON: `nb_lib/probe_results/pdh_pdl_liquidity_sweep_reversal_r4_probe.json`. |
