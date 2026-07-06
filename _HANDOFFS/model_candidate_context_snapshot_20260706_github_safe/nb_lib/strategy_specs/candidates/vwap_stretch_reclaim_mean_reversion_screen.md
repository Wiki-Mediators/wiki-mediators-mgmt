---
name: "VWAP Stretch Reclaim Mean Reversion Screen"
tagline: "Mean-reversion only after a VWAP stretch fails and closes back inside the band."
status: "screen-rejected"
created: 2026-06-30
source: "External mean-reversion video intake, translated into an MNQ-RTH objective predicate after rejecting direct daily-bar transfer."
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-15:30 ET"
hold_duration: "intraday"
signal_type: "vwap-stretch-reclaim-mean-reversion"
indicators: ["RTH VWAP", "expanding close-vs-VWAP deviation"]
timeframes_used: ["1-second source", "1-minute derived"]
position_sizing: "3 MNQ contracts for proxy screen"
screen_script: "nb_lib/scripts/candidate_c2_vwap_stretch_reclaim_screen.py"
source_artifact: "nb_lib/strategy_specs/source_artifacts/external_meanrev_video_intake_20260630.md"
---

# VWAP Stretch Reclaim Mean Reversion Screen

## Thesis

The rejected VWAP z-score fade entered while price was still extended
away from VWAP. This screen tests a different mean-reversion mechanism:
do not fade strength/weakness directly; wait for the extension to fail.

The predicate is intentionally simple and pre-registered before running:
price must first close beyond a 2-sigma RTH VWAP distance, then close
back inside the 1-sigma band within 10 completed 1-minute bars. Entry is
on the next 1-second bar after the reclaim bar, toward VWAP.

## Locked Window

- In-sample: 2024-08-01 through 2026-01-31.
- OOS hard halt: any date >= 2026-02-01.

## Locked Signal

All signal features use completed 1-minute bars only.

- RTH VWAP starts at 09:30 ET.
- Deviation is the expanding session standard deviation of
  `close - RTH_VWAP`, with minimum 20 completed bars.
- Scan starts 09:45 ET and ends 15:30 ET.
- Upper setup: a completed bar closes at least `+2.0` deviations above
  VWAP and at least 6 points from VWAP.
- Lower setup: a completed bar closes at least `-2.0` deviations below
  VWAP and at least 6 points from VWAP.
- Reclaim confirmation: within the next 10 completed bars, price closes
  back inside the `+/-1.0` deviation band.
- Direction: short after upper reclaim, long after lower reclaim.
- Entry: next 1-second bar open after the reclaim bar completes, with
  Band B entry slippage.
- One open trade at a time; maximum 3 trades per day; 10-minute cooldown
  after exit.

## Locked Proxy Exit

This is a mechanism-class screen, not a full strategy build.

- Target: signal-bar RTH VWAP, tick-rounded.
- Stop: adverse setup extreme plus `0.5 * signal_deviation`, tick-rounded.
- If both stop and target are touched in the same 1-second bar, stop wins.
- EOD flat: 15:58:30 ET.
- Exit P&L uses `compute_realistic_pnl` with Band B friction and
  conservative tick-rounded fills.

## Screen Rule

Run `screen_proxy_trades(...)` on the resulting proxy trade list.

- Any RED on hard axes 1-3 (`skew_concentration`, `cost_distance`,
  `frequency_power`) means **DO_NOT_BUILD**.
- If the screen does not clear, stop. Do not retune z thresholds,
  reclaim window, stop geometry, time window, or filters to rescue it.
- If and only if the screen clears, it becomes eligible for a separate
  full realsim build in the same session.

## Screen Result

Run date: 2026-06-30.

Artifacts:

- `nb_lib/scripts/candidate_c2_vwap_stretch_reclaim_screen.py`
- `nb_lib/probe_results/candidate_c2_vwap_stretch_reclaim_screen_proxy_trades.csv`
- `nb_lib/probe_results/candidate_c2_vwap_stretch_reclaim_screen_report.md`
- `nb_lib/probe_results/candidate_c2_vwap_stretch_reclaim_screen.json`

Summary:

| Metric | Value |
|---|---:|
| Trades | 515 |
| Distinct days | 307 |
| Net P&L | -$6,730.50 |
| Mean P&L / trade | -$13.07 |
| Win rate | 75.3% |
| Exit mix | 388 tp / 123 full_stop / 4 eod |
| Expected gross move | $115.33 |
| Round-turn cost | $7.50 |

Axis report:

| Axis | Flag | Read |
|---|---|---|
| skew_concentration | RED | Observed Sharpe is negative; MinTRL is infinite because the book does not clear the zero benchmark. |
| cost_distance | GREEN | Cost is not the problem (`phi=0.065`). |
| frequency_power | RED | `t=-1.243`; expectancy is negative despite 515 trades. |
| regime_concentration | GREEN | This is not a one-day / one-month concentration failure. |
| cross_correlation | RED | High overlap/correlation with existing sleeves, especially EMA/VWAP and the rejected VWAP fade. |

Formal screen decision: **DO_NOT_BUILD**.

Interpretation: the reclaim rule fixed the obvious flaw in the blind
fade construction by requiring failure evidence first, and it produced
the expected high-win-rate mean-reversion shape. But the left tail still
overwhelms the many small VWAP-target wins. This is a clean
screen-rejected predicate. Do not run a full realsim build or tune the
z/reclaim/window/stop parameters to rescue this sample.

## Carry-Forward Hypothesis: Higher-Timeframe Anchor, Lower-Timeframe Trigger

Status: **untested hypothesis layer / not a rescue of C2**.

The C2 screen used the same 1-minute timeframe for both parts of the
idea:

- anchor / structure: the `+/-2.0` VWAP-deviation stretch
- execution trigger: close back inside the `+/-1.0` band

That likely made the setup too microstructural. A 1-minute VWAP stretch
can be ordinary intraday noise, and the VWAP target is often too small
relative to the stop tail. The next legitimate hypothesis is a
multi-timeframe construction:

```text
higher timeframe defines whether the mean-reversion setup is real;
lower timeframe defines when to execute it.
```

Preliminary C3 shape, if pursued:

- Anchor timeframe: 30-minute or 1-hour RTH bars.
- Anchor state: completed HTF bar closes beyond `+/-2.0` HTF VWAP
  deviation bands, using VWAP and deviation computed only through the
  completed HTF bar.
- Execution timeframe: 10-minute or 1-minute completed bars.
- Trigger: after the HTF stretch is present, wait for LTF close-back-
  inside confirmation toward VWAP.
- Target: HTF VWAP or an objective intermediate level on the path back
  to HTF VWAP.
- Stop: structural invalidation beyond the HTF stretch extreme, not the
  LTF reclaim bar alone.

Reason this is a different hypothesis:

- C2 asked 1-minute noise to define both the opportunity and the entry.
- C3 asks a higher timeframe to define a larger, less noisy extension,
  then uses a lower timeframe only for timing.
- This directly addresses the cost-distance issue: a 30-minute or
  1-hour VWAP-band extension should create a larger VWAP-to-entry
  corridor than a 1-minute stretch.

Discipline note: this hypothesis must be pre-registered and screened as
its own predicate before any build. Do not tune the anchor timeframe,
trigger timeframe, z-thresholds, or stop geometry after seeing C3
results. The failed C2 result remains closed.
