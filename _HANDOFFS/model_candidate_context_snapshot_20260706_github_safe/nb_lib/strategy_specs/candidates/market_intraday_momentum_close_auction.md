---
name: "Market Intraday Momentum Close Auction"
tagline: "Once-daily hold-into-close market intraday momentum candidate: prior-close-to-10:00 return predicts the 15:30-15:58:30 closing-window move."
status: "screen-rejected-prebuild"
created: 2026-06-22
updated: 2026-06-22
source: "nb_lib/strategy_specs/source_artifacts/compass_market_intraday_momentum_mnq_candidate_20260622.md"

markets: ["MNQ"]
session: "RTH"
time_of_day: "15:30-15:58:30 ET"
hold_duration: "closing-window intraday"

signal_type: "market-intraday-momentum"
indicators: ["prior close to 10:00 return", "optional 15:00-15:30 confirmation label", "volatility labels", "volume labels", "catalyst labels"]
timeframes_used: ["1-minute signal bars", "1-second execution realism"]

implementation: "nb_lib/scripts/market_intraday_momentum_close_auction_screen.py"
composition_overlay_contract:
  intraday_target_invalidation_packet:
    baseline_mode: "label_only"
    registered_overlay_mode: "hard_gate"
    rule: "At 15:30 ET, compute targetability from lookahead-safe targets, structural invalidation, net R, and volatility reachability. Baseline records fields only; registered overlay trades only when targetability_pass is true."
screen_results:
  screen_date: 2026-06-22
  baseline_proxy_n: 379
  baseline_proxy_net_pnl_dollars: -3718.00
  baseline_proxy_mean_pnl_dollars: -9.81
  baseline_proxy_pf: 0.771
  baseline_avg_trades_per_month: 21.1
  targetability_proxy_n: 21
  targetability_proxy_net_pnl_dollars: -145.00
  targetability_proxy_mean_pnl_dollars: -6.90
  targetability_proxy_pf: 0.820
  targetability_avg_trades_per_month: 1.2
  targetability_skip_rate: 0.945
  decision: "DO_NOT_BUILD"
  oos_tested: false

related_candidates:
  - "intraday_momentum_continuation_base_hit"
  - "candidate_f_late_day_momentum_screen"
  - "first_hour_momentum_acceptance_base_hit"
  - "noise_area_intraday_momentum"

tags:
  - screen-rejected-prebuild
  - market-intraday-momentum
  - close-window
  - once-daily
  - high-frequency-relative
  - no-stop-baseline
  - ohlcv-testable
---

# Market Intraday Momentum Close Auction

## Status

Candidate banked from external research. Screened as a cheap proxy on
2026-06-22 and rejected pre-build. Not tested OOS.

This candidate is distinct from prior MNQ momentum builds because it
keeps the published effect in its cleanest form: one daily directional
bet into the close. The source note explicitly warns that Nasdaq/QQQ is
the weakest documented vehicle out-of-sample and that MNQ-specific
intraday OHLCV work has produced null institutional-validation results.
That makes this a serious but skeptical candidate, not an assumed edge.

## Screen Result (2026-06-22)

Screen/proxy artifact:
`nb_lib/probe_results/market_intraday_momentum_close_auction_screen_report.md`.

The raw close-auction momentum baseline fired often enough to satisfy
the intended frequency profile, but it failed economically:

- Baseline proxy: 379 trades, 21.1 trades/month, net -$3,718.00, PF
  0.771, mean -$9.81/trade, max DD $3,721.00.
- Targetability hard gate: 21 trades, 1.2 trades/month, net -$145.00,
  PF 0.820, mean -$6.90/trade, max DD $545.50.
- Targetability skip rate: 94.5%; dominant skip reason was
  `risk_reward_too_low` under the pre-entry targetability packet.

Decision: **DO_NOT_BUILD**. The baseline is negative, and the
targetability overlay destroys the candidate's frequency advantage while
remaining negative. Do not tune this overlay as a rescue. Any future
close-auction thesis must be a newly registered candidate, not a
continuation of this failed screen.

## Locked Baseline

- Universe: MNQ continuous front-month, RTH only.
- Signal return: `r1 = price_10:00_ET / prior_day_16:00_ET_close - 1`.
- Direction: long if `r1 > 0`; short if `r1 < 0`; no trade only if
  `r1 == 0` or required prices are missing.
- Entry: 15:30:00 ET.
- Exit: flat by 15:58:30 ET.
- Position size for validation: 1 MNQ.
- Stop: none in the registered baseline. A catastrophe stop, if ever
  tested, is a separate variant.
