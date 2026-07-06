---
name: "<Strategy Name>"
tagline: "<one-line tagline>"
status: "untested-ideation"
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
source: "<one-line origin>"

# Market and timing
markets: ["MNQ"]
session: "RTH"  # or "ETH"
time_of_day: "<HH:MM-HH:MM ET>"
hold_duration: "intraday"  # or "swing", "scalp", "weekly-event"

# Signal characteristics
signal_type: "<class>"  # e.g., "mean-reversion", "trend-continuation", "level-acceptance"
indicators: [<list>]
timeframes_used: [<list>]

# Execution
brackets: "<class>"
position_sizing: "<class>"

# Cross-references
canonical_spec: null
implementation: null
related_candidates: [<list>]

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

# Phase 0 readiness — REQUIRED for admissibility under template v2
admissibility:
  # R1 evidence diagnostic (v1.4+; required for new candidates)
  r1_edge_thesis:
    r1_diagnostic_convention_version: null   # REQUIRED (v1.4+): "v1" or "v1.1" (v1.1 = methodology v1.5)
    r1_diagnostic_script: null               # REQUIRED (v1.4+): relative path
    r1_diagnostic_output: null               # REQUIRED (v1.4+): relative path to JSON
    r1_diagnostic_window: null               # REQUIRED (v1.4+): ["YYYY-MM-DD", "YYYY-MM-DD"]
    r1_lookahead_minutes: null               # REQUIRED (v1.4+): per-class default (30/60/90) or pre-committed override
    r1_mechanism_class: null                 # REQUIRED (v1.5+): "fast-resolution" | "moderate" | "slow-resolution"
    r1_n_qualifying_events: null             # REQUIRED (v1.4+): int
    r1_low_confidence: null                  # REQUIRED (v1.5+): bool — true if n < 15
    r1_compound_filter_over_restrictive: null  # REQUIRED (v1.5+): bool — true if joint regime gate pass < 10%
    r1_reversion_rate: null                  # REQUIRED (v1.4+): float
    r1_neither_rate: null                    # REQUIRED (v1.4+): float; >0.25 flags lookahead-window mismatch
    r1_verdict: null                         # REQUIRED (v1.4+): "MET" | "PARTIAL" | "NOT MET" | "INCONCLUSIVE"

  r2_apex_survival:
    # Theoretical (pre-variance-probe; v1.2 baseline)
    risk_dollars_per_trade: null            # REQUIRED: integer dollars (e.g., 200, 300, 500)
    expected_stop_distance_pts_range: null  # REQUIRED: [min, max] points
    expected_loss_dollars_per_trade: null   # REQUIRED: integer dollars at typical stop
    worst_plausible_cluster_n: null         # REQUIRED: consecutive-loss count that plausibly happens in-sample
    worst_plausible_cluster_dollars: null   # REQUIRED: cluster_n * loss_dollars_per_trade
    cluster_vs_floor_ratio: null            # REQUIRED: cluster_dollars / 2000 — must be < 1.0 to survive
    favorable_first_week_independent: null  # REQUIRED: true | false (with rationale in body Section 5)
    # Variance-probe-derived (v1.3+; required for candidates that reach Phase 1 preflight)
    r2_variance_probe_version: null         # REQUIRED (v1.3+): e.g., "v1"
    r2_variance_probe_script: null          # REQUIRED (v1.3+): relative path
    r2_variance_probe_output: null          # REQUIRED (v1.3+): relative path to JSON
    r2_variance_pf_simulated: null          # REQUIRED (v1.3+): float, no-friction PF
    r2_variance_win_rate: null              # REQUIRED (v1.3+): float
    r2_variance_max_consecutive_losses: null  # REQUIRED (v1.3+): int
    r2_variance_max_running_drawdown_dollars: null  # REQUIRED (v1.3+): float
    r2_variance_trailing_dd_breach: null    # REQUIRED (v1.3+): bool — hard fail if true
    r2_variance_verdict: null               # REQUIRED (v1.3+): "PASS" | "MARGINAL" | "FAIL"
  r4_signal_frequency:
    probe_convention_version: "v1.2"        # REQUIRED: pin convention version used (current: v1.2)
    probe_script: null                      # REQUIRED: relative path to probe script
    probe_output: null                      # REQUIRED: relative path to probe JSON output
    probe_window_start: null                # REQUIRED: ISO date (sample window inside in-sample)
    probe_window_end: null                  # REQUIRED: ISO date
    probe_n_signals_observed: null          # REQUIRED: structural-signal count
    probe_signals_passing_fill_guards: null # REQUIRED (v1.1+): tradeable count after fill-geometry guards
    probe_attrition_rate: null              # REQUIRED (v1.1+): 1.0 - (passing / fired)
    probe_p95_drift_pts: null               # REQUIRED (v1.1+): 95th-pct |fill-price - signal-fire-price|
    probe_low_confidence_attrition: null    # REQUIRED (v1.2+): true if n_fired < 5
    probe_n_long: null                      # REQUIRED: integer
    probe_n_short: null                     # REQUIRED: integer
    probe_distinct_days_with_signal: null   # REQUIRED: integer
    expected_signals_per_60_trading_days: null  # REQUIRED: [low, high] extrapolated from signals_passing_fill_guards (v1.1)
    sparsity_class: null                    # REQUIRED: "sparse" | "moderate" | "dense" | "very dense"
    sparsity_class_rationale: null          # REQUIRED: short string referencing chop-fade or round-number patterns

