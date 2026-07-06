---
node_id: "intraday_target_invalidation_packet"
name: "Intraday Target / Invalidation Packet"
tagline: "Pre-entry and in-trade reward geometry packet: where is the next target, where is the invalidation, and is the trade worth carrying?"
status: "note-only-pending-liquidity-router-v2"
created: 2026-06-02
updated: 2026-06-22
source: "Operator design discussion after daily-bias and liquidity-zone transcript intake."
node_type: "pre-trade-filter / in-trade-management-context"
markets: ["MNQ"]
timeframe: "intraday"
depends_on:
  - "liquidity_zone_prior_router"
consumes:
  - "candidate entry price"
  - "candidate direction"
  - "liquidity-zone prior outputs"
  - "current HTF/1H bias packet"
  - "ATR / volatility regime"
  - "existing strategy trade candidates (G2, v2a, future producers)"
emits:
  - "targetability_pass"
  - "target_price"
  - "target_zone_type"
  - "invalidation_price"
  - "invalidation_rule"
  - "risk_points"
  - "reward_points"
  - "r_to_target"
  - "contracts_allowed"
  - "valid_until"
  - "pretrade_decision"
  - "no_target_reason"
  - "management_context"
implementation: null
validation: "overlay-experiment after liquidity-zone router exists"
related_artifacts:
  - "../source_artifacts/compass_no_target_no_trade_targetability_gate_mnq_20260622.md"
  - "liquidity_zone_prior_router.md"
  - "opening_momentum_acceptance_router.md"
  - "opening_range_rejection_state_router.md"
  - "../_MANAGEMENT_OBSERVER_MEMORY_LAYER.md"
  - "../candidates/premium_discount_sweep_shift_continuation.md"
tags:
  - composition-node
  - target-geometry
  - invalidation
  - liquidity-zone
  - observer-input
  - not-a-strategy
---

# Intraday Target / Invalidation Packet

## 1. Why This Node Exists

The management observer has mostly been post-entry: once risk is open,
it diagnoses the trade path. This node is the pre-entry sibling. It asks:

```text
Given the candidate entry, the next realistic liquidity target, and the
invalidation level, is this trade worth taking or carrying?
```

This is not a new entry strategy. It is a reward-geometry filter and
management context layer for existing trade producers. If entries are
commodity and management is the lever, then rejecting low-quality target
geometry before entry is part of management discipline.

## 2. Dependency Order

This node depends on an objective liquidity-zone taxonomy. Do not
implement it before `liquidity_zone_prior_router` exists or before the
project has locked objective definitions for the target candidates.

Correct order:

```text
liquidity_zone_prior_router
-> intraday_target_invalidation_packet
-> overlay on existing G2/v2a/future trade producers
```

The packet consumes zones. It does not define zones ad hoc.

## 3. Output Contract

```yaml
intraday_target_invalidation_packet:
  computed_at: datetime
  expires_at: datetime | null
  valid_until:
    - target_touched
    - invalidation_touched
    - structure_change
    - time_limit
    - closer_opposing_zone_appears

  source_strategy: string
  direction: long | short
  entry_candidate: float

  targetability_pass: bool
  no_target_reason: none | no_objective_target | target_too_close |
                    invalidation_missing | risk_reward_too_low |
                    volatility_reach_too_low | stale_packet

  target_zone_type: prior_day_level | opening_range_level |
                    one_hour_swing | equal_high_low |
                    round_number | opposing_zone |
                    imbalance_fill | unknown
  target_price: float
  target_distance_points: float
  target_reachable_by_volatility: bool

  invalidation_type: protected_swing | swept_liquidity_extreme |
                     supply_demand_zone_edge |
                     reclaim_against_bias |
                     acceptance_against_bias
  invalidation_price: float
  invalidation_rule: touch | wick_only | break_and_hold | acceptance
  invalidation_distance_points: float

  atr_context:
    atr_points: float
    risk_atr: float
    reward_atr: float

  risk_points: float
  reward_points: float
  r_to_target: float
  max_contracts_by_risk: int
  contracts_allowed: int

  pretrade_decision: allow | reduce | block | stale
  management_context: target_far | target_near | target_reached |
                      invalidation_near | invalidated |
                      geometry_unfavorable
```

## 3A. Targetability Gate: "No Target, No Trade"

This node is also the home for the operator's **Targetability Gate**:

```text
No target, no trade.
```

Before an entry strategy is allowed to put risk on, the packet must be
able to name a reachable, objective target and a falsifiable
invalidation level. A setup is not enough. A direction is not enough. A
trade needs somewhere to go.

Minimum pre-entry questions:

