---
name: "Tight-State Opening Breakout Long"
tagline: "Buy a first 2-minute RTH breakout when SMA20 and SMA200 are compressed."
status: "untested-ideation"
created: 2026-05-17
updated: 2026-05-17
source: "Operator transcript decomposition 2026-05-17; tight/wide state trader-art family adapted from equities to MNQ."

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-09:50 ET"
hold_duration: "intraday"

signal_type: "trend-continuation"
indicators: ["SMA(20) 2-min", "SMA(200) 2-min", "ATR(14) 2-min"]
timeframes_used: ["1-second source", "2-minute derived"]

brackets: "fixed-R baseline for R4; targets deferred to spec"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates: ["tight_open_breakout_short", "tight_problem_bar_removal_long"]

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
    expected_stop_distance_pts_range: [25, 26]
    expected_loss_dollars_per_trade: 300
    worst_plausible_cluster_n: 5
    worst_plausible_cluster_dollars: 1500
    cluster_vs_floor_ratio: 0.75
    favorable_first_week_independent: false
  r4_signal_frequency:
    probe_convention_version: "v1.2"
    probe_script: "nb_lib/scripts/probe_r4_tight_open_breakout_long.py"
    probe_output: "nb_lib/probe_results/tight_open_breakout_long_r4_probe.json"
    probe_window_start: "2024-09-09"
    probe_window_end: "2024-10-04"
    probe_n_signals_observed: 1
    probe_signals_passing_fill_guards: 1
    probe_attrition_rate: 0.0
    probe_median_drift_pts: 10.75
    probe_p95_drift_pts: 10.75
    probe_low_confidence_attrition: true
    probe_n_long: 1
    probe_n_short: 0
    probe_distinct_days_with_signal: 1
    expected_signals_per_60_trading_days: [1, 7]
    extrapolated_signals_per_60_trading_days: [1, 7]
    sparsity_class: "sparse"
    sparsity_class_rationale: "1 passing signals over 19 trading days; chop-fade-style sparsity risk."

tags:
  - rth-only
  - intraday
  - opening-window
  - two-minute
  - trend-continuation
  - fixed-risk-dollar
  - template-v2
---

# Tight-State Opening Breakout Long

## 0. Admissibility summary

- **R1 (edge thesis)**: When the 20-period and 200-period SMAs on 2-minute MNQ bars are tightly compressed at the RTH open, the first directional opening bar can represent balance breaking into expansion. The long version requires the first RTH 2-minute bar to close above both SMAs and print a bullish elephant or bottoming-tail trigger, then enters on a stop above that bar. The source is a stocks-derived trader-art opening-bar pattern adapted to MNQ, not an empirically validated MNQ edge.
- **R2 (Apex survival)**: Uses fixed-risk-dollar sizing at $300 per trade. Expected stop range is pinned to 25-26 points from the R4 fill-geometry probe or generic guard fallback. Worst plausible cluster is 5 consecutive losses = $1500, 0.75 of the Apex 50K EOD $2K drawdown floor. Favorable-first-week independence is false because a sparse opening-window strategy can start with a loss cluster before building cushion.
- **R3 (management lifecycle)**: No adaptive management is part of this candidate. D color-game add-on and E trailing-stop module are documented as future overlays, not standalone entries. Baseline exit for eventual Phase 1 should be fixed-R or time-window close.
- **R4 (signal frequency)**: R4 v1.2 probe on 19 trading days (2024-09-09 to 2024-10-04) fired 1 structural signals and 1 fill-guard-passing signals. Extrapolated 60-day range: [1, 7]. Sparsity class: sparse. Low-confidence attrition: true.
- **R5 (direction handling)**: This is deliberately direction-restricted (LONG) because the transcript decomposes long and short variants separately. Direction selection is not a post-result optimization; the paired inverse candidate is authored separately.

## 1. Thesis

When the 20-period and 200-period SMAs on 2-minute MNQ bars are tightly compressed at the RTH open, the first directional opening bar can represent balance breaking into expansion. The long version requires the first RTH 2-minute bar to close above both SMAs and print a bullish elephant or bottoming-tail trigger, then enters on a stop above that bar. The source is a stocks-derived trader-art opening-bar pattern adapted to MNQ, not an empirically validated MNQ edge.

Counter-hypothesis: the pattern may be equities-specific. The original trader-art source assumes stock scanners, single-name attention, and equity opening behavior. MNQ is one continuous futures instrument, so this entry may preserve only the bar-geometry component while losing the market-structure context that made the original pattern appealing.

## 2. Mechanism (what edge it captures)

- Compressed SMA20/SMA200 distance marks a narrow state where overnight and opening participants have not yet established directional separation.
- A bullish first RTH bar above the cluster suggests opening buyers are accepting prices above the compressed reference area.
- The stop entry above bar one avoids buying inside the first bar and requires at least one more tick of continuation.

## 3. Signal logic (entry conditions)

**Pre-committed predicates for this wiki entry:**

