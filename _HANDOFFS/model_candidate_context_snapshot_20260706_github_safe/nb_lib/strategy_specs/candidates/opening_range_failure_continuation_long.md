---
name: "Opening Range Failure Continuation Long"
tagline: "Trade the hold, not the break: enter long only when an opening-range breakout pulls back and the level defends."
status: "tested-informational-rejected"
created: 2026-05-20
updated: 2026-05-21
source: "Strategic synthesis 2026-05-20 from session lessons: signal-at-start-of-move, objective levels, selectivity over frequency, with-trend continuation. Steers away from wide-state reversal (tested-dead) and signal-after-move mean reversion (fill-drift)."
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-11:00 ET"
hold_duration: "intraday"
signal_type: "trend-continuation"
indicators: ["opening range high/low", "ATR(14) 2-min", "EMA(8) 2-min"]
timeframes_used: ["1-second source", "2-minute derived"]
brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"
canonical_spec: "../canonical/opening_range_failure_continuation_long_spec_FINAL.md"
implementation: "../../scripts/opening_range_failure_continuation_long_canonical_alpha.py"
related_candidates:
  - "tight_opening_window_breakout_long"
  - "opening_range_width_switch"
test_results:
  in_sample_n: 69
  in_sample_pnl_dollars: -8608.30
  in_sample_pf: 0.38
  in_sample_win_rate: 31.9
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: "0/12"
tags:
  - rth-only
  - intraday
  - trend-continuation
  - breakout
  - pullback
  - opening-range
  - two-minute
  - objective-level
---

# Opening Range Failure Continuation Long

## 1. Thesis
The wide-state reversal family failed twice (price-only: -$14,054.50,
11/12 Apex failures; BVC-proxy: -$18,261.50, 12/12 failures) because it
faded extension against trend. This candidate does the opposite: it
trades WITH a confirmed opening-range break, but only after the break
proves itself by holding on a pullback.

Long thesis: price breaks above the opening-range high (first 30-minute
RTH range), then pulls back toward OR-high. If OR-high holds as support
(price does not re-enter the range and a completed 2-minute bar closes
back up off the level), enter long. The entry fires at the START of the
continuation leg (the hold), not after extension has already occurred.

Counter-hypothesis: most opening-range breaks fail, and the
pullback-hold may simply be a slower way of buying a failing breakout.
The selectivity of the hold-confirmation is the entire edge claim; if
holds are no more predictive than naive breaks, this is just a delayed
entry into the same failure surface.

## 2. Mechanism (what edge it captures)
- Opening-range high is an objective level watched by many participants;
  a break-and-hold signals acceptance above the morning balance.
- Most breaks fail (re-enter the range); requiring a pullback-hold
  filters the dense-signal problem by trading only breaks that defend.
- Signal fires at the hold (start of continuation), reducing the
  fill-time drift that hurt signal-after-move candidates.
- With-trend continuation, not counter-trend fade — avoids the
  wide-state reversal failure pattern.

## 3. Signal logic (entry conditions)
- Opening range = high/low of 09:30-10:00 ET (first fifteen 2-minute
  bars).
- After 10:00 ET, monitor for a break: a completed 2-minute bar closes
  above OR-high.
- After a confirmed break, monitor for a pullback toward OR-high:
  price trades back down to within 0.25 x ATR(14) of OR-high without a
  completed bar closing back below OR-high (no range re-entry).
- Entry trigger (the hold): a completed 2-minute bar closes back above
  the prior bar's high while price remains above OR-high, confirming
  the level defended.
- Long-only by design (paired short is a separate candidate; no
  post-hoc direction selection).
- Entry: stop-market at hold-bar high + 1 tick.
- Maximum one structural entry per day (the first valid hold).
- All bars evaluated on completion; lookback uses bars strictly before
  the current timestamp.

## 4. Exit logic (stops, targets, time-based exits)
- Initial stop: below OR-high - buffer (structural; the level that must
  hold for the thesis to be valid). Pre-commit buffer at spec stage.
