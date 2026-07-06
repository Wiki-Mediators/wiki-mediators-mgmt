---
name: "Opening Range Width Switch v2 Base Hit"
tagline: "Fade failed 15-minute opening-range breaks, but exit at the midpoint and reduce Apex variance."
status: "tested-rejected"
created: 2026-05-25
updated: 2026-05-25
source: "Derived from opening_range_width_switch failure investigation and 12-start marginal-registry characterization. This is a new candidate, not a modification of the tested ORWS audit trail."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-12:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "opening-range failed-break mean-reversion"
indicators: ["OpeningRange(15)", "ATR(20)", "VWAP"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "base-hit-midpoint"
position_sizing: "fixed-risk-dollar-reduced"

# Cross-references
canonical_spec: "nb_lib/strategy_specs/canonical/opening_range_width_switch_v2_base_hit_spec_FINAL.md"
implementation: "nb_lib/scripts/opening_range_width_switch_v2_base_hit_canonical_alpha.py"
related_candidates:
  - "opening_range_width_switch.md"

# Test status
test_results:
  in_sample_n: 329
  in_sample_pnl_dollars: -1307.70
  in_sample_pf: 0.95
  in_sample_win_rate: 0.5532
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: 0.4167

# Phase 0 readiness - inherited evidence plus new R2 requirement
admissibility:
  r1_edge_thesis:
    r1_diagnostic_convention_version: "inherited-orws-r1"
    r1_diagnostic_script: "nb_lib/scripts/diagnostic_orws_failed_break_reversion.py"
    r1_diagnostic_output: "nb_lib/probe_results/opening_range_width_switch_r1_diagnostic.json"
    r1_diagnostic_window: ["2024-08-01", "2025-01-31"]
    r1_lookahead_minutes: 30
    r1_mechanism_class: "fast-resolution"
    r1_n_qualifying_events: 161
    r1_low_confidence: false
    r1_compound_filter_over_restrictive: false
    r1_reversion_rate: 0.795
    r1_neither_rate: 0.205
    r1_verdict: "MET"
  r2_apex_survival:
    risk_dollars_per_trade: 200
    expected_stop_distance_pts_range: [8, 120]
    expected_loss_dollars_per_trade: 200
    worst_plausible_cluster_n: 6
    worst_plausible_cluster_dollars: 1200
    cluster_vs_floor_ratio: 0.60
    favorable_first_week_independent: false
    r2_variance_probe_version: "r2_variance_v1"
    r2_variance_probe_script: "nb_lib/scripts/probe_r2_variance_opening_range_width_switch_v2_base_hit.py"
    r2_variance_probe_output: "nb_lib/probe_results/opening_range_width_switch_v2_base_hit_r2_variance_probe.json"
    r2_variance_pf_simulated: 1.6137
    r2_variance_win_rate: 0.5655
    r2_variance_max_consecutive_losses: 5
    r2_variance_max_running_drawdown_dollars: 965.75
    r2_variance_trailing_dd_breach: false
    r2_variance_verdict: "PASS"
  r4_signal_frequency:
    probe_convention_version: "inherited-orws-phase1"
    probe_script: "nb_lib/scripts/opening_range_width_switch_entry_preflight.py"
    probe_output: "C:/VMShare/NT8lab/opening_range_width_switch_preflight_summary.json"
    probe_window_start: "2024-08-01"
    probe_window_end: "2026-01-31"
    probe_n_signals_observed: 278
    probe_signals_passing_fill_guards: 267
    probe_attrition_rate: 0.0396
    probe_p95_drift_pts: null
    probe_low_confidence_attrition: false
    probe_n_long: 140
    probe_n_short: 127
    probe_distinct_days_with_signal: null
    expected_signals_per_60_trading_days: [22, 89]
    sparsity_class: "moderate"
    sparsity_class_rationale: "Inherits ORWS Phase 1 preflight: 267 passing fill-time guards over full in-sample; 34.5 tradeable signals per 60 trading days."

# Tags
tags:
  - rth-only
  - intraday
  - opening-range
  - failed-break
  - mean-reversion
  - base-hit
  - reduced-risk
  - fixed-risk-dollar
  - post-hoc-derived
---

# Opening Range Width Switch v2 Base Hit

## 0. Admissibility Summary

- **R1 (edge thesis)**: Inherits the original ORWS MNQ-specific R1
  diagnostic: 161 post-OR break events over 127 in-sample days, with
  79.5% reverting back inside the 15-minute opening range within 30
  minutes. This remains the strongest empirical support in the project
  for an opening-range failed-break fade.
- **R2 (Apex survival)**: MET at variance-preflight level. The v2
  base-hit probe simulated the inherited ORWS signal set with $200 risk,
  full exit at the OR midpoint, and no TP2 runner. No-friction R2 result:
  267 simulated trades, PF 1.6137, win rate 56.55%, max running drawdown
  $965.75, max consecutive losses 5, no trailing-DD breach, verdict
  PASS. This is an optimistic preflight, not a deployability result.
- **R3 (management lifecycle)**: Static bracket only. No v2.4
  specialists. Unlike original ORWS, there is no post-TP1 runner. The
  trade either reaches the OR midpoint, hits the structural stop, or
  time-exits.
- **R4 (signal frequency)**: Inherits ORWS Phase 1 signal evidence:
  278 full-window signals, 267 passing fill-time guards, 3.96%
  attrition, moderate frequency, and no zero-month problem. Because the
  entry predicates are unchanged, no new R4 frequency probe is required
  unless the entry predicates change.
- **R5 (direction handling)**: Two-sided by default because the original
  R1 diagnostic showed symmetric failed-break reversion rates. However,
  the original multistart characterization showed long side carried the
  signal while short side dragged. Direction attribution is mandatory in
  every future probe/test; direction restriction must not be applied
  silently.

### Methodology Pipeline Order

This candidate does **not** reuse the old ORWS FINAL spec or
implementation. It starts as a new candidate with inherited R1/R4
evidence and a fresh R2 obligation:

1. Wiki entry authored - this document.
2. Fresh R2 variance preflight v1.3 for base-hit exit and reduced risk
   - completed 2026-05-25, PASS.
3. FINAL spec drafting is now the next eligible step.
4. New implementation under a new strategy id.
5. 12-start in-sample multistart.
6. OOS remains sealed unless pre-committed graduation criteria are met.

## 1. Thesis

The original `opening_range_width_switch` found a real but unstable
effect: failed breaks of the 15-minute MNQ opening range often revert
quickly back inside the range, but the original $300-risk, partial-TP1,
TP2-runner geometry created too much path variance for Apex 50K EOD.

This v2 candidate keeps the opening-range failed-break entry logic but
changes the trading intent from "capture the full return to the
opposite OR boundary" to "take the base hit at the OR midpoint." The
goal is lower variance, not higher headline profit.

The candidate is explicitly post-hoc to the original ORWS result. That
does not invalidate it, but it changes the methodological burden: v2
must not inherit the original test result as proof. It inherits only:

- The R1 failed-break reversion diagnostic.
- The Phase 1 signal-frequency evidence.
- The failure analysis showing variance and sizing were the main
  defects.

It must earn its own R2 variance pass, FINAL spec, implementation, and
multistart result.

## 2. Mechanism

- Opening range breaks attract initiating breakout traders.
- When price closes back inside the range, those breakout traders are
  trapped or at least wrong-footed.
- Responsive auction liquidity often fades the failed move back toward
  the opening-range midpoint.
- The midpoint is the natural "base hit" target: it asks only for a
  partial reversion, not a full traverse to the opposite OR boundary.
- Removing the TP2 runner should reduce tail dependence and lower the
  peak-to-trough damage that broke the original candidate's Apex path.

## 3. Signal Logic

Entry predicates are inherited unchanged from ORWS unless a future R2
or spec iteration explicitly rejects that inheritance.

**Pre-committed predicates:**

- Opening range: 09:30-09:45 ET.
- OR width filter: `OR_width >= 25 points`.
- Post-OR signal window: 09:45-11:00 ET.
- Trigger sequence:
  1. A 1-minute bar closes outside the OR.
  2. Within the next 10 bars, price produces two consecutive 1-minute
     closes back inside the OR.
  3. Signal fires at the second close-back-inside.
- Direction:
  - breakout above OR high then reclaim inside -> short fade.
  - breakout below OR low then reclaim inside -> long fade.
- Max one trade per RTH day.
- No new entries after 11:00 ET.

## 4. Exit Logic

This is the core v2 change.

- **Stop**: same structural stop as original ORWS: beyond the failed
  extreme plus 0.50 pt buffer.
- **Target**: full position exits at the OR midpoint / original TP1
  level. No partial close. No TP2 runner.
- **Breakeven**: none by default. There is no runner to protect after
  TP1.
- **Time exit**: if target/stop unresolved after 60 minutes, exit at
  next available 1-second close.
- **EOD flat**: mandatory at 15:58:30 ET, though this should rarely
  matter due the 60-minute max hold.

This is intentionally less ambitious than the original candidate. It
trades lower payout ceiling for a smoother account path.

## 5. Position Sizing And Apex Survival Rationale

Default risk is **$200/trade**, not $300.

Rationale:

- Original ORWS had positive aggregate multistart P&L but failed Apex
  in one monthly-start window and in the fixed-end account path.
- The original failure investigation found $250 likely avoided the
  original account breach, and $200 left more margin.
- A six-loss cluster at $200 is $1,200, or 60% of the Apex $2K drawdown
  floor. This leaves room for friction, slippage, and path variance.
- The base-hit target should reduce dependence on a few large TP2
  runners and may improve edge stability.

This still does not guarantee Apex survival. The original strategy's
bad paths were regime-sensitive, not just simple loss clusters. That is
why a fresh v1.3 R2 variance probe is mandatory before FINAL spec.

## 6. Required Indicators / Data

- 15-minute opening range from 09:30-09:45 ET.
- 1-minute bars for close-outside and close-back-inside predicates.
- 1-second OHLCV bars for fill simulation and bracket evaluation.
- ATR(20) on 5-minute bars for inherited sanity checks if retained at
  spec stage.
- Existing ORWS preflight signals may be reused for the R2 variance
  probe because entry predicates are unchanged.

## 7. Differentiation

This differs from `opening_range_width_switch` in three ways:

1. **Risk**: $200 default risk instead of $300.
2. **Exit**: full exit at OR midpoint; no TP2 runner.
3. **Methodology status**: treated as a new candidate due post-hoc
   derivation from a failed in-sample result.

It differs from the later `objective_level_liquidity_sweep_reversal`
family because it uses only the 15-minute opening range and the original
ORWS two-close reclaim logic. It does not bundle PDH/PDL or round/VWAP
sweeps, both of which recently produced negative evidence.

## 8. Required Research Before Spec Drafting

- R2 variance preflight is complete and passed. FINAL spec drafting may
  proceed as the next step.
- FINAL spec must preserve the R2 geometry that passed:
  - primary risk $200.
  - full exit at OR midpoint.
  - no TP2 runner.
  - no BE specialist by default.
  - entry predicates inherited unchanged from ORWS.
- FINAL spec should include the $250 sensitivity result as context only,
  not as the default risk setting.
- Direction attribution is now healthier in the base-hit R2 probe:
  both long and short simulated positive. Do not silently direction-filter.

## 9. Source / References

Primary source is the original ORWS methodology trail:

- Candidate: `nb_lib/strategy_specs/candidates/opening_range_width_switch.md`
- FINAL spec: `nb_lib/strategy_specs/canonical/opening_range_width_switch_spec_FINAL.md`
- R1 diagnostic script: `nb_lib/scripts/diagnostic_orws_failed_break_reversion.py`
- R1 output: `nb_lib/probe_results/opening_range_width_switch_r1_diagnostic.json`
- Phase 1 report: `C:/VMShare/NT8lab/nb_lib_phase1_preflight_opening_range_width_switch_report.md`
- Failure investigation: `C:/VMShare/NT8lab/nb_lib_opening_range_width_switch_failure_investigation.md`
- R2 variance retrospective: `C:/VMShare/NT8lab/nb_lib_v1_3_variance_preflight_orws_retrospective_validation.md`
- Marginal registry multistart report: `C:/VMShare/NT8lab/nb_lib_marginal_registry_multistart_report.md`

Informal exploratory analysis on 2026-05-25 approximated full-TP1
base-hit outcomes from the existing 12-start ORWS trade CSVs. That
analysis suggested lower drawdown and better aggregate P&L, but it is
not a substitute for a clean v1.3 R2 variance probe.

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-25 | `untested-ideation` | New v2 candidate authored from ORWS failure analysis. Inherits original ORWS R1/R4 evidence, but explicitly requires fresh v1.3 R2 variance preflight, fresh FINAL spec, fresh implementation, and fresh multistart. Existing ORWS wiki/spec remain unchanged as audit trail. |
| 2026-05-25 | `r2-variance-passed` | Fresh v1.3 R2 variance probe completed for v2 base-hit geometry. Primary $200 risk result: 267 simulated trades, +$11,866 no-friction P&L, PF 1.6137, win rate 56.55%, max running DD $965.75, max consecutive losses 5, no trailing-DD breach, verdict PASS. $250 sensitivity also PASS (+$14,529.25, PF 1.5911, max DD $1,165.50). Next eligible step: FINAL spec drafting. |
| 2026-05-25 | `spec-drafted-final` | FINAL spec drafted at `nb_lib/strategy_specs/canonical/opening_range_width_switch_v2_base_hit_spec_FINAL.md`. Spec preserves inherited ORWS entry predicates, $200 risk, full OR-midpoint exit, no TP2 runner, no BE, and 12-start in-sample multistart requirement. Existing ORWS artifacts remain unchanged. |
| 2026-05-25 | `tested-in-sample-pass` | New implementation and 12-start in-sample multistart completed. Result: 345 trades, +$9,487.40, PF 1.35, win rate 56.81%, 9/12 profitable starts, 0/12 failed starts, worst start max DD $1,143.30. All pre-committed in-sample criteria passed. OOS remains sealed; operator approval required before any OOS decision. Report: `C:/VMShare/NT8lab/nb_lib_opening_range_width_switch_v2_base_hit_multistart_report.md`. |
| 2026-05-25 | `tested-rejected` | Pre-OOS verification found a left-labeled 1-minute signal timestamp bug: the first multistart used the signal bar's start timestamp rather than the completed-bar timestamp. After fixing signal/fill timing and adding focused regression tests, the corrected 12-start in-sample multistart failed: 329 trades, -$1,307.70, PF 0.95, win rate 55.32%, 5/12 profitable starts, 0/12 failed starts, worst start max DD $1,699.30. The prior pass is treated as contaminated and invalid for OOS decision-making. OOS remains sealed. |
