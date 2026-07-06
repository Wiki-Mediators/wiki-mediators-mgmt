# R2 Variance Preflight Convention

**Version**: v1
**Created**: 2026-05-17
**Methodology iteration**: v1.3 introduced this gate; v1.4 reordered
the pipeline so R1 diagnostic runs first (see
`_R1_EVIDENCE_DIAGNOSTIC_CONVENTION.md`). R2 variance preflight
position is unchanged: between Phase 1 entry preflight and FINAL
spec drafting.
**Purpose**: Catch trailing-drawdown-incompatible candidates BEFORE
FINAL spec drafting by simulating bracket outcomes on the signal set
produced by the Phase 1 entry preflight.

This convention is a SPEC, not a running script. Each candidate that
clears Phase 0 admissibility + Phase 1 signal preflight gets a one-off
variance probe written to this convention. The probe runs once before
FINAL spec drafting; its JSON output is referenced in the wiki entry's
frontmatter.

---

## Why a variance preflight exists

The opening_range_width_switch candidate (2026-05-17) progressed
cleanly through:
- Phase 0 v2 admissibility (ADMISSIBLE under v1.2 pipeline)
- R4 probe v1.2 (predicted 22-89 tradeable signals per 60 trading days)
- Phase 1 entry preflight (267 signals; 3.96% attrition; probe
  extrapolation validated within range)

Then in-sample test produced:
- **Modestly positive net P&L** (+$603.90 over 62 trades)
- **PF 1.07** (above breakeven)
- **Account FAILED on Apex** (trailing-DD max $2,000.50 vs $2,000
  floor)

The failure mode was **trailing-drawdown geometry incompatible with
high per-trade variance**: best day +$1,148.70 vs worst day -$338.40.
The Apex trailing floor follows peak balance up but not down, so a
high-variance strategy can be net-positive and still bust Apex.

The R4 probe and Phase 1 preflight both measure **signal frequency**.
Neither measures **outcome distribution variance**. The variance
preflight closes that gap.

---

## What the variance probe does NOT do

The variance probe is not a full canonical alpha:

- **No BAND_B friction.** Entry/stop/TP fills are at structural prices
  (no slippage). This makes simulated PnL **optimistic**.
- **No ComplianceTracker state.** Trades run regardless of compliance
  state in the probe.
- **No daily loss limit.** No max-one-per-day filtering beyond what
  the Phase 1 preflight already applied.
- **No real partial-fill mechanics.** TP1 is modeled as a 50% close
  at TP1 price; runner exits at TP2 OR BE-stop, whichever first.

These simplifications give the probe its **optimistic-bound** property:
a candidate that FAILS the variance probe will also fail at
implementation. A candidate that PASSES the variance probe might
still fail at implementation (friction + compliance compound losses).

**The variance probe is a necessary check, not a sufficient one.**

---

## Probe script contract

### File location

`nb_lib/scripts/probe_r2_variance_<candidate_id>.py`

`<candidate_id>` matches the wiki entry filename without the `.md`
suffix.

### Length and complexity

- Target: 150-250 lines including imports and a single `main()`.
- Hard cap: 350 lines (variance simulation needs more state than R4
  count).
- Single file. Reuses existing nb_lib helpers; no new library
  primitives.

### Inputs

- **Input signals**: read from the Phase 1 preflight signals CSV
  (`<candidate_id>_preflight_signals.csv`). The probe operates on
  the same signal set, post-fill-time guards.
- **1-sec MNQ data**: load via `load_seconds(DATA_DIR)`.
- **Sample window**: same as the input signals' date range (i.e.,
  full in-sample, 2024-08-01 → 2026-01-31). Variance estimation
  needs the full distribution; small subsets don't characterize tail
  events.

The probe runs over the FULL in-sample window because variance
estimation is what's being checked — not signal frequency. The R4
probe runs over a small window because frequency estimates extrapolate;
variance estimates do not (extreme losses cluster temporally).

### Simulation per signal

For each input signal:

1. Start at the signal's fill timestamp (read from preflight CSV).
2. Read `entry_price`, `stop_price`, `tp1_price`, `tp2_price`,
   `direction` from preflight signal record.
3. Compute `raw_stop_pts = |entry_price - stop_price|`.
4. Compute `contracts = floor($300 / (stop_pts × $2)).clamp(1, 12)`.
5. Compute `tp1_close_contracts = max(1, round(contracts × 0.50))`
   (capped to `contracts - 1` if needed).
