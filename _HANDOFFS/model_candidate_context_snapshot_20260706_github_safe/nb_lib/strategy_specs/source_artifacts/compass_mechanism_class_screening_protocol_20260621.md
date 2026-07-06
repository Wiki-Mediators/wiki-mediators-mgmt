# Mechanism-Class Screening Protocol For Intraday Futures Strategies

Source status: operator-provided Compass artifact, banked 2026-06-21.
This is source material and methodology guidance, not a local validation
result. The executable local implementation begins at `nb_lib/screening.py`.

## Purpose

Before spending a full build on a new intraday futures strategy, run a
cheap proxy-trade screen across five axes:

1. Skew / concentration.
2. Cost-distance.
3. Frequency-power.
4. Regime-concentration.
5. Cross-correlation against existing sleeves.

The goal is to reject mechanism classes that are structurally unlikely
to become deployable in MNQ before they consume build time or trial
budget.

## Report Card

| Axis | Metric | Green | Yellow | Red |
|---|---|---|---|---|
| Skew / concentration | skew-adjusted MinTRL vs achievable n; best-trade share | MinTRL <= 0.5*n and max trade < 5% | MinTRL <= n or max trade 5-15% | MinTRL > n or max trade > 15% |
| Cost-distance | round-trip cost / expected gross move | <= 1/3 | 1/3 to 1/2 | > 1/2 |
| Frequency-power | achievable n and t = SR * sqrt(n) | t >= 3.0 | 2.0 <= t < 3.0 | t < 2.0 |
| Regime-concentration | conditional edge, P&L HHI, period dominance | HHI < 2/K and max day < 25% | HHI 2/K to 3/K or max day 25-50% | HHI > 3/K or max day > 50% |
| Cross-correlation | signal / P&L correlation, trade-day overlap | < 0.3 | 0.3 to 0.6 | > 0.6 |

Decision rule:

- Any RED on axes 1-3 means **do not build**.
- Any RED on axes 4-5 means **caution only**: not standalone, not a
  claimed diversifier.
- All green/yellow with at most one yellow means **build**.

## Core Formula

Use Bailey-Lopez de Prado style skew/kurtosis adjusted Minimum Track
Record Length:

```text
MinTRL = 1
       + [1 + 0.5*SR^2 - skew*SR + ((kurtosis - 3)/4)*SR^2]
         * (z_confidence / (SR - SR_benchmark))^2
```

Kurtosis is non-excess. If observed SR does not exceed the benchmark,
MinTRL is infinite for positive-edge proof.

## Case-Study Calibration

The screen is calibrated against three recent local failures:

- First-hour momentum acceptance: roughly 150 trades in hand versus
  roughly 954 MinTRL in the decision-relevant ex-January read. Fails
  Frequency-Power and monthly concentration.
- Tight / micro scalp style failures: expected move too close to MNQ
  friction. Fails Cost-Distance under the Carver one-third speed limit.
- Noise-area intraday momentum: pre-registered 90d/VM1.5 confirmation
  was net positive but single-day share was 109.5% of net profit.
  Fails Skew/Concentration and Regime-Concentration.

## Project Interpretation

This protocol shifts candidate generation from "build a plausible idea
and see" to "screen the mechanism class first." A candidate can be
interesting and still fail the pre-build screen if the sample size,
payoff skew, friction ratio, or concentration profile makes it
statistically non-deployable on MNQ.

The screen does not validate a strategy. It decides whether a strategy
deserves a full build.

## Implementation Pointer

Local executable helpers:

- `nb_lib/screening.py`
- `nb_lib/tests/test_screening.py`

Use `screen_proxy_trades()` when a cheap proxy trade list is available.
For source strategies that do not yet have exits, build the cheapest
mechanism-consistent proxy list first, then run the report card before
full execution simulation.
