---
name: "Gap Fill Pressure"
tagline: "Fade overnight gaps when RTH fails to confirm them."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-14
source: "Inspiration: classic gap-fill trading concept from index futures literature and discretionary trading. Retrofitted to template v2 on 2026-05-14."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-12:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "gap-fade"
indicators: ["PriorRTHClose", "RTHOpen", "VWAP", "DailyATR"]
timeframes_used: ["1-second", "1-minute", "15-minute", "daily"]

# Execution
brackets: "volatility-adaptive"
position_sizing: "fixed-risk-dollar"

# Cross-references
canonical_spec: null
implementation: null
related_candidates: []

# Test status
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

# Phase 0 readiness (template v2, 2026-05-14)
admissibility:
  r2_apex_survival:
    risk_dollars_per_trade: 300
    expected_stop_distance_pts_range: [30, 80]
    expected_loss_dollars_per_trade: 300
    worst_plausible_cluster_n: 6
    worst_plausible_cluster_dollars: 1800
    cluster_vs_floor_ratio: 0.90
    favorable_first_week_independent: false
  r4_signal_frequency:
    probe_convention_version: "v1.1"
    probe_script: "nb_lib/scripts/probe_r4_gap_fill_pressure_v1_1.py"
    probe_output: "nb_lib/probe_results/gap_fill_pressure_r4_probe_v1_1.json"
    probe_window_start: "2024-10-07"
    probe_window_end: "2024-11-01"
    probe_n_signals_observed: 5
    probe_signals_passing_fill_guards: 1
    probe_attrition_rate: 0.80
    probe_p95_drift_pts: 15.75
    probe_n_long: 2
    probe_n_short: 3
    probe_distinct_days_with_signal: 5
    expected_signals_per_60_trading_days: [1, 6]
    sparsity_class: "sparse"
    sparsity_class_rationale: "1 tradeable signal over 23 days under v1.1 (5 fired, 4 failed fill-time guards); 80% attrition flagged; ~8-50 trades projected over 12-start multistart, at or below typical Section 7.2 n>=80 threshold"
    v1_probe_output: "nb_lib/probe_results/gap_fill_pressure_r4_probe.json"  # retained for methodology comparison

# Tags
tags:
  - rth-only
  - intraday
  - gap-fade
  - mean-reversion
  - fixed-risk-dollar
---

# Gap Fill Pressure

## 0. Admissibility summary

- **R1 (edge thesis)**: Failed acceptance of overnight gap repricing
  identifies trapped overnight positioning; RTH non-confirmation
  produces unwind pressure toward prior close. Mechanism is
  participant-behavior-based (overnight thin-liquidity vs RTH
  rejection). Folklore-supported but operationalized via failed-15-min
  continuation, which makes it more disciplined than naive gap-fill.
  See Sections 1, 2, 9.
- **R2 (Apex survival)**: Risk $300/trade. Expected stop distance 30-80
  pts at first-15-min extreme; loss per trade ≈ $300 by sizing
  construction. Worst plausible cluster: 6 consecutive losses = $1,800
  (cluster/floor = 0.90 — TIGHT, marginal pass). Strategy does NOT
  require a favorable first week to survive. See Section 5 for full
  cluster-loss analysis.
- **R3 (management lifecycle)**: No v2.4 specialists used. Static
  brackets: stop beyond 15-min extreme; TP1 = half-gap; TP2 = full-gap;
  EOD time exit at 12:00 ET. Choosing static brackets avoids the round-
  number / mhw management-design-dead pattern. See Section 4.
- **R4 (signal frequency)**: Probe run 2026-05-14 on 23 trading days
  (2024-10-07 to 2024-11-01): 5 signals observed (2 long, 3 short),
  one per signal day, all at 10:00-11:00 ET. Extrapolated to a 60-
  trading-day window: 6-27 signals. Sparsity class: moderate. Probe
  caveats: catalyst-day skip not applied; reclaim look-ahead pinned at
  12:00 ET. See probe output for details.
- **R5 (direction handling)**: Two-sided. Methodological defense:
  overnight gaps occur in both directions on MNQ; failed-acceptance
  pressure should be mechanism-symmetric. Probe shows mild short bias
  (3S / 2L) at small sample size; pre-committed asymmetry interpretation:
  if Phase 1 shows > 2:1 directional imbalance in n, treat as regime-
  driven sample artifact pending more data, not strategy edge.