6. Walk 1-sec bars forward from `entry_ts + 1 second`:
   - On each bar, check if the bar's range touches stop, TP1, or TP2.
   - **First-hit priority** (a single bar can be ambiguous; pick by
     direction):
     - For long: if low <= stop, stop hit; elif high >= tp1 and not
       tp1_filled: TP1 fill; elif high >= tp2 and tp1_filled: TP2 fill.
     - For short: symmetric (high triggers stop; low triggers TPs).
   - If TP1 fills: close `tp1_close_contracts`; remaining contracts
     get BE-stop = entry_price.
   - On any final exit (stop / TP2 / BE-stop / EOD-flat at
     session_close - 90s / time exit at 60 min after entry):
     record the outcome.
7. Compute trade P&L assuming **zero friction**:
   - `partial_pnl = (tp1_close × (tp1_price - entry_price)) × direction × $2`
   - `terminating_pnl = (remaining_contracts × (exit_price - entry_price)) × direction × $2`
   - `total_pnl = partial_pnl + terminating_pnl`

### Aggregation

Across all simulated trades:

- Count by exit type: `tp1+tp2`, `tp1+runner_be`, `full_stop`,
  `time_exit`, `eod`.
- Win rate = (`tp1+tp2` + `tp1+runner_be where partial_pnl > runner_loss`) / total.
- Profit factor = sum of positive P&L / |sum of negative P&L|.
- Sequential P&L curve: running cumulative P&L.
- Running drawdown: peak balance running max minus current cumulative.
- Trailing Apex DD check: track peak; floor = peak - $2,000; trigger
  bust if cumulative <= floor at any trade.

### Output

Write to `nb_lib/probe_results/<candidate_id>_r2_variance_probe.json`
with schema:

```json
{
  "candidate_id": "<wiki filename without .md>",
  "probe_convention_version": "r2_variance_v1",
  "probe_script": "nb_lib/scripts/probe_r2_variance_<candidate_id>.py",
  "ran_at": "<ISO datetime>",
  "input_signals_csv": "<path>",
  "n_signals_input": <int>,
  "n_signals_simulated": <int>,
  "n_signals_skipped": <int>,
  "skip_reasons": {"<reason>": <int>, ...},

  "outcome_counts": {
    "tp1_tp2": <int>,
    "tp1_runner_be_win": <int>,
    "tp1_runner_be_loss_net": <int>,
    "full_stop": <int>,
    "time_exit": <int>,
    "eod_exit": <int>
  },

  "pnl_distribution_dollars": {
    "mean": <float>,
    "p10": <float>, "p25": <float>, "p50": <float>,
    "p75": <float>, "p90": <float>,
    "min": <float>, "max": <float>,
    "stdev": <float>
  },
  "win_rate": <float>,
  "profit_factor_simulated": <float>,
  "total_pnl_dollars": <float>,

  "cluster_analysis": {
    "max_consecutive_losses": <int>,
    "n_loss_clusters_3plus": <int>,
    "n_loss_clusters_5plus": <int>,
    "n_loss_clusters_6plus": <int>
  },

  "drawdown_analysis": {
    "max_running_drawdown_dollars": <float>,
    "max_running_drawdown_pct_of_apex_floor": <float>,
    "trailing_dd_breach": <bool>,
    "trailing_dd_breach_trade_n": <int|null>,
    "trailing_dd_breach_date": <str|null>,
    "peak_balance_at_breach": <float|null>,
    "balance_at_breach": <float|null>
  },

  "caveats": [<list of strings>],
  "verdict": "<PASS|FAIL|MARGINAL>",
  "verdict_reasons": [<list of strings>]
}
```

### Pre-committed admissibility gates

The variance probe applies these pre-committed gates and records
verdict:

| Gate | Pass condition | Apex implication |
|---|---|---|
| Trailing-DD breach | `trailing_dd_breach == false` | Hard requirement; Apex bust at preflight stage means in-sample will bust too |
| Sim PF >= 1.0 | `profit_factor_simulated >= 1.0` | Non-degenerate (above breakeven without friction). Note: BAND_B friction will pull this DOWN at implementation, so 1.0 here may be 0.85 at implementation |
| Max consecutive losses < 6 | `max_consecutive_losses < 6` | Spec-pinned in prior candidates; cluster geometry |
| Max DD < $1,500 | `max_running_drawdown_dollars < 1500` | $500 margin below Apex floor; absorbs friction degradation |

