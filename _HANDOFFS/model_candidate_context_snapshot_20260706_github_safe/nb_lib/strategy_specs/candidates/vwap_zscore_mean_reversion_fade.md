---
name: "VWAP Z-Score Mean Reversion Fade"
tagline: "Fade 2-sigma session VWAP stretches on non-trend RTH days, targeting a snapback to VWAP."
status: "tested-informational-rejected"
created: 2026-06-21
updated: 2026-06-21
source: "Operator-provided five-candidate frequency-adequate MNQ menu; Candidate C selected after momentum/breakout candidates failed on sparse contribution and concentration."
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-15:30 ET"
hold_duration: "intraday"
signal_type: "vwap-mean-reversion"
indicators: ["RTH VWAP", "session VWAP distance z-score", "ADX(14)"]
timeframes_used: ["1-second source", "1-minute derived"]
brackets: "static signal-VWAP target and static 3-sigma adverse stop"
position_sizing: "fixed contracts"
canonical_spec: null
implementation: "nb_lib/scripts/vwap_zscore_mean_reversion_fade.py"
source_artifact: "nb_lib/strategy_specs/source_artifacts/compass_five_frequency_adequate_mnq_candidates_20260621.md"
related_candidates:
  - "noise_area_intraday_momentum"
  - "ema_vwap_micro_pullback_scalp"
  - "vwap_stretch_snapback"
test_results:
  in_sample_window: ["2024-08-01", "2026-01-31"]
  in_sample_n: 950
  distinct_days: 357
  in_sample_pnl_dollars: -16722.00
  in_sample_pf: 0.81
  in_sample_win_rate: 0.239
  in_sample_max_drawdown_dollars: 18606.90
  avg_trades_per_month: 52.8
  in_sample_contracts: 3
  out_of_sample_tested: false
admissibility:
  r1_edge_thesis:
    r1_verdict: "FAILED_DIRECT_BACKTEST"
  r2_apex_survival:
    max_running_drawdown_dollars: 18606.90
    r2_variance_verdict: "FAILS_DEPLOYABILITY_AS_BUILT"
  r4_signal_frequency:
    probe_window_start: "2024-08-01"
    probe_window_end: "2026-01-31"
    probe_n_signals_observed: 950
    distinct_days_with_signal: 357
    sparsity_class: "high-frequency"
tags:
  - rth-only
  - intraday
  - mean-reversion
  - vwap
  - z-score
  - adx-filter
  - high-frequency
  - ohlcv-testable
---

# VWAP Z-Score Mean Reversion Fade

## 1. Thesis

The first-hour and noise-area momentum candidates both failed for
sparse, high-concentration reasons. This candidate deliberately tests
the opposite risk profile: frequent VWAP mean-reversion fades with many
small-to-medium trades rather than a few convex trend-day winners.

The local thesis: on non-trend RTH days, when MNQ stretches at least two
session-standard-deviations away from RTH VWAP, price should snap back
toward VWAP often enough to overcome costs.

## 2. Locked Signal

All measurements are in-sample only.

- Window: 2024-08-01 through 2026-01-31.
- OOS hard halt: any date >= 2026-02-01.
- Scan: 09:45 through 15:30 ET.
- RTH VWAP: cumulative session VWAP from 09:30.
- Deviation: expanding session standard deviation of `close - VWAP`.
- Z-score: `(close - VWAP) / session_deviation`.
- Long entry: `z <= -2.0`.
- Short entry: `z >= +2.0`.
- Trend-day filter: ADX(14) must be below 25.
- Minimum deviation: 4 points.
- Max trades per day: 3.
- Cooldown: 5 minutes after exit.

## 3. Locked Exit

This was the single pinned v0 construction.

- Size: 3 MNQ contracts.
- Target: signal-bar RTH VWAP.
- Stop: signal-bar adverse 3-sigma band.
- EOD flat: 15:58:30 ET.
- No BE, no trail, no partials.
- Exit fills use `nb_lib.compute_realistic_pnl` with Band B commission,
  slippage treatment, and conservative tick-rounded fills.

## 4. In-Sample Result

Run date: 2026-06-21.

Artifacts:

- `nb_lib/scripts/vwap_zscore_mean_reversion_fade.py`
- `nb_lib/probe_results/vwap_zscore_mean_reversion_fade_trades.csv`
- `nb_lib/probe_results/vwap_zscore_mean_reversion_fade_report.md`
- `nb_lib/probe_results/vwap_zscore_mean_reversion_fade.json`

Summary:

| Metric | Value |
|---|---:|
| Trades | 950 |
| Distinct days | 357 |
| Total P&L | -$16,722.00 |
| Profit factor | 0.81 |
| Win rate | 23.9% |
| Mean P&L / trade | -$17.60 |
| Direction split | 403 long / 547 short |
| Best day | +$1,633.80 |
| Worst day | -$1,671.30 |
| Max drawdown | $18,606.90 |
| Exit mix | 205 tp / 717 full_stop / 28 eod |
| Average trades/month | 52.8 |
| Daily absolute-P&L HHI | 0.0049 |
| Positive-day HHI | 0.0124 |

## 5. Interpretation

This candidate solved the frequency and concentration problems, but
failed the edge problem decisively.

The 950-trade sample is large enough for the result to be meaningful,
and the daily contribution profile is much healthier than the momentum
books: the result is not dominated by one day or one month. That is the
good news. The bad news is that the selection logic is wrong under this
construction: only 23.9% of trades hit the VWAP target, 717 of 950
trades hit the full stop, and PF is only 0.81 after realistic costs.

Verdict: **tested-informational-rejected**. Do not spend OOS. Do not
tune z-threshold or ADX threshold to rescue this sample. If VWAP
mean-reversion is revisited, the next hypothesis must explain why this
basic "2-sigma stretch on non-trend days" framing still catches too many
continuation/trend moves despite the ADX filter.

## 6. Mechanism-Class Screen

Screen run date: 2026-06-22.

Artifacts:

- `nb_lib/scripts/candidate_c_vwap_mean_reversion_screen.py`
- `nb_lib/probe_results/candidate_c_vwap_mean_reversion_screen_report.md`
- `nb_lib/probe_results/candidate_c_vwap_mean_reversion_screen.json`

The screen was applied to the existing `vwap_zscore_mean_reversion_fade`
trade list. No new strategy run was performed.

Formal screen decision: **DO_NOT_BUILD**.

| Axis | Flag | Read |
|---|---|---|
| skew_concentration | RED | Observed Sharpe is negative; MinTRL is infinite because the book does not clear the zero benchmark. |
| cost_distance | GREEN | Cost distance is not the problem (`phi=0.044` on the 3-contract construction). |
| frequency_power | RED | Frequency is high, but the t-stat is negative (`t=-2.294`) because expectancy is negative. |
| regime_concentration | GREEN | No one-day or one-month contribution problem; unlike the momentum books, this failure is not concentration-driven. |
| cross_correlation | RED | High overlap/correlation with existing sleeves, especially the EMA/VWAP micro-pullback scalp (`Jaccard=0.939`). |

Screen interpretation: Candidate C has the desired high-frequency,
low-concentration shape, but the pinned `z=2 / ADX<25` VWAP fade has no
edge. The trend filter is present, but losses still concentrate through
full stops: 717 full-stop exits produced about `-$90,034`, overwhelming
the VWAP-target wins and EOD exits. This remains
tested-informational-rejected; do not tune the z-threshold or ADX limit
to rescue the sample.

## 7. OOS Discipline

No OOS rows were loaded for results. Any date >= 2026-02-01 hard-halts
in the script.
