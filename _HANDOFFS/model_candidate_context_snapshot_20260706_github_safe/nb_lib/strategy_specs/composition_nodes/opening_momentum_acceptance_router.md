---
node_id: "opening_momentum_acceptance_router"
name: "Opening Momentum Acceptance Router"
tagline: "Classify whether early RTH momentum is being accepted or rejected, then use that state to gate or manage existing trade producers."
status: "implemented-untested"
created: 2026-06-02
updated: 2026-06-02
source: "Momentum-candidate inventory review after OR rejection router creation; G2/v2a bridge-substrate framing."
node_type: "session-state-router / direction-gate / management-context"
markets: ["MNQ"]
timeframe: "RTH intraday"
consumes:
  - "09:30-10:00 first-half-hour return"
  - "09:30-10:30 first-hour range expansion"
  - "opening-range break acceptance/rejection state"
  - "RTH VWAP location and slope"
  - "2-minute EMA/VWAP alignment"
  - "realized volatility / ATR regime"
  - "current bridge-substrate trades (G2 3c, v2a 15c)"
emits:
  - "momentum_state"
  - "long_permission"
  - "short_permission"
  - "size_multiplier"
  - "management_context"
implementation: "../../scripts/overlay_opening_momentum_acceptance_router.py"
validation: "overlay-experiment"
related_artifacts:
  - "../candidates/intraday_momentum_continuation_base_hit.md"
  - "../candidates/first_hour_range_expansion_breakout.md"
  - "../candidates/mnq_news_like_impulse_pullback.md"
  - "../candidates/momentum_high_water_trail_post_1030.md"
  - "opening_range_rejection_state_router.md"
  - "../../../nb_lib_g2_v2a_multistart_report.md"
tags:
  - composition-node
  - momentum
  - opening-range
  - acceptance
  - state-gate
  - overlay-validation
  - not-a-strategy
---

# Opening Momentum Acceptance Router

## 1. Why This Node Exists

The momentum inventory is mixed if read as standalone entry-strategy
evidence:

- `G2 3c` is the strongest live bridge-substrate producer and is
  momentum-like in practice.
- `intraday_momentum_continuation_base_hit` has a coherent external
  thesis but only inconclusive local diagnostic evidence so far.
- `first_hour_range_expansion_breakout` was closed because the 1.5x ATR
  expansion gate made it too sparse.
- `news_first_pullback_momentum` was equities-specific and not directly
  portable to MNQ.
- `mnq_news_like_impulse_pullback` and `momentum_high_water_trail_post_1030`
  remain untested ideas with real predicate-sparseness risk.

That argues against building another raw momentum entry first. The
better use of the momentum family is as a state layer over the current
bridge substrate: identify when early RTH momentum is being accepted,
when it is being rejected, and whether that state improves existing G2 /
v2a trades as a gate, size scaler, or management context.

## 2. What This Node Is

This is a composition node, not an entry strategy. It emits a causal
opening-momentum state label using information available at the decision
timestamp.

Possible v1 labels:

```text
no_momentum
bullish_acceptance
bearish_acceptance
bullish_failed_momentum
bearish_failed_momentum
range_expansion_without_acceptance
high_vol_chop
```

The core distinction is acceptance versus rejection:

- Acceptance means the early move breaks or extends from the opening
  range and then remains structurally supported by VWAP / EMA alignment
  and completed-bar continuation.
- Rejection means the early move expands but cannot hold outside the
  opening structure or quickly returns into the range.

This pairs with `opening_range_rejection_state_router`: that node asks
"did the opening break fail?", while this node asks "did momentum get
accepted enough to trust continuation exposure?"

## 3. What This Node Is Not

This node is not:

- a resurrection of closed momentum candidates;
- a new standalone entry strategy;
- permission to consume sealed OOS;
- a parameter search over first-hour thresholds;
- a substitute for counterfactual management scoring.

It earns value only by improving an existing trade producer under
day-level discovery/holdout discipline.

