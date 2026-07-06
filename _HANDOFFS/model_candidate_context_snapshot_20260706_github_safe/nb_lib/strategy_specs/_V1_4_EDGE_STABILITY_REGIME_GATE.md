# v1.4 Edge-Stability + Regime-Conditional Gate

**Version:** v1.4  
**Created:** 2026-05-18  
**Status:** working methodology gate  
**Scope:** candidate selection before FINAL spec / implementation  

This gate extends the existing template-v2 / R4 v1.2 admissibility
workflow. It does not replace R1-R5. It adds two requirements before a
candidate may graduate from wiki inventory to FINAL spec drafting:

- **R6 edge-stability:** the candidate must show that its signal
  opportunity is not concentrated in one small slice of in-sample data.
- **R7 regime-conditional thesis:** the candidate must define, before
  P&L testing, the market regime in which its edge is expected to exist
  and the regimes in which failure is expected.

The purpose is not to make the gate harder for its own sake. The recent
fleet showed that a one-window R4 pass can be too thin: it proves a
predicate can fire, but not that the candidate has enough stable
opportunity to justify implementation.

## 1. Existing Requirements Remain Active

Candidates still need the template-v2 admissibility surface:

| Gate | Requirement |
|---|---|
| R1 | Edge thesis: participant behavior and why it should work on MNQ |
| R2 | Apex survival thesis, including fixed-risk sizing and cluster-loss reasoning |
| R3 | Management lifecycle compatibility or explicit no-management scope |
| R4 | Signal-frequency probe per `_R4_PROBE_CONVENTION.md` |
| R5 | Direction handling rationale |

v1.4 adds R6 and R7. A candidate that fails R1-R5 does not reach v1.4.

## 2. R6 Edge-Stability Gate

**Question:** does the candidate produce tradeable signals across enough
independent in-sample slices that implementation is not just chasing one
good week?

### 2.1 Required Diagnostic

Run a no-P&L signal-stability probe inside the in-sample window only:

- Monthly slices from 2024-08 through 2026-01, or the largest subset
  supported by required warmup.
- For each month, count structural signals and fill-guard-passing
  signals.
- Use the candidate's existing R4 predicates; do not tune thresholds.
- Do not compute realized P&L.
- Do not load or touch OOS data beginning 2026-02-01.

### 2.2 Required Fields

The probe output must report:

```json
{
  "candidate_id": "<candidate>",
  "gate_version": "v1.4",
  "oos_guard": "assert max_date < 2026-02-01",
  "months_evaluated": 18,
  "months_with_signal": 0,
  "months_with_fill_guard_passing_signal": 0,
  "total_structural_signals": 0,
  "total_tradeable_signals": 0,
  "max_month_signal_share": 0.0,
  "median_tradeable_signals_per_active_month": 0.0,
  "zero_signal_months": 0,
  "signals_by_month": {
    "2024-08": 0
  },
  "verdict": "PASS | MARGINAL | FAIL"
}
```

### 2.3 R6 Verdict Rules

Default informed-prior thresholds:

| Verdict | Rule |
|---|---|
| PASS | `months_with_tradeable_signal >= 6`, `total_tradeable_signals >= 60`, and `max_month_signal_share <= 0.35` |
| MARGINAL | `months_with_tradeable_signal >= 4`, `total_tradeable_signals >= 30`, and `max_month_signal_share <= 0.50` |
| FAIL | Anything below MARGINAL |

These are not calibrated thresholds. They are guardrails to prevent a
single R4 sample window from carrying too much methodology weight.

## 3. R7 Regime-Conditional Gate

**Question:** is the candidate's expected edge explicitly tied to a
measurable regime before P&L is observed?

### 3.1 Required Regime Declaration

Each candidate must pre-declare:

- Primary regime variable(s), computed lookahead-clean.
- Expected favorable regime.
- Expected unfavorable regime.
- Whether the regime is an entry gate, an attribution tag, or both.
- What result would falsify the regime thesis.

Examples:

| Candidate family | Plausible regime declaration |
|---|---|
| Wide-state reversal | favorable when SMA20/SMA200 separation is wide and price is extended beyond SMA20; unfavorable in tight/middle state |
| Tight-state breakout | favorable when SMA20/SMA200 compression resolves with strong first-hour bar anatomy; unfavorable in wide state |
| Opening-range rejection | favorable when opening range is wide enough to represent extension, not balance |

### 3.2 Required Regime Attribution

The v1.4 probe must emit signal counts by regime bin:

```json
{
  "regime_bins": {
    "wide_downside": {"signals": 0, "tradeable": 0},
    "wide_upside": {"signals": 0, "tradeable": 0},
    "tight": {"signals": 0, "tradeable": 0},
    "middle": {"signals": 0, "tradeable": 0}
  }
}
```

For candidates whose entry predicate already requires the favorable
regime, the attribution still matters: it confirms that the strategy is
not silently firing outside its claimed state because of implementation
or warmup mistakes.

### 3.3 R7 Verdict Rules

