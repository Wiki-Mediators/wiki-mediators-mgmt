---
name: "MNQ News-Like Impulse Pullback"
tagline: "Trade the first controlled pullback after a mechanically detected MNQ impulse surge."
status: "untested-ideation"
created: 2026-05-13
updated: 2026-05-13
source: "Operator direction 2026-05-13; MNQ adaptation of transcript-captured equities first-pullback momentum pattern."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-15:15 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "momentum-pullback"
indicators: ["VolumeRatio(1m/30m)", "ATR(20) on 5-minute bars", "ATRRatio(5/30)", "BodyRangeRatio", "MACD(12,26,9)"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "structure-based"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: null
implementation: null
related_candidates: ["news_first_pullback_momentum.md"]

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
  - momentum
  - pullback
  - volatility-expansion
  - volume-conditional
  - fixed-risk-dollar
---

# MNQ News-Like Impulse Pullback

## 1. Thesis

MNQ does not have the equities scanner cascade, leading-gainer list, or
single-stock news-catalyst structure described in the original first
pullback transcript. What MNQ does have is event-like price action:
sudden volume expansion, wide directional bars, and a fast repricing
away from recent balance. This candidate tests whether the **first
controlled pullback after that kind of impulse** has continuation value.

The narrow hypothesis is not "news first pullback works on futures."
It is: when MNQ produces a news-like impulse that is visible directly in
price and volume, the first pullback that holds at least half the impulse
range may offer better risk location than buying the vertical move.

The counter-hypothesis is that this is just another continuation entry
with nicer language. Prior MNQ continuation and pullback systems have
failed. This candidate only earns a build if the entry design stays lean
enough to avoid the compound-predicate sparseness that closed
`choppiness_impulse_fade`.

## 2. Mechanism (what edge it captures)

- **Event-like repricing without a news feed.** A simultaneous volume
  spike, range expansion, and strong candle body is used as a mechanical
  proxy for "something just changed."
- **Do not buy the vertical bar.** The strategy waits for price to stop
  moving one-way and produce a first pullback, giving the impulse a
  chance to fail.
- **50% hold as demand/supply validation.** If the pullback holds the
  midpoint of the impulse leg, the initial move has not fully unwound.
- **First continuation trigger only.** The entry is the first break back
  in the impulse direction after the pullback, not the second or third
  attempt.
- **Fast-resolution discipline.** If the trade does not resolve quickly,
  the original impulse context is stale.

## 3. Signal logic (entry conditions)

This candidate should work with a deliberately small predicate set.
The proposed Phase 1 working set is:

1. **Impulse bar.** A completed 1-minute bar qualifies as an impulse if:
   volume is at least 3.0 times the trailing 30 completed 1-minute bars,
   bar range is at least 1.25 times ATR(20) from completed 5-minute
   bars, and body/range is at least 0.65.
2. **Impulse direction.** A green impulse bar creates a possible long
   setup. A red impulse bar creates a possible short setup.
3. **First pullback.** After the impulse, wait for at least one completed
   opposite-color 1-minute bar. The pullback can last up to 5 minutes.
4. **50% hold.** The pullback extreme must not retrace more than 50% of
   the impulse bar's open-to-close move.
5. **MACD momentum-health filter.** MACD(12,26,9) on completed
   1-minute closes should agree with the impulse direction. For longs,
   MACD line should be above the signal line or MACD histogram should be
   positive. For shorts, MACD line should be below the signal line or
   histogram should be negative. This ports the transcript's "do not buy
   once MACD has crossed against the move" rule without requiring a
   discretionary chart read.
6. **Continuation trigger.** Enter when the first completed 1-minute bar
   breaks the pullback's most recent high for a long, or most recent low
   for a short.

The design intentionally omits Level 2, daily resistance, news headline
confirmation, and leading-gainer rank. Those are valid parts of the
original equities strategy but are not available or not structurally
equivalent for MNQ. MACD is kept because it is mechanically calculable
from MNQ bars and maps directly to the original setup's trend-health
filter.

## 4. Exit logic (stops, targets, time-based exits)

- **Stop loss:** structure stop at the pullback extreme, plus a small
  buffer of 0.50 points.
- **Reward requirement:** require at least 1.50R available before the
  impulse extreme or projected continuation target. If not, skip.
- **TP1:** 1.0R, close 50% of contracts.
- **TP2:** 2.0R, close remaining contracts.
- **Break-even arming:** move runner stop to entry after TP1 fills or
  after MFE reaches 1.0R, whichever comes first.
- **Failure exit:** if price fails to move at least +0.50R within 5
  completed 1-minute bars after entry, exit at market on the next
  eligible 1-second bar.
- **Time exit:** exit any remaining position after 20 minutes or by
  15:58:30 ET, whichever comes first.

These are informed-prior brackets for a future Phase 1 spec. They are
not calibrated.

## 5. Position sizing

Use fixed-risk-dollar sizing:

```text
risk_dollars = 300
point_value = 2 dollars per MNQ point per contract
stop_pts = abs(entry_price - structure_stop)
contracts = floor(risk_dollars / (stop_pts * point_value))
contracts = clamp(contracts, 1, 15)
```

Skip if stop distance is below 3 points or above 25 points. Very small
stops are likely noise after friction; very large stops violate the
small-account pullback premise.

## 6. Required indicators / data

- MNQ 1-second OHLCV from the Databento store.
- 1-minute OHLCV derived from 1-second source.
- 5-minute ATR(20), Wilder smoothing, derived lookahead-clean from
  completed 5-minute bars.
- Trailing 30-bar 1-minute volume average.
- Body/range ratio from the completed impulse bar.
- MACD(12,26,9) on completed 1-minute closes. If nb_lib does not yet
  expose a MACD primitive, the Phase 1 spec must either add one or define
  a strategy-local computation using EMA(12), EMA(26), and EMA(9) of the
  MACD line.
- Optional Stage 0 diagnostic: ATRRatio(5/30) to describe whether
  impulse events cluster in volatility-expansion regimes. This should
  be descriptive only unless explicitly promoted in a later spec.

No external news feed, ES data, order book data, or equities scanner data
is required.

## 7. Differentiation (vs already-tested strategies)

This differs from Variant 1 and `noise_brk` because it does not trade a
fixed-time opening breakout. It waits for an actual detected impulse
event at any allowed time of day, then requires a first pullback and
continuation trigger.

It differs from PRJ_3 because it does not use fractal swing levels,
proximity touches, or a multi-stage trend-pullback rule. The level of
interest is the impulse bar itself and its 50% retracement.

It differs from `ema_trend` because no moving-average trend state is
used as the signal. Momentum is inferred from an event-like volume/range
bar, not from EMA slope or crossover.

It differs from `choppiness_impulse_fade` in the most important way:
this is continuation after an impulse that holds a first pullback, not a
fade of an impulse inside a choppy range. It also deliberately uses a
leaner predicate stack to avoid the sparse-signal failure mode.

It differs from the equities `news_first_pullback_momentum` entry
because this MNQ version replaces news/scanner/leading-gainer inputs
with price-and-volume proxies. It should be treated as a separate
futures hypothesis, not a direct port.

## 8. Required research before spec drafting

- Confirm whether the proposed impulse predicate fires often enough in
  the in-sample window before any P&L is measured.
- Decide whether the impulse anchor should be a single 1-minute bar or a
  multi-bar impulse leg. Single-bar is simpler and less gated; multi-bar
  may better match the transcript but risks sparseness.
- Verify whether the 3.0x volume and 1.25x ATR thresholds produce a
  useful number of candidate events. If not, do not repeatedly tune;
  either simplify the event definition or close the candidate.
- Decide whether shorts are allowed. The starting design is two-sided
  to avoid post-result direction selection.
- Decide whether MACD agreement is mandatory or whether the first
  signal-frequency preflight should count both with-MACD and
  without-MACD populations as descriptive diagnostics before locking the
  Phase 1 spec. If made mandatory, MACD must be treated as an informed
  prior and not tuned after P&L is observed.
- Define exact entry fill semantics using the existing T+1 second
  convention.
- Decide whether the "works instantly" exit belongs in Phase 1 or
  should be deferred to adaptive management.
- Run a lookahead audit on the impulse/pullback state machine before
  any in-sample P&L test.

## 9. Source / references

- Related wiki entry:
  [`news_first_pullback_momentum.md`](news_first_pullback_momentum.md),
  which preserves the original equities/news transcript logic.
- Operator direction on 2026-05-13: treat news as visible through price
  action, but label the MNQ adaptation separately and avoid over-gating.
- Internal cautionary precedent:
  `choppiness_impulse_fade` binding-constraint analysis, which showed
  that compound predicates can make otherwise plausible ideas too sparse
  to test cleanly.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-13 | `untested-ideation` | Created as separate MNQ adaptation of the equities first-pullback transcript. Working concept: news-like impulse detected by volume/range/body proxy, first pullback holds 50%, continuation entry, fixed-risk-dollar sizing. |
| 2026-05-13 | `untested-ideation` | Added MACD(12,26,9) as a mechanically calculable momentum-health filter, preserving the transcript's rule to avoid pullbacks after MACD turns against the move. |
| 2026-05-14 | `untested-ideation` | Phase 0 admissibility check: **INADMISSIBLE**. R3 (management lifecycle) and R4 (signal-frequency tolerance) not met; R1 (edge thesis), R2 (Apex survival), R5 (direction handling) partially met. Candidate does not progress to Phase 1 in current form. See `nb_lib_phase0_mnq_news_like_impulse_pullback.md`. |