## 1. Thesis

Overnight futures gaps can reflect thin-liquidity repricing. If RTH
opens with a meaningful gap but cannot extend in the gap direction,
price may revisit the prior RTH close or a settlement proxy.

This candidate separates overnight repricing from RTH acceptance. It
is not a generic gap-fill entry; it only trades when the RTH session
fails to confirm the overnight move.

## 2. Mechanism (what edge it captures)

- Measures the gap from prior RTH close to current RTH open.
- Requires failed continuation during the first 15 minutes.
- Targets a natural magnet: half gap fill and full gap fill.
- Trades the overnight-to-RTH transition rather than pure intraday
  momentum.

## 3. Signal logic (entry conditions)

Compute the gap from prior RTH close to current RTH open. Only
consider gaps larger than 0.35 × daily ATR. For a gap-down long, the
first 15 minutes must fail to make a new low after the initial
opening range and then price must reclaim RTH VWAP or the opening
print. A gap-up short is symmetric.

Skip known catalyst days and any session where the gap continues
cleanly through the first 15-minute extreme.

**Pre-committed predicates:**

- Gap magnitude: |RTH_open − prior_RTH_close| > 0.35 × daily ATR(20).
- Initial opening range: first 15 RTH minutes (09:30-09:45 ET).
- Failed continuation window: 15 minutes post-OR (09:45-10:00 ET); no
  new directional extreme beyond OR.
- Reclaim trigger: close back through RTH VWAP or RTH open print.
- Entry time gate: 09:30 to 12:00 ET (reclaim must occur in window).
- Max one trade per direction per day.

## 4. Exit logic (stops, targets, time-based exits)

Stop beyond the first 15-minute extreme. TP1 is half gap fill. TP2 is
full gap fill to prior RTH close or the chosen settlement proxy. Time
exit at 12:00 ET if neither target nor stop has resolved the trade.

**No v2.4 management specialists.** Static brackets only.

## 5. Position sizing and Apex survival rationale

**Risk: $300 per trade**, fixed-dollar, sized to stop distance per
`contracts = floor($300 / (stop_pts × $2)).clamp(1, 12)`.

**Apex survival analysis:**

- $50K starting balance, $2K trailing drawdown floor.
- Stop distance: 30-80 pts (first-15-min extreme beyond entry). Typical
  ≈ 50 pts → 3 contracts → $300 loss at full stop.
- **Worst plausible cluster: 6 consecutive losses = $1,800.** Six gap
  days in a row with failed reclaim + failed continuation in the gap
  direction (i.e., trend regime where gap-fades systematically fail).
  Plausible over a single month if the market enters a strong directional
  regime that walks through the gap.
- **Cluster/floor ratio = 0.90.** TIGHT but survivable. Note this is
  marginal: a single additional loss in a 6-loss cluster (i.e., 7
  consecutive losses = $2,100) breaches the floor.
- **Favorable-first-week independence: FALSE.** Six trades total over
  ~5 weeks at probe rate; the trailing-drawdown floor is computed from
  peak balance, so a $50K → $48K drawdown without prior wins is the
  Apex-failure scenario. The strategy is NOT favorable-first-week
  independent.
- **Comparison to closest tested relative**: no direct gap-fade
  relative in the 9-fleet failure matrix. Most prior failures were
  morning-momentum continuation. The gap-fade mechanism is mechanism-
  distinct, but the mean-reversion-failure-via-runaway-trend risk is
  similar to vwap_stretch_snapback (which failed Apex in-sample). The
  gap_fill_pressure stop is structural (beyond 15-min extreme) rather
  than VWAP-band-based, so the runaway-stop-punch risk is somewhat
  bounded.

**R2 verdict-readiness**: cluster/floor 0.90 is marginal. If Phase 1
shows trade count below 30/60 days, R2 would tighten (fewer trades
means each cluster bites harder); if Phase 1 shows count above 30/60
days, R2 would loosen (more trades absorb cluster).

## 6. Required indicators / data

Prior RTH close, current RTH open, RTH VWAP, daily ATR(20). Current
MNQ store supports this; overnight coverage to be verified (Section
8).

## 7. Differentiation (vs already-tested strategies)

