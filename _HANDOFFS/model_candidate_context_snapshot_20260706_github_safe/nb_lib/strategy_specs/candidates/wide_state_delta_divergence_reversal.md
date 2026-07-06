---
name: "Wide-State Delta Divergence Reversal"
tagline: "Fade wide-state extensions when price makes a new extreme without confirming delta."
status: "untested-ideation"
created: 2026-05-20
updated: 2026-05-20
source: "Operator-provided footprint/order-flow video synthesis, 2026-05-20."

markets: ["MNQ", "NQ"]
session: "RTH"
time_of_day: "09:30-12:00 ET"
hold_duration: "intraday"

signal_type: "mean-reversion"
indicators: ["SMA(20)", "SMA(200)", "ATR(14)", "delta", "delta ratio", "swing highs/lows"]
timeframes_used: ["tick/aggressor-side source", "2-minute", "5-minute"]

brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
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
  - order-flow
  - footprint
  - regime-conditional
  - data-acquisition-required
---

# Wide-State Delta Divergence Reversal

## 1. Thesis

This candidate repairs the blind spot in the wide-state opening-window
reversal family. The prior wide-state reversal test faded extension
using price structure alone and failed hard. This version requires
footprint disagreement: price reaches a new extreme, but delta fails to
confirm.

Short thesis: in a wide-upside state, a new price high with lower,
weak, or negative delta suggests exhaustion and possible reversal toward
the SMA cluster. Long thesis is the inverse.

Counter-hypothesis: delta divergence appears frequently during normal
trend pauses and is not sufficient to fade momentum.

## 2. Mechanism

- Wide SMA separation identifies expanded state.
- New price extreme identifies extension.
- Delta divergence identifies weakening aggressive participation.
- Break of the divergence candle or micro swing confirms reversal
  attempt.

## 3. Entry Logic

Short:

- SMA20 > SMA200.
- `abs(SMA20 - SMA200) / ATR14 >= 1.00`.
- Price extended above SMA20.
- Price makes a higher high versus the lookback window.
- Delta makes a lower high, or bar delta turns negative on the new price
  high.
- Entry on break below divergence bar low or micro swing low.
- Stop above divergence high.

Long:

- SMA20 < SMA200.
- `abs(SMA20 - SMA200) / ATR14 >= 1.00`.
- Price extended below SMA20.
- Price makes a lower low versus the lookback window.
- Delta makes a higher low, or bar delta turns positive on the new price
  low.
- Entry on break above divergence bar high or micro swing high.
- Stop below divergence low.

## 4. Exit Logic

Candidate targets:

- SMA20 touch.
- SMA midpoint between SMA20 and SMA200.
- VWAP.
- Fixed-R baseline.

## 5. Required Data

Requires bar-level delta from aggressor-side tick data. OHLCV cannot
test this candidate honestly.

## 6. Differentiation

This differs from `wide_opening_window_reversal_family` by requiring
order-flow divergence, not just wide-state price anatomy. The prior
family is evidence that price-only wide reversal is insufficient.

## 7. Phase 0 Questions

- Which divergence lookback is defensible before testing?
- Does divergence at wide state occur often enough for R4?
- Should levels such as prior high/low or OR high/low be required?
- Does divergence reduce the 11/12 Apex failure pattern seen in the
  price-only wide reversal family?

## 8. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-20 | untested-ideation | Wiki entry authored from footprint video synthesis. Intended as order-flow repair of failed price-only wide reversal family. |

