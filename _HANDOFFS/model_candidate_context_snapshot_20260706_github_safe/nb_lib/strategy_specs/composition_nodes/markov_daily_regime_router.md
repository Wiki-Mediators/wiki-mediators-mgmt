---
node_id: "markov_daily_regime_router"
name: "Markov Daily Regime Router"
tagline: "Daily bull/bear/sideways regime classifier that gates and sizes intraday strategies. Not an entry strategy."
status: "note-only"
created: 2026-05-20
updated: 2026-05-20
source: "Operator-provided transcript synthesis 2026-05-20: Markov regime transition model. Framed as a composition node (regime router), not an entry strategy, per operator direction."
node_type: "regime-filter / direction-gate"
timeframe: "daily"
consumes: ["MNQ daily close-to-close returns"]
emits: ["current_state", "p_bull_next", "p_bear_next", "p_sideways_next", "markov_signal", "long_permission", "short_permission", "confidence"]
implementation: null
validation_status: "not-yet-overlaid"
tags:
  - composition-node
  - regime-filter
  - direction-gate
  - daily-timeframe
  - walk-forward-required
  - higher-timeframe-context
---

# Markov Daily Regime Router

## 1. What this node is
A higher-timeframe daily regime classifier. It labels each day as bull,
bear, or sideways based on rolling return, builds a transition matrix
from historical state sequences, and uses today's state to estimate
tomorrow's state probabilities. From those it emits a directional bias
score and permission signals.

It is NOT an entry strategy. It produces no trades, no stops, no
targets. It is a conditioning layer that gates or sizes the intraday
entry strategies in `../candidates/`.

The core idea: the failure pattern this session (wide-state reversal
fading trend regardless of higher-timeframe direction, losing -$14K to
-$18K) suggests intraday strategies may benefit from a daily directional
context. A reversal short into a strongly bullish daily regime is a
different bet than the same short into a bearish daily regime. This node
provides that context.

## 2. Output contract
```
node_id: markov_daily_regime_router
timeframe: daily
outputs:
  current_state:     bull | bear | sideways
  p_bull_next:       float [0,1]   # P(tomorrow bull | today state)
  p_bear_next:       float [0,1]   # P(tomorrow bear | today state)
  p_sideways_next:   float [0,1]   # P(tomorrow sideways | today state)
  markov_signal:     float [-1,1]  # p_bull_next - p_bear_next
  long_permission:   allow | reduce | block
  short_permission:  allow | reduce | block
  confidence:        low | medium | high
```

Permission mapping (pre-committed defaults, tunable at implementation):
- markov_signal >= +0.15  -> long_permission=allow,  short_permission=reduce
- markov_signal <= -0.15  -> long_permission=reduce, short_permission=allow
- abs(markov_signal) < 0.15 -> both=allow (sideways; no strong bias)
- Strong bias (abs >= 0.35) -> opposing side = block, confidence=high

## 3. State definition
```
lookback_days: 20
bull_threshold:  rolling_20d_return >= +0.05
bear_threshold:  rolling_20d_return <= -0.05
sideways:        otherwise
```

These thresholds (5% / -5% over 20 days) are from the source transcript
and are ARBITRARY. They must be treated as pre-committed-but-unvalidated
parameters, not optimized values. Alternative lookbacks [10, 20, 40] and
thresholds [0.03, 0.05, 0.08] are candidate sensitivities to test, but
only pre-committed, not tuned to overlay results.

## 4. Transition matrix
A 3x3 grid: rows = today's state, columns = tomorrow's state, values =
historical transition frequencies.

```
                Tomorrow Bull   Tomorrow Sideways   Tomorrow Bear
Today Bull          P              P                  P
Today Sideways      P              P                  P
Today Bear          P              P                  P
```

The diagonal measures persistence (regime stickiness). The signal is
derived from the row corresponding to today's state:
`markov_signal = row[bull] - row[bear]`.

## 5. CRITICAL: lookahead discipline (walk-forward)
This is the central trap and a HARD requirement.