- Build 2-minute bars from MNQ 1-second OHLCV.
- Compute SMA20, SMA200, and ATR14 on 2-minute bars.
- At 09:30 ET, require abs(SMA20 - SMA200) / ATR14 <= 0.25.
- Require bar1 close > SMA20 and close > SMA200.
- Require bar1 to be bull_elephant or bull_bottoming_tail.
- Signal fire price is bar1 high + 0.25 point.
- Initial stop anchor is bar1 low - 0.25 point.

Common bar anatomy:

- `bar_range = high - low`
- `body = abs(close - open)`
- `close_location = (close - low) / bar_range`
- Bull elephant: green bar, body/ATR14 >= 0.40, range/ATR14 >= 0.75, close_location >= 0.70.
- Bear elephant: red bar, body/ATR14 >= 0.40, range/ATR14 >= 0.75, close_location <= 0.30.
- Bottoming/topping tail: wick >= 50% of bar range with close in the correct side of the range.

## 4. Exit logic (stops, targets, time-based exits)

Initial stop is structurally anchored to the trigger/problem bar plus one MNQ tick. The R4 probe uses a fixed 1.5R target only as a fill-geometry guard; this is not a FINAL spec target commitment.

Spec drafting must choose one baseline exit before any P&L test: fixed-R target, close after 20 minutes, or MA-touch/midpoint target for wide-state reversal variants. Management modules D and E are intentionally excluded from the baseline candidate.

## 5. Position sizing and Apex survival rationale

Risk is fixed at $300 per trade. Contract count at spec stage should be `floor(300 / (stop_pts * 2))`, bounded by Apex 50K limits and a pre-committed max-contract cap.

The Apex survival thesis is weak-to-moderate: the dollar loss is controlled, but the opening-window timing can cluster losses across consecutive days. A five-loss cluster equals $1500, 0.75 of the $2K EOD trailing floor. This does not require a catastrophic single trade to fail; it only requires an early unfavorable sequence. Therefore favorable-first-week independence is false.

## 6. Required indicators / data

- MNQ 1-second OHLCV from Databento store.
- Derived 2-minute OHLCV bars. This is a new primary timeframe for the project and should be explicitly verified before spec drafting.
- SMA(20), SMA(200), ATR(14) on 2-minute bars.
- No order-flow, bid/ask, options, scanner, or news feed dependency.

## 7. Differentiation (vs already-tested strategies)

This is closest to variant_1_lifecycle and noise_brk_canonical_alpha because it is a morning continuation breakout. The differentiator is the explicit tight-state SMA20/SMA200 compression gate and 2-minute first-bar trigger. The 9-fleet continuation failures make this candidate suspect; the only reason to keep it in inventory is to test whether compression-state selection changes the loss distribution.

The 9-fleet failure pattern remains material. This entry is preserved as an inventory candidate, not promoted. The R4 probe result should be treated as a cheap admissibility warning, not as an edge claim.

## 8. Required research before spec drafting

R2 and R4 are not deferred: they are quantified in frontmatter from the R4 probe.

Spec-stage research only:

- Decide whether 2-minute bars should include ETH history for SMA/ATR state or RTH-only history.
- Decide baseline exit mode before any P&L test.
- Decide fixed-risk max contract cap.
- Decide whether modules D/E are excluded from Phase 1 or introduced only after a baseline entry passes.
- If R4 is zero or low-confidence, decide whether to close the candidate or run a clearly labeled separate redesign rather than threshold-tuning this entry.

## 9. Source / references

Source is operator transcript decomposition of an equities trader-art lesson. The key claims are narrow-to-wide / wide-to-narrow state flow, SMA20/SMA200 compression/expansion, first 2-minute bar anatomy, problem-bar removal, and optional color-game/trailing modules.

Modules D and E are not standalone candidates:

- D `COLOR_GAME_ADD_ON` is a scale-in management overlay for later testing on top of entry families.
- E `TRAILING_STOP_ENGINE` is a stop-management overlay using fat-bar and color-sequence stop movement.

This candidate goes beyond folklore only by making the predicates mechanical and running an R4 v1.2 signal-frequency probe. It has not been Phase 0 evaluated, spec drafted, implemented, or P&L tested.

Probe caveats: 2-minute bars are derived from MNQ 1-second data; this is a new primary timeframe for the project. R4 probe uses v1.2 current local convention despite operator prompt naming v1.1. Stop/target guards are generic R4 geometry guards, not a FINAL spec. Stop-market trigger is approximated as fill at signal_ts + 1 second per R4 convention. low_confidence_attrition: fewer than 5 fired signals in the v1.2 probe window.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-17 | `untested-ideation` | Authored under template v2 from tight/wide-state transcript decomposition. R4 v1.2 probe run on 2024-09-09 to 2024-10-04: 1 fired, 1 passing fill guards, sparsity sparse. Likely Phase 0 R4 concern: nonzero but low-confidence count with fewer than 5 fired signals. |
