---
name: "Ten Fifteen Opening Drive State Router"
tagline: "At 10:15 ET, route the first-30-minute opening drive as accepted continuation or VWAP rejection reversal."
status: "tested-informational-rejected"
created: 2026-06-21
updated: 2026-06-21
source: "Operator asked for a strategy that tends to fire around 45 minutes after market open, observing the 10:00 turnaround / post-open state."
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:15 ET"
hold_duration: "intraday"
signal_type: "opening-drive-state-router"
indicators: ["first-30-minute move", "first-30-minute range", "RTH VWAP"]
timeframes_used: ["1-second source"]
brackets: "fixed 30/60 base-hit"
position_sizing: "fixed contracts"
canonical_spec: null
implementation: "nb_lib/scripts/ten_fifteen_opening_drive_vwap_reversal.py"
related_candidates:
  - "first_hour_momentum_acceptance_base_hit"
  - "noise_area_intraday_momentum"
test_results:
  in_sample_window: ["2024-08-01", "2026-01-31"]
  in_sample_n: 152
  distinct_days: 152
  in_sample_pnl_dollars: -1288.20
  in_sample_pf: 0.93
  in_sample_win_rate: 0.336
  in_sample_max_drawdown_dollars: 3812.70
  avg_trades_per_month: 8.4
  in_sample_contracts: 3
  out_of_sample_tested: false
admissibility:
  r1_edge_thesis:
    r1_verdict: "FAILED_DIRECT_BACKTEST"
  r2_apex_survival:
    max_running_drawdown_dollars: 3812.70
    r2_variance_verdict: "FAILS_DEPLOYABILITY_AS_BUILT"
  r4_signal_frequency:
    probe_window_start: "2024-08-01"
    probe_window_end: "2026-01-31"
    probe_n_signals_observed: 152
    distinct_days_with_signal: 152
    sparsity_class: "low-frequency"
tags:
  - rth-only
  - intraday
  - opening-drive
  - ten-fifteen
  - vwap
  - state-router
  - ohlcv-testable
---

# Ten Fifteen Opening Drive State Router

## 1. Thesis

The operator asked whether a strategy could fire around 45 minutes after
the 09:30 RTH open, using the common 10:00-10:15 turn window. The local
thesis was to avoid trading the open itself and instead classify the
state at 10:15:

- If the first-30-minute drive remains accepted beyond the opening
  range and on the same side of VWAP, trade continuation.
- If the first-30-minute drive rejects through VWAP by 10:15, trade the
  reversal.

## 2. Precursor Attempts

Two stricter VWAP-reversal versions were tried first and preserved as
zero-trade artifacts:

- `nb_lib/probe_results/ten_fifteen_opening_drive_vwap_reversal_v0_zero_report.md`
- `nb_lib/probe_results/ten_fifteen_opening_drive_vwap_reversal_v1_zero_report.md`

Those versions required a drive failure back toward VWAP with structural
reward/risk to the 10:15 VWAP target. They produced zero trades, which
showed that the strict "opening drive fails and reaches a tradable VWAP
reversion setup by 10:15" condition is essentially absent under the
pinned rules.

## 3. Locked Signal

All measurements are in-sample only.

- Window: 2024-08-01 through 2026-01-31.
- OOS hard halt: any date >= 2026-02-01.
- Opening drive: 09:30 through 10:00.
- Minimum first-drive size: 30 points.
- Decision time: 10:15 ET.
- Bull drive continuation: first drive >= +30, 10:15 close above the
  first-30-minute high, and 10:15 close above RTH VWAP.
- Bear drive continuation: first drive <= -30, 10:15 close below the
  first-30-minute low, and 10:15 close below RTH VWAP.
- Bull drive rejection: first drive >= +30 and 10:15 close below RTH
  VWAP; trade short.
- Bear drive rejection: first drive <= -30 and 10:15 close above RTH
  VWAP; trade long.
- Entry: next 1-second open after 10:15 signal.
- One trade per day maximum.

## 4. Locked Exit

This was a state test, not a management experiment.

- Size: 3 MNQ contracts.
- Stop: fixed 30 points.
- Target: fixed 60 points.
- Time exit: 12:00 ET.
- No BE, no trail, no partials.
- Exit fills use `nb_lib.compute_realistic_pnl` with Band B commission,
  slippage treatment, and conservative tick-rounded fills.

## 5. In-Sample Result

Run date: 2026-06-21.

Artifacts:

- `nb_lib/scripts/ten_fifteen_opening_drive_vwap_reversal.py`
- `nb_lib/probe_results/ten_fifteen_opening_drive_state_router_trades.csv`
- `nb_lib/probe_results/ten_fifteen_opening_drive_state_router_report.md`
- `nb_lib/probe_results/ten_fifteen_opening_drive_state_router.json`

Summary:

| Metric | Value |
|---|---:|
| Trades | 152 |
| Distinct days | 152 |
| Total P&L | -$1,288.20 |
| Profit factor | 0.93 |
| Win rate | 33.6% |
| Mean P&L / trade | -$8.48 |
| Direction split | 90 long / 62 short |
| Best day | +$357.90 |
| Worst day | -$189.60 |
| Max drawdown | $3,812.70 |
| Exit mix | 47 tp / 98 full_stop / 7 time_exit |
| Average trades/month | 8.4 |
| Daily absolute-P&L HHI | 0.0074 |
| Positive-day HHI | 0.0202 |

State counts:

| State | Count |
|---|---:|
| bull_drive_accepted_continuation | 52 |
| bear_drive_accepted_continuation | 38 |
| bull_drive_rejected_reversal | 24 |
| bear_drive_rejected_reversal | 38 |
| no_signal | 228 |
| skip | 89 |

## 6. Interpretation

This is a clean informational reject. The 10:15 state idea produced a
real but small sample, and the contribution profile was not grotesquely
concentrated. The problem is simpler: the state routing does not have
enough edge under the fixed 30/60 bracket, and the frequency is only
8.4 trades/month.

Compared with the earlier first-hour momentum candidate, this fired at
a similar low frequency but with worse economics. Compared with the
VWAP fade, it had much lower frequency. The specific 10:15
accepted-or-rejected opening-drive state is therefore not a strong
standalone substrate as pinned.

Verdict: **tested-informational-rejected**. Do not spend OOS. If the
10:00-10:15 idea is revisited, it should probably be as a contextual
feature on another entry, not as a standalone fixed-time strategy.

## 7. OOS Discipline

No OOS rows were loaded for results. Any date >= 2026-02-01 hard-halts
in the script.
