---
name: "First Hour Momentum Acceptance Base Hit"
tagline: "Trade a large first-30-minute RTH push only if price is still accepted outside the opening range at 10:30, using a simple fixed base-hit bracket."
status: "tested-informational"
created: 2026-06-21
updated: 2026-06-21
source: "Built after OU characterization closed generic management-as-alpha for current entry families; entry-substrate probe using the opening momentum acceptance state from the prior G2/v2a overlay."
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:30-15:58 ET"
hold_duration: "intraday"
signal_type: "opening-momentum-continuation"
indicators: ["first-30-minute return", "09:30-09:45 opening range", "RTH VWAP"]
timeframes_used: ["1-second source"]
brackets: "fixed base-hit"
position_sizing: "fixed contracts"
canonical_spec: null
implementation: "nb_lib/scripts/first_hour_momentum_acceptance_base_hit.py"
management_overlay_results:
  targetability_overlay_20260622:
    implementation: "nb_lib/scripts/first_hour_momentum_acceptance_targetability_overlay.py"
    report: "nb_lib/probe_results/first_hour_momentum_acceptance_targetability_overlay_report.md"
    baseline_n: 150
    baseline_pnl_dollars: 4024.50
    baseline_pf: 1.235
    allowed_n: 12
    allowed_pnl_dollars: -85.20
    allowed_pf: 0.944
    skip_rate: 0.920
    decision: "do_not_promote_targetability_overlay"
related_candidates:
  - "intraday_momentum_continuation_base_hit"
  - "opening_momentum_acceptance_overlay"
  - "g2"
test_results:
  in_sample_window: ["2024-08-01", "2026-01-31"]
  in_sample_n: 150
  in_sample_pnl_dollars: 4024.50
  in_sample_pf: 1.24
  in_sample_win_rate: 0.393
  in_sample_max_drawdown_dollars: 2867.40
  in_sample_contracts: 3
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: null
admissibility:
  r1_edge_thesis:
    r1_diagnostic_convention_version: null
    r1_diagnostic_script: null
    r1_diagnostic_output: null
    r1_verdict: "INFORMATIONAL_DIRECT_BACKTEST"
  r2_apex_survival:
    risk_dollars_per_trade: 189.60
    max_running_drawdown_dollars: 2867.40
    r2_variance_verdict: "FAILS_DEPLOYABILITY_AS_BUILT"
  r4_signal_frequency:
    probe_window_start: "2024-08-01"
    probe_window_end: "2026-01-31"
    probe_n_signals_observed: 150
    distinct_days_with_signal: 150
    sparsity_class: "healthy"
tags:
  - rth-only
  - intraday
  - momentum
  - trend-continuation
  - opening-range
  - vwap
  - base-hit
  - ohlcv-testable
  - entry-substrate
---

# First Hour Momentum Acceptance Base Hit

## 1. Thesis

The prior management work closed a lot of return-seeking management
paths for the existing entry families. This candidate pivots back to
entry quality: only trade days where the first 30 minutes make a large
directional move and price remains accepted in that direction at 10:30
ET.

The idea is intentionally simple. A large opening push alone can be a
trap; a large opening push that is still outside the 09:30-09:45
opening range and on the correct side of RTH VWAP at 10:30 is a cleaner
momentum-continuation state.

## 2. Locked Signal

All measurements are made from completed in-sample bars only.

- Window: 2024-08-01 through 2026-01-31.
- OOS hard halt: any date >= 2026-02-01.
- Momentum threshold: first 30-minute move >= +/-31.83 MNQ points.
- Long acceptance: first 30-minute move >= +31.83, 10:30 acceptance
  close above the 09:30-09:45 opening-range high, and above RTH VWAP
  through 10:30.
- Short acceptance: symmetric below -31.83, opening-range low, and
  VWAP.
- Entry: next 1-second open after 10:30:00, with 0.5 point entry
  slippage.
- One trade per day maximum.

## 3. Locked Exit

This is not a management experiment.

- Size: 3 MNQ contracts.
- Stop: fixed 30 points.
- Target: fixed 60 points.
- EOD flat: 15:58:30 ET.
- No BE, no trail, no partials.
- Exit fills use `nb_lib.compute_realistic_pnl` with Band B stop
  overshoot, commission, and conservative tick-rounded fills.

## 4. In-Sample Result

Run date: 2026-06-21.

Artifacts:

