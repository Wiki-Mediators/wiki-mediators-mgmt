---
name: "Prior Day Value Area Rejection"
tagline: "Trade failed acceptance outside yesterday's value."
status: "tested-rejected"
created: 2026-05-12
updated: 2026-05-14
source: "Inspiration: Market Profile and auction market theory. Retrofitted to template v2 on 2026-05-14."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-15:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "mean-reversion"
indicators: ["PriorDayVolumeProfile", "VAH", "VAL", "POC", "ATR(20)"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "volatility-adaptive"
position_sizing: "fixed-risk-dollar"

# Cross-references
canonical_spec: "nb_lib/strategy_specs/canonical/prior_day_value_area_rejection_spec_FINAL.md"
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
    expected_stop_distance_pts_range: [20, 60]
    expected_loss_dollars_per_trade: 300
    worst_plausible_cluster_n: 5
    worst_plausible_cluster_dollars: 1500
    cluster_vs_floor_ratio: 0.75
    favorable_first_week_independent: false
  r4_signal_frequency:
    probe_convention_version: "v1"
    probe_script: "nb_lib/scripts/probe_r4_prior_day_value_area_rejection.py"
    probe_output: "nb_lib/probe_results/prior_day_value_area_rejection_r4_probe.json"
    probe_window_start: "2024-10-07"
    probe_window_end: "2024-10-11"
    probe_n_signals_observed: 2
    probe_n_long: 0
    probe_n_short: 2
    probe_distinct_days_with_signal: 2
    expected_signals_per_60_trading_days: [12, 48]
    sparsity_class: "sparse"
    sparsity_class_rationale: "2 signals over 5 days; on sparse/moderate boundary, lower than the project's target band of 30+ trades over 12-start multistart. Direction asymmetry (0L/2S) is a FLAG at small sample but consistent with prior MNQ regime."

# Tags
tags:
  - rth-only
  - intraday
  - mean-reversion
  - volume-profile
  - fixed-risk-dollar
---

# Prior Day Value Area Rejection

## 0. Admissibility summary

- **R1 (edge thesis)**: Failed acceptance outside the prior day's
  value area identifies trapped auction activity (responsive sellers
  above VAH, responsive buyers below VAL). Market Profile / auction
  market theory provides the participant-behavior story. The wiki
  cites this literature; the operational definition tightens
  "rejection" to two consecutive 5-min closes back inside value, which
  separates rejection from intra-bar wicks.
- **R2 (Apex survival)**: Risk $300/trade. Expected stop distance
  20-60 pts (auction extreme + small buffer); loss per trade ≈ $300
  by sizing construction. Worst plausible cluster: 5 consecutive
  losses = $1,500 (cluster/floor = 0.75 — survivable). Strategy does
  NOT require a favorable first week. See Section 5.
- **R3 (management lifecycle)**: No v2.4 specialists used. Static
  brackets: stop at auction extreme, TP1 = entry-to-POC midpoint, TP2
  = POC, time exit at afternoon cutoff. Max one trade per day caps
  exposure. Choosing static brackets avoids management-design-dead.
- **R4 (signal frequency)**: Probe run 2026-05-14 on 5 trading days
  (2024-10-07 to 2024-10-11): 2 signals observed (0 long, 2 short),
  1 per signal day, both at 10:00-11:00 ET. Extrapolated to a 60-
  trading-day window: 12-48 signals. Sparsity class: sparse (on the
  sparse/moderate boundary). Probe caveats: volume profile uses 1-min
  midpoint approximation; "holds inside value" pinned to 1-min close
  inside [VAL, VAH] + wick ≤ 2pt from failed extreme.
- **R5 (direction handling)**: Two-sided by design (long below VAL,
  short above VAH). Probe shows 0L/2S — a 100% asymmetry at n=2.
  Pre-committed asymmetry interpretation: if Phase 1 confirms a
  > 2:1 short bias at meaningful n, this is FLAGGED as a likely
  regime-driven artifact (MNQ uptrend bias means below-VAL setups
  may be rarer than above-VAH setups in this in-sample window), NOT
  a strategy-edge claim. Direction handling stays two-sided regardless
  to avoid selection bias.

## 1. Thesis

When RTH opens or trades outside the prior day's value area but
cannot accept there, price may revert toward the prior point of
control. This candidate is a stricter value-area re-entry idea, not a
loose repeated bounce system.

The core question is whether failed acceptance outside yesterday's
value identifies trapped auction activity with enough discipline to
avoid overtrading.

## 2. Mechanism (what edge it captures)

- Uses prior RTH market structure: VAH, VAL, and POC.
- Requires failed acceptance outside value before entry.
- Targets POC rather than the opposite value-area extreme.
- Limits firing frequency to avoid repeated chop entries.

## 3. Signal logic (entry conditions)

Build the prior RTH volume profile and compute VAH, VAL, and POC.
Long setup: price trades below VAL, then prints two consecutive
5-minute closes back above VAL. Short setup: price trades above VAH,
then prints two consecutive 5-minute closes back below VAH.

Entry is on the first 1-minute pullback that holds inside value. Max
one trade per day.

**Pre-committed predicates:**

- Prior RTH volume profile: 1-pt bins, 70% value-area calculation,
  midpoint-volume attribution from 1-min OHLCV bars.
- VA computation method: smallest contiguous price range around POC
  containing 70% of prior-RTH volume.
- "Trade outside value": any 1-min high > VAH (short) or low < VAL
  (long) during current RTH.
- "Two consecutive 5-min closes back inside": two adjacent 5-min bars
  both with close in [VAL, VAH].
- "1-min pullback that holds inside": 1-min close in [VAL, VAH] AND
  wick within 2pt of the failed extreme (within 20 1-min bars of the
  5-min setup).
- Time window: 09:30-15:00 ET.
- Max one trade per RTH day.

## 4. Exit logic (stops, targets, time-based exits)

Stop outside the failed auction extreme. TP1 is the midpoint from
entry to POC. TP2 is POC. No runner beyond POC. Time exit if POC has
not been reached by a pre-committed afternoon cutoff.

**No v2.4 management specialists.** Static brackets only.

## 5. Position sizing and Apex survival rationale

**Risk: $300 per trade**, fixed-dollar, sized to auction-extreme stop
distance per `contracts = floor($300 / (stop_pts × $2)).clamp(1, 12)`.

**Apex survival analysis:**

- $50K starting balance, $2K trailing drawdown floor.
- Stop distance: 20-60 pts (failed auction extreme + 2-tick buffer).
  Typical ≈ 35 pts → 4 contracts → $280-300 loss at full stop.
- **Worst plausible cluster: 5 consecutive losses = $1,500.** Five VA-
  rejection setups in a row that fail (price accepts the breakout
  rather than reverting to POC) is plausible during a trend day
  sequence. With max-one-trade-per-day, 5 consecutive losses requires
  5 trading days — about one trading week of bad sequencing.
- **Cluster/floor ratio = 0.75.** Survivable with margin: cluster
  reaches 75% of floor.
- **Favorable-first-week independence: FALSE.** Probe extrapolation
  is 12-48 trades over 60 days; max-one-per-day means trade density
  is bounded. A bad first-week cluster directly damages the trailing
  drawdown floor without a prior cushion.
- **Comparison to closest tested relative**: vwap_stretch_snapback
  (tested-rejected 2026-05-12) was the closest mean-reversion
  relative. It used VWAP-band bounce; this candidate uses VA
  rejection. Key Apex difference: vwap_stretch_snapback's stop was
  ~10-15pt (tight band-anchored), producing 5-7 contract sizes; this
  candidate's stop is 20-60pt (wider auction extreme), producing 2-5
  contract sizes. The stop is structurally less prone to single-tick
  puncture in fast regimes.

**R2 verdict-readiness**: cluster/floor 0.75 is acceptable. Probe
extrapolation supports the cluster-loss assumption (≈1 trade/day max
on signal days, ~50% signal-day rate from probe).

## 6. Required indicators / data

MNQ 1-second or 1-minute bars with volume, prior-day volume profile
(computed via the probe convention's 1-min midpoint method), VAH, VAL,
POC, and ATR for sanity bounds. nb_lib needs a volume-profile
primitive at spec stage; probe uses a strategy-local implementation.

## 7. Differentiation (vs already-tested strategies)

The tested strategies did not use prior-day auction structure and
were mostly morning trend or breakout concepts. This candidate is
value-based mean reversion, requires acceptance failure, targets POC,
and limits to one trade per day.

The closest mean-reversion relative is vwap_stretch_snapback
(tested-rejected). The mechanism here is structurally different (prior-
day auction structure vs intraday VWAP), but the mean-reversion-
failure-via-trend-day risk is shared. Section 5 addresses the stop
geometry difference that bears on Apex survival.

## 8. Required research before spec drafting

**R2/R4 not deferred to this section under template v2.**

Spec-stage items only:

- Volume profile primitive: implement as nb_lib indicator or keep
  strategy-local? Probe used strategy-local.
- Volume-at-price approximation: probe uses 1-min midpoint-volume
  attribution. Spec may want a higher-resolution method (1-sec) or
  a true tick-volume primitive if available.
- Pin afternoon-cutoff time for time-exit.
- Pin POC-target tolerance (exact-touch vs ±N tick proximity).

## 9. Source / references

Market Profile and auction market theory (Steidlmayer, Dalton). The
participant-behavior story (responsive buyers/sellers reverting price
to POC when failed acceptance occurs outside value) is the literature-
grounded edge claim. This candidate operationalizes that story with
specific predicates rather than relying on discretionary recognition.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | Created by Codex 5.5 CLI batch 2 (Market Profile / auction theory class). |
| 2026-05-14 | `untested-ideation` (retrofit) | Retrofitted to template v2. R4 probe run 2026-05-14 on 5 trading days: 2 signals (0L/2S — direction asymmetry FLAGGED), extrapolated 12-48 per 60 days, sparsity sparse-boundary. R2 quantified: $300 risk/trade, worst-plausible cluster 5 losses = $1,500 (cluster/floor 0.75). Probe output at `nb_lib/probe_results/prior_day_value_area_rejection_r4_probe.json`. |
| 2026-05-14 | `phase-0-admissible` | Phase 0 v2 evaluation complete. Verdict: **ADMISSIBLE FOR PHASE 1.** Tally: all 5 requirements MET (R1 grounded in Market Profile literature; R2 cluster/floor 0.75 acceptable with max-one-trade-per-day cap; R3 no-management plainly stated, no-runner-beyond-POC thesis-coherent; R4 probe-derived; R5 pre-committed asymmetry interpretation). **First ADMISSIBLE verdict across five Phase 0 evaluations.** Caveats: R4 sparsity on lower boundary; direction asymmetry (0L/2S at probe n=2) is small-sample but real. Eligible for Phase 1 entry preflight when scheduled. Report at `C:/VMShare/NT8lab/nb_lib_phase0_v2_prior_day_value_area_rejection.md`. |
| 2026-05-14 | `phase-1-preflight-passed` | Phase 1 entry preflight complete over full in-sample (2024-08-01 to 2026-01-31, 469 trading days). **Probe extrapolation validated:** actual 137 signals over 374 eligible days = 22.0/60d, within probe range [12, 48]. Direction asymmetry resolved to 57L/80S (41.6% long, well under pre-committed 2:1 regime-artifact trigger). Per-month distribution stable (5-11/month, no zero-months). **Anomaly: 0 Monday signals** (likely stale-Friday-VA after weekend gap). **Stop-distance discovery:** actual stops mean 70.7pt p50 60.25pt range [8.75, 251.25] — wiki R2 pinned [20, 60] is too narrow; spec-stage stop-band guard required. **Methodology meta-finding:** first candidate in 15 iterations to pass Phase 0 v2 + have probe validated by preflight. Eligible for FINAL spec drafting. Preflight artifacts at `C:/VMShare/NT8lab/prior_day_value_area_rejection_preflight_*.csv|.json`. Report at `C:/VMShare/NT8lab/nb_lib_phase1_preflight_prior_day_value_area_rejection_report.md`. |
| 2026-05-14 | `spec-drafted-final` | FINAL spec drafted at `nb_lib/strategy_specs/canonical/prior_day_value_area_rejection_spec_FINAL.md` (16 sections, 4465 words). **First candidate to reach FINAL spec under admissibility-clean methodology** (template v2 + probe v1 + Phase 1 preflight). Preflight findings drove key parameters: stop-band guard [8, 100]pt (rejects 251pt outlier), TP-distance guard [5, 150]pt (rejects negative-POC and unreachable tails), explicit Monday skip (preflight 0/137 on Mondays). Zero v2.4 specialists (deliberate; mean-reversion-to-POC thesis is coherent with static brackets). Risk $300/trade, contract cap 12, DLL 2, max-one-per-day. Pre-committed Section 7 pass criteria: PF >= 1.50, n >= 80, no FAILED, asymmetry <= 65%, no 6+ loss clusters. **OOS-ELIGIBLE** if criteria met (not bypass). |
| 2026-05-15 | `tested-rejected` | Implementation + in-sample test complete. **574/574 tests pass** (57 new). 14 trades over 469-day in-sample window; PF 1.17, win rate 78.6% (11W/3L), total +$70.20. **Account SURVIVED Apex** ($50,070 final, peak $50,201, max DD $220.80 — well within $2K floor). Section 7 verdict: 7.3 PASS, 7.4 PASS (35.7%L), 7.5 PASS (3 losses); **7.1 FAIL (PF 1.17 < 1.50)**, **7.2 FAIL (n=14 < 80)**. Does NOT graduate to OOS. **Major methodology finding:** preflight's 137 structural signals attritted 89.8% to 14 tradeable trades due to 1-sec drift between pullback_close (signal-id reference) and entry_price (fill-time reference). R4 probe v1 ignores fill mechanics; v1.1 recommended. Failure pattern shifts from "Apex blowup" to "Apex-safe-but-no-edge" — first such outcome in 10 candidates. Report at `C:/VMShare/NT8lab/nb_lib_prior_day_value_area_rejection_implementation_report.md`. |
| 2026-05-16 | (no status change) | v1.1 retrospective probe run for methodology validation. **v1.1 on the default 5-day sample window did NOT catch the 90% attrition** that the in-sample test revealed: 2 signals fired, both passed fill-time guards (0% attrition), extrapolated [12, 48]/60d (same as v1). Sample-size variance dominates: the 5-day window contained only short-drift signals (median 6.62pt, p95 11.50pt) while the full 137-signal sample had p95 28.25pt drift. Methodology learning: v1.1 sample-window choice is more determinative than probe version. Recommendation for future v1.2 convention iteration: extend default window to 15-20 days OR add a full-window v1.1 preflight stage before FINAL spec drafting. Candidate status remains `tested-rejected`. Probe output at `nb_lib/probe_results/prior_day_value_area_rejection_r4_probe_v1_1.json`. Report at `C:/VMShare/NT8lab/nb_lib_phase0_v1_1_retrospective_prior_day_value_area_rejection.md`. |