The transition matrix MUST be rebuilt walk-forward using ONLY prior
days. On any given decision day D:
- The matrix is built from state transitions observed strictly BEFORE
  day D.
- The state label for day D uses the rolling-20d return ending at day
  D-1 (or D's close only if the decision is made after D's close for
  the NEXT day's trading).
- No transition from day D or any future day may enter the matrix used
  to make day D's decision.

A naively-built matrix (using the full history including future days)
would "know" future transition frequencies -- severe lookahead
contamination. This node is invalid unless walk-forward.

Refit cadence: daily or weekly (pre-commit at implementation). Train
window: rolling [500, 1000, 1500] days candidate (pre-commit one).

OOS discipline: the same 2026-02-01 OOS seal applies. Walk-forward
rebuild must not load OOS data when generating in-sample regime labels.

## 6. How this node gets validated (overlay experiment)
NOT by standalone P&L. The node produces no trades. It is validated by
overlay experiments on existing entry strategies:

Baseline vs node-conditioned comparison on:
1. tight_opening_window_breakout_long (provisional-seed) -- does Markov
   direction permission improve its marginal PF?
2. A liquidity-sweep-reversal candidate -- does Markov side-preference
   improve sweep reversals?
3. wide_opening_window_reversal_family (tested-dead) -- would Markov
   context have blocked the catastrophic counter-regime shorts?

The question for each: does layering this node improve the baseline?
A node that helps multiple unrelated families is more credible than one
that helps a single strategy (possible overfit coincidence).

The wide-reversal overlay is especially diagnostic: that family lost
-$14K to -$18K partly by fading trend without context. If Markov
permission would have blocked the worst counter-regime trades, that is
direct evidence the node has conditioning value -- even though the
underlying strategy stays rejected.

## 7. Honest cautions (from source analysis)
- A 3-state daily Markov chain is not magic; the "hedge fund method"
  framing in the source is oversimplified.
- Daily state probabilities may not predict intraday MNQ behavior well.
  Daily regime and intraday entry timing operate on different scales.
- The 5%/-5% thresholds are arbitrary and may not suit MNQ.
- Transition matrices go STALE when the market regime shifts; a matrix
  built on a trending year misleads in a choppy year. Walk-forward
  rebuild mitigates but does not eliminate this.
- A Hidden Markov Model variant (discovering regimes from data rather
  than hand-labeling) is mentioned in the source but is MORE prone to
  overfitting and must not be attempted before the simple manual version
  is overlay-validated.

The node may simply not help. That is a legitimate overlay-rejected
outcome and must be reported honestly, not rationalized.

## 8. Implementation plan (deferred)
Phase 1 (note-only): this document. No implementation.

Phase 2 (when prioritized): build the walk-forward daily regime
classifier as a standalone signal generator. Output the daily contract
(Section 2) as a time series. No trading yet. Verify walk-forward
correctness and no OOS leak.

Phase 3 (overlay experiment): apply the node's permissions/signal to one
or more baseline strategies. Compare baseline vs node-conditioned.
Report whether the node improves each family.

Phase 4 (only if overlay-validated): consider HMM variant; consider
wiring into the composition graph.

Do NOT skip to Phase 3 or 4. The simple manual Markov classifier must be
walk-forward-correct and overlay-tested before any HMM or graph work.

## 9. Relationship to the composition vision
This is the first concrete composition node in the project. It embodies
the regime-conditional-routing idea from the marginal registry's
composition vision. But building this note does NOT commit to the graph.
The node earns its place by demonstrating overlay value first. If it
improves existing strategies, it becomes a validated conditioning layer
and a candidate graph node. If it doesn't, it is overlay-rejected and
documented as such.

## 10. Status history
| Date | Status | Notes |
|------|--------|-------|
| 2026-05-20 | note-only | First composition node authored. Daily Markov regime router (bull/bear/sideways + directional bias). NOT an entry strategy. Output contract and walk-forward lookahead discipline pinned. Validation is by overlay experiment on existing strategies, not standalone P&L. No implementation yet. Honest cautions documented: daily-may-not-predict-intraday, arbitrary thresholds, matrix staleness, HMM overfitting risk. |
