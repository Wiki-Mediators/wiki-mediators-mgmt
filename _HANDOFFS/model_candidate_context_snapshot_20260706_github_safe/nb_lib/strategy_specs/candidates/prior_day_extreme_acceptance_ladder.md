---
name: "Prior Day Extreme Acceptance Ladder"
tagline: "Continue only after price accepts beyond yesterday's high or low."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: prior-day high/low acceptance behavior from auction market trading."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-15:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "level-acceptance"
indicators: ["PriorDayHigh", "PriorDayLow", "PriorDayClose"]
timeframes_used: ["1-second", "1-minute", "5-minute", "daily"]

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
  - breakout
  - level-based
  - fixed-risk-dollar
---

# Prior Day Extreme Acceptance Ladder

## 1. Thesis

Prior-day high and low are visible reference levels. A single poke
through them is often noise, but sustained acceptance beyond them can
signal that yesterday's range is no longer containing the auction.

This candidate uses only level-based adaptation: entries, stops, and
targets are placed relative to yesterday's high/low/close rather than
fixed point distances.

## 2. Mechanism (what edge it captures)

- Uses prior-day extremes as widely observed auction boundaries.
- Requires acceptance, not first touch.
- Places the stop where the acceptance thesis fails: back inside the
  prior range.
- Uses a level ladder for targets instead of fixed 10/80 brackets.

## 3. Signal logic (entry conditions)

**Adaptive elements:**
- Long acceptance level: prior RTH high.
- Short acceptance level: prior RTH low.

**Fixed elements:**
- Long entry requires two consecutive 5-minute closes above prior high,
  then a 1-minute pullback that holds above prior high.
- Short entry is symmetric below prior low.
- Time window: 09:45-15:00 ET.

The level matters because acceptance beyond yesterday's range suggests
new auction territory rather than a normal pullback inside value.

## 4. Exit logic (stops, targets, time-based exits)

**Adaptive elements:**
- Stop: 2 ticks back inside the prior range after entry.
- TP1: distance equal to the prior day's range midpoint extension from
  the broken extreme.
- TP2: full prior-day range extension from the broken extreme.

**Fixed elements:**
- No entry after 15:00 ET.
- EOD flat by 15:58:30 ET.

## 5. Position sizing

Use fixed dollar risk divided by stop distance. This will naturally
trade smaller size when the pullback entry is far from the invalidation
level and larger size when it is tight, subject to Apex caps.

## 6. Required indicators / data

Prior RTH high, low, and close from daily aggregation of MNQ bars;
1-minute and 5-minute bars for acceptance and pullback. Current data
supports these levels if daily aggregation is implemented carefully.

## 7. Differentiation (vs already-tested strategies)

PRJ_3 used developing fractal levels inside the morning window and a
proximity touch plus confirmation entry. This candidate uses prior-day
session extremes and requires acceptance beyond the level before a
pullback entry. The difference matters because the trade thesis is
range expansion from a public auction boundary, not continuation from a
local fractal swing.

It differs from batch-1 Failed ORB Fade because it continues after
accepted breakout rather than fading a failed opening range break.

## 8. Required research before spec drafting

- Define prior RTH high/low on half-days and holidays.
- Decide whether Globex highs/lows are excluded from the prior-day
  reference.
- Check whether two 5-minute closes is too slow or too strict.
- Verify that target ladder based on prior-day range does not create
  extreme reward targets on unusually wide days.

## 9. Source / references

Auction market and prior-day high/low breakout-acceptance concepts from
futures trading practice.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch 2 (dynamic adaptive intraday focus). |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.5 R1-first triage sweep applied.** R1 diagnostic measured PDH/PDL acceptance continuation (two-consec-5m close above PDH + 1-min pullback hold). **35 qualifying events (26L/9S — 74% long); 19 continued 1R within 30min (54.3%)**, 16 hit stop first, 0 neither. **R1 verdict: NOT MET** at 54.3% — highest in v1.5 sweep but still below 60% threshold. Direction asymmetry (74% L) exceeds 65% pre-committed bound but moot given R1 fail. Continuation past PDH/PDL has weak edge on MNQ intraday: roughly coin-flip in this sample. Median continuation time 0.6 min (very fast resolution). Candidate CLOSED at R1 gate. Diagnostic: `nb_lib/probe_results/prior_day_extreme_acceptance_ladder_r1_diagnostic.json`. Combined sweep closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_5_sweep_closures.md`. |
