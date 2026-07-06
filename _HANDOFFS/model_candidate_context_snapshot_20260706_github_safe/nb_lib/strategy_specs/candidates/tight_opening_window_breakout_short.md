---
name: "Tight-State Opening-Window Breakout Short"
tagline: "Short tight-state continuation triggers across the first RTH hour instead of only bar one."
status: "untested-ideation"
created: 2026-05-17
updated: 2026-05-17
source: "Operator direction 2026-05-17; structural scanner redesign of tight/wide-state transcript family after first-bar R4 sparsity."

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-10:30 ET"
hold_duration: "intraday"

signal_type: "trend-continuation"
indicators: ["SMA(20) 2-min", "SMA(200) 2-min", "ATR(14) 2-min"]
timeframes_used: ["1-second source", "2-minute derived"]

brackets: "fixed-R baseline for R4; targets deferred to spec"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates: ["tight_open_breakout_short", "tight_opening_window_breakout_long"]

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

admissibility:
  r2_apex_survival:
    risk_dollars_per_trade: 300
    expected_stop_distance_pts_range: [11, 33]
    expected_loss_dollars_per_trade: 300
    worst_plausible_cluster_n: 5
    worst_plausible_cluster_dollars: 1500
    cluster_vs_floor_ratio: 0.75
    favorable_first_week_independent: false
  r4_signal_frequency:
    probe_convention_version: "v1.2"
    probe_script: "nb_lib/scripts/probe_r4_tight_opening_window_breakout_short.py"
    probe_output: "nb_lib/probe_results/tight_opening_window_breakout_short_r4_probe.json"
    probe_window_start: "2024-09-09"
    probe_window_end: "2024-10-04"
    probe_n_signals_observed: 7
    probe_signals_passing_fill_guards: 7
    probe_attrition_rate: 0.0
    probe_median_drift_pts: 2.75
    probe_p95_drift_pts: 6.05
    probe_low_confidence_attrition: false
    probe_n_long: 0
    probe_n_short: 7
    probe_distinct_days_with_signal: 3
    expected_signals_per_60_trading_days: [11, 45]
    extrapolated_signals_per_60_trading_days: [11, 45]
    sparsity_class: "sparse"
    sparsity_class_rationale: "7 passing signals over 19 trading days; chop-fade-style sparsity risk."

tags:
  - rth-only
  - intraday
  - opening-window
  - two-minute
  - trend-continuation
  - scanner
  - template-v2
---

# Tight-State Opening-Window Breakout Short

## 0. Admissibility summary

- **R1 (edge thesis)**: This is the short-side structural redesign of the first-bar tight breakout. It scans completed 2-minute bars from 09:30 to 10:30 ET for bearish acceptance below a compressed SMA20/SMA200 cluster, capped at six signals per day.
- **R2 (Apex survival)**: Uses fixed-risk-dollar sizing at $300 per trade. Expected stop range is 11-33 points from the R4 fill-geometry probe. A five-loss cluster equals $1500, 0.75 of the Apex 50K EOD $2K drawdown floor. Favorable-first-week independence is false.
- **R3 (management lifecycle)**: No adaptive management is included. This candidate is an entry scanner only; exits are fixed-R/time-based placeholders until a FINAL spec chooses one.
- **R4 (signal frequency)**: R4 v1.2 probe on 19 trading days fired 7 structural signals and 7 fill-guard-passing signals. Extrapolated 60-day range: [11, 45]. Sparsity class: sparse. Cap diagnostics are recorded in the probe JSON.
- **R5 (direction handling)**: This is direction-restricted by design because the transcript decomposition splits long and short mechanics. The paired inverse candidate is authored separately; direction asymmetry is not a post-result optimization within this entry.

## 1. Thesis

This is the short-side structural redesign of the first-bar tight breakout. It scans completed 2-minute bars from 09:30 to 10:30 ET for bearish acceptance below a compressed SMA20/SMA200 cluster, capped at six signals per day.

Counter-hypothesis: the first-hour scan may simply turn one trader-art idea into repeated entries during noisy opening flow. The R4 probe only shows that signals exist; it does not show edge, Apex survivability under realized fills, or management quality.

## 2. Mechanism (what edge it captures)

