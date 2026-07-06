---
node_id: "mnq_directional_bias_atlas"
status: "descriptive_spec_not_implemented"
node_type: "diagnostic atlas / directional-bias map"
created: "2026-06-23"
source_artifact: "nb_lib/strategy_specs/source_artifacts/opus_directional_bias_atlas_guardrails_20260623.md"
oos_status: "sealed; use only dates < 2026-02-01 unless explicitly authorized"
---

# MNQ Directional Bias Atlas

## Purpose

This node asks a different question from the failed conditional entry
mechanisms:

```text
Does MNQ RTH have a persistent directional tilt that survives without a
clever trigger?
```

This is **descriptive only**. It is not an entry strategy, not a
management rule, and not a targetability overlay. It produces a map of
directional drift by clock window, structural segment, state, and
regime. The correct read is the shape of the panel, not the best cell.

## Why This Exists

Multiple OHLCV MNQ candidates have failed by adding clever conditional
logic that did not add edge. The recurring hint was a broad
directional/momentum factor: several candidates overlapped on trade
days, and the market often appeared to drift one way once a directional
state developed.

The atlas tests whether that intuition is real or just simple Nasdaq
beta in a strong uptrend.

## Output Contract

```yaml
node_id: mnq_directional_bias_atlas
timeframe: RTH intraday
outputs:
  daily_components:
    date: YYYY-MM-DD
    overnight_pts: float
    rth_pts: float
    rth_open: float
    rth_close: float
  cell_panel:
    cell_id: string
    cell_family: unconditional_window | time_segment | structural_segment | state_condition | regime_condition
    direction_tested: long | short | signed
    n: int
    mean_pts_raw: float
    mean_pts_net_of_intraday_baseline: float
    median_pts: float
    win_rate: float
    t_stat: float
    p_value_raw: float
    p_value_bonferroni: float
    q_value_fdr: float
    monthly_hhi: float
    best_month_share: float
    trade_day_jaccard_to_existing_sleeves: map
  panel_read:
    total_cells_examined: int
    baseline_intraday_mean_pts: float
    overnight_mean_pts: float
    broad_lean_direction: long | short | none
    beta_trap_status: pure_beta | excess_intraday_bias | no_bias | mixed
    multiple_comparison_status: broad_panel_shape | isolated_cell_artifact | no_signal
    verdict: descriptive_only_no_strategy | candidate_followup_earned
```

## Lookahead Discipline

- Use only dates before the sealed OOS boundary unless the operator
  explicitly authorizes an OOS spend.
- Every state label must be known at the conditioning timestamp.
- VWAP state at 10:30 uses VWAP cumulated only through 10:30.
- Opening-range and initial-balance labels are available only after
  their windows complete.
- Prior-day levels, prior value area, and prior close use only the
  prior completed RTH session.
- Overnight high/low are frozen at RTH open.
- ATR regime uses prior-days-only ATR history or bars closed before the
  decision point.
- Catalyst flags must come from a pre-frozen calendar, not a calendar
  authored after results are seen.

## Required Decomposition: Beta Guard

The atlas must decompose close-to-close return before reading any long
bias:

```text
overnight = RTH_open_today - RTH_close_prior_day
intraday = RTH_close_today - RTH_open_today
```

Report overnight drift separately. The atlas is about the intraday
component.

Every cell must be reported two ways:

1. Raw forward return.
2. Net of the all-day intraday baseline:

```text
cell_excess = cell_mean_raw - all_day_intraday_mean
```

A cell that is long-positive only because the entire index drifted up is
not a signal. The signal, if any, is excess drift in a specific
structural state.

## Multiple-Comparisons Guard

The atlas is allowed to examine many cells, but it must account for
that explicitly:

- report total number of cells inspected;
- report each cell's t-stat;
- report raw p-value, Bonferroni-adjusted p-value, and FDR/q-value;
- do not call a cell interesting unless it clears an adjusted bar or
  contributes to a broad coherent panel shape.

One spectacular cell inside a mostly flat panel is a likely selection
artifact. A broad same-direction lean across related structural states
is more interesting even if individual cells are only modestly
significant.

## Panel Families

### 1. Unconditional Windows

- 09:30-16:00.
- 10:00-16:00.
- 10:30-16:00.
- 14:00-15:55.
- Short mirror/control versions where useful.

### 2. Clock Segments

- 09:30-10:00.
- 10:00-10:30.
- 10:30-12:00.
- 12:00-14:00.
- 14:00-15:55.
- 15:30-15:58.

### 3. Structural Segments

These are preferred over arbitrary clock slices:

- opening drive;
- initial-balance complete;
- post-IB;
- European close around 11:30 ET;
- lunch lull;
- afternoon attention return;
- close auction.

### 4. State-Conditioned Forward Returns

- Overnight up/down into RTH.
- First 30 minutes up/down into rest of day.
- Above/below VWAP at 10:30 into rest of day.
- Open above/below prior close.
- Open above/below PDH/PDL.
- Open above/below ONH/ONL.

### 5. Regime-Conditioned Forward Returns

- ATR tercile: low, mid, high.
- Trend-day versus chop proxy.
- Day of week.
- Calendar flags: FOMC, CPI, NFP, OPEX if a frozen calendar exists.

## Required Read

The report must answer:

1. Is there a broad consistent directional lean?
2. Is any apparent lean excess over the baseline intraday drift, or is
   it simply Nasdaq beta?
3. Does any state-conditioned asymmetry survive the
   multiple-comparisons guard?
4. Is the shape broad and coherent, or just one or two spectacular
   cells?
5. Does the atlas justify a future pre-committed "dumb expression" of
   bias, or does it close the mechanism-free bias hypothesis?

## Non-Goals

- Do not select the best cell and call it a strategy.
- Do not add stop/target/management logic.
- Do not combine this with targetability.
- Do not tune structural segment definitions after seeing the panel.
- Do not use the sealed OOS window without explicit authorization.

## Verdict Language

Allowed:

- `descriptive_only_no_strategy`
- `pure_beta_no_intraday_edge`
- `flat_panel_no_bias`
- `isolated_cell_artifact`
- `broad_excess_bias_followup_earned`

Forbidden:

- `validated`
- `deployable`
- `strategy passed`
- any language implying an entry edge before a separate pre-committed
  build exists.

## Implementation Note

If implemented, the first script should be named:

```text
nb_lib/scripts/mnq_directional_bias_atlas.py
```

The output report should live at:

```text
nb_lib/probe_results/mnq_directional_bias_atlas_report.md
```

This run would consume no Section 12 trial draw because it is
descriptive and no cell is promoted to a strategy inside the atlas.

## Status History

- **2026-06-24 — verdict `pure_beta_no_intraday_edge`** — intraday
  09:30→16:00 flat (mean −2.07 pt, p=0.86), long tilt is overnight beta
  (+18.3 pt, marginal), 0 of 39 cells survive Bonferroni/BH-FDR.
  Mechanism-free intraday-bias hypothesis **closed for this window**.
  *Why banked:* the negative panel result is the deliverable — it shuts
  the last "find a cleverer trigger" escape hatch on the MNQ-OHLCV
  thread, so a future agent reading this spec must see the closure
  before redesigning around it. Consolidated session findings:
  `_worker_reports/INTEGRITY_SWEEP_FINDINGS_2026-06-24.md` and the
  current-state block in `_PROJECT_ALTITUDE_MAP.md`.
