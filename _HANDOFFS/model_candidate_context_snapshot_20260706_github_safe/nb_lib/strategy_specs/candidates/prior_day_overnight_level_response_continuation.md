---
name: "Prior-Day / Overnight Level Response Continuation"
status: "screen_only_rejected"
created: "2026-06-23"
mechanism_class: "level-response continuation"
implementation: "nb_lib/scripts/candidate_a_level_response_screen.py"
screen_report: "nb_lib/probe_results/candidate_a_level_response_screen_report.md"
screen_json: "nb_lib/probe_results/candidate_a_level_response_screen.json"
proxy_trades: "nb_lib/probe_results/candidate_a_level_response_screen_proxy_trades.csv"
oos_status: "sealed; no OOS rows used for results"
decision: "do_not_build"
---

# Prior-Day / Overnight Level Response Continuation

This candidate was created after the first-hour targetability snapshot
review showed that targetability works as structural hygiene but cannot
rescue an entry with weak directional edge. The natural next question
was whether a level-response entry, where target and invalidation are
intrinsic to the thesis, could carry the targetability idea better.

Methodology decision: screen the bare entry mechanism first. Do not bolt
on the targetability gate until the unfiltered entry earns a build.

## Locked Screen Proxy

Run date: 2026-06-23.

Artifact:

- `nb_lib/scripts/candidate_a_level_response_screen.py`
- `nb_lib/probe_results/candidate_a_level_response_screen_report.md`
- `nb_lib/probe_results/candidate_a_level_response_screen.json`
- `nb_lib/probe_results/candidate_a_level_response_screen_proxy_trades.csv`

Screen-only proxy, not a full strategy engine:

- Window: 2024-08-01 through 2026-01-31.
- OOS cutoff: 2026-02-01; no OOS rows used for results.
- Objective trigger levels frozen at RTH open: PDH, PDL, ONH, ONL when
  overnight bars exist.
- Completed 10-minute bar breaks the level by at least 3 points.
- Retest/hold must occur within the next 3 completed 10-minute bars.
- Entry at the next 10-minute bar open in the breakout direction.
- Regime gate: 10-minute ADX(14) >= 20, or RTH open outside prior
  session value area.
- Stop: 3 points back inside the broken level.
- Target: nearest objective level in direction at least 25 points away
  from entry. Objective target pool includes prior-day/overnight levels,
  prior value area, floor pivots, and round-number targets.
- First qualifying trade per day.
- Exit proxy: stop, target, or flat at 15:55 ET.
- Flat cost: 1.25 points / $2.50.

## Screen Result

| Metric | Value |
|---|---:|
| Proxy trades | 252 |
| Net P&L | +$165.00 |
| Mean/trade | +$0.65 |
| Profit factor | 1.023 |
| Win rate | 38.9% |
| Expected gross move | $58.05 |

Five-axis screen:

| Axis | Flag | Read |
|---|---|---|
| Skew / concentration | RED | best trade = 80.3% of net; MinTRL ~29,879 |
| Cost distance | GREEN | cost/gross phi 0.043 |
| Frequency / power | RED | t-stat 0.151 |
| Regime concentration | RED | best month = 153.9% of net |
| Cross-correlation | RED | max trade-day Jaccard 0.663 |

Trigger mix:

| Trigger source | n |
|---|---:|
| ONL | 78 |
| ONH | 76 |
| PDH | 56 |
| PDL | 42 |

Exit mix:

| Exit reason | n |
|---|---:|
| proxy_stop | 154 |
| proxy_target | 96 |
| time_exit | 2 |

Decision: **DO_NOT_BUILD**.

## Interpretation

This screen did not fail because of frequency or friction. It produced
252 trades and the cost-distance axis was green. It failed because the
post-cost expectancy was essentially flat, the observed Sharpe was near
zero, MinTRL was unreachable, and the tiny positive net was highly
concentrated.

The result also weakens the hope that this level-response construction
would be an orthogonal portfolio sleeve. Its max trade-day Jaccard was
0.663 against the existing EMA/VWAP scalp sleeve and 0.646 against the
VWAP z-score fade sleeve. Directional correlation was low, but the
trade-day overlap was too high for this proxy to count as a clean
diversifier.

Do not add the targetability gate to this candidate as a rescue. The
banked rule from the targetability snapshot review was: screen the bare
entry first, then compose the gate only if the entry earns it. This
entry did not earn it.

## Closeout

This is a useful negative. It tested the most natural home for the
no-target/no-trade idea and found that the locked prior-day/overnight
break-retest continuation proxy is not strong enough to build.

Future level-response work must be materially different, not a
parameter rescue of this construction. Examples of materially different
questions would be:

- response/rejection rather than continuation;
- current opening-range levels rather than prior-day/overnight levels;
- a non-OHLCV confirmation source;
- a separate pre-committed screen using a different mechanism class.

Those would be new candidates, not iterations of this rejected screen.