1. **What is the target?** The target must come from the locked target
   hierarchy: 10m/30m swing, prior-day level, opening-range level,
   equal high/low, round number, VWAP band, or another pre-defined
   router output. Do not invent discretionary targets at runtime.
2. **What invalidates the idea?** The invalidation must be structural
   and known before entry: protected swing, zone edge, reclaim against
   bias, or acceptance against bias.
3. **Is the target reachable?** Reward distance must be large enough
   relative to current volatility and not so far that the strategy is
   implicitly depending on a tail day.
4. **Is the reward worth the risk?** `r_to_target` must clear the
   pre-committed minimum after measuring from candidate entry to target
   and invalidation.
5. **Is there a nearer obstruction?** A closer opposing zone can turn a
   nominal target into a poor trade. The packet should block or reduce
   when the first obstruction is too close.

Suggested v1 pass condition:

```text
targetability_pass =
  objective_target_exists
  and invalidation_exists
  and r_to_target >= 1.5
  and reward_atr >= 0.25
  and target_reachable_by_volatility
```

The threshold values are placeholders from the original packet design.
They must be pre-committed before scoring and must not be swept to
rescue a candidate.

The gate can be used two ways:

- **Hard gate:** block entries with no reachable target. This is
  appropriate for discretionary-looking continuation and pullback
  candidates where a static bracket would otherwise create blind trades.
- **Label first:** record targetability fields without gating. This is
  appropriate for unconditional anomaly candidates, such as
  market-intraday-momentum close-window tests, where adding a target gate
  would change the hypothesis and cut the frequency being tested.

## 3B. Evidence Status And Non-Alpha Warning

The 2026-06-22 targetability source artifact sharpens the status of this
node:

```text
Targetability is hygiene, not alpha.
```

The gate can remove structurally poor trades from an already useful
entry stream. It should not be expected to create edge from random or
negative-expectancy entries. Under a random-walk / first-passage view,
choosing a reward:risk ratio mostly trades win rate for payoff size; it
does not manufacture positive expected value after costs.

Important R:R boundary:

```text
R:R is legitimate for sizing a verified edge, not for creating one.
```

Once an edge is established, reward:risk can inform position sizing
through a Kelly-style fraction, for example:

```text
f = (p * b - q) / b
```

where `p` is win probability, `q = 1 - p`, and `b` is payoff ratio. A
40% win rate at 2:1 gives `f = (0.40 * 2 - 0.60) / 2 = 0.10`.

Using a minimum R:R gate to create the edge is circular. If the entry
stream has no positive expectancy, raising the minimum R:R usually
changes the win-rate/payoff mix and reduces frequency; it does not, by
itself, make the stream profitable. Therefore, `risk_reward_too_low` is
a hygiene/blocking reason, not evidence that the remaining allowed set
has alpha.

This matters for project discipline:

- do not use targetability to rescue candidates already classified as
  decisive negative unless the test is explicitly an overlay audit;
- do not tune the target hierarchy, R multiple, or reachability
  multiplier after seeing P&L;
- score it as a marginal overlay: baseline entries vs targetability
  `allow` / `block` / `label-only`;
- require it to beat cheap baselines such as fixed 1.5R targets,
  nearest round-number targets, or VWAP-only targets.

The first thing to measure is not raw P&L. It is calibration:

```text
When the packet says a target is reachable and worth at least X R,
does price reach that target before invalidation more often than a
cheap baseline would predict?
```

If the answer is no on high-n trade lists, the gate is not useful yet.

## 3C. Lookahead-Safe Target Sources

Targets and invalidations must be knowable at or before the entry
decision. The preferred v1 source set:

- prior RTH high/low and close-derived floor pivots;
- prior-day high/low and prior-session value area / POC;
- overnight high/low frozen at the RTH open;
- opening-range high/low only after that opening range is complete;
- session VWAP and VWAP bands frozen at the entry timestamp;
- major round numbers;
- confirmed swing highs/lows only after their confirmation lag has
  elapsed.

Forbidden v1 sources:

- current in-progress bar high/low as a target;
- developing current-session value area unless explicitly frozen before
  entry;
- swing pivots marked at the pivot bar before the right-side
  confirmation bars exist;
- any target chosen because later price happened to reach it.

Swing levels are usable only from the confirmation timestamp onward. If
a five-bar pivot needs two bars to the right, the level becomes eligible
only after those two future bars have closed; it must not be used earlier
in the backtest.

## 3D. Reachability Rule

Target distance must pass both reward sufficiency and volatility
reachability:

```text
reward_points / risk_points >= min_R_multiple
target_distance_points <= reachability_limit
reachability_limit = min(k_atr * ATR_entry, c_remaining * remaining_expected_range)
```

The source artifact suggests MNQ starting points to validate, not to
treat as truth:

