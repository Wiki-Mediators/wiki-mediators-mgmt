---
name: "True Zone Liquidity Sweep Reference"
tagline: "Reference note for zone quality, stop sweeps, reclaim, and volume-confirmed reversal logic."
status: "research-reference"
created: 2026-05-21
updated: 2026-05-21
source: "Operator-provided transcript synthesis, 2026-05-21."

markets: ["MNQ", "NQ"]
session: "RTH"
time_of_day: "varies"
hold_duration: "intraday"

signal_type: "liquidity-sweep-reversal"
indicators: ["support/resistance zones", "previous day high/low", "opening range", "volume MA", "volume profile optional"]
timeframes_used: ["1-minute", "2-minute", "5-minute"]

brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
  - "pdh_pdl_liquidity_sweep_reversal"
  - "footprint_confirmed_supply_demand_reaction"
  - "wide_state_absorption_reversal"

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
  - research-reference
  - intraday
  - liquidity-sweep
  - support-resistance
  - volume-confirmation
---

# True Zone Liquidity Sweep Reference

## 1. Purpose

This note preserves the operator's transcript synthesis for a liquidity-sweep support/resistance framework. This is not a normal "buy support / sell resistance" idea. The core rule is:

**Do not trade the obvious level immediately. Wait for price to sweep the stops around that level, reclaim/reject, and confirm the reversal with volume.**

The transcript's system has three filters:

1. Zone quality.
2. Liquidity awareness.
3. Volume confirmation.

It tries to avoid being the trader who buys obvious support, places a stop just below it, gets swept, and watches price reverse without them.

## 2. Core Mechanism

Obvious levels attract clustered stops:

- Stops below obvious support.
- Stops above obvious resistance.
- Stops around previous day high/low.
- Stops around round numbers.
- Stops around visually obvious swing highs/lows.

The strategy waits for the sweep of that liquidity first. For a long, price trades below support or a demand level, triggers stops, then reclaims upward. For a short, price trades above resistance or supply, triggers stops, then rejects downward.

Volume is the confirmation layer. The transcript's clean line is:

> A bounce without volume is a suggestion. A bounce with volume is a statement.

## 3. Filter 1 - Zone Quality

Do not draw every swing high/low. A strong zone should be:

- A sharp reversal area.
- Touched multiple times.
- Visually obvious.
- Recent.

Potential parameter families:

```yaml
zone_quality:
  min_touches: [2, 3, 4]
  max_age_bars: [50, 100, 200, 500]
  min_rejection_atr: [0.5, 1.0, 1.5, 2.0]
  max_chop_inside_zone_bars: [3, 5, 8]
```

For systematic MNQ/NQ testing, start with objective zones before subjective swing-zone construction:

- Previous day high.
- Previous day low.
- Opening range high.
- Opening range low.
- Round numbers.
- VWAP or VWAP bands.

## 4. Filter 2 - Liquidity Sweep

Long:

- Identify support/demand.
- Price trades below the level by a minimum sweep distance.
- Price reclaims back above the level.
- Stop goes below the sweep wick.

Short:

- Identify resistance/supply.
- Price trades above the level by a minimum sweep distance.
- Price rejects back below the level.
- Stop goes above the sweep wick.

Potential parameter family:

```yaml
liquidity_filter:
  min_sweep_ticks: [1, 2, 4, 8]
  max_sweep_ticks: [8, 12, 20]
  reclaim_required: true
```

## 5. Filter 3 - Volume Confirmation

The reclaim/rejection candle should show volume expansion:

```yaml
volume_confirmation:
  volume_ma_len: [20, 50, 100]
  volume_spike_mult: [1.25, 1.5, 2.0, 2.5]
  require_reversal_candle: true
```

OHLCV is enough to test this basic volume version. Footprint data can later upgrade the confirmation layer with delta flip, absorption, or stacked imbalance at the swept extreme.

## 6. Strategy Families In The Transcript

The transcript decomposes into four testable families:

1. Liquidity sweep reversal long/short.
2. Support/resistance flip retest.
3. Volume-confirmed breakout.
4. Volume-profile confluence bounce.

The main first candidate is the liquidity sweep reversal.

## 7. Best First Backtest

The clean OHLCV-first version is:

```yaml
strategy_id: PDH_PDL_LIQUIDITY_SWEEP_REVERSAL
instrument: MNQ
bar_size: 1min
levels:
  - previous_day_high
  - previous_day_low
long_setup:
  - price sweeps below PDL by at least 2 ticks
  - price closes back above PDL
  - reversal candle volume >= 1.5 * volume_MA20
  - entry on break of reversal candle high
  - stop below sweep low minus 1 tick
short_setup:
  - price sweeps above PDH by at least 2 ticks
  - price closes back below PDH
  - reversal candle volume >= 1.5 * volume_MA20
  - entry on break of reversal candle low
  - stop above sweep high plus 1 tick
risk:
  max_trades_per_day: 2
  one_trade_per_level: true
```

Why this first:

- Previous day high/low are objective.
- Sweeps are easy to detect.
- Volume spike is computable from OHLCV.
- Stops and targets are mechanical.
- No subjective zone drawing is required.

## 8. Connection To Other Candidates

This is more immediately testable than the footprint candidates because it does not require bid/ask volume at price. It can later be upgraded with footprint confirmation:

- Delta flip.
- Absorption at sweep extreme.
- Stacked imbalance at reclaim.

It also connects to wide-state reversal: wide upside plus PDH sweep plus volume rejection is a cleaner short thesis than fading every wide-upside bar.

## 9. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-21 | research-reference | Transcript synthesis captured. Main buildable first candidate split into `pdh_pdl_liquidity_sweep_reversal`. |
