---
name: "News First Pullback Momentum"
tagline: "Buy the first pullback after a news-driven momentum squeeze once price proves it can hold above the 50% retracement."
status: "phase-0-inadmissible-closed"
created: 2026-05-13
updated: 2026-05-13
source: "Operator-provided trading-class transcript, 2026-05-13; discretionary small-account first-pullback momentum setup."

# Market and timing
markets: ["US equities"]
session: "pre-market/RTH"
time_of_day: "pre-market through morning RTH; exact window TBD"
hold_duration: "intraday"

# Signal characteristics
signal_type: "momentum-pullback"
indicators: ["news catalyst", "relative volume", "MACD", "daily resistance levels", "Level 2 liquidity"]
timeframes_used: ["1-minute", "daily", "Level 2/order book"]

# Execution
brackets: "structure-based"
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
  - intraday
  - momentum
  - pullback
  - news-driven
  - small-account
  - data-acquisition-required
---

# News First Pullback Momentum

## 1. Thesis

News-driven small-cap momentum can attract attention rapidly through
scanners, relative-volume alerts, and leading-gainer lists. The initial
move creates crowd awareness, but buying into the vertical squeeze has
poor risk location. The first pullback gives the trade a chance to fail;
if it holds above the 50% retracement and then makes a new high, the
next leg can resolve quickly as late buyers and dip buyers enter.

The setup is explicitly designed for consistency rather than home-run
holding. The speaker frames it as a small-account pattern: wait for the
highest-conviction pullback, define risk at the pullback low, require
roughly 2:1 reward-to-risk toward high-of-day or the next major level,
and bail quickly if the trade does not work immediately.

## 2. Mechanism (what edge it captures)

- **Scanner attention cascade.** Breaking news plus unusual relative
  volume puts the stock on many traders' scanners at the same time.
- **First-pullback validation.** The first red candle or brief pullback
  tests whether early profit-taking will fully unwind the move. Holding
  above the 50% retracement is treated as proof the move still has
  demand.
- **Trend-shift trigger.** The first candle to make a new high after the
  pullback marks a micro trend shift from pullback back to continuation.
- **Obviousness premium.** Leading percentage gainers with news are more
  visible, so the crowd can keep returning to the same symbol.
- **Fast-resolution discipline.** The speaker's rule is "breakout or
  bailout": if the trade does not move immediately after entry, exit
  early rather than waiting for max loss.

## 3. Signal logic (entry conditions)

Core long setup:

- Instrument is a stock with a fresh catalyst or breaking news.
- Stock is moving unusually fast on high relative volume and ideally is
  among the leading percentage gainers.
- Initial move consists of one or more strong green candles.
- Wait for the first pullback: at least one red candle, with two or
  three red candles acceptable.
- Pullback must hold at least the 50% retracement of the initial move.
- MACD should remain positive; avoid entries after MACD crosses
  negative.
- Optional confirmation: bottoming tail on the pullback candle, large
  buyer on Level 2, or obvious support near half/whole-dollar level.
- Entry is the first candle to make a new high after the pullback.

Do not enter:

- During the initial vertical squeeze before a pullback.
- If the pullback retraces more than 50% of the initial move.
- If the stock has no real catalyst and appears to be a scanner false
  alarm.
- If nearby daily resistance, a large Level 2 seller, or negative MACD
  suggests the continuation leg is unlikely.

## 4. Exit logic (stops, targets, time-based exits)

- **Stop loss:** low of the pullback. The speaker warns against
  arbitrary tight stops because the chart can remain valid even if a
  too-tight stop is tagged.
- **Reward requirement:** target should offer about 2:1 reward-to-risk.
  If entry-to-pullback-low risk is 20 cents, the high-of-day retest or
  next target should be roughly 40 cents away.
- **Primary target:** retest of high of day.
- **Secondary targets:** half-dollar and whole-dollar levels, then
  larger psychological levels if momentum continues.
- **Failure exit:** if the trade does not work instantly after the new
  high trigger, exit early rather than waiting for full stop.
- **Runner exit:** take profits into topping tails, heavy sellers on
  Level 2, first red candle after a strong extension, or loss of
  momentum.