- `nb_lib/scripts/first_hour_momentum_acceptance_base_hit.py`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_trades.csv`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_report.md`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit.json`

Summary:

| Metric | Value |
|---|---:|
| Trades | 150 |
| Distinct days | 150 |
| Total P&L | +$4,024.50 |
| Profit factor | 1.24 |
| Win rate | 39.3% |
| Mean P&L / trade | +$26.83 |
| Direction split | 87 long / 63 short |
| Best day | +$357.90 |
| Worst day | -$189.60 |
| Best day % of total | 8.89% |
| Max drawdown | $2,867.40 |
| Exit mix | 90 full_stop / 59 tp / 1 eod |

Attribution quick check:

| Slice | n | P&L | PF | Win rate | Max DD |
|---|---:|---:|---:|---:|---:|
| Long | 87 | +$1,024.80 | 1.10 | 36.8% | $2,552.10 |
| Short | 63 | +$2,999.70 | 1.45 | 42.9% | $1,580.70 |

Month stability: 12 of 18 months positive, 6 negative. The January
2026 month contributed +$2,104.80, so a future stability pass should
check whether the result is overly dependent on the late in-sample
period before any promotion.

State counts:

| State | Days |
|---|---:|
| bullish_acceptance | 87 |
| bearish_acceptance | 63 |
| failed_momentum | 103 |
| no_momentum | 127 |
| skip | 89 |

## 5. Interpretation

This is a live lead, not a deployment candidate. The entry substrate is
not dead: a plain, same-direction first-hour acceptance rule produced a
positive in-sample result after realistic stop overshoot, commission,
and tick-rounded exits.

The drawdown is too high relative to the net profit at 3 contracts, so
the as-built fixed 30x60 bracket does not satisfy deployability. The
next sensible work is not OOS and not rescue-tuning; it is a
pre-committed shape check:

- long-vs-short attribution;
- month/block stability;
- whether the edge comes from 1-2 isolated periods;
- whether a structurally defined stop/target improves drawdown without
  killing the entry finding.

OOS remains sealed for this candidate.

## 6. Robustness Diagnostic

Run date: 2026-06-21.

Artifacts:

- `nb_lib/scripts/first_hour_momentum_acceptance_robustness.py`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_robustness_report.md`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_robustness.json`
- Raw source prompt/reference:
  `nb_lib/strategy_specs/source_artifacts/compass_formula_level_menu_intraday_mnq_momentum_20260621.md`

The formula-menu warning was correct: the result is promising but not
yet statistically clean.

Concentration:

| Metric | Value |
|---|---:|
| Top-1 month share of total P&L | 52.3% |
| Top-3 month share of total P&L | 103.5% |
| Top-5 month share of total P&L | 137.0% |
| Positive-month HHI adjusted | 0.050 |
| Monthly absolute Gini | 0.344 |

Leave-one-month-out:

- Removing January 2026 leaves +$1,919.70 over 138 trades, PF 1.12,
  expectancy +$13.91/trade.
- Full stationary-bootstrap expectancy CI95:
  -$16.97 to +$73.20/trade; P(total P&L <= 0) = 10.9%.
- Ex-January stationary-bootstrap expectancy CI95:
  -$26.94 to +$54.76/trade; P(total P&L <= 0) = 24.8%.

Interpretation: the candidate survives the crude "remove the lucky
month" check in point-estimate terms, but the uncertainty interval
still crosses zero. Treat as a research substrate, not a validated edge.
The next variant should be pre-committed and stability-oriented:
volatility-normalized brackets, VWAP-z acceptance, or structural
opening-range bracket geometry. Do not run OOS yet.

## 7. ATR Mechanism Check

Run date: 2026-06-21.

Artifacts:

- `nb_lib/scripts/first_hour_momentum_acceptance_atr_mechanism.py`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_atr_mechanism_report.md`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_atr_mechanism.json`

Question: is the January-heavy fixed-bracket result mostly a
high-volatility / high-ATR artifact that a volatility-normalized bracket
would naturally de-concentrate?

Result: **NO**.

| Check | Value |
|---|---:|
| Trades joined to `PRJ_1_atr_history.csv` | 149 / 150 |
| Monthly P&L vs avg monthly ATR20 corr | -0.383 |
| Per-trade P&L vs day ATR20 corr | -0.136 |
| January 2026 avg ATR20 rank | 11 of 18 |
| January 2026 avg ATR20 | 271.75 |

ATR bucket result:

| ATR bucket | n | P&L | Avg ATR20 | PF | Win rate | Expectancy |
|---|---:|---:|---:|---:|---:|---:|
| Low | 50 | +$537.00 | 230.29 | 1.09 | 36.0% | +$10.74 |
| Mid | 49 | +$3,849.60 | 290.75 | 1.81 | 49.0% | +$78.56 |
| High | 50 | -$172.50 | 420.50 | 0.97 | 34.0% | -$3.45 |

One trade did not join to ATR history: 2024-10-14, long full-stop,
-$189.60. This does not change the read.

Decision: **do not build the volatility-normalized bracket as the next
step**. The concentration is not primarily explained by high ATR. The
next investigation should inspect direction, calendar/month state, or
entry-state composition. A volatility-normalized bracket may still be a
future structural variant, but the pre-committed Step 0 gate did not
justify it as the immediate fix.

## 8. Direction / ATR / Time Attribution

Run date: 2026-06-21.

Artifacts:

- `nb_lib/scripts/first_hour_momentum_acceptance_attribution_decomposition.py`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_attribution_decomposition_report.md`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_attribution_decomposition.json`

Purpose: characterize the existing 150-trade book across fixed axes
without adding filters or changing the bracket.

Direction:

| Direction | n | P&L | PF | Win rate | Expectancy |
|---|---:|---:|---:|---:|---:|
| Long | 87 | +$1,024.80 | 1.10 | 36.8% | +$11.78 |
| Short | 63 | +$2,999.70 | 1.45 | 42.9% | +$47.61 |

ATR regime:

| ATR | n | P&L | PF | Win rate | Expectancy |
|---|---:|---:|---:|---:|---:|
| Low | 50 | +$537.00 | 1.09 | 36.0% | +$10.74 |
| Mid | 49 | +$3,849.60 | 1.81 | 49.0% | +$78.56 |
| High | 50 | -$172.50 | 0.97 | 34.0% | -$3.45 |

Direction x ATR:

| Cell | n | P&L | PF | Win rate | Small-n note |
|---|---:|---:|---:|---:|---|
| Long x high | 29 | -$570.90 | 0.85 | 31.0% | borderline |
| Long x low | 29 | -$570.90 | 0.85 | 31.0% | borderline |
| Long x mid | 28 | +$2,356.20 | 1.89 | 50.0% | borderline |
| Short x high | 21 | +$398.40 | 1.16 | 38.1% | small |
| Short x low | 21 | +$1,107.90 | 1.52 | 42.9% | small |
| Short x mid | 21 | +$1,493.40 | 1.72 | 47.6% | small |

Cell concentration:

- Positive direction x ATR cells: 4.
- Positive-cell HHI adjusted: 0.093.
- Top positive cell: long x mid ATR, +$2,356.20, n=28, PF 1.89.
- Top cell share of total net P&L: 55.9%.
- Top cell share of positive gross cell P&L: 44.0%.

Leading hypothesis check:

| Slice | n | P&L | PF | Win rate | Expectancy |
|---|---:|---:|---:|---:|---:|
| Short x low+mid ATR | 42 | +$2,601.30 | 1.62 | 45.2% | +$61.94 |
| Everything else | 108 | +$1,423.20 | 1.11 | 37.0% | +$13.18 |
| Long standalone | 87 | +$1,024.80 | 1.10 | 36.8% | +$11.78 |
| High ATR all directions | 50 | -$172.50 | 0.97 | 34.0% | -$3.45 |

Verdict: **A_WEAK_COHERENT_HYPOTHESIS_NEEDS_CAUTION**. There is some
shape: high ATR is weak/dead, shorts are stronger than longs, and short
x low+mid ATR is materially better than the rest. But the top single
cell is actually long x mid ATR, and every direction x ATR cell is at or
below the 25-30 trade reliability threshold. This is attribution, not
permission to add a filter. Do not promote a filtered variant from this
alone.

## 9. Minimum Track Record Length / Power Analysis

Run date: 2026-06-21.

Artifacts:

- `nb_lib/scripts/first_hour_momentum_acceptance_mintrl_power.py`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_mintrl_power_report.md`
- `nb_lib/probe_results/first_hour_momentum_acceptance_base_hit_mintrl_power.json`

