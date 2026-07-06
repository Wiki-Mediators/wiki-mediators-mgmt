---
name: "Candidate F Late-Day Momentum"
tagline: "Follow a strong first-hour move at 15:00 only when midday realized range sits in its trailing middle tercile."
status: "screen-rejected-prebuild"
created: 2026-06-21
updated: 2026-06-21
source: "Operator/Claude proposed Candidate F as the first real-world test of the new mechanism-class screening protocol."

markets: ["MNQ"]
session: "RTH"
time_of_day: "15:00-15:58:30 ET"
hold_duration: "late-day intraday"

signal_type: "late-day-momentum"
indicators: ["first-hour return", "10:30-15:00 realized range", "trailing 20-day realized-range tercile"]
timeframes_used: ["1-second source"]

implementation: "nb_lib/scripts/candidate_f_late_momentum_screen.py"
screen_results:
  proxy_n: 40
  proxy_net_pnl_dollars: -264.50
  proxy_mean_pnl_dollars: -6.6125
  decision: "DO_NOT_BUILD"
  hard_red_axes: ["skew_concentration", "frequency_power"]
  caution_red_axes: ["cross_correlation"]
  oos_tested: false

related_candidates:
  - "first_hour_momentum_acceptance_base_hit"
  - "noise_area_intraday_momentum"
  - "ema_vwap_micro_pullback_scalp"

tags:
  - screen-only
  - prebuild-rejected
  - momentum
  - late-day
  - rth-only
---

# Candidate F Late-Day Momentum

## Status

Screen-rejected before full build. OOS remained sealed.

This candidate was the first real use of the new mechanism-class
screening protocol. It was intentionally treated as a gate-validation
case: if the screen rejected a plausible momentum proposal, the protocol
would be doing its job rather than merely decorating the workflow.

## Locked Proxy

- Window: 2024-08-01 through 2026-01-31.
- OOS hard halt: 2026-02-01.
- First-hour return threshold: absolute 09:30-10:30 return >= 0.45%.
- Midday realized-vol proxy: 10:30-15:00 high-low range.
- Vol filter: current midday range in the middle tercile of its trailing
  20-day distribution.
- Direction: sign of the first-hour return.
- Proxy entry: 15:00 close.
- Proxy stop: 1x 10:30-15:00 realized range.
- Proxy exit: stop or 15:58:30 close.
- Flat round-turn cost: 1.25 points / $2.50 per MNQ.

This was not a full execution simulation and did not model queue,
slippage path, or strategy lifecycle. It was intentionally a cheap
proxy list for `nb_lib/screening.py`.

## Screen Result

```text
Proxy trades: 40
Net P&L: -$264.50
Mean/trade: -$6.61

Decision: DO_NOT_BUILD
Reason: red hard-gate axis: skew_concentration, frequency_power

skew_concentration: RED
  observed Sharpe does not clear benchmark

cost_distance: GREEN
  phi = 0.027

frequency_power: RED
  t-stat = -0.306

regime_concentration: GREEN
  no red/yellow period concentration because net is negative

cross_correlation: RED
  direction correlation is high against prior momentum sleeves
```

Cross-correlation detail:

| Existing sleeve | Overlap days | Jaccard | Direction corr |
|---|---:|---:|---:|
| first_hour_momentum_acceptance_base_hit | 29 | 0.180 | 1.000 |
| noise_area_intraday_momentum_14d_vm1 | 27 | 0.126 | 1.000 |
| noise_area_intraday_momentum_90d_vm15 | 16 | 0.137 | 1.000 |
| ema_vwap_micro_pullback_scalp | 40 | 0.105 | 0.826 |

## Read

Candidate F is not rejected because of positive-convex concentration; it
is rejected because the proxy is sparse and negative. It produces only
40 trades in the in-sample window, observed Sharpe is below zero, and
Frequency-Power is deeply red. The trade-day Jaccard versus the first
hour strategy is below the explicit 0.5 "reskin" bar, but signal
direction is perfectly aligned against the prior momentum sleeves on
common days. This is not a fresh mechanism.

No full build should be run without a new thesis. The clean rejection is
a successful test of the screening protocol.

## Artifacts

- Report: `nb_lib/probe_results/candidate_f_late_day_momentum_screen_report.md`
- Proxy trades: `nb_lib/probe_results/candidate_f_late_day_momentum_screen_proxy_trades.csv`
- JSON: `nb_lib/probe_results/candidate_f_late_day_momentum_screen.json`
- Script: `nb_lib/scripts/candidate_f_late_momentum_screen.py`
