---
name: "Loose VWAP Reclaim + Sneaky Level Hybrid"
tagline: "Broaden C2 VWAP reclaim, then require the setup probe to occur near a prior-day or opening-15m objective level."
status: "diagnostic-tested-not-promoted"
created: 2026-06-30
updated: 2026-06-30
source: "Hybrid of C2 VWAP stretch-reclaim diagnostics and the sneaky-pivot transcript candidate."

markets: ["MNQ"]
session: "RTH"
time_of_day: "10:00-12:30 ET diagnostic window"
hold_duration: "intraday"

signal_type: "mean-reversion level-response hybrid"
indicators: ["RTH VWAP", "VWAP deviation", "prior-day high/low", "opening 15m high/low"]
timeframes_used: ["1-minute", "15-minute-derived levels", "1-second fills"]

brackets: "C2 VWAP target / C2 structural stop"
position_sizing: "fixed contracts inherited from C2 proxy"

canonical_spec: null
implementation: "nb_lib/scripts/candidate_c5_loose_vwap_sneaky_level_diagnostic.py"
related_candidates:
  - "vwap_stretch_reclaim_mean_reversion_screen"
  - "c2_midmorning_targetability_mean_reversion_screen"
  - "sneaky_pivot_15m_level_reversal"

test_results:
  in_sample_n: 51
  in_sample_pnl_dollars: 1232.40
  in_sample_pf: 1.341
  in_sample_win_rate: 0.745
  out_of_sample_tested: false

tags:
  - rth-only
  - intraday
  - mean-reversion
  - vwap
  - level-response
  - diagnostic-only
---

# Loose VWAP Reclaim + Sneaky Level Hybrid

## 1. Purpose

This note records the requested attempt to loosen the previous C2/C4
VWAP-reclaim strategy and mix in the newly archived "sneaky pivot"
level-response idea.

This is not a promoted strategy. It is an exploratory diagnostic over a
known rejected family. The result is useful because it shows the tradeoff:
the sneaky-level condition can improve PF on a loosened pool, but it cuts
frequency even further.

## 2. Construction

Source trades:

- `nb_lib/probe_results/candidate_c2_context_baseline_trades.csv`

Added deterministic level context:

- For long trades, check the C2 setup probe against prior-day low and
  completed opening-15m low.
- For short trades, check the C2 setup probe against prior-day high and
  completed opening-15m high.
- `near_sneaky_level = true` if the probe is within 20 MNQ points of
  the relevant level.

The C2 entry, target, stop, and fill model are unchanged. This is not
the full standalone sneaky-pivot strategy; it is a mixed overlay on the
C2 trade set.

## 3. Diagnostic Results

Artifacts:

- Script:
  `nb_lib/scripts/candidate_c5_loose_vwap_sneaky_level_diagnostic.py`
- Enriched trades:
  `nb_lib/probe_results/candidate_c5_loose_vwap_sneaky_level_diagnostic_trades.csv`
- Report:
  `nb_lib/probe_results/candidate_c5_loose_vwap_sneaky_level_diagnostic_report.md`
- JSON:
  `nb_lib/probe_results/candidate_c5_loose_vwap_sneaky_level_diagnostic.json`

Selected cells:

| Cell | N | Trades/mo | Net | PF | Read |
|---|---:|---:|---:|---:|---|
| Loose 10:15-12:00, R>=0.25 | 180 | 10.0 | +$1,351.50 | 1.072 | More trades, but edge nearly flat and concentrated. |
| Loose 10:15-12:00, R>=0.25, near sneaky level | 51 | 2.8 | +$1,232.40 | 1.341 | Cleaner PF, but far too sparse. |
| Loose 10:00-12:00, R>=0.25, near sneaky level | 71 | 3.9 | +$1,197.90 | 1.244 | Slightly more sample, still sparse. |
| Strict C4 10:30-12:00, R>=0.35 | 91 | 5.1 | +$2,586.90 | 1.278 | Still the best informative slice, but failed screen on frequency/concentration. |

## 4. Interpretation

The hybrid does not solve the C2/C4 problem. Adding objective
sneaky-pivot level proximity improves quality in the loosened pool, but
the sample collapses to 51-71 trades over 18 months. Broadening the
window without the level condition restores frequency but pushes PF
toward 1.0.

Current read:

```text
The level-response idea may be a useful quality feature, but as an
overlay on C2 it does not produce enough trade count to justify a build.
```

The standalone sneaky-pivot candidate remains separate and untested.
If pursued, it should be screened from raw 15m level interactions rather
than as a C2 rescue overlay.

## 5. OOS Discipline

No OOS rows were loaded for this diagnostic. The source C2 trade list
and the 1-second data slice are in-sample only.

## 6. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-06-30 | `diagnostic-tested-not-promoted` | Loosened C2 and added sneaky-level proximity. PF improved in sparse cells, but frequency problem worsened. |
