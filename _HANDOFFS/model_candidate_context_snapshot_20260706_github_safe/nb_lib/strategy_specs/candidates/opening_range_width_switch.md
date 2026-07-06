---
name: "Opening Range Width Switch"
tagline: "Fade failed breakouts of the 15-minute opening range when OR is meaningfully wide."
status: "tested-apex-failure"
created: 2026-05-12
updated: 2026-05-17
source: "Inspiration: opening structure interpreted through volatility-normalized range width. Retrofitted to template v2 on 2026-05-17."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-12:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "initial-balance"
indicators: ["OpeningRange(15)", "ATR(20)", "VWAP"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "volatility-adaptive"
position_sizing: "fixed-risk-dollar"

# Cross-references
canonical_spec: "nb_lib/strategy_specs/canonical/opening_range_width_switch_spec_FINAL.md"
implementation: null
related_candidates: ["failed_orb_fade.md"]

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

# Phase 0 readiness (template v2, 2026-05-17)
admissibility:
  r2_apex_survival:
    risk_dollars_per_trade: 300
    expected_stop_distance_pts_range: [3, 65]
    expected_loss_dollars_per_trade: 300
    worst_plausible_cluster_n: 6
    worst_plausible_cluster_dollars: 1800
    cluster_vs_floor_ratio: 0.90
    favorable_first_week_independent: false
  r4_signal_frequency:
    probe_convention_version: "v1.2"
    probe_script: "nb_lib/scripts/probe_r4_opening_range_width_switch.py"
    probe_output: "nb_lib/probe_results/opening_range_width_switch_r4_probe.json"
    probe_window_start: "2024-09-09"
    probe_window_end: "2024-10-04"
    probe_n_signals_observed: 18
    probe_signals_passing_fill_guards: 17
    probe_attrition_rate: 0.0556
    probe_p95_drift_pts: 38.00
    probe_low_confidence_attrition: false
    probe_n_long: 11
    probe_n_short: 7
    probe_distinct_days_with_signal: 18
    expected_signals_per_60_trading_days: [22, 89]
    sparsity_class: "moderate"
    sparsity_class_rationale: "17 tradeable signals over 23 days under v1.2; low 5.6% attrition; well-positioned for 12-start multistart"

# Tags
tags:
  - rth-only
  - intraday
  - opening-range
  - volatility-adaptive
  - fixed-risk-dollar
---

# Opening Range Width Switch

## 0. Admissibility summary

- **R1 (edge thesis)**: Wide opening ranges in the 09:30-09:45 window
  are exhaustion-prone; failed breakouts of a wide OR draw responsive
  fade liquidity. Empirical support: MNQ R1 diagnostic 2026-05-17
  (`probe_results/opening_range_width_switch_r1_diagnostic.json`)
  measured **79.5% reversion within 30 minutes** across 161 OR-break
  events in 127 in-sample days (79.7% up-breaks / 79.3% down-breaks —
  direction-symmetric). Median minutes-to-reversion: 2.0. The
  previous candidate-design "acceptance mode" was dropped on
  2026-05-17 after the v1.2 probe revealed it was structurally
  unreachable with ATR(20) on 5-min bars. Candidate now operates as
  rejection-only. See Sections 2, 7, 9.
- **R2 (Apex survival)**: Risk $300/trade. Probe-observed stop distance
  range [3, 65] pts (p50 24.62). With 3pt minimum stop, BAND_B
  friction (~1.7pt) consumes a significant fraction; spec stage should
  add a stop-floor guard. Worst plausible cluster: 6 losses × $300 =
  $1,800 (cluster/floor 0.90 — TIGHT). Does NOT require favorable
  first week.
- **R3 (management lifecycle)**: No v2.4 specialists used. Static
  brackets: stop on OR-anchor or beyond failed extreme, TP1 = 1×OR_width,
  TP2 = 2×OR_width, time exit at 12:00 ET, no new entries after 11:00.
  Static brackets are coherent with the candidate's mechanism.
- **R4 (signal frequency)**: Probe run 2026-05-17 on 23 trading days
  (2024-09-09 to 2024-10-04, v1.2 default): 18 signals fired, 17
  passed fill-time guards (attrition 5.6%). Extrapolated 22-89
  tradeable per 60 days. Sparsity class: moderate. v1.2 caught
  attrition cleanly with low_confidence_attrition flag false.
- **R5 (direction handling)**: Two-sided by mechanism (long if breakout
  is below OR; short if breakout is above). Probe shows 11L/7S (61%
  long) — within pre-committed 65% asymmetry bound. Pre-committed
  asymmetry interpretation: > 2:1 imbalance at Phase 1 n is regime-
  driven artifact, not strategy edge.

## 1. Thesis

When MNQ breaks outside the 15-minute opening range early in RTH, a
majority of those breaks fail and price returns inside the OR within
30 minutes (79.5% empirically; see Section 9). The failure-of-break
identifies trapped breakout positioning; responsive auction liquidity
fades the trapped flow back to the OR midpoint.

The candidate restricts entry to days where the OR is meaningfully
wide — not chop days where the entire range is friction.

**Reframed 2026-05-17**: this candidate was originally authored with
a two-mode "width switch" (acceptance for narrow OR, rejection for
wide OR). The v1.2 probe found the acceptance threshold structurally
unreachable with the wiki-specified ATR period (OR_width/ATR ratios
were always ≥ 2.2, far above the 0.35 acceptance cap). The candidate
was reframed as rejection-only, dropping the acceptance leg.

## 2. Mechanism (what edge it captures)

- Failed breakouts of the 15-min opening range identify trapped
  initiating positioning.
- Responsive auction participants fade the trapped flow back to the
  OR — empirically, 79.5% revert within 30 minutes.
- The 2-minute close-back-inside trigger is a disciplined rejection
  confirmation (not a wick).
- Stops anchored beyond the failed extreme bound risk to the
  initiating attempt's exhaustion point.

## 3. Signal logic (entry conditions)

**Pre-committed predicates:**

- Opening range: 09:30-09:45 ET (15 minutes).
- OR width filter: `OR_width >= 25 points` (sanity threshold to exclude
  chop days; calibrated from probe data showing min OR width 50pt in
  Sept-Oct sample; 25pt is the floor below which the candidate skips
  the day).
- Trigger sequence:
  1. Price closes outside the OR (any 1-min bar's close) in the
     post-OR window 09:45 to 11:00 ET.
  2. Within the next 10 bars, two consecutive 1-minute closes back
     inside the OR.
  3. Signal fires at the second close-back-inside.
- Direction: short if the breakout was above OR_high; long if below
  OR_low.
- Max one trade per RTH day.
- Time gate end: 11:00 ET (no new entries after).

## 4. Exit logic (stops, targets, time-based exits)

- **Stop**: beyond the failed-extreme + 0.50pt buffer (2 ticks).
- **TP1**: entry + OR_midpoint - entry  (long: midpoint; short: midpoint).
  Equivalently, TP1 = halfway from entry to the opposite OR boundary.
- **TP2**: opposite OR boundary (the OR side opposite the failed
  break — long: OR_high; short: OR_low).
- **Time exit at 12:00 ET** if unresolved.
- **No new entries after 11:00 ET**.
- **No v2.4 management specialists** (static brackets).

## 5. Position sizing

Use fixed dollar risk divided by the structure-defined stop distance.
This is level-derived adaptive sizing, capped by Apex limits.

## 6. Required indicators / data

15-minute opening range, ATR(20) on 5-minute bars, VWAP for optional
sanity checks, 1-minute and 2-minute confirmation bars, and 1-second
execution bars. Current MNQ data supports this.

## 7. Differentiation (vs already-tested strategies)

Noise_brk was a fixed 9:36 breakout (continuation, failed). batch-1
Failed ORB Fade used the same "fade failure" structure but lacked
the 2-min-close-back-inside confirmation; signals were less
disciplined. This candidate's confirmation requires TWO 1-min closes
back inside, eliminating wick-only reversals.

The reframing on 2026-05-17 dropped the originally-claimed
acceptance mode; the rejection-only design is structurally clean and
empirically supported (79.5% reversion rate; Section 9).

It is not PRJ_3-like: no fractal pullback levels, no T+2 confirmation,
and no fixed 25/10/80 brackets.

## 8. Required research before spec drafting

- Pre-commit OR_width / ATR thresholds before testing.
- Decide whether 15-minute OR is correct or whether 30-minute OR is more
  stable.
- Curve-fit risk is real because this strategy has a mode switch; the
  thresholds must not be tuned after seeing results.
- Verify enough no-trade days remain acceptable for Apex eval pace.

## 9. Source / references

Opening range and failed-break-fade interpretation from auction-market
and intraday trading practice.

**MNQ-specific empirical evidence** (added 2026-05-17 to address R1):

Diagnostic at
`nb_lib/scripts/diagnostic_orws_failed_break_reversion.py` measured
the failed-break reversion rate on MNQ in-sample data from 2024-08-01
to 2025-01-31:

- Trading days with computable OR: 127
- Total OR-break events (post-OR through 11:00 ET): 161
- Reversion within 30 minutes: 128 (**79.5%**)
- Up-break reversion: 79.7% (63 of 79)
- Down-break reversion: 79.3% (65 of 82)
- Median minutes-to-reversion: 2.0
- Continuation (no reversion within 30 min): 33 (20.5%)

The 79.5% reversion rate is substantially above the 50% null
hypothesis. The symmetric up/down reversion rates support two-sided
operation. The 2-minute median time-to-reversion is consistent with
the 2-min-close-back-inside trigger specification.

Output JSON: `nb_lib/probe_results/opening_range_width_switch_r1_diagnostic.json`.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch 2 (dynamic adaptive intraday focus). |
| 2026-05-17 | `untested-ideation` (retrofit v2) | Retrofitted to template v2 + R4 probe v1.2 (first candidate under v1.2 default 20-day window). Probe run on 2024-09-09 to 2024-10-04: **18 signals fired, 17 passing fill-time guards (5.6% attrition — lowest of any candidate probed)**, extrapolated 22-89 tradeable per 60 days, sparsity moderate, low_confidence_attrition false. Direction balance: 11L/7S (61% long, within bounds). **Empirical finding: the wiki's "acceptance mode" (ratio ≤ 0.35) is structurally unreachable** — probe found OR_width/ATR(20, 5m) ratios in [2.20, 5.78] across all 23 days. The candidate operates as REJECTION-ONLY in practice. R2 quantified: $300 risk/trade, cluster 6 × $300 = $1,800 (cluster/floor 0.90 TIGHT). Probe drift: median 9.38pt, p95 38.00pt — within bracket-absorption capacity. |
| 2026-05-17 | `phase-0-conditionally-admissible` | Phase 0 v2 evaluation under v1.2. **Verdict: CONDITIONALLY ADMISSIBLE.** Tally: R2, R3, R4, R5 MET; R1 PARTIAL. R1 gap is the mode-switch design defect (acceptance mode unreachable as written; ATR period mismatch) plus folklore-only edge thesis. To progress to FINAL spec, address R1 via wiki revision (drop acceptance mode, reframe as rejection-only; or re-specify ATR period) plus supply MNQ-specific failed-break reversion-rate diagnostic. R2 is TIGHT (0.90) with stop-floor concern at the 3pt observed minimum (spec stage MUST add stop-floor guard). **First candidate completed under the full v1.2 pipeline.** Report at `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_2_opening_range_width_switch.md`. |
| 2026-05-17 | `untested-ideation` (R1 resolution) | **R1 resolved via wiki reframing + MNQ diagnostic.** Wiki Sections 1, 2, 3, 4, 7, 9, tagline edited to drop the unreachable acceptance mode; candidate reframed as **rejection-only**. Section 9 now cites MNQ-specific empirical evidence: failed-break reversion rate diagnostic measured **79.5% reversion within 30 min** across 161 OR-break events over 127 in-sample days (79.7% up / 79.3% down — direction-symmetric; median 2.0 min to reversion). Diagnostic at `nb_lib/scripts/diagnostic_orws_failed_break_reversion.py`, output at `nb_lib/probe_results/opening_range_width_switch_r1_diagnostic.json`. Frontmatter admissibility unchanged from v1.2 probe (still rejection-only signals 17/18 passing fill guards). Re-evaluation: see next status_history row. |
| 2026-05-17 | `phase-0-admissible` | **Phase 0 v2 re-evaluation under v1.2 after R1 resolution.** Tally: R1 MET (empirically supported with 79.5% MNQ reversion rate); R2 MET (TIGHT); R3 MET; R4 MET; R5 MET. **Verdict: ADMISSIBLE FOR PHASE 1.** First fully ADMISSIBLE candidate under the v1.2 pipeline. Eligible for Phase 1 entry preflight. The R2 TIGHT margin and 3pt minimum stop concern remain spec-stage considerations (FINAL spec must add stop-floor guard). Report at `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_2_opening_range_width_switch_re-eval.md`. |
| 2026-05-17 | `phase-1-preflight-passed` | **Phase 1 entry preflight PASSED.** 469 in-sample days; 464 eligible. **278 signals fired, 267 passing fill-time guards** (3.96% attrition — lowest of any candidate). Actual 34.5/60d **WITHIN probe range [22, 89]** — methodology fully validated. Direction balance: 140L / 127S (52.4% long — well-balanced, probe's 61% L bias washed out at scale). Stable monthly distribution (10-18 signals/month across 18 months; no zero-months). All 5 weekdays produce signals (Mondays included — no stale-prior issue). Stop distance distribution: mean 37.94pt, p50 33.00pt, range [5.75, 107.50] — **wider than wiki R2 frontmatter [3, 65]**; spec stage MUST add 8pt stop-floor guard. TP distances clean: [5.12, 161.00]. **Second candidate to reach FINAL-spec-ready under the methodology-clean pipeline.** Report at `C:/VMShare/NT8lab/nb_lib_phase1_preflight_opening_range_width_switch_report.md`. |
| 2026-05-17 | `spec-drafted-final` | FINAL spec drafted at `nb_lib/strategy_specs/canonical/opening_range_width_switch_spec_FINAL.md` (16 sections, 4102 words). **Second candidate to reach FINAL spec under methodology-clean pipeline; first under complete v1.2 pipeline.** Preflight findings drove parameters: 8pt stop-floor guard (rejects ~10-15% of signals with stops below BAND_B-friction-tolerable threshold), stop band [8, 120]pt, TP-distance band [5, 200]pt, ATR-sanity band [4, 50]. Zero v2.4 specialists (deliberate; OR-midpoint thesis coherent with static brackets). Risk $300/trade, contract cap 12, DLL 2, max-one-per-day. Time exit 60 min (tighter than prior_day_VA's 90 — OR mean-reversion expected faster than POC mean-reversion). Pre-committed Section 7 pass criteria: PF >= 1.50, n >= 150, no FAILED, asymmetry <= 65%, no 6+ loss clusters. **OOS-ELIGIBLE** if criteria met (not bypass). Higher pre-test prior (0.30 OOS-edge) than any prior candidate due to R1 evidence quality and end-to-end validated methodology. |
| 2026-05-17 | `tested-apex-failure` | Implementation + in-sample test complete. **629/629 tests pass** (55 new). 62 trades over Aug 1 → Dec 4 before **account FAILED** via compliance_drawdown ($2,000.50 max DD breached the $2K trailing floor by 50 cents on trade #62 of 62). PF 1.07 (just above breakeven), win rate 53.2% (33W/29L), total **+$603.90** (positive absolute P&L but Apex-busting trailing-DD geometry). Section 7 verdict: 7.4 PASS (55% L); **7.1, 7.2, 7.3 FAIL**. Does NOT graduate. Implementation bug surfaced (TradeLifecycle requires `use_runner=True` for partial close; cost ~250 trades to 17 before fix). Methodology pipeline executed cleanly otherwise: probe predicted [22, 89] tradeable/60d; pre-FAIL rate matched at ~0.7 trades/day. **Strategy mechanics failure, not methodology failure** — trailing-DD geometry incompatible with high per-trade variance (best day +$1,149 vs worst -$338). 11-fleet Apex-failure pattern. Report at `C:/VMShare/NT8lab/nb_lib_opening_range_width_switch_implementation_report.md`. |
| 2026-05-18 | (no status change) | Failure-mode investigation. **Peak at trade #46 (Oct 30)**: a single short trade hit TP1+TP2 for +$996.50, pushing cum to $2,604 and immediately setting trailing floor at $604. Subsequent 16-trade Nov-Dec drawdown eroded the $2,000 cushion through **regime sensitivity**, not cluster losses (max consecutive losses was only 3; DLL never triggered). Distribution analysis: **median trade +$48; top trade +$1,148 = 190% of total net P&L; net excluding top trade is -$544.80** — strategy is tail-driven, not consistent-edge. Counterfactual: at risk_dollars=$250 (not $300), no breach. At $200, no breach with margin. Aug-Oct phase: 61% WR +$2,604; Nov-Dec phase: 31% WR -$2,001 (same strategy, different regime). **Engineering finding**: lowering risk to $250 would have saved Apex on this window. **Composition role**: solo Apex eval at $250 risk likely viable; portfolio tail-capture component with regime-diversification partner viable; solo high-edge workhorse NOT viable. **No spec change, no re-test** — post-result tuning avoided. Investigation surfaced two potential v1.4 methodology gates: edge-stability check (net excluding top-K trades) and regime-conditional outcome check (per-bucket PF variance). Report at `C:/VMShare/NT8lab/nb_lib_opening_range_width_switch_failure_investigation.md`. |
| 2026-05-25 | (no status change) | **v1.3 R2 variance preflight applied retrospectively** — methodology validation, not strategy re-attempt. Simulated 267 Phase-1 preflight passing signals with no-friction bracket geometry. Results: total $15,322 sim P&L (vs actual $603), PF 1.47 (vs actual 1.07), **max running DD $1,805.50** (vs actual $2,000.50 — friction degradation $195 effect), max consecutive losses 5, trailing-DD breach FALSE in sim (vs TRUE in actual). **Verdict: MARGINAL** — 3/4 v1.3 gates PASS; max-DD gate FAILS by $305 ($1,805 sim > $1,500 threshold). **The $1,500 gate's $500 friction buffer was almost exactly calibrated**: actual friction effect was $195, well within $500 budget. **If v1.3 had existed pre-implementation**, MARGINAL verdict would have routed ORWS to spec revision (lower risk, tighter TP2, daily P&L cap) BEFORE in-sample test — matching the engineering fixes the 2026-05-18 failure investigation later identified. **End-to-end methodology v1.0→v1.5 pipeline now validated against historical failures.** Validation does NOT change ORWS status (remains tested-apex-failure); no spec revision; no re-implementation. Variance probe at `nb_lib/scripts/probe_r2_variance_opening_range_width_switch.py`. Output at `nb_lib/probe_results/opening_range_width_switch_r2_variance_probe.json`. Validation report at `C:/VMShare/NT8lab/nb_lib_v1_3_variance_preflight_orws_retrospective_validation.md`. |