Purpose: stop slicing and quantify the sample gap using the Compass
formula-menu MinTRL / PSR framework. Confidence = 95%, benchmark
Sharpe SR* = 0.0. Uses skew/kurtosis-adjusted MinTRL.

| Slice | n | Mean/trade | Std | Sharpe | Skew | Kurtosis | MinTRL |
|---|---:|---:|---:|---:|---:|---:|---:|
| Full | 150 | +$26.83 | $267.80 | 0.100 | 0.431 | 1.191 | 260 |
| Ex-Jan-2026 | 138 | +$13.91 | $264.69 | 0.053 | 0.534 | 1.291 | 954 |
| Mid ATR | 49 | +$78.56 | $276.53 | 0.284 | 0.041 | 1.002 | 35 |
| High ATR positive-edge test | 50 | -$3.45 | $261.99 | -0.013 | 0.676 | 1.456 | inf |
| High ATR negative-edge context | 50 | +$3.45 | $261.99 | 0.013 | -0.676 | 1.456 | 15,743 |

Verdict: **B_SEVERELY_UNDERPOWERED**. The full sample would need about
260 trades at the observed effect size, but the conservative
ex-January read needs about 954 trades. Since January concentration is
the core concern, the ex-January MinTRL is the decision-relevant number.

Implication: treat this as a sample-size problem, not a filter-design
problem. More slicing or gating will manufacture small cells; it will
not establish the edge. Do not spend OOS on this candidate. Either
collect much more same-spec data, or shelve until a stronger entry
substrate appears.

