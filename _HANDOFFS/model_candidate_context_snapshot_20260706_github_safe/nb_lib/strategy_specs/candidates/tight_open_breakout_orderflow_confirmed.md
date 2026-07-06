---
name: "Tight Open Breakout Order-Flow Confirmed"
tagline: "Use footprint delta and imbalance confirmation as a filter on tight-state opening breakouts."
status: "untested-ideation"
created: 2026-05-20
updated: 2026-05-20
source: "Operator-provided footprint/order-flow video synthesis, 2026-05-20."

markets: ["MNQ", "NQ"]
session: "RTH"
time_of_day: "09:30-10:30 ET"
hold_duration: "intraday"

signal_type: "trend-continuation"
indicators: ["SMA(20)", "SMA(200)", "ATR(14)", "bar delta", "delta ratio", "ask/bid imbalances"]
timeframes_used: ["tick/aggressor-side source", "2-minute"]

brackets: "fixed-risk-dollar; stop at trigger bar extreme"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
  - "tight_opening_window_breakout_long"
  - "tight_opening_window_breakout_short"
  - "footprint_orderflow_reference"

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
  - trend-continuation
  - order-flow
  - footprint
  - regime-conditional
  - data-acquisition-required
---

# Tight Open Breakout Order-Flow Confirmed

## 1. Thesis

This candidate revisits the tight-state opening breakout family using
footprint confirmation. The prior tight opening-window breakout long
produced weak-positive but non-graduating informational results. The
hypothesis here is that tight-state continuation entries need evidence
that aggressive order flow is actually confirming the breakout.

For a long breakout, the trigger bar should have positive delta and/or
ask-side imbalance. For a short breakout, the trigger bar should have
negative delta and/or bid-side imbalance. The footprint layer is a filter,
not the primary structure.

Counter-hypothesis: delta confirmation is obvious and arrives too late,
removing good entries or keeping bad ones. It may reduce signal count
without improving expectancy.

## 2. Mechanism

- Tight SMA20/SMA200 state identifies compressed local structure.
- A completed breakout bar identifies directional attempt.
- Delta confirmation checks whether aggressive participants are aligned
  with the breakout.
- Imbalance confirmation checks whether the order flow is concentrated
  enough to matter.
- Opposite absorption is a warning that the breakout may be failing.

## 3. Entry Logic

Base structure:

- 2-minute MNQ/NQ RTH bars.
- SMA20/SMA200 compression: `abs(SMA20 - SMA200) / ATR14 <= 0.25`.
- Opening-window scan, likely 09:30-10:30 ET.

Long:

- Bar closes above SMA20 and SMA200.
- Bull elephant or bottoming-tail trigger.
- `bar_delta > 0`.
- `delta_ratio >= informed_prior_threshold`.
- Optional: ask imbalances present.
- No buying absorption on the trigger bar.

Short:

- Bar closes below SMA20 and SMA200.
- Bear elephant or topping-tail trigger.
- `bar_delta < 0`.
- `abs(delta_ratio) >= informed_prior_threshold`.
- Optional: bid imbalances present.
- No selling absorption on the trigger bar.

## 4. Exit Logic

Initial stop:

- Long: trigger low minus one tick.
- Short: trigger high plus one tick.

Candidate targets:

- Fixed-R baseline.
- 20-minute time exit.
- Later management only after the entry edge is measured.

## 5. Required Data

Blocked until the project has real footprint/order-flow data:

- Aggressor buy volume.
- Aggressor sell volume.
- Bid/ask volume at price for imbalance computation.

Do not approximate delta from candle direction.

## 6. Differentiation

This differs from `tight_opening_window_breakout_long` and its short
pair by requiring footprint confirmation. It is not a parameter tweak of
the previous family; it changes the evidence required for entry.

## 7. Phase 0 Questions

- Can the data pipeline compute delta and delta ratio lookahead-clean?
- Does the filter preserve enough R4 signal count?
- Does order-flow confirmation reduce clustered losses, or merely reduce
  sample size?
- Should long and short be tested as a paired family or separately?

## 8. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-20 | untested-ideation | Wiki entry authored from footprint video synthesis. Data acquisition / footprint metric layer required before Phase 0. |

