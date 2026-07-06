---
name: "Regime-Time-Gated MTF Pullback Continuation"
tagline: "Trade MNQ trend continuation only when 30-minute trend, 10-minute ADX, time-of-day, and 5-minute pullback-resumption align."
status: "screen-rejected-prebuild"
created: 2026-06-22
updated: 2026-06-22
source: "Compass intraday trend-continuation MNQ candidate menu, archived at ../source_artifacts/compass_intraday_trend_continuation_mnq_candidate_menu_20260622.md"

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-11:00 ET and 15:00-16:00 ET"
hold_duration: "intraday multi-bar"

signal_type: "trend-continuation"
indicators: ["EMA20", "EMA50", "ADX(14)", "ATR(14)", "Chandelier-style trail"]
timeframes_used: ["1-second source", "5-minute", "10-minute", "30-minute"]

brackets: "atr-scaled"
position_sizing: "fixed-contracts for screen; deployment sizing deferred"

canonical_spec: null
implementation: "../../scripts/candidate_d_regime_time_gated_mtf_pullback_screen.py"
screen_results:
  proxy_n: 128
  proxy_net_pnl_dollars: -455.75
  proxy_mean_pnl_dollars: -3.56
  proxy_pf: 0.933
  trades_per_month: 7.11
  stop_out_rate: 0.8516
  decision: "DO_NOT_BUILD"
  hard_red_axes: ["skew_concentration", "frequency_power"]
  caution_axes: ["cross_correlation"]
  oos_tested: false
related_candidates:
  - "intraday_momentum_continuation_base_hit"
  - "momentum_high_water_trail_post_1030"
  - "ema_trend_canonical_alpha"
  - "candidate_f_late_day_momentum_screen"
  - "noise_area_intraday_momentum"

test_results:
  in_sample_n: 128
  in_sample_pnl_dollars: -455.75
  in_sample_pf: 0.933
  in_sample_win_rate: 0.3438
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: null

tags:
  - rth-only
  - intraday
  - trend-continuation
  - pullback
  - multi-timeframe
  - atr-scaled
  - screen-rejected
---

# Regime-Time-Gated MTF Pullback Continuation

## Status

Screen-rejected before full build. OOS remained sealed.

The locked proxy screen generated 128 trades in the 2024-08-01 to
2026-01-31 in-sample window, or about 7.1 trades/month. The five-axis
screen returned `DO_NOT_BUILD` because two hard axes were red:
`skew_concentration` and `frequency_power`.

This candidate should not be promoted to a full strategy build without
a new thesis. Do not tune the ADX threshold, stop multiple, time
windows, or trigger after seeing this screen.

Screen artifacts:

- Report:
  `../../probe_results/candidate_d_regime_time_gated_mtf_pullback_screen_report.md`
- Proxy trades:
  `../../probe_results/candidate_d_regime_time_gated_mtf_pullback_screen_proxy_trades.csv`
- JSON:
  `../../probe_results/candidate_d_regime_time_gated_mtf_pullback_screen.json`
- Script:
  `../../scripts/candidate_d_regime_time_gated_mtf_pullback_screen.py`

## Screen Result

Locked proxy:

- symmetric long/short;
- 30-minute trend context;
- 10-minute ADX(14) > 22;
- 5-minute pullback to EMA20 with resumption trigger;
- entries only 09:45-11:00 and 15:00-16:00 ET;
- next 5-minute bar open entry;
- stop = max(1.5 x ATR(14, 5-minute), 30 points);
- exit = 2 x ATR chandelier-style trail or 13-bar time stop;
- no partial-profit logic in the proxy.

Result:

```text
Decision: DO_NOT_BUILD
Reason: red hard-gate axis: skew_concentration, frequency_power

n=128
trades/month=7.11
net P&L=-$455.75
mean/trade=-$3.56
PF=0.933
WR=34.38%
stop/trail exit rate=85.16%
cost-distance phi=0.024 (GREEN)
frequency-power t=-0.211 (RED)
MinTRL=Infinity because observed Sharpe did not clear benchmark
cross-correlation=YELLOW, max direction corr 0.588 vs noise-area 14d/vm1
```

Read:

- Cost-distance passed easily; moves were large enough relative to MNQ
  round-turn friction.
- Frequency did not come close to the source artifact's desired
  15-30/month. This landed in the same underpowered trend-continuation
  trap the research warned about.
- The resumption trigger did not solve the pullback-entry failure mode:
  the stop/trail exit rate was 85.16%, worse than the 80.7% warning
  cited by the source artifact.
- The proxy was not killed by one giant positive day; it was simply
  negative and underpowered.

## 1. Thesis

Naive continuous intraday trend-following on MNQ, especially on
5-minute bars, has a poor prior after costs. The source artifact argues
that any viable MNQ trend-continuation candidate should avoid uniform
all-session firing and instead require trend regime, time-of-day, and
multi-timeframe alignment.

This candidate records the source artifact's recommended first screen:
a 30-minute trend filter, 10-minute ADX trend-presence gate, and
5-minute pullback-resumption entry restricted to the open continuation
and power-hour windows. It is a contender for a cheap mechanism-class
screen first, not a full strategy build.

