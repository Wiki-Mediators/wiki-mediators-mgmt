---
node_id: "opening_range_rejection_state_router"
name: "Opening Range Rejection State Router"
tagline: "Use robust opening-range failed-break/reversion behavior as a state gate for existing trade producers."
status: "note-only"
created: 2026-06-02
updated: 2026-06-02
source: "Candidate inventory review after transcript-derived candidate proved weak/inconclusive; registry and ORWS regime-stability review."
node_type: "session-state-router / entry-gate / management-context"
markets: ["MNQ"]
timeframe: "RTH intraday"
consumes:
  - "09:30-09:45 opening range"
  - "first post-OR break direction"
  - "time-to-reversion back inside / across OR"
  - "OR width percentile"
  - "current bridge-substrate trades (G2 3c, v2a 15c)"
emits:
  - "or_state"
  - "trend_permission"
  - "reversion_permission"
  - "risk_warning"
  - "size_multiplier"
  - "management_context"
implementation: null
validation: "overlay-experiment"
related_artifacts:
  - "../candidates/_MARGINAL_STRATEGIES_REGISTRY.md"
  - "../candidates/opening_range_width_switch.md"
  - "../_MANAGEMENT_OBSERVER_MEMORY_LAYER.md"
  - "../../probe_results/orws_regime_stability.json"
tags:
  - composition-node
  - opening-range
  - regime-router
  - state-gate
  - overlay-validation
  - not-a-strategy
---

# Opening Range Rejection State Router

## 1. Why This Node Exists

The candidate inventory keeps pointing at the same divide:

- Many new entry ideas fail at R1.
- The current viable replay substrate is small: `G2 3c + v2a 15c`.
- The strongest reusable non-deployable signal is **opening-range
  failed-break/reversion**.

`opening_range_width_switch` is rejected as a standalone strategy because
its implementation has Apex path/variance risk. But its R1 behavior is
unusually robust: ORWS reversion measured 77-82% across three
non-overlapping six-month windows, with median time-to-revert around 2
minutes in each window.

That makes ORWS a poor standalone answer but a good candidate state
router. The first blend should not add more entries. It should ask
whether opening-range state improves the trades we already have.

## 2. What This Node Is

This is a composition node. It observes the early RTH opening-range
auction and emits a state label.

Possible v1 labels:

```text
no_break_yet
up_break_clean
down_break_clean
up_break_failed_fast
down_break_failed_fast
up_break_accepted
down_break_accepted
wide_or
tight_or
```

The labels are causal. They use only the opening range and completed
post-OR bars available at the decision timestamp.

## 3. What This Node Is Not

This node is not:

- a new standalone entry strategy;
- a resurrection of ORWS as deployable;
- permission to consume OOS;
- a parameter sweep over opening-range definitions;
- a reason to combine weak candidates before overlay evidence exists.

It is a state tagger and router. It earns value only if overlay tests show
that the tag improves existing strategies or management policies.

## 4. Candidate Output Contract

```yaml
node_id: opening_range_rejection_state_router
timestamp: datetime
lookahead_clean: true

inputs:
  or_start: "09:30:00 ET"
  or_end: "09:45:00 ET"
  or_high: float
  or_low: float
  or_width_points: float
  first_break_direction: up | down | none
  first_break_ts: datetime | null
  reversion_ts: datetime | null
  accepted_outside_or: bool

outputs:
  or_state: no_break_yet | up_break_clean | down_break_clean |
            up_break_failed_fast | down_break_failed_fast |
            up_break_accepted | down_break_accepted
  or_width_regime: tight | normal | wide
  trend_permission: allow | reduce | block
  reversion_permission: allow | reduce | block
  risk_warning: none | elevated | hostile
  size_multiplier: float
  management_context: neutral | fade_risk | trend_acceptance | chop_reversion
```

## 5. First Overlay Experiment

Start with the current bridge substrate:

```text
G2 canonical alpha at 3 contracts
Savor-Wilson v2a canonical alpha at 15 contracts
combined G2 3c + v2a 15c
```

Pre-committed question:

```text
Does opening-range state improve the current bridge substrate as a gate
or size reducer without degrading both discovery and holdout partitions?
```

Suggested v1 policy map to test:

| OR state | Hypothesis |
|---|---|
| fast failed break | trend-continuation entries may be lower quality; reduce or block G2-style continuation |
| accepted outside OR | trend-continuation entries may be higher quality; allow default |
| wide OR | reduce size or require stronger substrate signal |
| tight OR | allow continuation if later acceptance confirms; otherwise watch for chop/reversion |

No tuning inside the first run. If this node helps only one tiny cell, it
is not validated.

## 6. Why This Is The Best Current Starting Point

Registry review found four preserved weak/component entries:

- `opening_range_width_switch`: component-useful, positive multistart
  expectancy signature but Apex path risk.
- `tight_opening_window_breakout_long`: provisional bullish continuation
  seed, weak PF, low count.
- `prior_day_value_area_rejection`: low-priority auction rejection seed,
  too sparse and monthly-start negative.
- `objective_level_liquidity_sweep_reversal_family` opening-range branch:
  faint branch seed, especially long-side, but too thin.

Of those, ORWS has by far the strongest measurement as a reusable state:
large R1 event count, cross-window stability, and a clear mechanism. It
is therefore the right first node to test as a blend/gate.

## 7. Validation Rules

Use the same discipline as other management/composition overlays:

- OOS remains sealed.
- Partition by day or monthly start, not event row.
- Compare baseline vs gated/sized overlay.
- Report P&L, PF, max drawdown, pass/fail/in-progress monthly-start
  outcomes, and trade count removed.
- Require improvement in both discovery and holdout before belief.
- Track trial count: each policy map is a trial draw.
- Do not optimize OR thresholds after seeing results.

## 8. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-06-02 | `note-only` | Created after candidate/registry review. Best current blend starting point is ORWS-derived opening-range state as a gate/router over current G2/v2a bridge substrate, not a new entry strategy. |
