---
name: "EMA VWAP Micro Pullback Scalp"
tagline: "Frequency-first intraday continuation scalp using EMA20/VWAP alignment and micro-pullback reclaim."
status: "tested-informational-rejected"
created: 2026-06-21
updated: 2026-06-21
source: "Generated after First Hour Momentum Acceptance Base Hit proved severely underpowered; purpose was to test whether a fresh MNQ/RTH candidate could reach enough trade frequency for realistic inference."
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:00-15:00 ET"
hold_duration: "intraday"
signal_type: "micro-continuation-scalp"
indicators: ["EMA(20) 1-minute", "RTH VWAP", "ATR(14) 1-minute"]
timeframes_used: ["1-second source", "1-minute derived"]
brackets: "ATR-scaled static bracket"
position_sizing: "fixed contracts"
canonical_spec: null
implementation: "nb_lib/scripts/ema_vwap_micro_pullback_scalp.py"
related_candidates:
  - "first_hour_momentum_acceptance_base_hit"
test_results:
  in_sample_window: ["2024-08-01", "2026-01-31"]
  in_sample_n: 1140
  distinct_days: 380
  in_sample_pnl_dollars: -8643.00
  in_sample_pf: 0.86
  in_sample_win_rate: 0.430
  in_sample_max_drawdown_dollars: 11266.20
  avg_trades_per_month: 63.3
  in_sample_contracts: 3
  out_of_sample_tested: false
admissibility:
  r1_edge_thesis:
    r1_verdict: "FAILED_DIRECT_BACKTEST"
  r2_apex_survival:
    max_running_drawdown_dollars: 11266.20
    r2_variance_verdict: "FAILS_DEPLOYABILITY_AS_BUILT"
  r4_signal_frequency:
    probe_window_start: "2024-08-01"
    probe_window_end: "2026-01-31"
    probe_n_signals_observed: 1140
    distinct_days_with_signal: 380
    sparsity_class: "high-frequency"
tags:
  - rth-only
  - intraday
  - momentum
  - micro-pullback
  - ema
  - vwap
  - atr-bracket
  - frequency-first
  - ohlcv-testable
---

# EMA VWAP Micro Pullback Scalp

## 1. Thesis

The First Hour Momentum Acceptance candidate produced an interesting
shape but only 150 trades across 18 months. That left the result
severely underpowered: the conservative ex-January MinTRL estimate was
about 954 trades.

This candidate was built as a fresh frequency-first test. It keeps the
research inside the MNQ/RTH/1-second data stack but moves away from the
one-trade-per-day opening setup. The thesis was simple continuation:
when 1-minute price is aligned with both EMA20 and RTH VWAP, a shallow
pullback into EMA20 followed by a reclaim may provide enough small
continuation attempts to clear the sample-size problem.

## 2. Locked Signal

All measurements are in-sample only.

- Window: 2024-08-01 through 2026-01-31.
- OOS hard halt: any date >= 2026-02-01.
- Scan: 10:00:00 through 15:00:00 ET.
- Trend filter: close is on the correct side of EMA20 and RTH VWAP,
  with EMA20 slope aligned.
- Pullback: prior completed 1-minute bar touches or approaches EMA20
  within a small tolerance.
- Reclaim trigger: current completed 1-minute bar reclaims in the
  continuation direction.
- Max trades per day: 3.
- Cooldown: 5 minutes between entries.

## 3. Locked Exit

This was not a management experiment.

- Size: 3 MNQ contracts.
- Stop: 0.75 x 1-minute ATR14, clamped between 8 and 30 points.
- Target: 1.25R.
- Time exit: 20 minutes.
- No BE, no trail, no partials.
- Exit fills use `nb_lib.compute_realistic_pnl` with realistic
  stop/target handling, commission, and conservative tick-rounded
  fills.

## 4. In-Sample Result

Run date: 2026-06-21.

Artifacts:

- `nb_lib/scripts/ema_vwap_micro_pullback_scalp.py`
- `nb_lib/probe_results/ema_vwap_micro_pullback_scalp_trades.csv`
- `nb_lib/probe_results/ema_vwap_micro_pullback_scalp_report.md`
- `nb_lib/probe_results/ema_vwap_micro_pullback_scalp.json`

Summary:

| Metric | Value |
|---|---:|
| Trades | 1,140 |
| Distinct days | 380 |
| Total P&L | -$8,643.00 |
| Profit factor | 0.86 |
| Win rate | 43.0% |
| Mean P&L / trade | -$7.58 |
| Direction split | 629 long / 511 short |
| Best day | +$668.70 |
| Worst day | -$568.80 |
| Max drawdown | $11,266.20 |
| Exit mix | 645 full_stop / 487 tp / 8 time_exit |
| Average trades/month | 63.3 |

## 5. Interpretation

This candidate solved the frequency problem and failed the edge
problem. It produced 1,140 trades across 380 in-sample days, averaging
63.3 trades per month, so sample size was not the limiting factor.

The result is therefore a useful negative control: simply increasing
trade count through common EMA/VWAP micro-continuation logic does not
create an edge. The as-built shape loses money after realistic fills
and commissions, with PF 0.86 and a drawdown larger than the absolute
loss.

Verdict: **tested-informational-rejected**. Do not spend OOS. Do not
rescue-tune this exact construction. Any future use of EMA/VWAP
micro-pullback logic needs a new thesis about why it should select
better trades, not merely a higher-frequency variant of this failed
form.

## 6. OOS Discipline

No OOS rows were loaded for results. Any date >= 2026-02-01 hard-halts
in the script.