## 2. Mechanism

- **Trend windows, not all-session trend chasing.** The open and late
  afternoon carry more price discovery and institutional positioning
  flow than midday. Restricting entries to those windows should reduce
  lunch-chop whipsaw.
- **Higher-timeframe trend context.** A 30-minute EMA stack and slope
  filter is meant to prevent taking 5-minute continuation entries
  against the larger intraday direction.
- **Trend-presence gate.** A 10-minute ADX filter is a cheap way to
  suppress range-bound entries before the 5-minute trigger is even
  considered.
- **Pullback-resumption rather than passive pullback limit.** The
  source artifact explicitly warns that passive pullback entries in MNQ
  can stop out at high rates. This candidate should require a 5-minute
  confirmation/resumption bar before entry.
- **Right-tail preservation.** Exits should use ATR-scaled stops and a
  trailing/structural component rather than tight fixed targets, because
  trend-continuation needs its rare large winners.

## 3. Signal Logic

The screen candidate should evaluate RTH days only.

Long-side sketch:

- Time window is 09:45-11:00 ET or 15:00-16:00 ET.
- 30-minute trend context is bullish: price above EMA20 above EMA50,
  with EMA50 slope positive.
- 10-minute ADX(14) is above a pre-committed trend-presence threshold
  in the rough 22-25 area.
- On 5-minute bars, price pulls back toward a rising EMA20.
- Entry requires a resumption trigger, such as a 5-minute close back
  above the prior bar high, rather than a passive touch of the EMA.

Short side mirrors the logic only if the first screen explicitly
pre-commits symmetric shorts. If the screen starts long-only, it must
say so before running.

## 4. Exit Logic

The source artifact suggests:

- Initial stop: 1.5-2.0 x ATR(14) on 5-minute bars, with a practical
  lower bound around 30 MNQ points so friction is not a large share of
  stop distance.
- Profit handling: preserve the right tail. Candidate exits include a
  2x ATR Chandelier-style trail and/or a partial at 2R with a runner.
- Time exit: flat by the RTH close. A screen may also test a fixed
  multi-bar hold proxy around 10-13 bars if declared before running.

Exact exit choice is not pinned yet. The next step should be a cheap
proxy screen that declares one exit proxy and runs once.

## 5. Position Sizing

Use fixed contract sizing for the pre-build screen. Deployment sizing is
not relevant until a candidate survives the mechanism-class screen and
full robustness checks.

## 6. Required Indicators / Data

- MNQ RTH 1-second source data, aggregated to 5-minute, 10-minute, and
  30-minute bars.
- EMA20 and EMA50 on 30-minute bars.
- ADX(14) on 10-minute bars.
- EMA20 and ATR(14) on 5-minute bars.
- RTH calendar / half-day handling.

No order-flow, MBP, external volatility index, or non-MNQ feed is
required for the first screen.

## 7. Differentiation vs Already-Tested Strategies

- Unlike `ema_trend_canonical_alpha`, this is not a single fixed-time
  EMA-slope entry. It requires time-window, 30-minute trend context,
  10-minute trend-presence, and 5-minute resumption.
- Unlike `candidate_f_late_day_momentum_screen`, this is not a
  first-hour-to-power-hour momentum handoff. It is a multi-timeframe
  continuation/pullback structure.
- Unlike `noise_area_intraday_momentum`, this is not a broad breakout
  convexity bet. It tries to reduce concentration and chop by requiring
  pullback-resumption inside known trend windows.
- Unlike passive pullback candidates, it must not enter merely because
  price touched an average. Confirmation is part of the thesis.

## 8. Required Research Before Spec Drafting

- Run the mandatory mechanism-class screen first. If any hard axis is
  red, do not build the full strategy.
- Pre-commit whether the first screen is long-only or symmetric
  long/short.
- Pre-commit the ADX threshold, ATR stop multiple, and screen exit
  proxy from source reasoning, not parameter sweeping.
- Report trade frequency first. The source artifact expects roughly
  15-30 trades/month; if the screen produces less than 12/month, this
  candidate may be underpowered by construction.
- Report concentration explicitly: best day share, top month share,
  HHI, and calendar-year stability.
- Compare against prior momentum sleeves for trade-day overlap and
  direction correlation. If it is merely another same-day momentum
  reskin, stop.

## 9. Source / References

- Raw source artifact:
  `../source_artifacts/compass_intraday_trend_continuation_mnq_candidate_menu_20260622.md`
- Local methodology gate:
  `../../screening.py` via `screen_proxy_trades(...)`.
- Related source artifact:
  `../source_artifacts/compass_mechanism_class_screening_protocol_20260621.md`

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-06-22 | `untested-ideation` | Archived Compass source and recorded the recommended Candidate D as a contender. Build deferred; first action must be a pre-build screen. |
| 2026-06-22 | `screen-rejected-prebuild` | Locked proxy screen returned `DO_NOT_BUILD`: n=128, -$455.75, PF 0.933, 7.11 trades/month, 85.16% stop/trail exit rate; hard-red skew/expectancy and frequency-power. |
