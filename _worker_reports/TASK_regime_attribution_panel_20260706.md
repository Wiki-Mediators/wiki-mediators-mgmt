---
title: "TASK — Implement and Run the Regime Attribution Panel"
status: task-issued
created: 2026-07-06
issued_by: operator (via management-side review session)
executes_spec: nb_lib/strategy_specs/composition_nodes/regime_attribution_panel.md
vault_destination: _worker_reports/TASK_regime_attribution_panel_20260706.md
task_class: research-diagnostic (NOT housekeeping)
---

# TASK — Implement and Run the Regime Attribution Panel

## 0. Intake instructions (for the agent placing this file)

This file arrives via the operator's Downloads folder. Copy it into the
working vault at the `vault_destination` path above, then execute the
task. Self-orient via the AGENTS.md read-order first if this is a fresh
session. The spec this task executes was booked on 2026-07-06 as
`composition_nodes/regime_attribution_panel.md` — that spec is the
authority on design; this file is the execution trigger with the
pre-commitments restated, because pre-commitments only bind when they
are present at execution time.

## 1. Goal in one line

Determine whether the candidate graveyard contains regime-conditional
edges — closed candidates that were positive in a definable,
causally-knowable day-state and failed only because they were tested
unconditionally. A survivor here becomes the cheapest available path to
a decent strategy: a fresh pre-registered conditional candidate built on
an entry mechanism we already own, rather than a new invention.

## 2. Why this is the current best strategy-finding move

- It reuses existing closed-candidate trade CSVs: no new data, no new
  builds, no OOS spend.
- Every outcome is decision-useful: survivors → conditional candidates;
  a null panel → the MNQ negative result deepens and strengthens fork
  option (b); the management-divergence question (v2a/V4 vs G2) may
  resolve as regime composition.
- Nothing else in the research queue outranks it; the liquidity-zone
  screen is the only rival and is itself one of this panel's first
  targets.

## 3. Pre-commitments (binding, restated at execution time)

1. **In-sample only.** OOS stays sealed. No results computed on
   2026-02-01+ data. If a candidate's trade log spans the seal, truncate
   to in-sample and say so in the report.
2. **Declare the panel surface BEFORE computing any result.** The report
   must open with a declaration header written first: the exact list of
   included strategies, the exact state axes and their definitions, and
   the total cell count. If the surface changes mid-run, the change is
   logged and the correction threshold recomputed — no silent widening.
3. **Whole-panel report with multiple-comparison correction.** FDR
   (Benjamini–Hochberg) or stricter, applied across the declared cell
   count. No best-cell selection as the finding. Sample size (n) beside
   every cell. Treat perfect-looking cells as suspicious until checked.
4. **Causal tags only.** Every state tag must be knowable strictly
   before trade entry (prior-day trend state; OR expansion/rotation only
   after the range completes; volatility percentile from completed
   sessions/bars; above/below VWAP or prior close as of the completed
   bar before entry). Anything that peeks at later session outcome is
   marked `descriptive_only` and cannot be used as a gate or headlined
   as a finding.
5. **No resurrection in this task.** A promising cell produces a
   RECOMMENDATION to register a fresh pre-registered conditional
   candidate through the normal pipeline. It does not modify, reopen,
   or re-test the old candidate spec, and it does not consume OOS.
6. **No retuning.** State definitions are fixed in the declaration
   header. Do not adjust a state boundary after seeing which side of it
   the P&L falls on.

## 4. Scope guidance (agent's judgment within these bounds)

- Prefer the spec's simple causal tags over any model-based classifier
  for v1. The Markov node is note-only; do not block on it. Confirm the
  cheap tags are computable from existing data BEFORE declaring the
  surface — if a tag can't be computed causally, drop the axis and
  declare the smaller surface, don't improvise a proxy.
- Keep the surface modest. The spec's §3 schema implies several axes ×
  ~36 strategies; a full cross of everything is a huge correction
  burden. A first panel of 3–4 well-chosen axes is better than 6 diluted
  ones. Declare what you choose and why in one line each.
- First targets per the spec: (1) ORWS / opening-range-width-switch
  families, (2) level-response and liquidity-zone candidates, (3) the
  management-policy result sets (v2a / V4 / G2 divergence). If runtime
  forces a subset, run targets 1–3 first and declare the deferral.
- Where a closed candidate's closure rested on a predicate-loose R1
  proxy (see the R1 convention's ORWS case), note that beside its row —
  its closure evidence is weaker than the others'. Note only; do not
  re-open.

## 5. Deliverables

1. The attribution script (pre-committed; path under `nb_lib/scripts/`
   or wherever convention places diagnostics).
2. Per-trade tagged output CSV(s) — the raw table, so results are
   independently checkable.
3. The panel report at
   `nb_lib/probe_results/regime_attribution_panel_report.md`, opening
   with the declaration header (strategies, axes, cell count, correction
   method) and containing the full aggregate table: strategy × state,
   with n, net P&L, PF, win rate, mean trade, corrected significance,
   and a one-line interpretation per strategy.
4. A short verdict section: (a) list of cells surviving correction, if
   any, each with a recommendation to register (or not) a fresh
   conditional candidate; (b) whether the management divergence shows a
   regime-composition explanation; (c) the honest headline —
   REGIME-CONDITIONAL SURVIVORS FOUND / PANEL NULL / MIXED — and what it
   implies for the parked research fork.
5. Update the composition-node row status
   (`booked-spec-not-implemented` → implemented status per convention)
   and log the run in the spec's status history.

## 6. Honest expectation

The most likely outcome for any single dead strategy is "bad
everywhere." The panel's value is that it checks all of them at once,
cheaply, and converts the next fork-level decision from vibes to
measurement. A null result is a real deliverable — report it with the
same care as a positive.
