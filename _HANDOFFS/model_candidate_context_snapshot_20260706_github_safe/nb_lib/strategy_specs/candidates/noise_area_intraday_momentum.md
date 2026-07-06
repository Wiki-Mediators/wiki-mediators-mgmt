---
name: "Noise Area Intraday Momentum"
tagline: "Time-of-day noise-band breakout with VWAP confirmation and half-hour grid exits."
status: "tested-informational-shelved"
created: 2026-06-21
updated: 2026-06-24
source: "Operator-provided five-candidate frequency-adequate MNQ menu; Candidate A selected first because it was designed to clear both frequency and cost-distance constraints."
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:00-15:58 ET"
hold_duration: "intraday"
signal_type: "noise-area-intraday-momentum"
indicators: ["time-of-day absolute move band", "RTH VWAP"]
timeframes_used: ["1-second source", "1-minute derived", "half-hour decision grid"]
brackets: "grid-based trailing/reversal exit"
position_sizing: "fixed contracts"
canonical_spec: null
implementation: "nb_lib/scripts/noise_area_intraday_momentum.py"
source_artifact: "nb_lib/strategy_specs/source_artifacts/compass_five_frequency_adequate_mnq_candidates_20260621.md"
related_candidates:
  - "first_hour_momentum_acceptance_base_hit"
  - "ema_vwap_micro_pullback_scalp"
test_results:
  in_sample_window: ["2024-08-01", "2026-01-31"]
  in_sample_n: 302
  distinct_days: 201
  in_sample_pnl_dollars: -467.70
  in_sample_pf: 0.99
  in_sample_win_rate: 0.325
  in_sample_max_drawdown_dollars: 15015.00
  avg_trades_per_month: 16.8
  in_sample_contracts: 3
  confirmation_90d_vm15:
    n: 136
    pnl_dollars: 7646.40
    pf: 1.21
    win_rate: 0.346
    max_drawdown_dollars: 4886.10
    avg_trades_per_month: 9.7
    top_day_pnl_dollars: 8371.20
    top_day_share_of_net: 1.095
  out_of_sample_tested: false
admissibility:
  r1_edge_thesis:
    r1_verdict: "BASELINE_FLAT_CONFIRMATION_POSITIVE_BUT_SHELVED"
  r2_apex_survival:
    max_running_drawdown_dollars: 15015.00
    r2_variance_verdict: "FAILS_DEPLOYABILITY_AS_BUILT"
  r4_signal_frequency:
    probe_window_start: "2024-08-01"
    probe_window_end: "2026-01-31"
    probe_n_signals_observed: 302
    distinct_days_with_signal: 201
    sparsity_class: "borderline"
tags:
  - rth-only
  - intraday
  - momentum
  - noise-area
  - vwap
  - half-hour-grid
  - cost-distance
  - ohlcv-testable
---

# Noise Area Intraday Momentum

## 1. Thesis

The prior fresh high-frequency EMA/VWAP scalp reached large sample size
but lost money after costs. The operator then provided a frequency-
adequate, cost-aware menu of five distinct MNQ RTH strategy candidates.
Candidate A, the noise-area intraday momentum strategy, was selected
first because it was designed to address both recent failure modes:

- enough trades to avoid the severe MinTRL problem;
- large enough price distance that MNQ friction should not dominate.

The local thesis: if MNQ breaks outside a time-of-day-specific
volatility band around the RTH open, and price is also accepted on the
same side of RTH VWAP, the imbalance may persist toward the close.

## 2. Locked Signal

All measurements are in-sample only.

- Window: 2024-08-01 through 2026-01-31.
- OOS hard halt: any date >= 2026-02-01.
- Noise lookback: 14 prior RTH days.
- Volatility multiplier: 1.0.
- For each minute-of-day, compute `sigma` as the prior-14-day average
  absolute percentage move from that day's 09:30 open to the same
  minute.
- Upper band: `max(today_open, prior_RTH_close) * (1 + VM * sigma)`.
- Lower band: `min(today_open, prior_RTH_close) * (1 - VM * sigma)`.
- Decision grid: half-hour bars from 10:00 through 15:30.
- Long entry: close above upper band and above RTH VWAP.
- Short entry: close below lower band and below RTH VWAP.
- Fill: next 1-second open with Band B entry slippage.

## 3. Locked Exit

This was a baseline translation, not a parameter sweep.

- Size: 3 MNQ contracts.
- Long grid exit: half-hour close below `max(upper_band, RTH_VWAP)` or
  opposing short signal.
- Short grid exit: half-hour close above `min(lower_band, RTH_VWAP)` or
  opposing long signal.
- EOD flat: 15:58:30 ET.
- No BE, no partials, no added filters.
- Exit fills use `nb_lib.compute_realistic_pnl` with Band B commission,
  slippage treatment, and conservative tick-rounded fills.

## 4. In-Sample Result

Run date: 2026-06-21.

Artifacts:

- `nb_lib/scripts/noise_area_intraday_momentum.py`
- `nb_lib/probe_results/noise_area_intraday_momentum_trades.csv`
- `nb_lib/probe_results/noise_area_intraday_momentum_report.md`
- `nb_lib/probe_results/noise_area_intraday_momentum.json`

Summary:

| Metric | Value |
|---|---:|
| Trades | 302 |
| Distinct days | 201 |
| Total P&L | -$467.70 |
| Profit factor | 0.99 |
| Win rate | 32.5% |
| Mean P&L / trade | -$1.55 |
| Direction split | 140 long / 162 short |
| Best day | +$8,371.20 |
| Worst day | -$2,260.20 |
| Max drawdown | $15,015.00 |
| Exit mix | 203 trail_stop / 99 eod |
| Average trades/month | 16.8 |
| Warmup days skipped | 13 |

## 5. Interpretation Of 14-Day / VM 1.0 Baseline

This local baseline does **not** earn promotion. It reached 302 trades
over the in-sample window, so it is not as starved as the first-hour
candidate, but it still fell below the desired 20 trades/month frequency
floor and failed the cost-aware edge test: PF 0.99, negative expectancy,
and a very large drawdown.

The external artifact remains useful as a design reference, but the
project-native MNQ implementation did not reproduce a deployable edge
under the locked baseline. The result is also highly path-concentrated:
one best day of +$8,371.20 exists inside a negative total book, which
is not a healthy promotion profile.

Verdict: **tested-informational-rejected as implemented**. Do not spend
OOS. Do not sweep lookback / volatility multiplier to rescue the result
without explicitly logging each variant as a separate trial. If this
family is revisited, the next attempt needs a genuinely new pinned
construction, not a quiet parameter tweak.

## 6. Single External-Parameter Confirmation

Run date: 2026-06-21.

Reason for run: the operator-provided source artifact explicitly noted
that the 14-day / VM 1.0 version was the paper baseline, while external
SPY/NQ work highlighted a 90-day lookback and VM around 1.5 as stronger
settings. This was run once as an externally pre-specified confirmation,
not as a grid search.

Locked confirmation parameters:

- Noise lookback: 90 prior RTH days.
- Volatility multiplier: 1.5.
- Same half-hour decision grid.
- Same VWAP confirmation.
- Same exit logic.
- No intermediate values, no additional filters, no OOS.

Artifacts:

- `nb_lib/probe_results/noise_area_intraday_momentum_confirm_90d_vm15_trades.csv`
- `nb_lib/probe_results/noise_area_intraday_momentum_confirm_90d_vm15_report.md`
- `nb_lib/probe_results/noise_area_intraday_momentum_confirm_90d_vm15.json`

Summary:

| Metric | Value |
|---|---:|
| Trades | 136 |
| Distinct days | 93 |
| Total P&L | +$7,646.40 |
| Profit factor | 1.21 |
| Win rate | 34.6% |
| Mean P&L / trade | +$56.22 |
| Direction split | 55 long / 81 short |
| Best day | +$8,371.20 |
| Worst day | -$2,120.70 |
| Best day % of total | 109.5% |
| Max drawdown | $4,886.10 |
| Exit mix | 93 trail_stop / 43 eod |
| Average trades/month | 9.7 |
| Daily absolute-P&L HHI | 0.0335 |
| Positive-day HHI | 0.0878 |

Interpretation: the external setting did flip the edge bar from flat to
positive, but it failed the broader project bar. Frequency fell to 136
trades, only 9.7/month after the 90-day warmup. The best day
(+$8,371.20) exceeded the entire net profit, so the result is carried
by one outsized day and remains unsuitable for deployability or OOS.

Mechanism lesson: this is not merely "good edge, too few trades." The
90-day / VM 1.5 run appears to have preserved one exceptional trend day
while leaving the rest of the book approximately negative/noisy. That
is the convex breakout profile the external literature celebrates, but
the local sample does not contain enough trades for that skew to average
out. The source paper's thousands of trades can absorb a few monster
trend days; this 136-trade MNQ RTH sample cannot. Treat noise-area as a
clean example of a mechanism that may be real yet still fail this
project's deployability constraints because contribution is too sparse
and concentrated.

Verdict: **B - edge improves, but frequency and concentration fail**.
The family is shelved, not promoted. Do not run more lookback / VM
variants without treating each as a separate pre-committed trial. The
ranked-next fresh mechanism from the source artifact is Candidate C:
VWAP z-score mean-reversion fade.

## 7. OOS Discipline

No OOS rows were loaded for results. Any date >= 2026-02-01 hard-halts
in the script.

## 8. Status History

- **2026-06-24 — DISAMBIGUATION.** This candidate
  (`noise_area_intraday_momentum_90d_vm15`: 90-day %-move band, VWAP
  filter, half-hour grid, 136 trades, PF 1.21, top-day share 109.5% of
  net) IS the entry on the dead scoreboard labeled "noise-area band
  breakout — concentration-fatal (109.5% of net)." It is **NOT** the
  deployed `noise_brk` (different mechanism: ATR band around the open,
  managed). *Why banked:* the scoreboard's loose name "noise-area band
  breakout — concentration-fatal" reads as if it threatens the live
  edge. It does not — these are two different mechanisms that share a
  naming root. Recording the disambiguation here prevents future agents
  re-scaring themselves with the same collision. See
  `_worker_reports/INTEGRITY_SWEEP_FINDINGS_2026-06-24.md` §1 for the
  ground-truth measurement of the live edge's actual concentration
  (2.78% worst day, broad book).
