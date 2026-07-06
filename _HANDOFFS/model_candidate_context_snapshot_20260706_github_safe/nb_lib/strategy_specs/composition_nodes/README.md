# Composition Nodes

This directory holds **composition nodes** -- artifacts that are NOT
entry strategies by themselves. They are conditioning layers that gate,
size, route, or contextualize the entry strategies in `../candidates/`.

For the project-level intuition behind why nodes are separate from entry
strategies, read `../_METHODOLOGY_INTUITION.md`.

## Why this category exists

The project's strategy pipeline (`../candidates/` -> Phase 0 -> Phase 1 ->
variance preflight -> FINAL spec -> implementation -> test) is built for
ENTRY strategies: things that produce trades. But the long-term
composition vision (see
`../candidates/_MARGINAL_STRATEGIES_REGISTRY.md`) requires a different
KIND of artifact -- layers that don't trade themselves but change how
the entry strategies behave.

Forcing these into the candidate wiki would corrupt both: a regime
filter has no entry, no stop, no per-trade P&L, so it fails every
candidate gate trivially while not being a failure at all. It's a
different object. This directory keeps it separate.

## What is a composition node

A composition node is any of:

| Node type | What it does |
|---|---|
| Regime filter | Classifies higher-timeframe market state (bull/bear/sideways, trending/rotational) |
| Direction gate | Permits/blocks long or short based on context |
| Volatility regime label | Tags the session's volatility state for bracket scaling |
| Session classifier | Labels the session type (trend day, range day, etc.) |
| Confidence scaler | Outputs a size multiplier based on signal confluence |
| Strategy router | Decides which strategy family is active under current conditions |

None of these produce trades alone. All of them change how entry
strategies behave when layered on top.

## How nodes differ from candidates

| Aspect | Candidate (entry strategy) | Composition node |
|---|---|---|
| Produces trades? | Yes | No |
| Has entry/stop/target? | Yes | No |
| Tested by | Multistart P&L, Apex survival | Overlay experiment: does it improve existing strategies? |
| Pass criterion | PF, n, account survival | Does layering it improve a baseline strategy's metrics? |
| Lives in | `../candidates/` | `nodes/` (here) |

## Required: output contract

Every node MUST define an explicit output contract -- the structured
signal it emits for consumption by strategies or the future composition
layer. Example (regime router):

```
node_id: <node_name>
timeframe: <daily | session | intraday>
outputs:
  <field>: <type and range>
  ...
lookahead_discipline: <how the node avoids using future data>
```

The lookahead discipline field is mandatory. Many node types (regime
classifiers, transition models) are easy to contaminate with future
data if computed naively. The node must document exactly how it stays
causal (e.g., walk-forward rebuild using only prior days).

## How nodes get validated

NOT by standalone P&L. A node is validated by an OVERLAY EXPERIMENT:

1. Take an existing entry strategy with known baseline results.
2. Apply the node as a gate/filter/scaler.
3. Compare: does the node-conditioned version improve on the baseline?

The question is never "does this node trade profitably" (it doesn't
trade). The question is "does applying this node improve the strategies
it conditions?"

A node that improves multiple unrelated strategy families is more
valuable than one that helps only a single strategy (which may be
overfit coincidence).

## Relationship to the composition vision

These nodes are the building blocks of the eventual probabilistic
node/graph composition system described in the marginal registry. But
building a node here does NOT commit to the full graph. A node earns
its place by demonstrating overlay value on existing strategies first.
The graph comes later, only after several nodes and several
marginal-edge strategies exist with comparable data.

Build the node. Test it as an overlay. Only wire it into composition
once it has demonstrated standalone conditioning value.

For the architecture that governs how these nodes attach to candidate
strategies, read `_CANDIDATE_SUPPORT_STACK.md`. The short version:
composition overlays are gates and context layers, not a rescue mechanism
for failed candidates; overlay contracts must be declared before testing.

## Current nodes

| Node | Status | What it does |
|---|---|---|
| markov_daily_regime_router | note-only (no implementation) | Daily bull/bear/sideways regime + directional bias score |
| realized_volatility_management_router | note-only (no implementation) | Causal realized-volatility regime -> management policy router for stops, BE, trails, targets, and size |
| opening_range_rejection_state_router | note-only (no implementation) | ORWS-derived opening-range failed-break / acceptance state -> gate, size, or management context for existing trade producers |
| opening_momentum_acceptance_router | implemented-untested | First-30m / first-hour momentum acceptance state -> direction gate, size scaler, or management context for G2/v2a bridge trades; script scaffold exists but first run is blocked in Codex desktop runtime by missing DBN reader package |
| intraday_target_invalidation_packet | note-only-pending-liquidity-router-v2 | Pre-entry and in-trade reward geometry packet plus Targetability Gate ("no target, no trade"): next liquidity target, invalidation level, volatility reachability, risk/reward, and management context for existing trade producers; waits for liquidity-router v2 cleanup before implementation |
| liquidity_zone_prior_router | overlay-mixed (descriptive-v2-partial) | Objective OHLCV-derived liquidity-zone labels for observer context. v2 descriptive (2026-06-02): OR_H/OR_L and round_50/round_100 survive the distance-matched control (+16-20pp on rejection-given-sweep, partition-consistent); PDH/PDL retracted as control-bias artifacts; PDC retained as "through-prone" label. First overlay against G2/v2a bridge substrate (2026-06-02): G2 shows DIRECTION-CONSISTENT lower WR for trades near a reject-prone zone (both favor- and against-side) on both partitions, but holdout magnitude collapses below the pre-committed bar; v2a does not replicate. Top verdict: **overlay-mixed** — informative observation on G2, NO control logic earned. Not an entry strategy. |
| mnq_directional_bias_atlas | descriptive_spec_not_implemented | Diagnostic atlas for unconditional and state-conditioned MNQ RTH directional drift. Must decompose overnight beta from intraday drift, report raw and net-of-baseline cell returns, apply Bonferroni/FDR multiple-comparison guards, and read the whole panel rather than selecting the best cell. Not a strategy. |

## Management workflow

For the project-level workflow behind management routers, read
`../_REGIME_CONDITIONED_MANAGEMENT_WORKFLOW.md`.

## Status conventions for nodes

| Status | Meaning |
|---|---|
| note-only | Designed as a note; no implementation yet |
| implemented-untested | Built; overlay experiment not yet run |
| overlay-validated | Demonstrated improvement on >= 1 strategy family |
| overlay-rejected | Did not improve (or hurt) the strategies it conditioned |
| graph-wired | Integrated into the composition layer (future) |