# Tags
tags:
  - <list>
---

# <Strategy Name>

## 0. Admissibility summary (FILL AFTER OTHER SECTIONS)

A reader should be able to read this section alone and judge readiness:

- **R1 (edge thesis)**: <one paragraph; cite Section 1 / 9 PLUS the
  R1 diagnostic verdict from frontmatter admissibility.r1_edge_thesis>
- **R2 (Apex survival)**: <one paragraph quoting numbers from frontmatter
  admissibility.r2_apex_survival>
- **R3 (management lifecycle)**: <one paragraph: management used or not,
  if used which specialists; if not, plain statement>
- **R4 (signal frequency)**: <one paragraph quoting probe results from
  frontmatter admissibility.r4_signal_frequency>
- **R5 (direction handling)**: <one paragraph: two-sided vs restricted,
  defense, pre-committed asymmetry interpretation>

### Methodology pipeline order (v1.4)

This candidate must clear each gate in order before advancing:

1. Wiki entry authored (template v2 — this document).
2. **R1 evidence diagnostic** (`_R1_EVIDENCE_DIAGNOSTIC_CONVENTION.md`):
   < 60% reversion → close at this gate.
3. R4 probe v1.2 (`_R4_PROBE_CONVENTION.md`): only if R1 ≥ 60%.
4. Phase 0 v2 review: only if R4 acceptable.
5. Phase 1 entry preflight: only if Phase 0 admissible.
6. R2 variance preflight v1 (`_R2_VARIANCE_PROBE_CONVENTION.md`):
   only if Phase 1 passes; FAIL → spec revision required.
7. FINAL spec drafting: only if variance preflight passes.
8. Implementation + in-sample test.

## 1. Thesis

What participant behavior does this candidate capture? Why on MNQ at
this timeframe? Cite Market Profile / order-flow / volatility literature
or an MNQ-specific empirical observation in Section 9. "Common trader
pattern" alone is INSUFFICIENT.

## 2. Mechanism (what edge it captures)

Bullet the participant-behavior story. Each bullet should name what
participants are doing, not just describe price.

## 3. Signal logic (entry conditions)

State the entry predicates in enough detail that they can be coded
unambiguously. Predicates are what the R4 probe will count.

**Pre-committed predicates (do not change in spec stage):**

- ...
- ...

## 4. Exit logic (stops, targets, time-based exits)

State stops, targets, time exits. **Stop distance must be pinnable into
the R2 frontmatter field `expected_stop_distance_pts_range`.**

## 5. Position sizing and Apex survival rationale

State the risk-dollar number that goes in frontmatter
`r2_apex_survival.risk_dollars_per_trade`. Then defend:

- Why this loss size? (relative to the $2K floor cushion)
- Cluster-loss expectation: worst plausible N consecutive losses on
  this strategy. Cite prior-strategy comparisons or regime reasoning.
- Why does the candidate not require a favorable first week?
- If the closest tested relative failed Apex, explicitly state why this
  candidate's loss distribution differs.

## 6. Required indicators / data

List indicators with their nb_lib paths or note where a primitive is
missing.

## 7. Differentiation (vs already-tested strategies)

Name the strategies this is differentiated from and what's different
mechanism-side (not just label-different).

## 8. Required research before spec drafting

**This section must NOT defer R2 or R4 to "future research."** Items
in this section may include:

- Edge-clarification questions
- Indicator-implementation questions
- Spec-stage parameter choices

But NOT:

- Loss-size estimation (must be in Section 5 / frontmatter)
- Signal-frequency estimation (must be in Section 0 / frontmatter,
  derived from R4 probe)
- Direction symmetry defense (must be in Section 0 / Section 5)

If you find yourself writing "decide whether stop is too tight" or
"check whether the gate leaves enough samples," STOP and resolve
before publishing the entry.

## 9. Source / references

Cite literature or empirical references that support R1. If support
is purely trader-folklore, name it as such and explain why this
candidate goes beyond folklore.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| <YYYY-MM-DD> | `untested-ideation` | Authored under template v2. R4 probe run on <probe window>: n=<X> signals. |

---

## Template v2 authoring notes (DELETE BEFORE PUBLISHING)

This template was created 2026-05-14 to address the Phase 0 R2/R4
failure pattern across four prior INADMISSIBLE candidates. Key
differences from v1:

1. **Frontmatter `admissibility:` block**: required quantitative fields
   for R2 and R4. A null in any required field renders the entry
   INADMISSIBLE by template construction.
2. **R4 probe data**: derived from a probe script run on a sample
   window of the in-sample data. See `_R4_PROBE_CONVENTION.md` for the
   probe spec. The probe is a one-off — script name in
   `admissibility.r4_signal_frequency.probe_script`, output JSON in
   `probe_output`.
3. **Section 0 admissibility summary**: written LAST, citing the
   frontmatter numbers. A reader judges readiness from Section 0 alone.
4. **Section 8 deferral restriction**: R2 and R4 questions cannot be
   deferred to Section 8 "future research." They must be answered in
   the entry or the entry is not ready.

Before submitting for Phase 0:

- All `admissibility` frontmatter fields are non-null.
- Section 0 paragraph for each R is written.
- Section 5 cluster-loss analysis is concrete.
- R4 probe script + output file both exist at the listed paths.
- If the closest tested relative failed Apex, Section 5 explicitly
  addresses why this candidate differs.

If any of these are not done, the entry is `untested-draft`, not
`untested-ideation`.