The failed strategies used morning intraday signals after RTH began
and mostly followed direction. This candidate keys off the overnight-
to-RTH transition and fades failed acceptance, with stop distance
determined by the first 15-minute auction rather than a fixed bracket.

No direct comparison to the 9 failed strategies. Closest in spirit is
vwap_stretch_snapback (mean-reversion); closest in mechanism is no
prior candidate.

## 8. Required research before spec drafting

**R2/R4 not deferred to this section under template v2.**

Spec-stage items only:

- Decide whether "prior RTH close" or official settlement proxy is the
  canonical gap anchor.
- Verify overnight coverage quality in the MNQ store.
- Define catalyst-day skip list before testing (CPI, FOMC, NFP, OPEX,
  major earnings).
- Pin "failed continuation" look-ahead: probe used 15 min post-OR;
  spec may extend to 30 min.
- Pin reclaim trigger: VWAP-only, open-print-only, or either. Probe
  used "either-or" with 12:00 ET time bound.

## 9. Source / references

Classic index futures gap-fill concept; widely documented in
discretionary intraday literature (Sperandeo, Lefèvre-derived
folklore). No peer-reviewed citation; this candidate's edge claim
rests on the disciplined failed-continuation filter rather than
naive gap-fill.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | Created by Codex 5.5 CLI batch 2 (Apr-event-style mean-reversion class). |
| 2026-05-14 | `untested-ideation` (retrofit) | Retrofitted to template v2. R4 probe run 2026-05-14 on 23 trading days: 5 signals (2L/3S), extrapolated 6-27 per 60 days, sparsity moderate. R2 quantified: $300 risk/trade, worst-plausible cluster 6 losses = $1,800 (cluster/floor 0.90 TIGHT). Probe output at `nb_lib/probe_results/gap_fill_pressure_r4_probe.json`. |
| 2026-05-14 | `phase-0-conditionally-admissible` | Phase 0 v2 evaluation complete. Verdict: **CONDITIONALLY ADMISSIBLE.** Tally: R2, R3, R4, R5 MET; R1 PARTIALLY MET (folklore-grounded edge thesis lacking MNQ-specific reversion-rate diagnostic). First non-INADMISSIBLE verdict across five Phase 0 evaluations. R2 cluster/floor 0.90 flagged as TIGHT margin. To progress to Phase 1, supply an MNQ failed-vs-continued continuation reversion-rate diagnostic. Report at `C:/VMShare/NT8lab/nb_lib_phase0_v2_gap_fill_pressure.md`. |
| 2026-05-16 | `phase-0-inadmissible-under-v1.1` | R4 probe re-run under convention v1.1 (fill-mechanics simulation). **80% attrition** at fill-time guards: 5 signals fired, 1 passed (4 failed on stop-band or TP-distance). Extrapolation revised: 1-6 tradeable/60d (was 6-27 under v1); sparsity revised: sparse (was moderate). R4 verdict flipped from MET to NOT MET. Combined with pre-existing R1 PARTIAL, candidate now has two unaddressed gaps. **Verdict revised: INADMISSIBLE** (CONDITIONALLY ADMISSIBLE requires one gap, this has two). Drift profile: median 5.75pt, p95 15.75pt — moderate but compounded by structural timing issue (reclaim trigger fires after TP1 may already be reached; 3 of 5 signals had negative tp_dist at fill). Wiki R2 expected_stop_distance_pts_range [30, 80] also empirically violated (3 of 5 fills had stops outside this range). Recommended next step: close candidate; do not advance to FINAL spec. Report at `C:/VMShare/NT8lab/nb_lib_phase0_v2_gap_fill_pressure_v1_1_revaluation.md`. |
| 2026-05-16 | `phase-0-inadmissible-closed` | Candidate formally closed per v1.1 re-evaluation recommendation. Does NOT advance to FINAL spec. Two unaddressed gaps (R1 partial + R4 not met) plus a structural timing issue (reclaim-after-significant-reversion produces negative TP1 distance at fill). A future "v2 candidate" addressing both gaps would need (a) MNQ-specific failed-vs-continued reversion-rate diagnostic for R1, and (b) entry predicates that fire BEFORE significant reversion to fix the timing issue — that would be a different strategy under a different name. Methodology learning preserved in v1.1 case-study section of `_R4_PROBE_CONVENTION.md`. |
