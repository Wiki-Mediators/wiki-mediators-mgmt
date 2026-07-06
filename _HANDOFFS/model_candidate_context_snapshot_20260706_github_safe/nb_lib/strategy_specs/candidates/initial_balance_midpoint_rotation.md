---
name: "Initial Balance Midpoint Rotation"
tagline: "Fade failed one-hour range extension back toward the initial balance midpoint."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: Initial Balance rotation concepts from auction market theory."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:30-14:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "level-rejection"
indicators: ["InitialBalanceHigh", "InitialBalanceLow", "InitialBalanceMid"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "volatility-adaptive"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: null
implementation: null
related_candidates: []

# Test status (only populated when status >= tested-*)
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

# Tags for organization (recommended controlled vocabulary in README)
tags:
  - rth-only
  - intraday
  - range-bound
  - level-based
  - fixed-risk-dollar
---

# Initial Balance Midpoint Rotation

## 1. Thesis

The first hour often defines the day's initial auction range. When price
extends outside that range but fails to hold, the initial balance
midpoint can act as the natural rotation magnet.

This candidate is level-only adaptation. It uses the first-hour high,
low, and midpoint as structural levels and avoids ATR or volatility
regime filters in the first version.

## 2. Mechanism (what edge it captures)

- Uses Initial Balance high/low as session structure, not arbitrary
  fixed bands.
- Requires failed extension outside the one-hour range.
- Targets the midpoint, where two-sided trade often rotates.
- Avoids the first hour itself because those levels are not complete
  until 10:30 ET.

## 3. Signal logic (entry conditions)

**Adaptive elements:**
- Rejection levels: Initial Balance high and low from 9:30-10:30 ET.
- Target anchor: Initial Balance midpoint.

**Fixed elements:**
- Short setup: price trades above IB high, then two consecutive
  5-minute closes back below IB high.
- Long setup: price trades below IB low, then two consecutive 5-minute
  closes back above IB low.
- Entry on the next 1-minute pullback that stays inside the IB.

## 4. Exit logic (stops, targets, time-based exits)

**Adaptive elements:**
- Stop: beyond the failed extension extreme.
- TP1: halfway from entry to IB midpoint.
- TP2: IB midpoint.

**Fixed elements:**
- No runner beyond the midpoint in v1.
- Time exit at 14:30 ET.

## 5. Position sizing

Use fixed dollar risk divided by the distance from entry to the failed
extension stop, capped by Apex limits.

## 6. Required indicators / data

Initial Balance high, low, and midpoint from 9:30-10:30 ET; 1-minute
and 5-minute bars for confirmation and entry. Current MNQ data supports
this.

## 7. Differentiation (vs already-tested strategies)

PRJ_3 used local fractal levels during the first 30 minutes and then
looked for continuation. This candidate waits until the full first-hour
range is known, trades failed extension back inside the range, and
targets the IB midpoint. It is structurally a rotation strategy, not a
fractal-pullback continuation.

It differs from batch-1 Failed ORB Fade because it uses the full
one-hour Initial Balance and midpoint target, not the 15-minute opening
range and opposite boundary.

## 8. Required research before spec drafting

- Decide whether Initial Balance is exactly 60 minutes on half-days.
- Check whether two 5-minute closes back inside is too restrictive.
- Decide one trade per day versus one per side.
- Verify whether midpoint targets pay enough after friction.

## 9. Source / references

Auction market theory and Initial Balance rotation concepts. No
strategy-specific performance claim is made.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch 2 (dynamic adaptive intraday focus). |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.4 R1-first triage applied.** R1 evidence diagnostic over 127 in-sample days measured 1-hr IB failed-extension reversion rate. **1,196 two-consec-inside events; 64 pullback-qualified; 55 qualifying after stop-band filter [8, 150]; 19 reverted 1R within 30min = 34.5%** — LOWEST R1 of any candidate tested project-wide. Direction: short 27.6% (8/29), long 42.3% (11/26); "neither" 36.4% (slow mechanism, median 10.5 min revert). **R1 verdict: NOT MET** (34.5% << 60% threshold). Compare to ORWS R1 79.5% — IB-rotation is **45 percentage points lower** despite using a "more developed" 1-hr level. **Initial Balance theory's "more development = stronger rejection" narrative is empirically refuted** on MNQ in this sample. **Candidate CLOSED at R1 gate** — no R4 probe, no FINAL spec, no implementation. Fourth consecutive R1-gate closure; v1.4 R1-first triage cumulative time saved ~24-40h. 15-pattern update. **Methodology pattern emerging**: across 5 mean-reversion/reversal R1 measurements, ONLY ORWS (79.5%) clears the 70% MET threshold; all variants and structural cousins underperform substantially. Diagnostic: `nb_lib/probe_results/initial_balance_midpoint_rotation_r1_diagnostic.json`. Closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_4_initial_balance_midpoint_rotation_closure.md`. |
