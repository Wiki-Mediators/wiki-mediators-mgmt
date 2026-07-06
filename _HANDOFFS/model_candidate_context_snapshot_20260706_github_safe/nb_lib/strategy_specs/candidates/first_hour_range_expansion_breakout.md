---
name: "First Hour Range Expansion Breakout"
tagline: "Trade the resolution of the morning balance only when the break arrives with range expansion."
status: "phase-0-inadmissible-closed"
created: 2026-05-20
updated: 2026-05-20
source: "Strategic synthesis 2026-05-20 from session lessons: signal-at-expansion-bar timing, objective level (first-hour range), expansion filter for selectivity, balance-resolution continuation."
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:30-13:00 ET"
hold_duration: "intraday"
signal_type: "breakout"
indicators: ["first-hour range high/low", "ATR(14) 2-min", "recent range expansion ratio"]
timeframes_used: ["1-second source", "2-minute derived"]
brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"
canonical_spec: null
implementation: null
related_candidates:
  - "tight_opening_window_breakout_long"
  - "opening_range_width_switch"
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
tags:
  - rth-only
  - intraday
  - breakout
  - trend-continuation
  - volatility-expansion
  - first-hour-range
  - two-minute
  - objective-level
---

# First Hour Range Expansion Breakout

## 1. Thesis
The first trading hour (09:30-10:30 ET) establishes a balance area. When
that balance resolves with a decisive, expansion-driven break AFTER
10:30, the move that follows is the day's directional resolution. This
candidate trades that resolution — but only when the breaking bar shows
genuine range expansion, filtering the many weak pokes through the
first-hour boundary that immediately fail.

Long thesis: after 10:30, a completed 2-minute bar closes above the
first-hour high AND that bar's range exceeds a multiple of recent ATR
(expansion confirmation). Enter long in the breakout direction. Short
thesis: symmetric below first-hour low.

Counter-hypothesis: post-balance breakouts are a well-known, heavily
traded pattern. Any edge may be arbitraged away, or the expansion filter
may simply select the most volatile (and most likely to reverse) breaks.

## 2. Mechanism (what edge it captures)
- First-hour range is an objective, widely-watched balance area.
- Expansion requirement (breakout bar range > multiple of ATR) is a
  selectivity filter: it trades only decisive breaks, not the dense
  stream of marginal pokes that the failed wide-reversal and
  round-number families over-traded.
- Signal fires at the expansion bar (the start of the resolution move),
  not after the move has extended — reduces fill-time drift.
- Trades a different timing window (post-10:30 balance resolution) than
  opening-drive breakouts, which fire in the first few minutes.

## 3. Signal logic (entry conditions)
- First-hour range = high/low of 09:30-10:30 ET (first thirty 2-minute
  bars).
- After 10:30 ET, monitor for a breakout: a completed 2-minute bar
  closes above first-hour high (long) or below first-hour low (short).
- Expansion filter: the breakout bar's range (high - low) must be
  >= 1.5 x ATR(14) measured on bars before the breakout bar.
- Entry: stop-market at breakout-bar high + 1 tick (long) /
  low - 1 tick (short).
- Two-sided by design; direction set by which boundary breaks first.
- Maximum one structural entry per day (the first valid expansion
  break; once the day resolves, no second entry).
- Bars evaluated on completion; ATR lookback strictly before breakout
  bar.

## 4. Exit logic (stops, targets, time-based exits)
- Initial stop: mid-point of the first-hour range (structural; if price
  returns to mid-balance the breakout has failed). Alternative:
  fixed multiple of ATR. Pre-commit at spec stage.
- Stop-band guard: reject signal if stop distance < 5 pts or > 40 pts.
- TP1: 1.0R, close half.
- TP2: 2.25R.
- BE arm: 1.5R (late; expansion breakouts that work tend to run).
- Max hold: 40 minutes.
- EOD flat by 15:58:30 ET.

## 5. Position sizing
Fixed dollar risk, $300 per trade: contracts = floor(300 / (stop_points
x $2)), capped at 12 MNQ contracts. Skip if contracts < 1. Daily loss
limit: 2 realized losing trades per RTH date.

## 6. Required indicators / data
First-hour range high/low (09:30-10:30 ET), ATR(14) on 2-minute bars,
recent range-expansion ratio (breakout bar range / ATR). 2-minute bars
derived from MNQ 1-second OHLCV. No footprint or order-flow dependency
— fully OHLCV-testable.

## 7. Differentiation (vs already-tested strategies)
Unlike tight_opening_window_breakout_long (scans 09:30-10:30 for
breakouts), this trades the resolution AFTER 10:30 of the balance that
formed during that window — different timing, different thesis (balance
resolution vs opening continuation). Unlike opening_range_width_switch
(used OR width to switch modes, Apex-failed on variance), this uses a
fixed expansion filter and a one-trade-per-day cap to control the
tail-driven path risk. Unlike wide-state reversal (tested-dead), this is
with-direction breakout, not counter-trend fade.

The core differentiator: the expansion filter. Most prior breakout
candidates entered on any boundary break; this requires the break to
arrive with measurable range expansion, trading only decisive
resolutions.

## 8. Required research before spec drafting
- R4 probe: how often does a post-10:30 expansion break occur per RTH
  day? The expansion filter could make this sparse (few breaks meet the
  1.5x ATR bar). Verify frequency supports n >= 80 across multistart.
- Pre-commit the expansion multiple (1.5x ATR) and stop reference
  (range mid vs ATR multiple) before testing.
- Overlap check: does the expansion filter select genuinely different
  trades than a naive first-hour breakout, or just the most volatile
  (and most reversal-prone) ones?
- Honest concern: post-balance breakout is a crowded pattern. The
  expansion filter is the edge claim; if expansion-filtered breaks are
  no better than naive breaks, this joins the failed continuation fleet.
- Direction balance check (upside vs downside resolution).

## 9. Source / references
Strategic synthesis from 2026-05-20 session. First-hour balance and
range expansion are standard intraday concepts; the post-10:30
expansion-filtered framing is shaped by session lessons about
selectivity (expansion filter) and signal-at-start-of-move timing
(the expansion bar is the entry trigger).

## 10. Status history
| Date | Status | Notes |
|------|--------|-------|
| 2026-05-20 | untested-ideation | Authored from session-lesson synthesis. Post-10:30 first-hour balance resolution with mandatory range-expansion filter. With-direction breakout, expansion-selective, one-trade-per-day cap. OHLCV-testable. Pending R4 probe for expansion-break frequency. |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.4 R1-first triage applied (Phase A batch).** R1 evidence diagnostic measured post-10:30 expansion-break continuation rate. 1.5×ATR expansion filter passed **only 2 of 127 days (1.6%)** — extreme over-restrictiveness. 1 long event continued; 1 short event "neither" within 30min. **R1 verdict: NOT MET at 50.0% with n=2 (low-confidence — statistical CI [0%, 100%]).** **Filter over-restrictiveness is the binding constraint** — same pattern as APTH's compound regime gate (97.5% of days eliminated). The expansion filter's selectivity is so high that the candidate cannot generate enough events for meaningful R1 measurement. Section 8 of wiki acknowledged this risk ("The expansion filter could make this sparse"). Candidate CLOSED at R1 gate. Diagnostic: `nb_lib/probe_results/first_hour_range_expansion_breakout_r1_diagnostic.json`. Combined Phase A closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_4_phase_a_closures.md`. |
