---
name: "Footprint-Confirmed Supply Demand Reaction"
tagline: "Trade structure-first supply/demand bounces only when footprint confirms the response."
status: "untested-ideation"
created: 2026-05-20
updated: 2026-05-20
source: "Operator-provided footprint/order-flow video synthesis, 2026-05-20."

markets: ["MNQ", "NQ"]
session: "RTH"
time_of_day: "09:30-15:30 ET"
hold_duration: "intraday"

signal_type: "supply-demand-reaction"
indicators: ["prior-day levels", "opening range", "VWAP bands", "delta", "stacked imbalances", "absorption"]
timeframes_used: ["tick/aggressor-side source", "1-minute", "5-minute"]

brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
  - "stacked_imbalance_zone_retest"
  - "wide_state_absorption_reversal"
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
  - mean-reversion
  - order-flow
  - footprint
  - data-acquisition-required
---

# Footprint-Confirmed Supply Demand Reaction

## 1. Thesis

This is the broad structure-first footprint strategy suggested by the
video. The trade begins with a real level: prior-day high/low, opening
range high/low, VWAP band, swing supply/demand, or a stacked imbalance
zone. Footprint is then used to confirm whether buyers or sellers are
responding at that level.

Counter-hypothesis: combining many possible structure sources creates an
over-broad discretionary framework that is hard to test cleanly. Phase 0
must narrow the structure source before implementation.

## 2. Mechanism

- Structure identifies where a reaction could matter.
- Price returning to that structure creates the setup.
- Delta turning in the reaction direction confirms participation.
- Stacked imbalances support the response.
- Absorption against the intended direction blocks the trade.

## 3. Entry Logic

Long demand reaction:

- Price returns to pre-defined demand.
- Delta turns positive.
- Ask imbalance or stacked ask imbalance appears.
- No buying absorption against the move.
- Response candle closes or breaks upward.
- Entry on break above response bar high or limit at zone midpoint.

Short supply reaction:

- Price returns to pre-defined supply.
- Delta turns negative.
- Bid imbalance or stacked bid imbalance appears.
- No selling absorption against the move.
- Response candle closes or breaks downward.
- Entry on break below response bar low or limit at zone midpoint.

## 4. Exit Logic

Stops are outside the structure zone. Targets may be fixed-R, VWAP,
opening-range midpoint, prior swing, or opposite structure. A FINAL spec
must choose one baseline before testing.

## 5. Required Data

Requires footprint metrics and a pre-defined structure source. Without
both, this becomes discretionary and should not be implemented.

## 6. Differentiation

This is broader than `stacked_imbalance_zone_retest`: the zone can come
from non-footprint structure, but footprint must confirm the reaction.
It is also more complex, so it should not be the first footprint build.

## 7. Phase 0 Questions

- Which one structure source is tested first?
- Does the chosen structure source have enough retests?
- Can no-absorption be expressed mechanically?
- Should this be split into separate supply and demand entries?

## 8. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-20 | untested-ideation | Wiki entry authored from footprint video synthesis. Broad framework captured for future narrowing; not first recommended build. |