- Cost model: 1.25 points / $2.50 round turn per MNQ, with a 2.0-point
  stress read.
- OOS: sealed unless the operator explicitly authorizes a separate OOS
  spend for this candidate.

## Registered Variants

These are not tuning knobs. Each variant is a separate registered trial
if it is ever run.

1. `r1_threshold_025`: trade only when `abs(r1) >= 0.25%`.
2. `r1_r12_agreement`: trade only when `r1` and the 15:00-15:30 return
   agree in sign.
3. `targetability_hard_gate`: same `r1` direction and same 15:30 entry
   clock as baseline, but trade only if the pre-entry targetability
   packet passes.

Volatility, volume, FOMC/CPI/GDP, and targetability fields should be
recorded as labels first, not used as gates in the baseline. The
candidate's main advantage is frequency; adding filters before the
baseline read risks destroying the power advantage that makes it worth
testing.

## No Target, No Trade Relationship

The baseline intentionally does **not** hard-gate on targetability. The
published effect is an unconditional closing-window pressure effect; a
targetability gate would make it a different strategy.

However, every run should emit the `intraday_target_invalidation_packet`
where possible:

- nearest objective target in the trade direction;
- structural invalidation or catastrophe boundary;
- reward/risk and volatility reachability labels;
- `targetability_pass` as a label for post-run attribution.

If the unconditional baseline earns further work, a targetability-gated
overlay can be registered as a separate experiment. It must beat the
unconditional baseline after accounting for lower trade count.

## Targetability-Modified Version

The operator-selected modified version is:

```text
market_intraday_momentum_close_auction + targetability_hard_gate
```

This keeps the candidate's entry idea fixed and changes only the
pre-entry management criterion.

At 15:30 ET:

1. Compute the baseline direction from `r1`.
2. Build a targetability packet using only levels known at or before
   15:30.
3. Trade only if the packet has:
   - objective target ahead in the trade direction;
   - structural invalidation or catastrophe boundary;
   - `r_to_target_net_of_cost >= 1.5`;
   - target distance within the volatility reachability limit;
   - no stale or already-touched target.
4. If the packet fails, record `no_target_reason` and skip.

Allowed target sources at 15:30:

- prior RTH high/low and floor pivots;
- prior value area / POC if available from completed prior session;
- overnight high/low frozen before RTH;
- completed opening-range high/low;
- session VWAP and VWAP bands frozen at 15:30;
- major round numbers;
- confirmed swing levels only after their confirmation lag.

Forbidden target sources:

- any level requiring price action after 15:30;
- unconfirmed swing pivots;
- the in-progress bar's high/low;
- developing current-session value area unless frozen before entry.

This is a registered overlay, not a rescue. It must be compared to the
unconditional baseline on the same in-sample window. The useful question
is whether targetability improves expectancy and concentration enough to
justify the lower trade count.

## Pre-Build Screen Expectations

Run a cheap proxy through `nb_lib/screening.py` before any full build.
The important axes are:

- **frequency_power:** baseline should approach one trade per RTH day;
- **cost_distance:** expected closing-window move must comfortably
  exceed the 1.25-point cost model;
- **skew_concentration:** best-day and best-20-day share must not
  recreate the concentration failures seen in the prior momentum
  family;
- **cross_correlation:** report whether it is merely a re-skin of
  first-hour momentum/noise-area days or a distinct close-window sleeve.

Suggested in-sample gates from the source note:

- after-cost PF >= 1.15;
- net edge >= 1.0 point per trade;
- trades/month >= 20 for the baseline;
- best-day share below roughly 10-15%;
- positive net in at least 3 of 4 calendar years when enough years are
  available.

For the targetability-modified overlay, also report:

- baseline trade count versus targetability-allowed trade count;
- skip-rate by `no_target_reason`;
- PF / expectancy / max drawdown of allowed trades;
- whether blocked trades were actually worse than allowed trades;
- whether the overlay still clears `trades/month >= 20`, or if the gate
  destroys the candidate's frequency advantage.

## Read Discipline

The honest base-rate expectation is decay or regime dependence. A clean
negative screen should kill the candidate before build. A positive
screen should still be treated as in-sample only until a separately
authorized OOS protocol exists.

If the raw baseline fails, do not use the targetability overlay to
search for a green subset. If the baseline is flat-to-positive, the
overlay can be read as a pre-committed management improvement trial.
