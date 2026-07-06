---
name: "Intraday Momentum Continuation Base Hit"
tagline: "Trade the documented first-move-predicts-later-move momentum effect, but deliver it through a variance-controlled base-hit bracket instead of a hold-to-close."
status: "untested-ideation"
created: 2026-05-25
updated: 2026-05-25
source: "Strategic synthesis 2026-05-25 from the published market-intraday-momentum literature (first half-hour return predicts last half-hour return; asymmetric and volatility-conditional). Execution structure inherited from opening_range_width_switch_v2_base_hit variance-control lesson."
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:00-15:00 ET"
hold_duration: "intraday"
signal_type: "momentum-continuation"
indicators: ["first-half-hour return", "ATR(20) daily", "RTH VWAP", "EMA(8) 2-min"]
timeframes_used: ["1-second source", "2-minute derived", "daily"]
brackets: "base-hit-target"
position_sizing: "fixed-risk-dollar"
canonical_spec: null
implementation: null
related_candidates:
  - "opening_range_width_switch_v2_base_hit"
  - "first_hour_range_expansion_breakout"
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
  r1_edge_thesis:
    r1_diagnostic_convention_version: "v1.1"
    r1_diagnostic_script: "nb_lib/scripts/diagnostic_imcb_intraday_momentum_continuation_r1.py"
    r1_diagnostic_output: "nb_lib/probe_results/intraday_momentum_continuation_base_hit_r1_diagnostic.json"
    r1_diagnostic_window: ["2024-08-01", "2025-01-31"]
    r1_lookahead_minutes: 60
    r1_mechanism_class: "moderate"
    r1_n_qualifying_events: 8
    r1_low_confidence: true
    r1_compound_filter_over_restrictive: false
    r1_reversion_rate: 0.125
    r1_neither_rate: 0.0
    r1_verdict: "INCONCLUSIVE"
  r2_apex_survival:
    risk_dollars_per_trade: 200
    expected_stop_distance_pts_range: [5, 35]
    expected_loss_dollars_per_trade: 200
    worst_plausible_cluster_n: 6
    worst_plausible_cluster_dollars: 1200
    cluster_vs_floor_ratio: 0.60
    favorable_first_week_independent: false
    r2_variance_probe_version: null
    r2_variance_probe_script: null
    r2_variance_probe_output: null
    r2_variance_pf_simulated: null
    r2_variance_win_rate: null
    r2_variance_max_consecutive_losses: null
    r2_variance_max_running_drawdown_dollars: null
    r2_variance_trailing_dd_breach: null
    r2_variance_verdict: null
  r4_signal_frequency:
    probe_convention_version: "v1.2"
    probe_script: null
    probe_output: null
    probe_window_start: null
    probe_window_end: null
    probe_n_signals_observed: null
    probe_signals_passing_fill_guards: null
    probe_attrition_rate: null
    probe_p95_drift_pts: null
    probe_low_confidence_attrition: null
    probe_n_long: null
    probe_n_short: null
    probe_distinct_days_with_signal: null
    expected_signals_per_60_trading_days: null
    sparsity_class: null
    sparsity_class_rationale: null
tags:
  - rth-only
  - intraday
  - momentum
  - trend-continuation
  - regime-conditional
  - volatility-conditional
  - base-hit
  - per-direction-attribution
  - objective-level
  - ohlcv-testable
  - new-dimension
---

# Intraday Momentum Continuation Base Hit

## 1. Thesis
There is a documented, replicated, cross-asset market effect: the first
half-hour RTH return predicts the later-day return, the effect is
ASYMMETRIC (much stronger when the first half-hour return is positive
than negative), and it is stronger on high-volatility days. This is
published academic work (market intraday momentum literature), not
trader folklore.

The raw academic strategy holds a position into the close. That is
Apex-hostile: a multi-hour hold has uncontrolled path variance and no
defined stop geometry, and would almost certainly fail the trailing
drawdown floor the way every high-variance candidate has.

This candidate takes the ROBUST part of the finding (the asymmetric,
volatility-conditional momentum signal) and delivers it through the
ONE execution structure that survived Apex this session: the v2
base-hit discipline. Defined entry on the established intraday trend, a
base-hit target at a fixed R, no runner, tight structural stop. The bet
is that a documented continuation signal, expressed through
variance-controlled execution, can capture part of the momentum edge
without the hold-to-close path risk.

Counter-hypothesis: bracketing the trade may destroy the edge. The
academic effect is a hold-to-close, end-of-day return prediction; a
2R base-hit target may exit before the predicted move materializes, or
the stop may be hit by intraday noise before the close-ward drift
occurs. The momentum effect may live entirely in the close print, not
in the intraday path, in which case no bracket can capture it.

## 2. Mechanism (what edge it captures)
- The first half-hour return is an objective, completed measurement
  (known at 10:00 ET) requiring no discretionary marking.
