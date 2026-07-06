# R4 Signal-Frequency Probe Convention

**Version**: **v1.2** (revised 2026-05-16 to extend default sample window)
**Pipeline position (as of v1.4 methodology, 2026-05-25)**: R4 probe
runs as **step 3** in the pipeline, AFTER the R1 evidence diagnostic
(step 2; see `_R1_EVIDENCE_DIAGNOSTIC_CONVENTION.md`). Skip the R4
probe for candidates that fail R1 at < 60% reversion.
**v1.1 created**: 2026-05-16 (fill-mechanics simulation)
**v1 created**: 2026-05-14
**Purpose**: Eliminate R4 (signal-frequency tolerance) deferrals in
wiki entries by replacing speculative count estimates with measured
predicate-firing counts on a small sample of in-sample data.

This convention is a SPEC, not a running script. Each candidate gets
its own one-off probe script written to this convention. The script
runs once during retrofit/authoring; its JSON output is referenced in
the wiki entry's frontmatter.

**Version 1.2 changes** (see "v1.2 changes" section near the end of
this document for full detail):
- Default sample window extended from 5 to **20 trading days** to
  catch tail-driven attrition that small samples miss.
- New JSON output field: `low_confidence_attrition` (boolean) — set
  when `signals_fired_at_signal_ts < 5` regardless of computed rate.
- Motivated by the prior_day_value_area_rejection v1.1 retrospective:
  the 5-day default window contained only 2 signals (both passing
  fill guards, 0% attrition) while the full 374-day window produced
  90% attrition. Sample-window choice is more determinative than
  probe version.
- v1.1 probes are NOT retroactively invalidated. v1.2 applies to new
  probes and any candidate going forward.

**Version 1.1 changes** (retained for reference):
- New requirement: probes MUST simulate fill at `signal_ts + 1 second`
  and report fill-time drift.
- New requirement: stop/TP guards MUST be evaluated at fill-time
  geometry, not signal-fire geometry.
- New required JSON output fields: `signals_fired_at_signal_ts`,
  `signals_with_valid_fill`, `signals_passing_fill_guards`,
  `attrition_rate`, `median_signal_to_fill_drift_pts`,
  `p95_signal_to_fill_drift_pts`.
- The v1.1 `signals_passing_fill_guards` count replaces the v1 count
  as the basis for R4 admissibility extrapolation.
- v1 probes are NOT retroactively invalidated. v1.1 applies to new
  probes and any candidate going forward.

---

## Why a probe convention exists

Four Phase 0 evaluations to date (mnq_news_like, closing_imbalance,
mhw, vwap_band) all failed R4 because candidates deferred
signal-frequency expectation to "Section 8 research." After mhw's
informational multistart confirmed the candidate produced ~14 trades
vs the spec's 60–180 estimate, it became clear that:

- Theoretical R4 estimates are unreliable (mhw was ~5× too optimistic).
- Authoring discipline alone is insufficient (mhw was authored
  admissibility-aware and still deferred).
- The cheapest way to ground R4 is to actually count.

The probe is the smallest data-derived check that turns R4 from prose
into a number.

---

## Probe script contract

### File location

`nb_lib/scripts/probe_r4_<candidate_id>.py`

`<candidate_id>` matches the wiki entry filename without the `.md`
suffix.

### Length and complexity