- `min_R_multiple`: 1.5 as a frequency-friendly floor; 2.0 only if the
  entry stream already supports the higher required win rate;
- `target_distance <= 1.5-2.0 x ATR(14)` on the entry timeframe;
- also require the target to fit inside a time-of-day-adjusted
  remaining-session range;
- tighten reachability after midday because much of the session's range
  has often already been spent.

Costs must be included in the read. On MNQ, a 1.25-2 point round-trip
cost is small relative to a 20-40 point trade but can dominate tiny
stops or scalp targets. Very small invalidation distances should be
penalized because the cost as a fraction of 1R becomes too large.

## 3E. Pre-Entry Criteria Module

The management-system application is a pre-entry checklist that runs
after an entry signal exists but before order submission:

```text
entry signal -> targetability packet -> allow / reduce / block / label-only
```

This is the concrete pre-entry criteria contract:

```yaml
pre_entry_targetability_criteria:
  mode: hard_gate | label_only
  computed_at: entry_decision_time
  lookahead_boundary: all inputs must be known at or before computed_at

  required_inputs:
    entry_price: float
    direction: long | short
    structural_invalidation_price: float
    candidate_targets:
      - price: float
        source: pdh_pdl | floor_pivot | overnight_extreme |
                opening_range | frozen_vwap_band | round_number |
                prior_value_area | confirmed_swing
        known_since: datetime
    atr_entry_timeframe: float
    remaining_session_range_estimate: float
    round_trip_cost_points: float

  pass_conditions:
    target_exists_in_trade_direction: true
    invalidation_exists: true
    target_known_without_lookahead: true
    target_not_already_touched_or_stale: true
    r_to_target_net_of_cost >= 1.5
    target_distance_points <= min(2.0 * atr_entry_timeframe,
                                  0.75 * remaining_session_range_estimate)
    cost_as_fraction_of_r <= pre_committed_max

  output:
    pretrade_decision: allow | reduce | block | label_only
    targetability_pass: bool
    no_target_reason: string | null
    selected_target_price: float | null
    selected_target_source: string | null
    r_to_target_net_of_cost: float | null
    target_distance_points: float | null
    invalidation_distance_points: float | null
```

Mode discipline:

- `hard_gate` is appropriate for structural discretionary-style
  candidates: pullbacks, reversals, sweeps, opening-range responses, and
  continuation entries where a static bracket would otherwise be blind.
- `label_only` is appropriate for unconditional anomaly candidates,
  including close-window market-intraday-momentum, where the hypothesis
  is intentionally "take the effect every day" and target gating would
  define a different strategy.

The default v1 gate should use `min_R = 1.5`, `k_atr = 2.0`, and
`c_remaining = 0.75` only as a first pre-commit. These values are not
permission to sweep. A future implementation may replace the simple
remaining-range estimate with a calibrated MNQ RTH cumulative-range
curve, but that curve must be built before scoring.

Order of target choice:

1. Generate all eligible targets from lookahead-safe sources.
2. Remove targets not strictly ahead of entry in the trade direction.
3. Remove stale or already-touched targets.
4. Compute net R after costs for each target.
5. Select the nearest target that passes both net-R and reachability.
6. If none pass, block or label `no_target_reason`.

This "nearest qualifying target" rule prevents the gate from skipping
reachable near targets in favor of flattering but unrealistic far
targets.

Canonical v1 pseudocode:

```text
function targetability_gate(entry_price, direction, t, structure, stop_price, params):
    # structure holds ONLY data known at/before bar t:
    #   prior-session OHLC -> pivots P,R1..R3,S1..S3
    #   PDH, PDL, ONH, ONL
    #   ORH, ORL only if the opening range completed at/before t
    #   VWAP_t and VWAP bands cumulated through t, frozen
    #   round levels
    #   prior-session VAH, VAL, POC
    #   confirmed swings only after their confirmation lag
    #   ATR_entry = ATR(14) computed through closed bar t-1
    #   ADR / time-of-day fraction curve calibrated to MNQ RTH

    all_levels = structure.lookahead_safe_targets

    if direction == long:
        candidates = [lvl for lvl in all_levels if lvl.price > entry_price]
    else:
        candidates = [lvl for lvl in all_levels if lvl.price < entry_price]
    if candidates is empty:
        return deny(no_target_reason = no_objective_target)

    risk = abs(entry_price - stop_price)
    if risk <= 0:
        return deny(no_target_reason = invalidation_missing)

    rem_range = structure.ADR * (1 - cum_range_fraction(time_of_day(t)))
    reach_limit = min(params.k_atr * structure.ATR_entry,
                      params.c_range * rem_range)

    for lvl in sort_by_distance(candidates, entry_price):
        dist = abs(lvl.price - entry_price)
        R_gross = dist / risk
        R_net = (dist - params.round_trip_cost_points) / risk

        if R_net >= params.min_R and dist <= reach_limit:
            return allow(target = lvl.price,
                         target_source = lvl.source,
                         R = R_net,
                         dist = dist)

    return deny(no_target_reason = risk_reward_too_low)
```

