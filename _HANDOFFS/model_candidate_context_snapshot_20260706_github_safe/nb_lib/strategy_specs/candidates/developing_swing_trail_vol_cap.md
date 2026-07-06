---
name: "Developing Swing Trail Vol Cap"
tagline: "Use developing swings for exits, but only in a bounded volatility regime."
status: "untested-ideation"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: structure-based trailing exits with volatility-regime guardrails."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:00-14:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "momentum"
indicators: ["VWAP", "ATRPercentile(60 sessions)", "DevelopingSwingHighLow(5-minute)"]
timeframes_used: ["1-minute", "5-minute"]

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
  - momentum
  - level-based
  - regime-conditional
---

# Developing Swing Trail Vol Cap

## 1. Thesis

Fixed targets can cut off a move too early, while unrestricted runners
can give too much back. This candidate uses developing 5-minute swing
levels as a trailing exit, but only when ATR percentile is moderate
enough that swing structure is not being shredded by extreme volatility.

The level adaptation is in the exit, not the entry. This is important:
it avoids repeating PRJ_3's failed fractal-pullback entry pattern.

## 2. Mechanism (what edge it captures)

- Enters simple intraday momentum after price holds on one side of VWAP.
- Uses ATR percentile to avoid both dead markets and extreme shock
  markets.
- Trails behind developing 5-minute swing levels as structural
  invalidation.
- Lets the market define the runner exit rather than using a fixed
  80-point TP2.

## 3. Signal logic (entry conditions)

**Adaptive elements:**
- Regime gate: ATRPercentile(60 sessions) must be between 0.40 and
  0.80.

**Fixed elements:**
- Long entry: price above VWAP for three consecutive 5-minute closes,
  then a 1-minute continuation close above the prior 1-minute high.
- Short entry: symmetric below VWAP.
- Time window: 10:00-14:30 ET.

The volatility cap is meant to find sessions where swing structure is
usable: enough movement to trail, but not so much jumpiness that every
swing is noise.

## 4. Exit logic (stops, targets, time-based exits)

**Adaptive elements:**
- Initial stop: most recent confirmed 5-minute swing low for longs or
  swing high for shorts.
- Runner trail: after +1.0R, move stop to each newly confirmed
  favorable 5-minute swing.

**Fixed elements:**
- TP1 at +1.0R closes half.
- No fixed TP2; runner exits on swing trail or EOD.
- EOD flat by 15:58:30 ET.

## 5. Position sizing

Use fixed dollar risk divided by the distance to the initial swing stop,
capped by Apex limits.

## 6. Required indicators / data

VWAP, ATRPercentile over 60 sessions, 1-minute bars, 5-minute bars, and
a confirmed developing swing high/low detector. This may reuse a
fractal-style concept, but it must be implemented as an exit-trailing
primitive, not a PRJ_3 entry trigger.

## 7. Differentiation (vs already-tested strategies)

PRJ_3 used fractal levels to enter after a pullback and then used fixed
targets. This candidate enters on VWAP-side momentum and uses developing
swings only for stop and runner management. The difference matters
because it tests whether structure improves exit behavior, not whether
fractal-touch entries have edge.

It differs from batch-1 ATR Regime Pullback Continuation because the
adaptive level component is the trailing exit, not the pullback entry.

## 8. Required research before spec drafting

- Define confirmed 5-minute swing without lookahead leakage.
- Pre-commit ATR percentile bounds.
- Decide whether swing trail confirmation is too slow for intraday
  execution.
- Watch curve-fit risk: this combines a volatility gate and a structural
  trail, so no further adaptive knobs should be added in v1.

## 9. Source / references

Structure-based trailing stop concepts from discretionary futures
trading and systematic trend-following. No specific research backing is
claimed.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch 2 (dynamic adaptive intraday focus). |