- Target: 80–150 lines including imports and a single `main()`.
- Hard cap: 200 lines. If the probe needs more, the predicates are
  too complex for an R4 probe and should be simplified for the probe
  (note any simplification in the JSON output's `caveats` field).
- Single file. No new library primitives. Reuse:
  - `nb_lib.scripts.atr_regime_pullback_continuation_canonical_alpha`
    helpers: `load_seconds`, `to_minutes`, `to_five_min`,
    `split_by_calendar_day`, `DATA_DIR`, window date constants.
  - Any existing `nb_lib.indicators.*` primitive.
  - `nb_lib.calendar.TradingCalendar` for trading-day filtering.

### Inputs

- **Sample window** (v1.2): 20 consecutive trading days inside the
  in-sample window (2024-08-01 → 2026-01-31). The window must NOT
  touch OOS (2026-02-01 →).
- **Default sample window** (v1.2): 2024-09-09 to 2024-10-04
  (4 calendar weeks, ~20 trading days, mid-in-sample, no major
  holiday or FOMC event in the date range). Override per candidate
  if a regime gate makes the window unrepresentative.
- **v1 / v1.1 default window** (deprecated): 2024-10-07 to
  2024-10-11 (5 days). The 5-day window proved insufficient for
  attrition detection on tail-driven candidates; the case study is
  prior_day_value_area_rejection (v1.1 retrospective showed 0%
  attrition on 5 days vs 90% over the full window).

### Predicate scope

The probe counts **entry predicates only**, NOT full strategy:

- Build the required indicators from the sample window's 1-sec / 1-min /
  5-min bars.
- Evaluate the candidate's Section 3 entry predicates on each
  eligible bar.
- **(v1.1)** Simulate the fill at `signal_ts + 1 second` (or whatever
  the strategy's FILL_ASSUMPTIONS specifies) and record both
  `signal_fire_price` and `fill_simulated_price`.
- **(v1.1)** Compute stop/TP geometry from `fill_simulated_price`
  using the candidate's structural anchors (e.g., PD-VA-anchored
  stop), then apply any pre-committed structural guards (stop-band,
  TP-distance) AT FILL-TIME GEOMETRY.
- Emit one row per qualifying signal:
  `(signal_ts, direction, signal_fire_price, fill_ts,
  fill_simulated_price, drift_pts, stop_pts_at_fill, tp_dist_at_fill,
  passed_fill_guards)`.

What the probe MUST NOT do:

- Compute realized P&L or trade outcomes.
- Apply BE-arm, structure_trail, or any management.
- Apply commission, slippage, or other fill friction beyond the
  1-second drift. (v1.1's fill simulation is the bar's open price at
  T+1s; it does NOT add slippage. The strategy's `entry_slippage`
  applies in the canonical alpha, not in the probe.)
- Apply daily compliance gating.
- Touch OOS data (assert at script top).

### Output

Write to `nb_lib/probe_results/<candidate_id>_r4_probe.json` with
schema:

```json
{
  "candidate_id": "<wiki filename without .md>",
  "probe_convention_version": "v1.1",
  "probe_script": "nb_lib/scripts/probe_r4_<candidate_id>.py",
  "ran_at": "<ISO datetime>",
  "sample_window_start": "<ISO date>",
  "sample_window_end": "<ISO date>",
  "sample_window_n_trading_days": <int>,

  // ===== v1 counts (retained for back-compat + methodology comparison) =====
  "signals_fired_at_signal_ts": <int>,    // (== v1's n_signals_observed)
  "n_signals_observed": <int>,            // alias for signals_fired_at_signal_ts
  "n_long": <int>,
  "n_short": <int>,
  "distinct_days_with_signal": <int>,
  "signals_by_day": {"<YYYY-MM-DD>": <int>, ...},
  "signals_by_hour": {"<HH>": <int>, ...},
  "predicate_gate_passes": {
    "<predicate_name_1>": <int qualifying bars>,
    ...
  },

  // ===== v1.1 fill-mechanics fields (REQUIRED) =====
  "signals_with_valid_fill": <int>,
    // signals where the 1-sec bar at fill_ts had usable data (no
    // session-edge missing bar, no gap-over-fill timestamp). Should
    // equal signals_fired_at_signal_ts under normal conditions.
  "signals_passing_fill_guards": <int>,
    // signals that survive ALL pre-committed structural guards
    // (stop-band, TP-distance, etc.) evaluated at fill-time geometry.
    // This is the v1.1 admissibility-extrapolation basis.
  "attrition_rate": <float>,
    // 1.0 - (signals_passing_fill_guards / signals_fired_at_signal_ts).
    // 0.0 = no attrition (signal geometry = fill geometry).
    // 0.9+ = severe attrition (case study; see methodology log).
  "low_confidence_attrition": <bool>,
    // (v1.2) true iff signals_fired_at_signal_ts < 5. When true,
    // attrition_rate is not statistically reliable regardless of its
    // value — the sample is too small. Authors should either extend
    // the sample window or treat the probe as a count-only check.
  "median_signal_to_fill_drift_pts": <float>,
    // |fill_price - signal_fire_price|, median across all signals.
  "p95_signal_to_fill_drift_pts": <float>,
    // 95th-percentile of |drift|. Diagnostic for fast-regime exposure.
  "max_signal_to_fill_drift_pts": <float>,
    // Max absolute drift observed.

  // ===== v1.1 extrapolation basis (REVISED) =====
  "extrapolated_signals_per_60_trading_days": {
    "low": <int>, "high": <int>,
    "basis": "signals_passing_fill_guards"
    // v1.1 extrapolation uses signals_passing_fill_guards as the
    // numerator. v1 used signals_fired_at_signal_ts. The change makes
    // the extrapolation a tradeable-signal estimate, not a structural-
    // signal estimate.
  },

  "caveats": [<list of strings; any simplification, missing data, etc.>],
  "sparsity_class": "<sparse|moderate|dense|very dense>",
  "sparsity_class_rationale": "<short string>"
}
```

### Extrapolation method

**(v1.1 revised)** Compute
`tradeable_signals_per_trading_day = signals_passing_fill_guards / n_trading_days`.
Then:

- `low = floor(60 * tradeable_signals_per_trading_day * 0.5)`
- `high = ceil(60 * tradeable_signals_per_trading_day * 2.0)`

The ×0.5/×2.0 brackets reflect that 5-day extrapolation has wide
uncertainty. If the candidate has a regime gate that fires
infrequently, the extrapolation may understate the true range; note
this in `caveats`.

**The extrapolation basis is `signals_passing_fill_guards`** (v1.1),
not `signals_fired_at_signal_ts` (v1). The v1.1 number is the
tradeable-signal estimate; the v1 number is the structural-signal
estimate and is preserved for methodology comparison only.

### Sparsity classification

**(v1.2 revised)** Classify based on `signals_passing_fill_guards`,
scaled to the v1.2 default 20-day window:

| `signals_passing_fill_guards` over 20 days | Class |
|---|---|
| 0–8 | sparse |
| 9–40 | moderate |
| 41–100 | dense |
| 101+ | very dense (red flag for round-number-style overtrading) |

(The v1/v1.1 5-day bands are deprecated; if a candidate uses a
non-default window, scale the bands proportionally.)

These bands map to the chop-fade (sparse) and round-number (very
dense) cautionary patterns. "moderate" is the desired band for a
12-start multistart-friendly candidate.

**If `attrition_rate > 0.5`**: flag as `attrition_concern` in
`caveats`. High attrition means many structural signals fail at fill;
the spec stage MUST address whether fill-time guards stay or the
structural anchors loosen.

**If `low_confidence_attrition` is true**: do NOT use the
`attrition_rate` as a quality signal. Extend the sample window or
treat the probe as count-only.

### OOS safety

The probe script MUST contain at the top:

```python
SAMPLE_WINDOW_END_HARD_CAP = date(2026, 1, 31)  # OOS guard
assert SAMPLE_WINDOW_END <= SAMPLE_WINDOW_END_HARD_CAP
```

A probe that loads any data ≥ 2026-02-01 is a HARD-HALT-OOS-LEAK.

### Determinism

The probe should be deterministic — running it twice on the same
sample window produces byte-identical JSON output (modulo `ran_at`
timestamp).

### Cost budget

**(v1.2)** Each probe should run in under **180 seconds** on the
dev machine (extended from 60s in v1/v1.1 due to the 20-day default
window). Probes that exceed this are too complex; simplify by
sampling fewer bars or simplifying predicates.

For reference: 20 trading days of MNQ 1-second data is approximately
2.5M bars (~10× a 5-day load). Streaming indicator computations
should still complete in under 3 minutes; if not, the indicator
implementation is too slow for probe purposes.

---

## How retrofitting uses the probe

When retrofitting an existing candidate to template v2:

1. Read the candidate's Section 3 (Signal logic) — these are the
   predicates to encode.
2. Write `probe_r4_<candidate_id>.py` per this convention.
3. Run it. Confirm output JSON exists and has all required fields.
4. Copy the JSON values into the new template's
   `admissibility.r4_signal_frequency` frontmatter fields.
5. Reference the probe paths in Section 10 status_history.

When authoring a NEW candidate under template v2:

1. Draft Section 3 predicates before publishing.
2. Write + run the probe.
3. If `signals_passing_fill_guards == 0` over 5 sample days: STOP and
   reconsider the predicates before publishing the wiki entry.
4. **(v1.1)** If `attrition_rate > 0.5`: investigate the
   fill-mechanics mismatch before publishing. High attrition is a
   spec-stage problem that should be resolved at design time, not
   discovered at in-sample test.
5. Fill the frontmatter from the probe output, including the new
   v1.1 fields (`signals_passing_fill_guards`, `attrition_rate`,
   drift percentiles).

---

## What the probe does NOT prove

The R4 probe answers: **does the predicate stack fire enough times
to be testable?** It does NOT answer:

- Is the signal profitable? (Phase 1 + in-sample test answers this.)
- Is the signal robust across regimes? (Multistart answers this.)
- Does the candidate survive Apex? (**R2 variance preflight** —
  see `_R2_VARIANCE_PROBE_CONVENTION.md` — answers this empirically
  pre-implementation as of methodology v1.3.)

A probe-passing candidate is admissible for Phase 0 review but not
automatically admissible. R1, R2, R3, R5 still apply. Under
methodology v1.3, the R2 variance preflight is a separate gate
between Phase 1 entry preflight and FINAL spec drafting.

---

## v1.2 changes (summary)

The v1.2 revision extends the default sample window from 5 to 20
trading days to address sample-size variance, motivated by the
prior_day_value_area_rejection v1.1 retrospective.

| Concern | v1.1 behavior | v1.2 behavior |
|---|---|---|
| Default sample window | 5 trading days | **20 trading days** |
| Default window dates | 2024-10-07..10-11 | **2024-09-09..10-04** |
| Cost budget per probe | 60 seconds | **180 seconds** |
| Low-confidence-attrition flag | none | **`low_confidence_attrition: true` when n_fired < 5** |
| Sparsity bands | over 5 days | rescaled for 20 days (×4) |

Backward compatibility: v1.1 probes are NOT retroactively invalidated.
Candidates evaluated under v1.1 may stay at v1.1 unless re-probed.
New probes and any re-probes use v1.2.

---

## v1.1 changes (summary)

The v1.1 revision adds fill-mechanics simulation to address a
methodology gap discovered by the
prior_day_value_area_rejection case study (see Methodology Learning
Log below).

| Concern | v1 behavior | v1.1 behavior |
|---|---|---|
| Signal price | bar's close where predicate fired (e.g., pullback_close) | both signal_fire_price AND fill_simulated_price recorded |
| Stop/TP geometry | computed from signal_fire_price | computed from fill_simulated_price |
| Guards (stop-band, TP-distance) | evaluated at signal_fire_price | evaluated at fill_simulated_price |
| Extrapolation basis | `n_signals_observed` (structural) | `signals_passing_fill_guards` (tradeable) |
| Sparsity classification basis | `n_signals_observed` | `signals_passing_fill_guards` |
| Drift tracking | none | median, p95, max drift in JSON output |
| Attrition rate | none | reported; `attrition_rate > 0.5` triggers caveat flag |

Backward compatibility: v1 probes are NOT retroactively invalidated.
Candidates evaluated under v1 may stay at v1 unless re-probed. New
probes and any re-probes use v1.1.

---

## Methodology Learning Log

### Case study (v1.2 motivation): prior_day_value_area_rejection v1.1 retrospective (2026-05-16)

After the v1.1 convention was introduced (fill-mechanics simulation),
prior_day_value_area_rejection was re-probed under v1.1 on the same
5-day window as v1. Result:

| Source | Window | n fired | n passing fill guards | Attrition |
|---|---|---|---|---|
| v1.1 retrospective | 5 days | 2 | 2 | **0%** |
| Full-window in-sample | 374 days | 137 (predicted) | 14 (actual) | **90%** |

**The 5-day v1.1 probe did NOT detect the attrition that the
in-sample test revealed.** Sampling variance dominated: the 5-day
window's 2 signals happened to both fall in the
fill-guard-passing region. The fat tail of drift (p95 28.25pt
across the full 137-signal sample) was absent from the 5-day
subsample (p95 11.50pt).

**Methodology lesson**: probe-version improvement (v1 → v1.1) is
not sufficient by itself. Sample-window size and representativeness
matter at least as much.

**Empirical guidance from the two v1.1 case studies**:

| Candidate | Window | n fired | Attrition detected | Matched reality? |
|---|---|---|---|---|
| gap_fill_pressure | 23 days (extended) | 5 | 80% | ✓ matched |
| prior_day_VA | 5 days (default) | 2 | 0% | ✗ missed (real was 90%) |

The gap_fill_pressure window was forced to extend because the
gap-size gate produced zero qualifying days on the 5-day default —
the extension was an accidental methodology win.

**Resolution (v1.2)**: extend the default window to 20 trading
days, give every candidate the same kind of representativeness the
gap_fill_pressure extension accidentally provided. Add a
`low_confidence_attrition` flag for when n_fired remains too small
even at 20 days.

**Open question for v1.3 (not implemented)**: should there be a
mandatory "v1.x preflight" stage — a full-in-sample-window signal
scan with fill-time guards — before FINAL spec drafting? This would
be even more reliable than a 20-day probe but adds an additional
pipeline stage. Defer until evidence of 20-day insufficiency
emerges.

---

### Case study: prior_day_value_area_rejection (2026-05-14 → 2026-05-15)

**Headline**: A v1 probe predicted 137 signals over 5 trading days
(extrapolating to 22 signals per 60 trading days; sparsity class
"moderate"). Phase 1 entry preflight validated the structural count
(actual 22.0/60d, within probe range [12, 48]). The candidate
advanced to FINAL spec and implementation.

**Result**: in-sample test produced **14 tradeable trades** over the
same 374 eligible trading days. 89.8% of the structural signals were
rejected at fill-time by the spec's stop-band and TP-distance
guards.

**Cause**: 1-second drift between `pullback_close` (the bar-close
price where the v1 predicate evaluated) and `entry_price` (the
strategy's actual fill at signal_ts + 1 second + slippage).

**Drift statistics** (137 preflight signals, empirically measured):

| Statistic | Value (pts) |
|---|---|
| Signed mean drift | +0.58 |
| Signed range | [-41.75, +50.50] |
| \|drift\| mean | 10.84 |
| \|drift\| p50 | 7.75 |
| \|drift\| p95 | **28.25** |
| \|drift\| p99 | 41.75 |
| \|drift\| max | 50.50 |
| Signals with \|drift\| > 5pt | 91 / 137 (66.4%) |
| Signals with \|drift\| > 10pt | 58 / 137 (42.3%) |
| Signals with \|drift\| > 20pt | 24 / 137 (17.5%) |

**Specific example** (2024-08-07 short):

| Reference | Price |
|---|---|
| pullback_close (v1 signal_fire_price) | 18373.00 |
| 1-sec bar open at signal_ts + 1s | 18344.00 |
| With entry slippage (-$0.50 for short) | 18344.50 |
| Drift | -28.5 pts |

For that signal, v1 measured `tp_distance_to_poc = 30.0pt`
(comfortably above the 5pt TP-distance-guard lower bound). v1.1
would have measured `tp_distance_to_poc = 1.5pt` at fill, FAILING
the guard.

**Implication**: v1 estimates were ~10× too optimistic for
fill-geometry-sensitive guards. The 137 → 14 attrition is the
empirical consequence.

**Resolution**: v1.1 simulates fill mechanics and applies guards at
fill-time geometry. The extrapolation basis becomes the
tradeable-signal count, not the structural-signal count.

**What v1.1 cannot promise**: even with fill-mechanics simulation,
the probe still does NOT model:
- BAND_B slippage on the fill price (probe uses bar open;
  canonical alpha adds entry_slippage). Drift dominates slippage at
  this scale, so this gap is acceptable for R4 estimation.
- Daily compliance state at fill time.
- Cumulative cluster-loss-state of the strategy.

These are out of scope for R4 admissibility. R2 (Apex survival) and
Phase 1 preflight cover them.

---

## v1.1 reference probe template (sketch)

The standard probe shape for v1.1 candidates:

```python
def main():
    # ... load data, build indicators ...
    sig_fired_count = 0
    sig_with_fill = 0
    sig_passing_fill_guards = 0
    drifts = []
    for day in sample_days:
        signals = evaluate_entry_predicates_for_day(...)
        for sig in signals:
            sig_fired_count += 1
            signal_fire_price = sig["signal_fire_price"]
            fill_ts = sig["signal_ts"] + pd.Timedelta(seconds=1)
            # v1.1: simulate fill
            try:
                fill_bar = seconds_df.loc[fill_ts]
                fill_simulated_price = float(fill_bar["open"])
            except KeyError:
                # Edge case (session-edge, no bar at fill_ts)
                cand = seconds_df[seconds_df.index >= fill_ts]
                if len(cand) == 0:
                    continue  # no valid fill
                fill_simulated_price = float(cand.iloc[0]["open"])
            sig_with_fill += 1
            drift = abs(fill_simulated_price - signal_fire_price)
            drifts.append(drift)
            # v1.1: compute geometry from fill price + structural anchors
            structural_stop = sig["failed_extreme"]  # or whatever anchor
            tp_target = sig["poc"]  # or whatever target
            stop_pts_at_fill = abs(fill_simulated_price - structural_stop)
            tp_dist_at_fill = abs(tp_target - fill_simulated_price)
            # v1.1: apply pre-committed guards at fill geometry
            if passes_stop_band(stop_pts_at_fill) and passes_tp_dist(tp_dist_at_fill):
                sig_passing_fill_guards += 1
    # ... compute attrition, write JSON ...
```

This is illustrative, not prescriptive. The probe author adapts the
structural-anchor logic to the candidate.

---

## Convention history

| Version | Date | Notes |
|---|---|---|
| v1 | 2026-05-14 | Initial convention. Authored alongside template v2 in response to the four-Phase-0-INADMISSIBLE pattern (mnq_news_like, closing_imbalance, mhw, vwap_band) where R4 was deferred in every case. |
| v1.1 | 2026-05-16 | Added fill-mechanics simulation requirement. Probes now compute stop/TP geometry from `fill_simulated_price` (the 1-sec bar at `signal_ts + 1s`), not from the signal-fire reference price. Guards evaluated at fill-time geometry. New JSON output fields: `signals_with_valid_fill`, `signals_passing_fill_guards`, `attrition_rate`, drift percentiles. Extrapolation basis revised to `signals_passing_fill_guards`. Sparsity classification revised to use the same basis. Motivated by the prior_day_value_area_rejection case study: 137 structural signals → 14 tradeable trades (89.8% attrition due to 1-sec drift, with p95 \|drift\| = 28.25pt). v1 probes are NOT retroactively invalidated; v1.1 applies to new probes and re-probes. |
| v1.2 | 2026-05-16 | Extended default sample window from 5 to 20 trading days. Default dates shifted from 2024-10-07..10-11 to 2024-09-09..10-04. Cost budget extended from 60s to 180s. Added `low_confidence_attrition` flag (true when `signals_fired_at_signal_ts < 5`). Sparsity bands rescaled for the 20-day default (×4 from v1.1). Motivated by the prior_day_value_area_rejection v1.1 retrospective: a 5-day v1.1 probe did NOT detect the 90% attrition that the full-window in-sample later revealed. Empirical evidence shows sample-window size matters at least as much as probe version. v1.1 probes (gap_fill_pressure 23-day, prior_day_VA 5-day) are NOT retroactively invalidated; v1.2 applies to new probes and re-probes. |
