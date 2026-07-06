---
name: "Footprint Order-Flow Reference"
tagline: "Reference note for delta, imbalance, stacked imbalance, and absorption concepts as strategy filters."
status: "research-reference"
created: 2026-05-20
updated: 2026-05-20
source: "Operator-provided footprint/order-flow video synthesis, 2026-05-20."

markets: ["MNQ", "NQ"]
session: "RTH"
time_of_day: "varies"
hold_duration: "intraday"

signal_type: "order-flow-confirmation"
indicators: ["delta", "delta_ratio", "bid/ask volume at price", "stacked imbalances", "absorption"]
timeframes_used: ["tick/aggressor-side source", "1-minute", "2-minute", "5-minute"]

brackets: "not applicable"
position_sizing: "not applicable"

canonical_spec: null
implementation: null
related_candidates:
  - "tight_open_breakout_orderflow_confirmed"
  - "wide_state_delta_divergence_reversal"
  - "wide_state_absorption_reversal"
  - "stacked_imbalance_zone_retest"
  - "footprint_confirmed_supply_demand_reaction"

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
  - order-flow
  - footprint
  - data-acquisition-required
  - research-reference
---

# Footprint Order-Flow Reference

## 1. Purpose

This note preserves the footprint/order-flow concepts from the operator
video synthesis. It is a reference layer, not a strategy. The video does
not provide a complete standalone system; it provides confirmation tools
that can be layered onto structure-first strategies.

Core rule:

> Identify structure first. Use footprint to see who is active at the
> level.

For this project, footprint should be treated as a filter or trigger
layer on top of existing MNQ/NQ structures: tight-state breakouts,
wide-state reversals, opening-range levels, prior-day levels, VWAP bands,
and swing supply/demand.

## 2. Required Data

Normal OHLCV bars are not enough.

Required data for honest testing:

- Bid volume at each price level inside each bar.
- Ask volume at each price level inside each bar.
- Total volume at each price level.
- Bar-level delta.
- Preferably tick data with aggressor-side classification, or a
  historical footprint export from a platform.

If the project only has 1-second OHLCV, these candidates remain blocked.
Do not approximate footprint from candle color. That would erase the
point of the signal.

## 3. Delta

```python
delta = aggressive_buy_volume - aggressive_sell_volume
delta_ratio = delta / total_volume
```

Interpretation:

- Price up with positive delta: move confirmed.
- Price down with negative delta: move confirmed.
- Price up with weak or negative delta: possible exhaustion.
- Price down with weak or positive delta: possible exhaustion.

`delta_ratio` is preferred over raw delta for MNQ/NQ because raw volume
varies by session, contract, and event state.

## 4. Imbalances And Stacked Imbalances

A footprint imbalance compares aggressive activity at adjacent price
levels. Candidate formulas:

```python
ask_imbalance = ask_volume_at_price / bid_volume_at_price_below
bid_imbalance = bid_volume_at_price / ask_volume_at_price_above
```

A single imbalance is context. Three or more consecutive imbalances form
a stronger signal:

- Stacked ask imbalances near a low can mark demand.
- Stacked bid imbalances near a high can mark supply.

This should usually create a zone first. The trade happens on retest and
response, not blindly on the original stack.

## 5. Absorption

Absorption is high effort with low progress:

```text
high volume + large delta + little/no price movement
```

Examples:

- Large positive delta but price cannot make new highs: buying may be
  absorbed by passive sellers.
- Large negative delta but price cannot make new lows: selling may be
  absorbed by passive buyers.

Absorption is most useful at pre-defined structure: prior high/low,
opening-range extreme, VWAP band, wide SMA-state extension, or a
pre-existing supply/demand zone.

## 6. Strategy Families Captured From This Reference

The concepts decompose into five candidate families:

1. `tight_open_breakout_orderflow_confirmed` - tight-state breakout
   with delta/imbalance confirmation.
2. `wide_state_delta_divergence_reversal` - wide-state reversal when
   price extends but delta weakens or diverges.
3. `wide_state_absorption_reversal` - wide-state reversal after large
   one-sided delta fails to produce progress.
4. `stacked_imbalance_zone_retest` - supply/demand zone created by a
   stacked imbalance, traded on later retest.
5. `footprint_confirmed_supply_demand_reaction` - broader structure
   bounce/rejection confirmed by delta and imbalances.

## 7. Build Order

Do not build all strategies at once.

Practical order:

1. Build footprint metric extraction:
   - `bar_delta`
   - `delta_ratio`
   - ask/bid imbalance counts
   - stacked imbalance counts
   - absorption score
2. Add delta confirmation to an existing tight-state breakout.
3. Test wide-state reversal with absorption or delta divergence.
4. Only then test stacked imbalance zone retests.

## 8. Methodology Notes

- Footprint data is a new data class for this project.
- Any candidate using it needs a data readiness pass before Phase 0.
- R4 count probes must use real footprint-derived fields, not OHLCV
  proxies.
- A footprint filter can reduce trade count sharply; signal frequency
  must be measured before spec drafting.
- Structure-first is non-negotiable: footprint alone is not a strategy.

## 9. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-20 | research-reference | Footprint/order-flow concepts captured as a reference note. Candidate entries split separately. Data availability is the primary blocker. |