## 4. Candidate Output Contract

```yaml
node_id: opening_momentum_acceptance_router
timestamp: datetime
lookahead_clean: true

inputs:
  rth_open: float
  price_1000: float | null
  price_1030: float | null
  first_30m_return: float
  first_hour_range_points: float
  first_hour_range_vs_atr: float
  or_state: string
  vwap_position: above | below | mixed
  vwap_slope: up | down | flat
  ema_alignment: bullish | bearish | mixed
  realized_vol_regime: low | normal | high

outputs:
  momentum_state: no_momentum | bullish_acceptance | bearish_acceptance |
                  bullish_failed_momentum | bearish_failed_momentum |
                  range_expansion_without_acceptance | high_vol_chop
  long_permission: allow | reduce | block
  short_permission: allow | reduce | block
  size_multiplier: float
  management_context: neutral | continuation_acceptance |
                      failed_momentum | high_vol_chop
```

Lookahead discipline: every field must be computed from completed bars
only. A 10:00 state can use the completed first 30 minutes but not later
bars. A 10:30 state can use completed bars through 10:30 but not the
subsequent path. Overlay scoring must partition by day, not by trade row
or checkpoint row.

## 5. First Overlay Experiment

Start with the current bridge substrate:

```text
G2 canonical alpha at 3 contracts
Savor-Wilson v2a canonical alpha at 15 contracts
combined G2 3c + v2a 15c
```

Pre-committed question:

```text
Does opening-momentum acceptance state improve the current bridge
substrate as a gate, size reducer, or management context without
degrading both discovery and holdout partitions?
```

Suggested v1 policy map to test:

| Momentum state | Hypothesis |
|---|---|
| bullish_acceptance | Permit or default-size long-biased continuation exposure |
| bearish_acceptance | Reduce long-biased continuation exposure unless the substrate has an independent long catalyst |
| bullish_failed_momentum | Reduce or block long continuation; consider tighter management |
| bearish_failed_momentum | Long continuation may improve if the failure is a downside trap; test only as label first |
| high_vol_chop | Reduce size or require stronger substrate confirmation |
| no_momentum | Default baseline unless evidence says otherwise |

The first run should be a read-only overlay: tag existing G2/v2a trades,
compare baseline versus state-conditioned variants, and report whether
the node improves PF, drawdown, pass rate, and loss clustering. Do not
retune thresholds after seeing P&L.

## 6. Momentum Candidates: Current Read

Momentum is not dead, but the useful interpretation is narrow:

- The fleet already has a practical momentum producer in `G2 3c`.
- Pure first-hour expansion was too sparse when over-filtered.
- News-like impulse pullback may still deserve a Stage 0 frequency probe
  later, but it is a separate entry-research branch.
- The next high-leverage use of momentum is as context over the existing
  bridge substrate, especially when paired with opening-range rejection
  state.

This node preserves that conclusion so the project does not keep
rebuilding standalone momentum entries when the immediate opportunity is
to ask whether momentum state improves trades already being produced.

## 7. Implementation Note

Implementation scaffold added 2026-06-02:

```text
nb_lib/scripts/overlay_opening_momentum_acceptance_router.py
```

The script is a read-only overlay against existing bridge trade logs:

```text
codex_tmp/g2_nb_lib_redo_20260527_trades.csv
codex_tmp/v2a_nb_lib_redo_20260527_trades.csv
```

It computes opening-momentum state from completed 1-second DBN bars
through 10:30 ET, tags G2/v2a/combined trades, and compares fixed
policies:

```text
baseline_all
bullish_acceptance_only
block_bearish_acceptance
block_failed_momentum
block_bearish_or_failed
```

First run attempt from the Codex desktop bundled Python did not score
because that runtime lacks the real `databento` package required by
`nb_lib.data.load_mnq_1s`. No data was downloaded. The test remains
ready to run in an environment where the existing nb_lib strategies can
decode the local DBN store.
