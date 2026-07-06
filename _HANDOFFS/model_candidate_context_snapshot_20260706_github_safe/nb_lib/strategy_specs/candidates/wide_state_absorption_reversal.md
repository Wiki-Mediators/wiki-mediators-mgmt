---
name: "Wide-State Absorption Reversal"
tagline: "Fade wide-state extensions when large one-sided delta produces little price progress."
status: "untested-ideation"
created: 2026-05-20
updated: 2026-05-20
source: "Operator-provided footprint/order-flow video synthesis, 2026-05-20."

markets: ["MNQ", "NQ"]
session: "RTH"
time_of_day: "09:30-12:00 ET"
hold_duration: "intraday"

signal_type: "mean-reversion"
indicators: ["SMA(20)", "SMA(200)", "ATR(14)", "delta", "relative volume", "absorption score"]
timeframes_used: ["tick/aggressor-side source", "2-minute", "5-minute"]

brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
  - "wide_state_delta_divergence_reversal"
  - "wide_opening_window_reversal_long"
  - "wide_opening_window_reversal_short"
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
  - mean-reversion
  - absorption
  - order-flow
  - footprint
  - data-acquisition-required
---

# Wide-State Absorption Reversal

## 1. Thesis

Absorption is high effort with low progress. This candidate fades
wide-state extensions only when aggressive participants appear unable to
move price further.

Short thesis: in a wide-upside state near resistance or an opening-range
high, strong positive delta with little upward progress means passive
sellers may be absorbing buyers. Long thesis is the inverse.

Counter-hypothesis: large delta with small progress can be normal
rotation inside a strong trend and may not predict reversal.

## 2. Mechanism

- Wide-state extension marks a stretched price condition.
- Large same-direction delta marks effort.
- Small candle body or failed new extreme marks lack of progress.
- Break of the absorption candle confirms that the absorbed side lost
  control.

## 3. Entry Logic

Short absorption:

- Wide-upside state.
- Price at or near resistance, opening-range high, prior-day high, VWAP
  upper band, or supply zone.
- Strong positive delta by percentile or delta ratio.
- High volume relative to recent bars.
- Body-to-range small, or price progress capped within a few ticks.
- Entry on break below absorption bar low.
- Stop above absorption high.

Long absorption:

- Wide-downside state.
- Price at or near support, opening-range low, prior-day low, VWAP lower
  band, or demand zone.
- Strong negative delta by percentile or delta ratio.
- High volume relative to recent bars.
- Body-to-range small, or price progress capped within a few ticks.
- Entry on break above absorption bar high.
- Stop below absorption low.

## 4. Exit Logic

Targets can be fixed-R, VWAP, opening-range midpoint, or SMA20 touch.
The first spec should choose one baseline before P&L testing.

## 5. Required Data

Requires aggressor-side delta and volume. Absorption cannot be inferred
from OHLCV alone.

## 6. Differentiation

This is a stronger filter than price-only wide reversal. It asks for
failed order-flow effort at the stretched location before fading.

## 7. Phase 0 Questions

- Which structure levels are mandatory?
- What is the absorption score formula?
- Are absorption events too sparse for MNQ/NQ R4?
- Does requiring structure plus absorption over-filter the signal?

## 8. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-20 | untested-ideation | Wiki entry authored from footprint video synthesis. Data and absorption metric implementation required before Phase 0. |