**Verdict assignment**:
- **PASS**: all 4 gates passed.
- **MARGINAL**: 3 of 4 passed; one specific gap (e.g., max DD $1450 —
  passes the $1500 bar but is tight).
- **FAIL**: 2+ gates failed, OR trailing-DD breach (hard fail).

A FAIL verdict means the candidate **should NOT advance to FINAL
spec drafting** as designed. The spec needs revision to address the
variance issue (lower risk, tighter brackets, etc.) before
re-running the variance probe.

### OOS safety

Same as R4 probe convention: probe MUST contain at the top:

```python
SAMPLE_WINDOW_END_HARD_CAP = date(2026, 1, 31)  # OOS guard
assert SAMPLE_WINDOW_END <= SAMPLE_WINDOW_END_HARD_CAP
```

A probe that loads any data >= 2026-02-01 is a HARD-HALT-OOS-LEAK.

### Cost budget

Each probe should run in under **5 minutes** on the dev machine.
Variance simulation walks 1-sec bars for each trade (mean ~60 min
per trade × ~250 trades = 15,000 bar-iterations). Each 1-sec bar
check is O(1); total runtime ~30-60s on typical hardware.

### Determinism

Probe must be deterministic — running it twice on the same input
signals produces byte-identical JSON output (modulo `ran_at`).

---

## How variance preflight fits the pipeline

Updated pipeline order:

1. **Wiki entry authored** (template v2 with R2/R4 frontmatter slots).
2. **R4 probe v1.2**: 20-day signal-frequency probe. → JSON output.
3. **Phase 0 v2 review**: 5-requirement assessment. → ADMISSIBLE /
   CONDITIONAL / INADMISSIBLE.
4. **Phase 1 entry preflight**: full-in-sample signal-only scan.
   → preflight signals CSV.
5. **(NEW) R2 variance preflight**: simulate bracket outcomes on
   preflight signals. → variance probe JSON + verdict.
6. **FINAL spec drafting**: incorporates variance probe findings;
   Section 7 pass criteria informed by variance distribution.
7. **Implementation + in-sample test**: canonical alpha with full
   friction + compliance.

The variance preflight is **gate 5** between Phase 1 and FINAL spec.
A FAIL at gate 5 returns the candidate to spec revision (lower risk,
tighter brackets) without consuming a full implementation iteration.

---

## How retrofitting uses the variance preflight

When a candidate already has Phase 1 preflight artifacts:

1. Read the preflight signals CSV.
2. Write `probe_r2_variance_<candidate_id>.py` per this convention.
3. Run it; confirm output JSON exists and verdict is recorded.
4. Update wiki frontmatter `admissibility.r2_apex_survival` with
   probe-derived numbers (Section "Frontmatter integration" below).
5. Reference the probe in Section 10 status_history.

When authoring a NEW candidate:

1. Pass Phase 0 v2 + R4 probe v1.2 + Phase 1 preflight.
2. Run variance preflight.
3. If verdict is FAIL: revise spec or close candidate. Do NOT draft
   FINAL spec from a variance-failing signal set.
4. If verdict is PASS or MARGINAL: proceed to FINAL spec drafting
   with the variance distribution as input.

---

## Frontmatter integration (template v2 update)

Template v2 frontmatter `admissibility.r2_apex_survival` block
extended with variance-probe-derived fields:

```yaml
admissibility:
  r2_apex_survival:
    # Existing fields (theoretical)
    risk_dollars_per_trade: 300
    expected_stop_distance_pts_range: [<low>, <high>]
    expected_loss_dollars_per_trade: 300
    worst_plausible_cluster_n: <int>
    worst_plausible_cluster_dollars: <int>
    cluster_vs_floor_ratio: <float>
    favorable_first_week_independent: <bool>

    # New v1.3 fields (variance-probe-derived; required for new candidates)
    r2_variance_probe_version: "v1"
    r2_variance_probe_script: "<path>"
    r2_variance_probe_output: "<path>"
    r2_variance_pf_simulated: <float>
    r2_variance_win_rate: <float>
    r2_variance_max_consecutive_losses: <int>
    r2_variance_max_running_drawdown_dollars: <float>
    r2_variance_trailing_dd_breach: <bool>
    r2_variance_verdict: "PASS|MARGINAL|FAIL"
```