- A positive, high-volatility first-half-hour return predicts
  continued same-direction drift (the documented effect, strongest in
  exactly this regime).
- Trading WITH the established move (continuation) avoids the fade-class
  failure that has killed roughly five candidates this session.
- The base-hit target controls Apex path variance (the v2 lesson):
  capture a defined piece of the predicted drift rather than holding
  for the full close-ward move.
- The asymmetry is a pre-committed structural feature: the research
  says the long/positive side is the stronger signal, so a long-biased
  or long-only first version is justified BY THE RESEARCH, not by
  post-hoc direction selection on results.

## 3. Signal Logic (entry conditions)
All inputs computed from completed bars only; lookback strictly before
the decision timestamp.

Pre-committed measurements (known at 10:00 ET):
- r1 = (price at 10:00 ET - RTH open) / RTH open  (first half-hour
  return).
- vol_elevated = today's first-half-hour realized range >= 1.0 * ATR(20,
  daily)  (the high-volatility condition the effect requires).
- trend_align = RTH price above RTH VWAP and above EMA(8) on 2-min
  (confirms the move is established, not already reversing).

Branch LONG (the research-favored side, v1 primary):
- r1 >= +0.3% (positive first-half-hour return, pre-committed threshold).
- vol_elevated == true.
- trend_align == true (price above VWAP and EMA8).
- Entry trigger: after 10:00 ET, a 2-min pullback that holds — a
  completed bar closes back up through the prior bar high while price
  stays above VWAP (enter on continuation resumption, not at the
  extended high — this is start-of-the-next-leg timing, not
  signal-after-move).
- Entry: stop-market at the resumption bar high + 1 tick.
- One trade per day. No entry after 14:00 ET.

Branch SHORT (the research-weaker side, logged in v1, traded only if
v1 long branch shows edge):
- Symmetric with r1 <= -0.3%. Per the research the negative side is a
  much weaker predictor (R2 0.3-0.9% vs 2.3-4.5%). v1 LOGS short
  signals for attribution but does NOT trade them, to test whether the
  documented asymmetry holds on MNQ before committing capital to the
  weak side. This is a pre-committed research-driven choice, recorded
  before any results, NOT post-hoc direction filtering.

## 4. Exit Logic (stops, targets, time-based exits)
- Target: 2.0R base hit. Full exit. No runner. (The v2 lesson: runner
  geometry on these strategies creates the tail-driven variance that
  fails Apex. Capture a defined piece of the drift.)
- Stop: below the resumption-bar low - buffer (long), structural. If
  the continuation resumption fails immediately, the thesis is wrong.
  Pre-commit buffer at spec stage.
- Stop-band guard: reject if stop distance < 5 pts or > 35 pts.
- BE arm: 1.0R (modest; protect the base-hit once the move extends, but
  not at entry).
- Max hold: 90 minutes (the predicted drift is a slow same-direction
  push; if 2R is not reached in 90 min the edge is likely not present
  that day).
- EOD flat 15:58:30 ET.

## 5. Position Sizing And Apex Survival Rationale
Fixed-risk-dollar, $200 per trade (the v2 ORWS lesson on reversion
applies equally to continuation: lower per-trade risk plus no runner
controls the Apex path). contracts = floor(200 / (stop_pts * 2)),
capped at 12, skip if < 1. Daily loss limit: 2 realized losses.

The Apex concern specific to continuation: continuation strategies
cluster losses on chop days where the early move reverses. The
vol_elevated + trend_align filters are designed to trade only on days
where the move is established and volatility supports continuation -
this is precisely the regime the research says the effect is strongest,
and it should also be the regime with the fewest false continuations.
The R2 variance preflight must check loss clustering on days where the
early move reverses despite passing the filters.

## 6. Required Indicators / Data
- RTH open, price at 10:00 ET (first-half-hour return).
- First-half-hour realized range, ATR(20) daily (volatility condition).
- RTH VWAP, EMA(8) on 2-min (trend alignment + entry trigger).
- 2-min bars for the pullback-resumption trigger.
- 1-second bars for fill simulation.

Fully OHLCV-testable. No overnight/globex data required (uses RTH open
forward). No footprint or order-flow dependency.

## 7. Differentiation (vs already-tested strategies)
This is a new dimension AND a with-trend mechanism, which together make
it distinct from the exhausted funnel:

- It is built on a published, replicated momentum effect, not a
  chart-pattern hypothesis. The edge thesis has external empirical
  support before the project's own R1 even runs.
- It is CONTINUATION, not a fade. The five-plus fade rejections this
  session do not apply to it; the continuation-class cluster risk does,
  and is addressed by the volatility/trend-alignment filters.
- It conditions on the first-half-hour return and its documented
  asymmetry, an input the funnel has not used at the entry level.
- It inherits the v2 base-hit variance control (defined target, no
  runner, $200 risk) - the only execution structure the project has
  evidence can survive Apex.

