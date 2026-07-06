---
name: "HTF VWAP Stretch / LTF Reclaim Mean Reversion Screen"
tagline: "Use 30-minute VWAP-band extension as structure, 1-minute reclaim as execution."
status: "screen-rejected"
created: 2026-06-30
source: "Carry-forward hypothesis from C2 failure: separate structural anchor timeframe from execution trigger timeframe."
markets: ["MNQ"]
session: "RTH"
time_of_day: "after anchor availability through 15:30 ET"
hold_duration: "intraday"
signal_type: "multi-timeframe-vwap-mean-reversion"
indicators: ["30-minute RTH VWAP", "30-minute VWAP deviation", "1-minute close-back-inside trigger"]
timeframes_used: ["1-second source", "1-minute trigger", "30-minute anchor"]
position_sizing: "3 MNQ contracts for proxy screen"
screen_script: "nb_lib/scripts/candidate_c3_htf_vwap_reclaim_screen.py"
source_artifact: "nb_lib/strategy_specs/source_artifacts/external_meanrev_video_intake_20260630.md"
---

# HTF VWAP Stretch / LTF Reclaim Mean Reversion Screen

## Thesis

C2 failed despite a high win rate because the setup and trigger both
lived on 1-minute bars. The resulting VWAP target was often too small
relative to the stop tail. C3 tests the operator's scale-separation
hypothesis:

```text
higher timeframe defines whether the mean-reversion setup is real;
lower timeframe defines when to execute it.
```

## Locked Predicate

This is a pre-build mechanism screen. It is not a full strategy build.

- In-sample window: 2024-08-01 through 2026-01-31.
- OOS hard halt: any date >= 2026-02-01.
- Anchor timeframe: completed 30-minute RTH bars.
- Anchor VWAP: cumulative RTH VWAP on 30-minute bars, through the
  completed anchor bar only.
- Anchor deviation: expanding standard deviation of 30-minute
  `close - anchor_vwap`, with minimum 4 completed 30-minute bars.
- Anchor setup:
  - upper stretch: completed 30-minute close >= `+2.0` anchor
    deviations and at least 20 points above anchor VWAP.
  - lower stretch: completed 30-minute close <= `-2.0` anchor
    deviations and at least 20 points below anchor VWAP.
- Execution timeframe: completed 1-minute bars after the anchor bar
  completes.
- Reclaim trigger: within the next 10 completed 1-minute bars, close
  back inside the `+/-1.0` anchor-deviation band.
- Direction: short after upper reclaim; long after lower reclaim.
- Entry: next 1-second bar open after the reclaim bar completes, with
  Band B entry slippage.
- Target: anchor VWAP, tick-rounded.
- Stop: adverse anchor extreme plus/minus `0.5 * anchor_deviation`,
  tick-rounded.
- If stop and target touch on the same 1-second bar, stop wins.
- Max trades/day: 2.
- Cooldown after exit: 20 minutes.
- EOD flat: 15:58:30 ET.

## Screen Rule

Run `screen_proxy_trades(...)` on the proxy trade list.

- Any RED on hard axes 1-3 means **DO_NOT_BUILD**.
- No retuning of anchor timeframe, trigger timeframe, z-threshold,
  reclaim window, minimum distance, or stop geometry after seeing the
  result.
- If and only if this clears the mechanism screen, it becomes eligible
  for a full realsim build.

## Screen Result

Run date: 2026-06-30.

Artifacts:

- `nb_lib/scripts/candidate_c3_htf_vwap_reclaim_screen.py`
- `nb_lib/probe_results/candidate_c3_htf_vwap_reclaim_screen_proxy_trades.csv`
- `nb_lib/probe_results/candidate_c3_htf_vwap_reclaim_screen_report.md`
- `nb_lib/probe_results/candidate_c3_htf_vwap_reclaim_screen.json`

Summary:

| Metric | Value |
|---|---:|
| Trades | 48 |
| Distinct days | 44 |
| Net P&L | -$2,089.80 |
| Mean P&L / trade | -$43.54 |
| Win rate | 72.9% |
| Exit mix | 35 tp / 11 full_stop / 2 eod |
| Expected gross move | $106.06 |
| Round-turn cost | $7.50 |

Axis report:

| Axis | Flag | Read |
|---|---|---|
| skew_concentration | RED | Observed Sharpe is negative; MinTRL is infinite because the book does not clear the zero benchmark. |
| cost_distance | GREEN | The HTF anchor solved the cost-distance issue (`phi=0.071`). |
| frequency_power | RED | `t=-1.203`; sparse and negative. |
| regime_concentration | GREEN | Not a one-day / one-month concentration problem. |
| cross_correlation | RED | Low day overlap but high direction correlation on overlapping days. |

Formal screen decision: **DO_NOT_BUILD**.

Interpretation: the scale-separation hypothesis behaved structurally
as intended: it produced a larger target corridor than the 1-minute C2
construction and kept a high win rate. But the small number of HTF
setups was negative, and the stop tail still dominated the VWAP-target
wins. The construction is therefore rejected pre-build. Do not retune
the anchor timeframe, trigger timeframe, stretch threshold, reclaim
window, or stop geometry on this sample to rescue it.
