---
name: "ATR Ratio Expansion Scalp"
tagline: "Trade short bursts only when short-term volatility expands faster than baseline volatility."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: volatility expansion breakout logic using short/long ATR ratio."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:00-15:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "momentum"
indicators: ["ATRRatio(5,30)", "DonchianWidth(20)", "RealizedRange(5)"]
timeframes_used: ["1-minute", "5-minute"]

# Execution
brackets: "atr-scaled"
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
  - volatility-adaptive
  - fixed-risk-dollar
---

# ATR Ratio Expansion Scalp

## 1. Thesis

Intraday momentum can be cleaner immediately after short-term volatility
expands faster than the prevailing baseline. This candidate uses
ATRRatio(5,30) as the adaptive trigger and keeps the rest of the design
simple.

The strategy is not an opening breakout. It can fire later in the day
when a fresh volatility expansion appears after quiet or balanced
conditions.

## 2. Mechanism (what edge it captures)

- Detects volatility regime shift with short ATR rising faster than long
  ATR.
- Requires Donchian width to expand so the volatility burst is not just
  two-sided noise.
- Enters only after directional 1-minute closes confirm the burst.
- Uses short holding time to avoid turning a scalp into a trend-day bet.

## 3. Signal logic (entry conditions)

**Adaptive elements:**
- Regime trigger: ATRRatio(5,30) on 1-minute bars must be >= 1.35.
- Expansion confirmation: DonchianWidth(20) must be greater than its
  value 10 bars earlier.

**Fixed elements:**
- Long entry: three consecutive 1-minute closes higher after the regime
  trigger.
- Short entry: three consecutive 1-minute closes lower.
- Time window: 10:00-15:00 ET.

The ATRRatio threshold asks whether current realized movement is
meaningfully different from the recent baseline, rather than assuming
all times of day deserve the same brackets.

## 4. Exit logic (stops, targets, time-based exits)

**Adaptive elements:**
- Stop: 0.8 x ATR(5) on 1-minute bars.
- TP: 1.4 x ATR(5) on 1-minute bars.

**Fixed elements:**
- No runner in v1.
- Time exit after 12 minutes.
- EOD flat still applies.

## 5. Position sizing

Use fixed dollar risk, for example $300-$400, divided by stop dollars.
The lower risk suggestion reflects the higher turnover and the danger of
false volatility bursts.

## 6. Required indicators / data

ATRRatio(5,30), DonchianWidth(20), RealizedRange(5), and 1-minute bars.
Current nb_lib indicators and MNQ data appear sufficient.

## 7. Differentiation (vs already-tested strategies)

The tested breakout systems used early fixed-time signals. This
candidate uses a volatility-ratio trigger that can happen at any time in
the intraday window and uses short adaptive exits. It also differs from
batch-1 Lunch Compression Break because it does not require a midday box
or volume confirmation; the adaptive source is volatility expansion
itself.

There is no PRJ_3-like fractal level or proximity entry here.

## 8. Required research before spec drafting

- Pre-commit ATRRatio threshold and Donchian lookback.
- Decide whether three consecutive closes is too slow for a scalp.
- Check turnover and transaction-cost sensitivity.
- Confirm the strategy does not simply fire after news shocks where
  slippage dominates.

## 9. Source / references

Common volatility expansion and short-term momentum framework. No
specific paper or proprietary source is claimed.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch 2 (dynamic adaptive intraday focus). |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.5 R1-first triage sweep applied.** R1 diagnostic measured 3-consec-up-close scalp continuation in ATR-Ratio(5,30)>=1.35 + Donchian-expansion regime. **83 qualifying events (26L/57S — 31% long); 39 continued 1R within 30min (47.0%)**, 44 hit stop first, 0 neither. **R1 verdict: NOT MET** at 47% (slightly below null). Direction asymmetry (31% L) exceeds 65% pre-committed bound but moot given R1 fail. The 3-consec-up/down-close pattern in an ATR-expansion regime doesn't produce edge above coin-flip in this sample. Median 1.2 min cont — very fast resolution consistent with scalp class. Candidate CLOSED at R1 gate. Diagnostic: `nb_lib/probe_results/atr_ratio_expansion_scalp_r1_diagnostic.json`. Combined sweep closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_5_sweep_closures.md`. |