Implementation notes:

- `stop_price` must be the structural invalidation for the entry idea,
  not an optimized bracket distance.
- `ATR_entry` excludes the in-progress bar and is frozen at decision
  time.
- `cum_range_fraction()` must be calibrated before scoring. If it is
  missing, label-only mode should record `missing_remaining_range`
  rather than silently substituting a guessed curve.
- The loop exits at the first qualifying level so the gate chooses the
  most reachable valid target, not the most flattering target.

## 4. Validity / Staleness Rules

The packet is timestamped. It is not valid forever.

Expire or refresh the packet when:

- the target is touched or swept before entry;
- the invalidation level is touched or accepted before entry;
- a new structure break changes the active swing range;
- a closer opposing liquidity zone appears;
- a pre-committed time limit passes.

This is the load-bearing rule. Static targets create stale confidence.
Timestamped packets make the target/invalidation geometry falsifiable.

## 5. Locked Target Selection Discipline

The target list is overfit-prone. Do not search target rules after seeing
P&L. The first implementation must lock a priority order before any
scoring.

Recommended first priority order:

For longs:

1. nearest unswept structural level above:
   `PDH`, `OR_high`, or confirmed `1H_swing_high`, whichever is nearest;
2. nearest major round number above (`25/50/100` point grid);
3. equal highs above, only under a pre-committed tolerance from the
   liquidity-zone router;
4. imbalance fill / opposing zone only if already defined by the zone
   router.

For shorts:

1. nearest unswept structural level below:
   `PDL`, `OR_low`, or confirmed `1H_swing_low`, whichever is nearest;
2. nearest major round number below (`25/50/100` point grid);
3. equal lows below, only under a pre-committed tolerance from the
   liquidity-zone router;
4. imbalance fill / opposing zone only if already defined by the zone
   router.

Trendlines are excluded from v1. They may be added only after a strict
line-fitting rule exists and only as a separate trial.

## 6. Locked "Far Enough To Matter" Rule

Do not define "far enough" in raw points. Use volatility-normalized
geometry.

Recommended v1 rule:

```text
allow only if r_to_target >= 1.5R
and reward_atr >= 0.25 ATR
and risk_atr <= pre-committed max_risk_atr
```

The exact ATR thresholds should be locked before first scoring and not
swept afterward. The principle is that target geometry must survive
volatility regime changes.

## 7. Dual Consumers

### Pre-Trade Filter

Before an existing strategy entry is allowed:

```text
entry candidate -> packet -> allow / reduce / block
```

Example:

```text
entry = 21840
invalidation = 21820
target = 21878
risk = 20 pts
reward = 38 pts
r_to_target = 1.9R
decision = allow
```

If `r_to_target` is too low, the trade is blocked or reduced even if the
entry signal itself fires.

### In-Trade Management Context

After entry, the same packet can inform management:

- `target_reached` -> consider `take_partial` or `flatten`;
- `target_near` and MFE is high -> de-risking may be justified;
- `invalidation_near` -> thesis health becomes damaged;
- `acceptance_against_bias` -> thesis invalidated, flatten is the clean
  exposure-ending action to score first;
- `target_still_far` and thesis intact -> hold may be preferred over
  premature protection.

This avoids building separate pre-trade and post-entry systems. The
packet generator is shared; consumers differ by timing.

## 8. First Validation

Do not test as standalone P&L. Validate as an overlay:

1. Take existing trade candidates from G2/v2a/future substrates.
2. Generate packets at the candidate entry timestamp.
3. Compare baseline trades versus packet-conditioned trades:
   - all trades;
   - `allow` only;
   - `block geometry_unfavorable`;
   - size-reduced adverse geometry.
4. Score PF, drawdown, Apex pass/fail, loss clustering, and whether
   target-before-invalidation predictions were calibrated.

Prediction scoring should include:

```text
When packet says r_to_target >= 1.5R, how often does price reach target
before invalidation?
```

The packet only earns belief for marginal improvement over cheap
baselines such as fixed 1.5R targets or nearest round-number targets.

## 9. Status

Current status: design banked only. `liquidity_zone_prior_router` now has
a v1 descriptive diagnostic, but the packet should wait for the v2
liquidity-router cleanup: target-vs-sweep distinction, round-number zone
emission, and distance-matched controls.