- **Time horizon:** very short intraday hold, often minutes.

## 5. Position sizing

Position size is based on dollar risk to the pullback low:

`shares = risk_dollars / (entry_price - pullback_low)`

The speaker emphasizes that the same pattern can be traded with small
or large accounts; only size changes. For nb_lib translation, use
fixed-risk-dollar sizing rather than fixed contracts/shares.

## 6. Required indicators / data

This is not directly testable with the current MNQ-only nb_lib store.
Required data for the original equities setup:

- Intraday equities OHLCV, preferably 1-minute or finer.
- News catalyst feed with timestamp.
- Relative volume or scanner-style unusual-volume metric.
- Leading percentage gainer rank.
- Daily chart levels and moving averages, especially nearby resistance.
- MACD.
- Level 2/order book size for large buyers/sellers.

Current nb_lib gaps:

- No equities universe.
- No scanner data.
- No news feed for equities.
- No Level 2/order book data.
- MACD is not currently in nb_lib.

Possible MNQ adaptation would need to replace "breaking news stock on
scanner" with an event-driven futures catalyst or an unusual-volume /
range-expansion proxy. That would be a different strategy and should
not be assumed equivalent.

## 7. Differentiation (vs already-tested strategies)

This differs from `noise_brk` and Variant 1 because it does not buy a
fixed-time morning breakout. It waits for an existing news-driven move,
then enters only after the first pullback proves it can hold.

It differs from PRJ_3 because the level is not a fractal pullback within
a generic trend. The whole setup depends on catalyst-driven attention,
relative volume, leading-gainer obviousness, and a first-pullback
microstructure trigger.

It differs from `ema_trend` because MACD is only a filter against a
failed trend shift, not the primary signal.

It differs from current MNQ candidates because it is originally an
equities/scanner/news strategy. Treating it as immediately portable to
MNQ would be a category error unless a futures-specific catalyst and
attention proxy are specified.

## 8. Required research before spec drafting

- Decide whether this remains an equities-only wiki idea or gets an MNQ
  adaptation.
- If equities-only: identify data source for intraday OHLCV, news,
  relative volume, leading-gainer rank, and Level 2.
- Define "fresh catalyst" mechanically.
- Define "leading gainer" threshold mechanically.
- Define the initial move and 50% retracement anchor.
- Decide whether pre-market signals are allowed or only RTH.
- Replace discretionary Level 2 observations with testable proxies, or
  explicitly mark Level 2 as required.
- Add MACD to nb_lib if this becomes a candidate for implementation.
- Define "works instantly" as a mechanical bailout rule, such as failure
  to move +0.5R within N bars.
- Decide how to handle multiple pullbacks. The transcript favors first
  and second pullbacks, with first strongest.

## 9. Source / references

- Operator-provided transcript from a trading class on the "first
  pullback" candlestick pattern, 2026-05-13.
- The speaker describes a discretionary small-account strategy centered
  on breaking-news momentum stocks, scanner attention, first pullback,
  50% retracement hold, first candle to make a new high, pullback-low
  stop, and 2:1 reward-to-risk.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-13 | `untested-ideation` | Added from operator-provided transcript. Preserves the original equities/news first-pullback logic and flags current nb_lib data gaps before any MNQ adaptation. |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.5 R1-first triage sweep — closed as INAPPLICABLE to MNQ.** Wiki frontmatter explicitly declares `markets: ["US equities"]`. Predicates reference stock-trading infrastructure: "Instrument is a stock with a fresh catalyst", "large buyer on Level 2", "scanner false alarm." These concepts (single-name news flow, Level 2 multi-venue order book, relative-volume scanners, leading percentage gainers) don't apply to index futures. **No R1 diagnostic run** — candidate is target-mismatched for the MNQ project, not predicate-mismatched. Post-hoc reframing to make a stock-trading candidate testable on MNQ would substantially change the candidate's intent, which is the post-hoc-tuning trap project discipline avoids. Wiki remains for reference (operator may extract concepts into a future MNQ-targeted catalyst-volume candidate). Combined sweep closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_5_sweep_closures.md`. |