- Stop-band guard: reject signal if stop distance < 5 pts or > 35 pts
  (Apex survival control from prior lessons).
- TP1: 1.0R, close half.
- TP2: 2.25R.
- BE arm: 1.5R (late, avoids the early-BE management trap seen in
  round_number and mhw).
- Max hold: 30 minutes (breaks that hold tend to run or fail fast).
- EOD flat by 15:58:30 ET.

## 5. Position sizing
Fixed dollar risk, $300 per trade: contracts = floor(300 / (stop_points
x $2)), capped at 12 MNQ contracts. Skip if contracts < 1. Daily loss
limit: 2 realized losing trades per RTH date.

## 6. Required indicators / data
Opening-range high/low (09:30-10:00 ET), ATR(14) on 2-minute bars,
EMA(8) on 2-minute bars (optional trend context). 2-minute bars derived
from MNQ 1-second OHLCV. No footprint, delta, or order-flow dependency
— fully OHLCV-testable.

## 7. Differentiation (vs already-tested strategies)
Unlike wide_opening_window_reversal_family (tested-dead, twice), this is
with-trend continuation, not counter-trend extension fade. Unlike
tight_opening_window_breakout_long (provisional-seed, marginal), it does
not enter on the breakout bar itself; it waits for the pullback-hold,
which is a selectivity filter the tight-opening scanner lacked. Unlike
opening_range_width_switch (component-useful, Apex-failed on variance),
it has a hard one-trade-per-day cap and tighter stop-band to control the
tail-driven path risk that strategy showed.

The core differentiator vs all prior breakout candidates: the entry is
the HOLD confirmation, not the break. This trades only breaks that have
already demonstrated acceptance.

## 8. Required research before spec drafting
- R4 probe: how often does a break-then-hold occur per RTH day? Risk is
  sparsity (most breaks fail outright, never producing a hold).
- Pre-commit the pullback-proximity threshold (0.25 x ATR) and the
  hold-confirmation bar logic before testing.
- Decide initial stop buffer below OR-high.
- Verify the hold-confirmation is not just a delayed entry into the same
  trades a naive breakout would take (overlap analysis vs naive OR
  breakout signals).
- Check whether one-trade-per-day cap leaves enough trades for n >= 80
  across 12-start multistart.

## 9. Informational multistart result
The operator explicitly bypassed the R4/v1.4 gate and requested direct
FINAL-spec implementation plus multistart on 2026-05-21. The result was
informational only and does not consume OOS.

Across 12 monthly starts (2024-08-01 through 2025-07-01, 42 trading-day
cap per start), the strategy produced 69 trades, aggregate P&L
-$8,608.30, aggregate PF 0.38, 31.9% win rate, 1/12 failed account
states, and 1/12 profitable starts. Exit attribution was dominated by
full stops (46 of 69 trades), which means the pullback-hold filter did
not produce the intended continuation survival advantage.

Report:
`C:\VMShare\NT8lab\nb_lib_opening_range_failure_continuation_long_multistart_informational_report.md`

## 10. Source / references
Strategic synthesis from 2026-05-20 session. Opening-range break-and-hold
is a standard intraday continuation pattern; the specific
pullback-hold-confirmation framing is shaped by session lessons about
signal-at-start-of-move timing and selectivity over raw frequency.

## 11. Status history
| Date | Status | Notes |
|------|--------|-------|
| 2026-05-20 | untested-ideation | Authored from session-lesson synthesis. With-trend OR break-and-hold continuation; deliberately steers away from wide-state reversal (tested-dead) and signal-after-move patterns (fill-drift). OHLCV-testable. Pending R4 probe for break-then-hold frequency. |
| 2026-05-21 | tested-informational-rejected | Operator bypassed R4/v1.4 gate and requested direct FINAL spec, implementation, and 12-start multistart. Informational result: n=69, P&L -$8,608.30, PF 0.38, win rate 31.9%, 1/12 failed starts, 0/12 pass rate. OOS not consumed. |
