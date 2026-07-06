# Regime-Conditioned Management Workflow

**Status**: methodology-note  
**Created**: 2026-05-25  
**Scope**: reusable management architecture, not an entry strategy  

## 1. Why This Exists

The project has repeatedly found plausible MNQ entry ideas that fail as
standalone strategies. H4 (2026-05-25) tested the optimistic version of
the regime-resurrection idea on the entry axis and found a clean negative:
121 candidate/regime cells examined, 0 cells passed both discovery and
holdout partitions, and 1 discovery-only ghost versus roughly 6 expected
chance passes. The strategy graveyard did not contain obvious
regime-conditional entry survivors.

This workflow therefore does not assume closed candidates are waiting to
be resurrected by a regime label. It treats management as a different
axis: not "which entries should have been taken," but "given risk is
already open, should stops, targets, breakeven, trails, size, and
de-risking behave differently under the current market and trade state?"

This workflow formalizes the next layer of research: build reusable
management nodes that condition stop behavior, targets, breakeven timing,
trailing, sizing, and de-risking on causal market state.

The goal is not to predict direction. The goal is to manage open trades
more intelligently once a separate entry strategy has created risk.

The active pivot artifact for this work is
`_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`. The regime router supplies market
context; the observer/memory layer supplies trade-path diagnosis,
falsifiable predictions, and counterfactual replay scoring.

## 2. Core Distinction

Entry strategies answer:

```text
Should we enter long, enter short, or stay flat?
```

Management nodes answer:

```text
Given an existing or proposed trade, how should risk be managed now?
```

This distinction is mandatory. A management node is not allowed to become
a disguised entry strategy unless it is explicitly re-authored as a
candidate under the normal candidate pipeline.

## 3. Primary Hypothesis

The current working hypothesis is:

```text
Trade state is the primary management driver. Realized-volatility regime
is the primary market-state modifier. Directional pressure is secondary.
```

Reasoning:

- Two years of MNQ data is too thin for robust HMM transition estimation.
- Published index-regime work consistently finds persistent volatility
  regimes, but directional transition probabilities are less portable.
- An input's trust should scale with its independent-observation count
  and persistence. Trade-state observations are most local and numerous;
  volatility earns more weight than direction; weekly/monthly regimes
  earn little weight until years of data accumulate.
- Prior project failures often look like risk-expression failures:
  loss clusters, runner variance, stop geometry, and Apex trailing-DD
  sensitivity.
- The best surviving evidence so far favors base-hit / variance-control
  execution over open-ended runner structures.

## 4. v1 Design Principle

Start with a simple causal realized-volatility classifier.

Do not start with:

- EM-fitted Hidden Markov Models
- borrowed transition matrices from outside papers
- future-aware regime labels
- post-hoc P&L slicing presented as a deployable gate

The v1 classifier should use only information available before or at the
management decision timestamp.

## 5. Inputs

Candidate causal inputs:

| Input | Purpose |
|---|---|
| trailing realized volatility percentile | primary volatility state |
| ATR percentile | slower volatility context |
| 1-minute / 5-minute realized range | current local movement |
| volatility expansion ratio | detects sudden regime change |
| session range percentile | identifies large-range sessions |
| current bar range vs recent range | detects local disorder |
| time of day | separates open, midday, late session |
| VWAP slope / EMA slope | secondary directional context |
| opening range position | session structure context |
| trade MFE / MAE / unrealized R | trade-specific state |

The first implementation should use the smallest useful subset. Extra
inputs are not free; they create more states and more ways to overfit.
Trust/weight should follow observation count and persistence, not how
interesting the input sounds.

## 6. Regime States

Start with three states:

```text
low_vol
normal_vol
high_vol
```

Potential later split:

```text
high_vol_directional
high_vol_disorderly
```

Do not introduce many states until overlay experiments show that the
simple states are useful. The purpose is management clarity, not model
sophistication.

## 7. Output Contract

Every management node must publish a structured output contract. A
realized-volatility management router should emit fields like:

```yaml
node_id: realized_volatility_management_router
timestamp: <decision timestamp>
lookahead_clean: true

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

Strategies may consume these outputs, but the node itself does not place
trades.

## 8. Example Management Policies

These are research hypotheses, not deployed rules.

| Regime | Possible management posture |
|---|---|
| low_vol | tighter stops, earlier BE, smaller fixed targets acceptable |
| normal_vol | default strategy management |
| high_vol_directional | delayed BE, wider breathing room, structure trail allowed |
| high_vol_disorderly | reduced size, faster de-risk, no runner, stricter daily stop |

The project should test policies as overlays against existing strategies
before adopting them. A policy that sounds sensible but worsens baseline
results is rejected.

## 9. Validation Workflow

Management nodes are validated by overlay experiment, not standalone P&L.

1. Select existing strategies with historical trade logs.
2. Reconstruct each trade with causal state at entry and at management
   evaluation timestamps.
3. Tag each trade with volatility regime and trade-state metrics.
4. Compare baseline management against node-conditioned management.
5. Use discovery / in-sample-holdout separation when searching policies.
6. Inherit the H4 guardrails: write the believe-it bar before looking,
   require a candidate policy to pass both partitions, and treat
   discovery-only wins as ghosts.
7. Track trial count if many policies, regimes, and candidates are
   explored. A single improved cell is not evidence; clustering across
   related policies or strategy families is the signal.
8. Compare observed pass counts against chance expectation. If ~100
   cells are examined, expect several apparent wins by chance.
9. Keep sealed OOS untouched until a pre-committed overlay earns it.

The first useful report is attribution, not optimization:

```text
strategy_id
baseline_pf
pf_by_vol_regime
loss_cluster_by_vol_regime
runner_value_by_vol_regime
BE_move_value_by_vol_regime
stop_trail_value_by_vol_regime
```

This tells us whether management behavior has regime-conditional value.
It should not be framed as a resurrection hunt unless the evidence
clusters across partitions and related strategies.

For observer-first validation, use the memory-layer workflow in
`_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`: diagnoses emit predictions,
recommendations are scored counterfactually on the actual 1-second path,
and policy control is introduced only after recommendation quality is
validated.

## 10. Relationship To Closed Candidates

Closed candidates should not be automatically resurrected. H4 already
tested entry-axis regime resurrection and found 0/121 cells passing both
partitions. The prior on reviving closed candidates with simple regime
gates should therefore be low.

Closed-candidate trade logs may still be useful as historical evidence
for management attribution, because management is a different axis from
entry selection. Use them to ask whether BE timing, runner behavior,
stop tightening, or de-risking would have behaved differently under
causal trade-state and volatility-state labels.

The question is:

```text
Was this management behavior bad everywhere, or bad only when applied in
the wrong trade/volatility state?
```

If a management policy is positive only in a state that was knowable at
the management decision timestamp, it may become:

- a marginal-registry component
- a branch in a composition node
- a strategy family gated by the management router

If the split is post-hoc, unstable, not causal, or discovery-only, it
remains rejected.

## 11. HMM / Markov Deferred

HMM and Markov transition models are deferred, not discarded.

Reasons:

- Two years of MNQ data has too few independent regime transitions.
- EM-fitted HMMs can look sophisticated while overfitting badly.
- Published transition matrices are instrument-, period-, and horizon-
  specific and should not be transplanted.
- Transition probabilities are non-stationary.

Future exploration may use direct transition counting on threshold-
defined states after the simple realized-volatility classifier proves
useful. HMM comes later, only if the simple node has overlay value and
more data is available.

## 12. Replay / Needle-Drop Integration

The replay front end should eventually make management nodes inspectable.

During replay, a trade could display:

```text
Regime: high_vol_directional
Management mode: allow_breathing_room
MFE: 0.8R
MAE: 0.3R
Recommendation: hold; do not tighten yet
```

This is important. The management system should not become a black box.
The operator should be able to needle-drop into historical trades, watch
the node state evolve, and decide whether the management recommendation
is sensible.

The replay integration target is the full observer case file: trade
state, market state, thesis health, prediction, recommendation, and
counterfactual result. See `_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`.

## 13. Hard Rules

- No future data in regime labels.
- No standalone P&L claims for management nodes.
- No HMM first pass.
- No post-hoc slicing presented as deployable validation.
- H4 guards required for overlay searches: pre-commit believe-it bar,
  pass both discovery and holdout, track trial count, and distrust
  isolated green cells.
- No direction prediction claims unless separately validated.
- No OOS usage until a pre-committed overlay experiment earns it.

## 14. Current Concrete Node

The first concrete node in this workflow is:

`composition_nodes/realized_volatility_management_router.md`

It is note-only and unimplemented. It exists to preserve the design
intent and output contract for future local-agent work.
