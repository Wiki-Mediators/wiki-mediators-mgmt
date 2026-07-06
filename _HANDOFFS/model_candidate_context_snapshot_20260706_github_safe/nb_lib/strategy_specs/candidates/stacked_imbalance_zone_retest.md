---
name: "Stacked Imbalance Zone Retest"
tagline: "Create supply/demand zones from stacked footprint imbalances and trade later retests."
status: "untested-ideation"
created: 2026-05-20
updated: 2026-05-20
source: "Operator-provided footprint/order-flow video synthesis, 2026-05-20."

markets: ["MNQ", "NQ"]
session: "RTH"
time_of_day: "09:30-15:30 ET"
hold_duration: "intraday"

signal_type: "supply-demand-retest"
indicators: ["bid/ask volume at price", "stacked ask imbalances", "stacked bid imbalances", "delta"]
timeframes_used: ["tick/aggressor-side source", "1-minute", "2-minute", "5-minute"]

brackets: "zone anchored"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
  - "footprint_confirmed_supply_demand_reaction"
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
  - intraday
  - supply-demand
  - order-flow
  - footprint
  - stacked-imbalance
  - data-acquisition-required
---

# Stacked Imbalance Zone Retest

## 1. Thesis

Stacked imbalances can mark zones where aggressive order flow created
meaningful supply or demand. This candidate does not enter on the first
stack. It records the zone, waits for price to return, and trades only
if the retest shows footprint confirmation.

Counter-hypothesis: stacked imbalances mark exhaustion as often as
continuation, and retests may occur after the original order-flow
information is stale.

## 2. Mechanism

- Consecutive ask imbalances near a swing low define demand.
- Consecutive bid imbalances near a swing high define supply.
- The zone high/low comes from the stacked price levels.
- A later retest tests whether the zone still attracts response.
- Delta confirmation on retest prevents blind limit buying/selling.

## 3. Entry Logic

Zone creation:

- `stacked_ask_imbalances_count >= 3` near swing low creates demand.
- `stacked_bid_imbalances_count >= 3` near swing high creates supply.
- Imbalances should be consecutive price levels, or separated by no
  more than one tick if explicitly pre-committed.

Long retest:

- Price returns to demand zone.
- Delta turns positive on retest.
- No bearish absorption.
- Entry on response bar high break or zone-mid limit.
- Stop below zone low plus buffer.

Short retest:

- Price returns to supply zone.
- Delta turns negative on retest.
- No bullish absorption.
- Entry on response bar low break or zone-mid limit.
- Stop above zone high plus buffer.

## 4. Exit Logic

Targets:

- Prior swing high/low.
- VWAP.
- Fixed-R.
- Opposite side of opening range.

## 5. Required Data

Requires bid/ask volume at each price level. Bar-level delta alone is
not sufficient.

## 6. Differentiation

This is the most footprint-native candidate from the video synthesis.
It differs from delta-confirmed breakouts because it creates and stores
zones from the footprint itself.

## 7. Phase 0 Questions

- Can the data store build reliable footprint ladders for MNQ/NQ?
- How long does a stacked imbalance zone remain valid?
- Is zone retest frequency sufficient?
- Does a limit entry or confirmation-break entry fit Apex better?

## 8. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-20 | untested-ideation | Wiki entry authored from footprint video synthesis. Requires footprint ladder data before Phase 0. |