Carry-forward hypothesis, not promotion: the mid-ATR concentration may
be retested on a future data tranche as a pre-registered hypothesis.
The accounting must explicitly deflate for the search that found it:
month, direction, ATR regime, and the direction x ATR cell grid were
all inspected. Do not convert mid-ATR into a live entry filter from the
current 150-trade sample.

## 10. Targetability Overlay Audit

Run date: 2026-06-22.

Artifacts:

- `nb_lib/scripts/first_hour_momentum_acceptance_targetability_overlay.py`
- `nb_lib/probe_results/first_hour_momentum_acceptance_targetability_overlay_report.md`
- `nb_lib/probe_results/first_hour_momentum_acceptance_targetability_overlay.json`
- `nb_lib/probe_results/first_hour_momentum_acceptance_targetability_overlay_packets.csv`
- `nb_lib/probe_results/first_hour_momentum_acceptance_targetability_overlay_allowed_trades.csv`

This was an overlay audit only. It reused the existing 150 in-sample
trades and their realized P&L. It did not recompute fills, change the
entry set, alter exits, or touch OOS.

Locked overlay:

- Gate timestamp: original entry timestamp, next 1-second open after
  10:30 ET.
- Structural invalidation: source trade stop price.
- Target choice: nearest qualifying objective target known at/before
  entry.
- Pass condition: net R >= 1.5 and target distance <=
  `min(2.0 x ATR14_1m, 0.75 x remaining range estimate)`.

Result:

| Variant | n | Avg/mo | P&L | PF | Win rate | Mean/trade | Max DD |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline source | 150 | 8.3 | +$4,024.50 | 1.235 | 39.3% | +$26.83 | $2,867.40 |
| Targetability allowed | 12 | 0.7 | -$85.20 | 0.944 | 33.3% | -$7.10 | $1,137.60 |

Targetability attribution:

| no_target_reason | n |
|---|---:|
| `missing_remaining_range` | 6 |
| `risk_reward_too_low` | 131 |
| `volatility_reach_too_low` | 1 |
| `none` / allowed | 12 |

Decision: **do not promote the targetability overlay** for this
candidate. The gate cut an already-underpowered survivor from 150 trades
to 12 trades and the allowed subset was negative. Read this as evidence
that the current v1 targetability rule is too restrictive for this
opening-momentum substrate, not as a reason to tune the R:R threshold or
target hierarchy. OOS remains sealed.

Snapshot review addendum (2026-06-22): five 5m quicklook images were
generated under
`nb_lib/probe_results/first_hour_targetability_snapshots_20260622/`
to inspect three recent blocked trades and two allowed trades. The
blocked examples were illuminating rather than contradictory: the gate
was doing exactly its intended hygiene job. In the most obvious case,
2026-01-27 entered long at 26042.25 while the nearest objective target
was the overnight high at 26043.50, only 1.25 points away against a
30-point source stop. That is a no-destination trade, and
`risk_reward_too_low` was the correct veto.

The allowed examples identify the real failure mode. Once room existed,
one allowed short won and one allowed short lost, matching the summary
statistics rather than revealing a hidden rescue. Therefore the banked
lesson is sharper than "the gate failed": targetability is a structural
hygiene filter, not an edge source. It can remove trades with no
objective destination, but it cannot create directional edge for an
entry family that is already weak, underpowered, or near-random.

Future use: apply targetability first to entry mechanisms where the
target is intrinsic to the thesis, such as opening-range or prior-day
level response toward the next objective level with invalidation at the
level just respected. Do not continue applying it as an aftermarket
rescue overlay on first-hour momentum.