Unlike first_hour_range_expansion_breakout (which trades a range break),
this trades the documented return-continuation effect conditioned on
volatility and the first-half-hour sign. Unlike the v2 ORWS base-hit
(a reversion fade), this is with-trend - same execution discipline,
opposite signal direction.

## 8. Required Research Before Spec Drafting
- R1 diagnostic result (2026-05-25): INCONCLUSIVE because the current
  conjunction produced zero qualifying events in the 2024-08-01 to
  2025-01-31 in-sample window. This does not disprove the published
  first-half-hour momentum effect on MNQ; it shows this specific
  bracketable implementation is over-gated before spec drafting.
  Follow-up stage counts identified the binding blocker: first-half-hour
  range >= prior daily ATR20 passed on 0/107 eligible days. Return
  threshold alone passed 26 long days and 26 short days, and trend
  alignment alone passed 55 long / 43 short days. The candidate is reset
  to untested-ideation pending a corrected R1 definition; do not treat
  the zero-fire run as an edge rejection.
- Corrected R1 diagnostic rerun (2026-05-25): volatility gate changed
  to first-half-hour range >= 0.40 * prior daily ATR20. This produced
  17 total bracketable events after guards: 8 primary longs and 9 logged
  shorts. Primary long continuation was weak at 1/8 (12.5%) reaching 2R
  before the structural stop; logged shorts were 2/9 (22.2%) with one
  neither. Verdict remains INCONCLUSIVE because primary n < 15, but the
  observed bracketed continuation behavior is not encouraging.
- R1 edge diagnostic (the make-or-break gate): over the in-sample
  window, measure whether a positive, high-volatility first-half-hour
  return actually predicts a tradeable same-direction continuation on
  MNQ - specifically, does a 2R base-hit target get reached more often
  than a 1R-equivalent stop on these days? The published effect is on
  broad indices and a hold-to-close horizon; MNQ on a bracketed horizon
  may not replicate it. R1 must MET before spec drafting.
- The asymmetry check: confirm on MNQ that the positive side is the
  stronger predictor (the research basis for the long-first design). If
  MNQ shows the opposite or symmetric behavior, the design assumption is
  wrong and must be revisited BEFORE testing, not after.
- R4 frequency: how many days produce a qualifying (positive + elevated
  vol + trend-aligned + pullback-resumption) long signal per 60 trading
  days? The stacked conditions may be sparse.
- Bracket-vs-hold check: does the 2R base-hit capture the effect, or
  does the effect live only in the close print (in which case the
  bracket destroys it)? This is the deepest risk and should be examined
  in the R1 diagnostic by comparing bracketed outcomes vs the raw
  close-ward drift.

## 9. Source / References
Strategic synthesis from 2026-05-25 session. The momentum effect is from
the market-intraday-momentum literature (first half-hour return predicts
last half-hour return; asymmetric, stronger when positive, stronger on
high-volatility days; replicated cross-asset). The pre-committed
thresholds (r1 >= 0.3%, vol >= 1.0x ATR) are starting points from that
research, to be treated as fixed for the R1 diagnostic, NOT tuned to
results. The base-hit execution discipline (defined target, no runner,
$200 risk) is inherited from opening_range_width_switch_v2_base_hit,
the one variance-controlled structure shown to survive Apex this
session. The long-first asymmetry is a research-driven structural
choice recorded before any MNQ results.

## 10. Status History
| Date | Status | Notes |
|------|--------|-------|
| 2026-05-25 | untested-ideation | Authored from the published market-intraday-momentum effect, delivered through the v2 base-hit variance-control structure. With-trend continuation (not a fade), conditioned on the documented first-half-hour-return asymmetry and high-volatility regime. New entry dimension (first-half-hour return). Long-first by research-driven asymmetry, recorded pre-results. Gated on an R1 diagnostic that must show the effect replicates on MNQ on a bracketed (not hold-to-close) horizon before spec drafting. Carries continuation-class cluster risk, addressed by volatility/trend filters and base-hit variance control. |
| 2026-05-25 | untested-ideation | R1 v1.1 diagnostic produced 0 qualifying events across 107 eligible in-sample days (long=0, short=0). Stage counts show the blocker was the volatility predicate: first-half-hour range >= prior daily ATR20 passed 0/107 days, while return threshold alone passed 26 long and 26 short days. Closure reversed; this is an R1 definition issue, not an edge rejection. |
| 2026-05-25 | untested-ideation | Corrected R1 rerun with volatility gate first-half-hour range >= 0.40 * prior daily ATR20. Stage counts: 36 vol-elevated days, 10 long setup days, 17 short setup days, 8 primary long events after stop-band, 9 logged short events. Primary long continuation 1/8 (12.5%); logged short continuation 2/9 (22.2%). Verdict INCONCLUSIVE due n<15, with weak observed bracketed continuation. |