- Tight SMA20/SMA200 compression can resolve lower after the first RTH bar.
- A bearish elephant or topping-tail bar below the compressed cluster marks seller acceptance.
- The bounded scanner tests whether morning continuation exists without forcing all evidence into the 09:30 candle.

## 3. Signal logic (entry conditions)

**Pre-committed predicates for this wiki entry:**

- Build 2-minute bars from MNQ 1-second OHLCV.
- Scan completed bars from 09:30 through 10:30 ET.
- Require abs(SMA20 - SMA200) / ATR14 <= 0.25.
- Require close < SMA20 and close < SMA200.
- Require bear_elephant or bear_topping_tail.
- Signal fires after bar completion; stop-market proxy uses signal_ts + 1 second.
- Entry reference is trigger low - 0.25 point; stop anchor is trigger high + 0.25 point.
- Accept no more than six structural signals per day.

Common bar anatomy:

- `bar_range = high - low`
- `body = abs(close - open)`
- `close_location = (close - low) / bar_range`
- Bull elephant: green bar, body/ATR14 >= 0.40, range/ATR14 >= 0.75, close_location >= 0.70.
- Bear elephant: red bar, body/ATR14 >= 0.40, range/ATR14 >= 0.75, close_location <= 0.30.
- Bottoming/topping tail: wick >= 50% of bar range with close in the correct side of the range.

## 4. Exit logic (stops, targets, time-based exits)

Initial stop is structurally anchored to the trigger bar plus one MNQ tick. The R4 probe uses a fixed 1.5R target only as a fill-geometry guard; this is not a FINAL spec target commitment.

Spec drafting must choose one baseline exit before any P&L test: fixed-R target, close after 20-30 minutes, or SMA-touch/midpoint target for wide-state reversal variants.

## 5. Position sizing and Apex survival rationale

Risk is fixed at $300 per trade. Contract count at spec stage should be `floor(300 / (stop_pts * 2))`, bounded by Apex 50K limits and a pre-committed max-contract cap.

The Apex survival thesis is still weak until P&L is tested. The scanner solves the first-bar count problem, but it can also cluster multiple same-day losses. The six-signal daily cap is therefore part of the candidate identity, not a convenience toggle.

## 6. Required indicators / data

- MNQ 1-second OHLCV from Databento store.
- Derived 2-minute OHLCV bars.
- SMA(20), SMA(200), ATR(14) on 2-minute bars.
- No news, scanner, order-flow, bid/ask, or Level II dependency.

## 7. Differentiation (vs already-tested strategies)

This is not a parameter tweak of tight_open_breakout_short. It changes the sampling unit from one opening bar to a first-hour state scanner. It remains continuation-class and therefore inherits skepticism from the 9-fleet, but the signal-frequency failure of the first-bar version is directly addressed.

The first-bar predecessor produced too few signals on MNQ. This entry is the explicit structural correction: a completed-bar opening-window scanner with a hard daily cap.

## 8. Required research before spec drafting

R2 and R4 are not deferred: they are quantified in frontmatter from the R4 probe.

Spec-stage research only:

- Decide whether 2-minute SMA/ATR history should be ETH-inclusive or RTH-only.
- Decide baseline exit mode before any P&L test.
- Decide whether repeated same-direction entries on the same day are independent enough to trade or should be collapsed by position state.
- Decide whether long/short paired candidates should be evaluated separately or as one two-sided family after Phase 0.

## 9. Source / references

Source is operator transcript decomposition plus the 2026-05-17 R4 finding that first-bar-only translation was too sparse. This candidate goes beyond folklore by making the scanner predicates mechanical and running an R4 v1.2 signal-frequency probe. It has not been Phase 0 evaluated, spec drafted, implemented, or P&L tested.

Probe caveats: 2-minute bars are derived from MNQ 1-second data; this is a new primary timeframe for the project. R4 probe uses v1.2 current local convention. This is a structural redesign of the first-bar family: scans completed 2-minute bars from 09:30 to 10:30 ET. Stop/target guards are generic R4 geometry guards, not a FINAL spec. Stop-market trigger is approximated as fill at signal_ts + 1 second per R4 convention.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-17 | `untested-ideation` | Authored under template v2 as structural scanner redesign of first-bar tight/wide family. R4 v1.2 probe: 7 fired, 7 passing fill guards, sparsity sparse. R4 needs review: sparsity class sparse. |
