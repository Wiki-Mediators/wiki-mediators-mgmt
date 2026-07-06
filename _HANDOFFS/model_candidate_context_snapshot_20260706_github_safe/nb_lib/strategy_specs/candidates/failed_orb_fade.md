---
name: "Failed Opening Range Breakout Fade"
tagline: "Trade the trap after the first breakout fails."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: common opening range breakout failure and fade pattern from discretionary futures trading."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-11:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "breakout-failure"
indicators: ["OpeningRange(09:30-09:45)", "ATR(20) on 5-minute bars"]
timeframes_used: ["1-second", "2-minute", "5-minute"]

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
  - opening-range
  - breakout-failure
  - fixed-risk-dollar
---

# Failed Opening Range Breakout Fade

## 1. Thesis

Opening range breakouts are crowded. When price breaks the early range
and quickly returns inside, trapped breakout traders may unwind and
create a move toward the opposite side of the range.

This candidate tests the failure of an opening breakout rather than the
breakout itself. It should only trigger after the market rejects the
outside auction and re-enters the opening range.

## 2. Mechanism (what edge it captures)

- Uses the 9:30-9:45 ET opening range as a liquidity reference.
- Requires a breakout failure, not just a test of the boundary.
- Trades against trapped momentum after range re-entry.
- Attempts to exploit choppy or balanced sessions where opening
  continuation is rejected.

## 3. Signal logic (entry conditions)

Define the 9:30-9:45 opening range high and low. A long setup requires
price to break below the OR low by at least 0.25 x ATR(20) on 5-minute
bars, then close back inside the range on a 2-minute bar. A short setup
is symmetric above the OR high.

Entry is on the first pullback or retest after re-entry, not immediately
on the failure close. No new entries after 11:30 ET.

## 4. Exit logic (stops, targets, time-based exits)

Stop beyond the failed breakout extreme. TP1 is the opening range
midpoint. TP2 is the opposite opening range boundary. EOD flat applies,
but the expected holding window is morning-only.

## 5. Position sizing

Use fixed dollar risk based on the actual stop distance from entry to
the failed breakout extreme, capped by Apex contract limits.

## 6. Required indicators / data

MNQ 1-second bars for execution, 2-minute bars for confirmation, and
ATR(20) on 5-minute bars for breakout-distance normalization. All data
is available from current MNQ bars.

## 7. Differentiation (vs already-tested strategies)

The rejected opening strategies attempted to participate in early
directional movement with fixed brackets. This candidate waits for the
opening breakout to fail and then trades the reversal back into the
range, with risk based on the actual failed-auction extreme.

## 8. Required research before spec drafting

- Define exact pullback/retest entry mechanics after re-entry.
- Decide whether one failed breakout per side or one total trade per
  day is allowed.
- Verify that 2-minute confirmation does not introduce timestamp
  lookahead.
- Check if strong trend opens should be filtered by VWAP slope or early
  realized range.

## 9. Source / references

Common opening range breakout failure and fade concept from
discretionary futures trading. No specific performance literature is
claimed.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | untested-ideation | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch. |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.5 R1-first triage sweep applied.** R1 diagnostic measured failed-OR-fade reversion (with 0.25*ATR sweep depth + 2-min close back inside). **132 qualifying events; 51 reverted 1R within 30min (38.6%)**, 80 hit stop first, 1 neither. **R1 verdict: NOT MET — 40.9pp below ORWS's 79.5%.** Structurally near-identical to ORWS (15-min OR + fade) with only the sweep-depth filter + 2-min confirmation as differences. **Third consecutive demonstration of filter-augments-don't-help pattern**: every ORWS variant with additional filters (OR-LSR, RNVLS, failed_orb_fade) underperforms the base by 27-41pp. **The base ORWS mechanism IS the edge; additional filters select for signals where the favorable reversion has already partially happened.** Candidate CLOSED at R1 gate. Diagnostic: `nb_lib/probe_results/failed_orb_fade_r1_diagnostic.json`. Combined sweep closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_5_sweep_closures.md`. |
