---
name: "ATR Regime Pullback Continuation"
tagline: "Only trade pullbacks when volatility regime supports continuation."
status: "tested-rejected"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: generic trend-pullback framework with volatility-regime filtering."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-14:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "trend-continuation"
indicators: ["EMA(20)", "EMA(50)", "VWAP", "ATR(20)", "ATRPercentile"]
timeframes_used: ["1-minute", "5-minute", "30-minute"]

# Execution
brackets: "atr-scaled"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: "../canonical/atr_regime_pullback_continuation.md"
implementation: "../../scripts/atr_regime_pullback_continuation_canonical_alpha.py"
related_candidates: []

# Test status (only populated when status >= tested-*)
test_results:
  in_sample_n: 15
  in_sample_pnl_dollars: -1656.30
  in_sample_pf: 0.30
  in_sample_win_rate: 0.40
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
  - multi-timeframe
  - atr-scaled
  - fixed-risk-dollar
---

# ATR Regime Pullback Continuation

## 1. Thesis

The failed PRJ_3-style idea may have mixed all volatility regimes.
Pullback continuation can work when volatility is expanding and
directional structure is clean, but fail in low-quality chop.

This candidate keeps the broad continuation idea but makes volatility
regime and multi-timeframe trend agreement mandatory before any entry.

## 2. Mechanism (what edge it captures)

- Uses 30-minute trend qualification before looking for entries.
- Requires 5-minute pullback to a dynamic reference such as EMA20 or
  VWAP.
- Uses 1-minute reversal for entry timing.
- Trades only when ATR is elevated but not extreme.

## 3. Signal logic (entry conditions)

For longs, the 30-minute trend requires price above EMA50 and agreement
with VWAP. Price must pull back on 5-minute bars to EMA20 or VWAP, then
print a 1-minute reversal candle in the direction of the 30-minute
trend. Shorts are symmetric.

Only trade when 5-minute ATR is above its 20-day median but below a
pre-committed extreme percentile.

## 4. Exit logic (stops, targets, time-based exits)

Stop is 1.25 x ATR(20) on 5-minute bars beyond the pullback low or high.
TP1 is 0.75 x ATR. TP2 is 2.5 x ATR. BE arm is 0.5 x ATR. EOD flat
applies.

## 5. Position sizing

Use fixed dollar risk: risk dollars divided by stop dollars, capped by
the Apex contract limit. This is explicitly not fixed 15-contract
sizing.

## 6. Required indicators / data

MNQ 1-minute, 5-minute, and 30-minute bars; EMA20, EMA50, VWAP, ATR(20),
and ATR percentile or median history. Current nb_lib indicators appear
to cover these needs.

## 7. Differentiation (vs already-tested strategies)

PRJ_3 was a morning fractal pullback with fixed brackets and no
volatility-regime gate. This candidate is still continuation, but it
requires multi-timeframe alignment, ATR percentile qualification, and
ATR-scaled exits with fixed-risk sizing.

## 8. Required research before spec drafting

- Pre-commit the ATR percentile bounds without OOS tuning.
- Define reversal candle mechanically and check for lookahead.
- Decide whether EMA20 or VWAP pullback gets priority when both occur.
- Verify signal count after multi-timeframe filters.
- Check whether fixed-risk sizing materially reduces Apex floor failure.

## 9. Source / references

Generic trend-pullback framework common in futures systems. This entry
does not claim a unique literature-backed edge.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | untested-ideation | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch. |
| 2026-05-12 | spec-drafted | FINAL spec drafted with 5-tier × 2-vol-mult conviction sizing + Mechanic 1 + Mechanic 2. Locked parameters in spec; ready for implementation iteration. See `../canonical/atr_regime_pullback_continuation.md`. |
| 2026-05-12 | implementation-in-progress | Strategy script implemented per FINAL spec; 11 new tests added (tier classifier, vol multiplier, cushions, contracts, brackets, watch-window skip, pullback episode, OOS guard, risk-dollar sizing); test count grew to 309. In-sample test pending. Script: `../../scripts/atr_regime_pullback_continuation_canonical_alpha.py`. |
| 2026-05-12 | implementation-in-progress | In-sample test attempt HALTED by `Section 12.4` runtime order-assertion: `PullbackEpisode.update` stores `trend_ts` (right-edge) and `start_5m_ts` (left-edge) at inconsistent conventions, failing the `trend_ts <= start_5m_ts` check on first signal-eligible session (2024-08-02). Two minor preconditional fixes applied (Unicode `→`-in-print and dead-code line in `_rolling_session_vwap`; both subtractive, no strategy-logic impact, tests still 309/309). Zero trades produced. Next iteration: fix timestamp convention (Option A: `start_5m_ts = bar.name + 5min`) and re-run. See `nb_lib_atr_regime_insample_results_report.md` Section F. |
| 2026-05-12 | tested-rejected | Option A timestamp fix applied (1 line); 1 regression test added (test count 309 → 310); in-sample re-run COMPLETED across all 469 sessions. **Result: n=15 trades, $-1,656.30, PF 0.30, 40% win rate**. Account FAILED via `compliance_drawdown` breach mid-run; 374 of 469 sessions skipped post-FAILED by outer-loop guard. All Section 12 runtime assertions passed. Eval phase never reached $53K (peak $50,352); Mechanic 2 never activated. Downstream `fill_assumption_used` enum needs extension in `nb_lib/trade_record.py` (next iteration); trade CSV not written this run but runtime summary preserved in log + report. Matches spec Section 0.3 "60% no-edge" prior. Five nb_lib-native canonical alphas now share Apex-eval-failure pattern at $-1.6K to $-2K. See `nb_lib_atr_regime_insample_rerun_report.md`. |
| 2026-05-12 | tested-rejected | 12-start multistart characterization run via wrapper script (strategy script untouched). Enum fix to `FILL_ASSUMPTIONS` applied (1 line; 310/310 preserved). 12 fresh-start accounts: 2024-08-01, 2024-09-03, ..., 2025-07-01, each running to 2026-01-31. **Result: 0 of 12 accounts passed. Mean P&L $-1,720.69, median $-1,723.50, stdev $313.56. Range: $-2,016 to $-1,104. 11 accounts FAILED via drawdown breach; 1 ended ACTIVE only because window cut off before breach.** Tight clustering confirms single-run result is representative — not start-date-sensitive. Per CRITICAL FRAMING outcome category: 0-2 pass = uniform no-edge confirmed. PRJ_3 fresh-start-artifact lesson honored (no cherry-picking). Status confirmed `tested-rejected`. See `nb_lib_atr_regime_multistart_report.md` and 12 per-account CSVs at `multistart_atr_regime/`. |