| Verdict | Rule |
|---|---|
| PASS | Regime is measurable, lookahead-clean, present in the probe output, and candidate signals are concentrated in the declared favorable regime |
| MARGINAL | Regime is measurable but the candidate's causal story is weak or the bin has sparse sample |
| FAIL | Regime is vague, post-hoc, unavailable in current data, or not represented in the probe |

## 4. Candidate Inventory Screen

The live wiki has more than 13 `untested-ideation` files, but only a
smaller subset currently carries R4 v1.2 probe metadata. v1.4 should be
applied first to candidates with existing quantitative R4 data; older
untested ideas need template-v2 retrofit before they can be compared.

### 4.1 R4-Ready Untested Candidates

| Candidate | R4 tradeable signals | R4 extrapolated / 60d | Status under v1.4 |
|---|---:|---:|---|
| `tight_open_breakout_long` | 1 | 1-7 | Reject for R6 pre-screen; too sparse |
| `tight_open_breakout_short` | 1 | 1-7 | Reject for R6 pre-screen; too sparse |
| `tight_opening_window_breakout_long` | 16 | 25-102 | Already informational-tested; do not pick as fresh candidate |
| `tight_opening_window_breakout_short` | 7 | 11-45 | Possible but sparse; lower priority |
| `tight_problem_bar_removal_long` | 0 | 0-0 | Reject for R6 pre-screen |
| `tight_problem_bar_removal_short` | 0 | 0-0 | Reject for R6 pre-screen |
| `wide_opening_window_reversal_long` | 14 | 22-89 | R6/R7 candidate |
| `wide_opening_window_reversal_short` | 16 | 25-102 | R6/R7 candidate |
| `wide_reversal_long` | 0 | 0-0 | Reject for R6 pre-screen |
| `wide_reversal_short` | 0 | 0-0 | Reject for R6 pre-screen |

### 4.2 Older Untested Ideas

These entries remain inventory, but cannot be fairly compared under
v1.4 until they are retrofitted to template-v2 with R4 v1.2 and R2
variance fields:

- `atr_percentile_trend_day_hold`
- `atr_ratio_expansion_scalp`
- `closing_imbalance_drift_proxy`
- `developing_swing_trail_vol_cap`
- `es_leads_nq_divergence_reversion`
- `failed_orb_fade`
- `first_loss_reversal_day`
- `gold_vs_nq_risk_off_rotation`
- `initial_balance_midpoint_rotation`
- `lunch_compression_break`
- `mnq_news_like_impulse_pullback`
- `momentum_high_water_trail_post_1030`
- `news_first_pullback_momentum`
- `prior_close_magnet_vol_filter`
- `prior_day_extreme_acceptance_ladder`
- `vwap_band_acceptance_regime`

Some of these may later be strong candidates, but selecting them now
would skip the newer gate discipline.

## 5. Current Pick

**Selected next candidate family:** `wide_opening_window_reversal`
using the paired wiki entries:

- `wide_opening_window_reversal_long`
- `wide_opening_window_reversal_short`

This is the cleanest v1.4 pick because:

1. It already has R4 v1.2 data with moderate signal frequency on both
   sides.
2. It is explicitly regime-conditional: the edge thesis is wide-state
   mean reversion from SMA20/SMA200 expansion back toward the cluster.
3. It is not a continuation-class repeat of the already weak-tested
   `tight_opening_window_breakout_long`.
4. It is structurally different from VWAP/value-area mean reversion:
   the anchor is moving-average state expansion, not VWAP stretch or
   prior-day auction levels.
5. It should be tested as a paired family before deciding direction,
   because both directions have similar R4 counts and the methodology
   prefers not to make a post-hoc long-only or short-only choice.

## 6. Next Execution Step

Before FINAL spec drafting, run a v1.4 diagnostic only:

`nb_lib/scripts/probe_v14_wide_opening_window_reversal_family.py`

The script should:

- Import or reuse the existing long/short R4 predicate logic without
  changing thresholds.
- Evaluate monthly slices from 2024-08 through 2026-01.
- Emit signal counts, fill-guard-passing counts, and regime bins by
  month.
- Compute R6 edge-stability verdict.
- Compute R7 regime-conditional verdict.
- Write JSON to:
  `nb_lib/probe_results/wide_opening_window_reversal_family_v14_probe.json`
- Write a short report to:
  `C:/VMShare/NT8lab/nb_lib_wide_opening_window_reversal_v14_gate_report.md`

No P&L, no fills beyond the existing R4 fill-geometry guard, no
strategy implementation, and no OOS data.

## 7. Promotion Rule

The candidate family may move to FINAL spec drafting only if:

- R6 is PASS or MARGINAL, and
- R7 is PASS, and
- the report confirms no OOS access, and
- the operator explicitly approves promotion after reading the report.

If R6 fails, the family stays in wiki inventory but does not progress.
If R7 fails, the family is conceptually incoherent as a regime strategy
and should be rewritten or closed before any test.

