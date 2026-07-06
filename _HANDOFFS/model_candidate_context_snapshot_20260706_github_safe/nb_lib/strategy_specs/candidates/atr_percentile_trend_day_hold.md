---
name: "ATR Percentile Trend Day Hold"
tagline: "Trade only when the day has enough volatility to sustain continuation."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: standard volatility-regime trend-following filter using ATR percentile."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:15-14:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "trend-continuation"
indicators: ["ATR(20)", "ATRPercentile(60 sessions)", "ChoppinessIndex(14)", "EMA(8)"]
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
  - trend-continuation
  - regime-conditional
  - atr-scaled
---

# ATR Percentile Trend Day Hold

## 1. Thesis

Some intraday continuation ideas fail because they trade calm sessions
that do not have enough range to pay for friction. This candidate only
activates when current 5-minute ATR is high relative to the last 60 RTH
sessions and the ChoppinessIndex says the session is directional rather
than rotational.

The adaptive element is deliberately narrow: volatility regime decides
whether the strategy is allowed to trade, and ATR sets the bracket size.
It does not adapt entry, stop, target, and sizing separately.

## 2. Mechanism (what edge it captures)

- Trades continuation only in regimes where movement capacity is present.
- Uses ChoppinessIndex to avoid high-volatility chop that can look
  attractive but rotate both ways.
- Uses ATR-scaled exits so the same trade idea is not over-stopped in
  fast markets or under-rewarded in quiet markets.
- Waits until after 10:15 ET so the opening auction has generated a
  measurable volatility regime.

## 3. Signal logic (entry conditions)

**Adaptive elements:**
- Regime gate: 5-minute ATR(20) percentile over the last 60 RTH sessions
  must be >= 0.70.
- Directional gate: ChoppinessIndex(14) on 5-minute bars must be < 38.

**Fixed elements:**
- Time window: 10:15-14:30 ET.
- Long entry: price above EMA(8) on 5-minute bars, then a 1-minute
  pullback closes back above EMA(8).
- Short entry: symmetric below EMA(8).

The ATR percentile gate is meant to answer "is there enough range to
hold a continuation trade?" before any entry is considered.

## 4. Exit logic (stops, targets, time-based exits)

**Adaptive elements:**
- Stop: 1.2 x ATR(20) on 5-minute bars from entry.
- TP1: 1.2 x ATR from entry.
- TP2: 2.4 x ATR from entry.

**Fixed elements:**
- BE arm at +1.0R after TP1 is reached.
- EOD flat by 15:58:30 ET.

ATR scaling is justified because a fixed 30-point stop can be too tight
on high-volatility trend days and too loose on low-volatility days.

## 5. Position sizing

Use fixed dollar risk per trade, for example $400, divided by stop
dollars: contracts = risk_dollars / (stop_points x $2), capped by the
Apex MNQ contract limit.

## 6. Required indicators / data

ATR(20) on 5-minute bars, ATRPercentile over 60 prior RTH sessions,
ChoppinessIndex(14) on 5-minute bars, EMA(8) on 5-minute bars, and
1-minute bars for entry timing. Current MNQ data should support these
inputs.

## 7. Differentiation (vs already-tested strategies)

Unlike noise_brk and ema_trend, this is not a fixed-time morning entry.
Unlike PRJ_3, it does not use fractal levels or a touch-plus-confirmation
pattern. Unlike batch-1 ATR Regime Pullback Continuation, this candidate
does not require multi-timeframe EMA/VWAP alignment; it isolates a
single question: do high ATR percentile and low choppiness improve
simple continuation holds?

The adaptive elements are principled because they answer movement
capacity and bracket scale, not because they were tuned to a backtest.

## 8. Required research before spec drafting

- Pre-commit ATR percentile threshold and Choppiness threshold before
  testing.
- Decide whether the 60-session percentile lookback is long enough.
- Verify enough trades remain after the regime gate.
- Check whether the strategy is just selecting a few trend months and
  therefore vulnerable to regime non-persistence.

## 9. Source / references

Standard ATR-based trend-following and volatility-regime filtering.
ChoppinessIndex is commonly used to distinguish trend from rotation.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch 2 (dynamic adaptive intraday focus). |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.4 R1-first triage applied (first continuation-class application).** R1 evidence diagnostic measured EMA-pullback continuation rate on regime-gated days. **Compound regime gate restrictiveness is the binding constraint**: ATR percentile ≥ 0.70 passes 37/158 days (23%); Choppiness < 38 passes 17/158 days (11%); **BOTH gates pass only 4/158 days (2.5%)**. Joint gate eliminates 97.5% of days. Over the 4 eligible days, 8 signals fired; **3 continued 1R within 30min (37.5%)**, 3 hit stop first, 2 neither. **R1 verdict: NOT MET** at 37.5% with low-confidence n=8 (statistical CI 95% [11%, 71%]). **Different failure mode from prior closures**: not "mechanism doesn't work" but "regime gates too restrictive to test mechanism." The wiki Section 8 anticipated this ("Verify enough trades remain after the regime gate") but compound gate correlation was not analyzed pre-authoring. **Candidate CLOSED at R1 gate** — no R4 probe, no FINAL spec, no implementation. Fifth consecutive R1-gate closure; v1.4 R1-first triage extends to continuation class. **Methodology learnings**: (1) compound regime gates need correlation analysis before deployment; (2) R1 low-confidence flag needed for n<15 (v1.5 candidate); (3) candidate funnel is exhausting at R1 gate — 6 measurements, 1 pass. Diagnostic: `nb_lib/probe_results/atr_percentile_trend_day_hold_r1_diagnostic.json`. Closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_4_atr_percentile_trend_day_hold_closure.md`. |