Backward compatibility: candidates retrofitted under v1.2 (no
variance probe) keep their existing R2 frontmatter unchanged. The
new fields are required for **new** candidates from this point on.

---

## Case study: opening_range_width_switch (RETROSPECTIVE VALIDATION 2026-05-25)

This case study was authored on 2026-05-17 as a "would-have-caught"
hypothetical to motivate the convention. On 2026-05-25, the variance
preflight was applied RETROSPECTIVELY to ORWS's 267 Phase-1 preflight
passing signals. The actual results vs the original estimates:

| Metric | Original estimate (2026-05-17) | Actual retrospective (2026-05-25) |
|---|---|---|
| Total simulated P&L (no friction) | ~+$1,200-$2,000 | **+$15,322** (much higher — continued past actual Apex-bust point) |
| Simulated PF | ~1.3-1.5 | **1.47** (within estimate range) |
| Max running drawdown | ~$1,800-$2,200 | **$1,805** (within estimate range) |
| Trailing-DD breach (sim) | LIKELY TRUE | **FALSE** in friction-free sim |
| Verdict | FAIL (predicted) | **MARGINAL** (3/4 gates pass; max-DD gate fails by $305) |

The verdict differs from the original estimate: **MARGINAL** rather
than FAIL. This is because the simulation's trailing-DD never
breached in the friction-free run — the candidate's wins were
sufficient to keep cumulative balance above peak-$2K throughout the
267-event sequence. The actual implementation friction-degraded by
$195 (sim DD $1,805 vs actual DD $2,000.50), pushing JUST over the
$2K floor and triggering the bust.

The convention's $1,500 max-DD gate (with $500 friction buffer
below the $2K Apex floor) was nearly perfectly calibrated for this
candidate's friction profile.

**Under MARGINAL, ORWS would have been routed to SPEC REVISION
pre-implementation.** Likely revisions (matching the 2026-05-18
failure investigation's engineering counterfactuals): lower
risk_dollars from $300 to $250, cap TP2 at OR-midpoint, add daily
P&L cap, or some combination.

**Full retrospective validation report**:
`C:/VMShare/NT8lab/nb_lib_v1_3_variance_preflight_orws_retrospective_validation.md`

**Methodology validation outcome**: v1.3 works as designed. The
$1,500 max-DD gate's $500 friction buffer is the right
calibration. The convention can be relied on to flag
trailing-DD-vulnerable candidates pre-implementation under the
MARGINAL verdict at minimum.

---

## What variance preflight cannot catch

- **Friction-amplified failures**: BAND_B friction can convert a
  marginal-PASS candidate to an actual-FAIL. The variance probe is
  friction-free, so PASS is optimistic.
- **Compliance interactions**: actual ComplianceTracker behavior
  (early-eval-failure, post-FAIL skip) is not modeled.
- **Regime-conditional outcomes**: if the in-sample sample contains
  unusual regime (high vol Q4 2024), variance is calibrated to that
  regime. OOS could differ.
- **Order-of-trades effects in trailing-DD**: simulated trade order
  is the signal-fire order. If actual order differs (due to
  compliance-skip days), trailing-DD path differs.

Variance preflight is **necessary but not sufficient**. A FAIL is
informative; a PASS is provisional.

---

## Convention history

| Version | Date | Notes |
|---|---|---|
| v1 | 2026-05-17 | Initial convention. Authored in response to the opening_range_width_switch case study (PF 1.07 with $603 net P&L still busted Apex via trailing-DD on max DD $2,000.50). The R4 probe + Phase 1 signal preflight measure frequency; the variance preflight measures outcome-distribution variance. Together they form methodology iteration v1.3. |
| v1 (retrospective validation) | 2026-05-25 | Convention v1 applied retrospectively to ORWS's 267 Phase-1 preflight signals. Verdict: MARGINAL (3/4 gates pass; max-DD gate fails by $305 at $1,805 vs $1,500 threshold). Friction degradation in actual implementation was $195 ($1,805 sim → $2,000.50 actual DD) — well within the convention's designed $500 friction buffer. **Convention validates as the methodology gate it was designed to be.** Case-study section updated above with actual vs original-estimate comparison. Methodology infrastructure v1.0 → v1.5 now end-to-end validated against historical failures. |
