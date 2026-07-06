---
name: "C2 Mid-Morning Targetability Mean Reversion Screen"
tagline: "C2 VWAP stretch-reclaim trades only during 10:30-12:00 ET when target/risk is not compressed."
status: "screen-rejected-positive-underpowered"
created: 2026-06-30
source: "Post-hoc C2 context baseline hypothesis; tested as an in-sample confirmation screen only."
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:30-12:00 ET"
hold_duration: "intraday"
signal_type: "vwap-stretch-reclaim-mean-reversion"
indicators: ["RTH VWAP", "expanding close-vs-VWAP deviation", "target/risk geometry"]
timeframes_used: ["1-second source", "1-minute trigger"]
position_sizing: "3 MNQ contracts for screen"
screen_script: "nb_lib/scripts/candidate_c4_midmorning_targetability_screen.py"
source_artifact: "nb_lib/probe_results/candidate_c2_context_hypothesis_value_test_report.md"
---

# C2 Mid-Morning Targetability Mean Reversion Screen

## Status Caveat

This is not a clean new discovery. The 10:30-12:00 bucket and the
target/risk floor came from the C2 context baseline. Therefore this
screen is an in-sample confirmation / falsification pass only. It may
earn a better candidate note, but it cannot validate edge or justify
OOS without a separate operator decision.

## Locked Predicate

Start from the existing C2 VWAP stretch-reclaim entry set:

- Setup: completed 1-minute close beyond `+/-2.0` RTH VWAP deviations.
- Reclaim: completed 1-minute close back inside `+/-1.0` within 10 bars.
- Entry: next 1-second bar after reclaim bar completion.
- Target: signal-bar RTH VWAP.
- Stop: adverse setup extreme plus/minus `0.5 * signal_deviation`.

Add two fixed gates:

- Entry time must be `10:30:00 <= entry_time < 12:00:00` ET.
- Target/risk geometry must be `intended_r >= 0.35`.

No volume filter is included because the first value test did not show
clear incremental separation from volume cooling.

## Screen Rule

Run the same five-axis mechanism screen on the filtered real/proxy C2
trade list.

- Any RED on hard axes 1-3 means **DO_NOT_BUILD**.
- Do not change the time bucket, target/risk floor, or stop geometry
  after seeing this result.
- OOS remains sealed.

## Screen Result

Run date: 2026-06-30.

Artifacts:

- `nb_lib/scripts/candidate_c4_midmorning_targetability_screen.py`
- `nb_lib/probe_results/candidate_c4_midmorning_targetability_screen_trades.csv`
- `nb_lib/probe_results/candidate_c4_midmorning_targetability_screen_report.md`
- `nb_lib/probe_results/candidate_c4_midmorning_targetability_screen.json`

Summary:

| Metric | Value |
|---|---:|
| Trades | 91 |
| Distinct days | 86 |
| Net P&L | +$2,586.90 |
| Mean P&L / trade | +$28.43 |
| Win rate | 74.7% |
| Profit factor | 1.278 |
| Max drawdown | $1,280.70 |
| Expected gross move | $177.02 |

Axis report:

| Axis | Flag | Read |
|---|---|---|
| skew_concentration | RED | Best trade is 22.0% of net; MinTRL is about 324 vs 91 in hand. |
| cost_distance | GREEN | Cost-distance is healthy (`phi=0.042`). |
| frequency_power | RED | `t=0.935`, below the 2.0 screen hurdle. |
| regime_concentration | YELLOW | Best day is 26.8% of net; best month is 39.0%. |
| cross_correlation | RED | Directional correlation with existing sleeves remains high on overlap days. |

Formal screen decision: **DO_NOT_BUILD**.

Interpretation: this is the best mean-reversion slice so far, and the
positive result is directionally useful. But it does not clear the
screen. It remains a hypothesis, not a build candidate: too few trades,
too much best-trade/month concentration, and insufficient t-stat.
