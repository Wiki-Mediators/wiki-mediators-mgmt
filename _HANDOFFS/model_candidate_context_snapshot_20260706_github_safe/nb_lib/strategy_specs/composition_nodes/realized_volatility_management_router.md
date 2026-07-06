---
name: "Realized Volatility Management Router"
tagline: "Condition stop, target, breakeven, trail, and sizing behavior on causal realized-volatility regime."
status: "note-only"
created: 2026-05-25
updated: 2026-05-25
source: "Operator direction 2026-05-25; formalized from discussion on regime-gated management, small-data HMM limits, and reusable management infrastructure."
node_type: "management-router"
markets: ["MNQ", "NQ"]
timeframes_used: ["1-second source", "1-minute", "5-minute", "session"]
consumes:
  - "realized volatility percentile"
  - "ATR percentile"
  - "volatility expansion ratio"
  - "trade MFE/MAE/unrealized R"
  - "optional directional context"
emits:
  - "current_vol_regime"
  - "management_mode"
  - "size_multiplier"
  - "breakeven policy"
  - "trail policy"
  - "target policy"
validation: "overlay-experiment"
implementation: null
related_methodology:
  - "../_REGIME_CONDITIONED_MANAGEMENT_WORKFLOW.md"
  - "../_MANAGEMENT_OBSERVER_MEMORY_LAYER.md"
  - "../_METHODOLOGY_INTUITION.md"
tags:
  - composition-node
  - management-router
  - realized-volatility
  - causal
  - overlay-validation
  - hmm-deferred
---

# Realized Volatility Management Router

## 1. Thesis

H4 (2026-05-25) tested whether the strategy graveyard contained obvious
regime-conditional entry survivors and found a clean negative: 121
candidate/regime cells examined, 0 passed both discovery and holdout
partitions, and 1 discovery-only ghost versus roughly 6 expected chance
passes. This node is therefore not framed as a likely way to resurrect
closed entries.

The management axis remains open. A strategy can fail unconditionally
because its open risk is expressed poorly under certain trade and
volatility states: too tight in high-volatility trend, too loose in
low-volatility chop, too eager to move to breakeven, or too dependent on
runners during hostile variance.

This node classifies trade state and current volatility regime using
causal inputs, then emits management-policy guidance for strategies that
already have a position or a pending trade. Trade state is the primary
management driver; realized-volatility regime is the primary market-state
modifier; directional context is secondary.

It is not an entry signal. It does not predict direction. Its purpose is
to condition risk expression.

## 2. What This Node Is

This is a composition node and management router. It consumes market-state
features and trade-state features, then emits management settings:

- whether to allow an early breakeven move
- whether to delay breakeven
- whether structure trailing is allowed
- whether runner behavior is disabled
- whether size should be reduced
- whether current volatility is hostile enough to de-risk faster

Entry strategies remain responsible for entries. This node only changes
how open risk is managed.

In the broader management architecture, this router is only the market
context layer. The companion observer/memory layer
(`../_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`) owns trade-path diagnosis,
falsifiable predictions, counterfactual scoring, and the memory store.

## 3. What This Node Is Not

This node is not:

- a standalone alpha
- a daily directional forecast
- a replacement for entry strategy logic
- an HMM in v1
- a Markov transition model in v1
- a permission slip for post-hoc regime slicing

If this node is ever used as an entry gate, that must be authored and
validated separately.

## 4. Causal Inputs

Potential inputs:

| Input | Notes |
|---|---|
| trailing realized-volatility percentile | primary v1 input |
| ATR percentile | slower context |
| 1-minute / 5-minute realized range | local volatility |
| volatility expansion ratio | current range vs trailing range |
| session range percentile | session-level state |
| time of day | open/midday/late-session differences |
| VWAP slope / EMA slope | optional secondary direction context |
| MFE / MAE / unrealized R | trade-state input |

All inputs must be computed from completed bars or current replay state
available at the decision timestamp.

Trust/weight should follow independent-observation count and persistence.
Trade state is closest to the decision and has the most observations;
realized volatility is more persistent and trustworthy than direction;
longer-horizon weekly/monthly regimes should receive little weight until
years of data accumulate.

## 5. Regime States

v1 should start with:

```text
low_vol
normal_vol
high_vol
```

Later versions may split high volatility into:

```text
high_vol_directional
high_vol_disorderly
```

Do not add state count until overlay experiments prove the simple states
are useful.

## 6. Output Contract

```yaml
node_id: realized_volatility_management_router
timestamp: datetime
lookahead_clean: bool

outputs:
  current_vol_regime: low_vol | normal_vol | high_vol
  vol_percentile: float
  vol_expansion_ratio: float
  directional_context: bullish | bearish | neutral | unknown
  management_mode: de_risk | default | allow_breathing_room
  size_multiplier: float
  allow_breakeven_move: bool
  breakeven_trigger_r: float
  trail_mode: none | fixed | structure | atr
  stop_tightening_permission: bool
  target_style: base_hit | vwap | structure | runner_disabled
  risk_warning: none | elevated | hostile
```

The output contract is the durable interface. Future strategy code,
replay UI, and overlay experiments should consume this structure rather
than reading internal classifier details.

## 7. Candidate Policy Map

Initial policy hypotheses:

| Regime | Management posture to test |
|---|---|
| low_vol | earlier BE, tighter stop, smaller target acceptable |
| normal_vol | strategy default |
| high_vol | reduced size, delayed BE, wider breathing room |
| high_vol_directional | structure trail allowed, runner maybe allowed |
| high_vol_disorderly | no runner, faster de-risk, stricter daily cap |

These are hypotheses. They are not validated rules.

## 8. HMM / Markov Deferred

HMM and Markov transition modeling are explicitly deferred.

Reason:

- Two years of MNQ gives too few regime transitions.
- EM-fitted HMMs can overfit while looking mathematically polished.
- Published transition matrices should not be transplanted across
  instrument, timeframe, horizon, or sample period.
- Volatility regime detection is the robust part; directional transition
  prediction is weaker.

Future work may test direct transition counting on threshold-defined
states after this simple realized-volatility node shows overlay value.

## 9. Validation Plan

Validation is overlay-based:

1. Take existing historical strategy trades.
2. Tag each trade with this node's causal regime at entry and during
   management evaluation.
3. Compare baseline management against regime-conditioned policy.
4. Use discovery / in-sample-holdout separation for policy search.
5. Inherit H4 guards: pre-commit the believe-it bar before looking,
   require pass in both partitions, and treat discovery-only wins as
   ghosts.
6. Track trial count if multiple policies, regimes, and candidate trade
   sets are explored. A single improved cell is not evidence; clustering
   across related policies or strategy families is the signal.
7. Compare observed pass counts against chance expectation.
8. Do not touch sealed OOS until a pre-committed overlay earns it.

Useful first reports:

- PF by volatility regime
- loss-cluster rate by regime
- runner value by regime
- BE move value by regime
- stop tightening value by regime
- strategy-by-regime conditional survival table

## 10. Replay Integration

The MNQ replay viewer should eventually display the node state during
manual or strategy replay:

```text
Regime: high_vol_directional
Management mode: allow_breathing_room
MFE: 0.8R
MAE: 0.3R
Recommendation: hold, no BE yet
```

This makes the router inspectable. A management node that cannot be
visually audited during replay is too easy to fool ourselves with.

## 11. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-25 | note-only | Authored as the first concrete management-router node. Uses causal realized-volatility classification as primary regime input. HMM/Markov transition modeling explicitly deferred. Awaiting overlay-attribution design and implementation. |
