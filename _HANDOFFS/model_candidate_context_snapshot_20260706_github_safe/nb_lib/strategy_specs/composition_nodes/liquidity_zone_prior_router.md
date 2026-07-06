---
node_id: "liquidity_zone_prior_router"
name: "Liquidity Zone Prior Router"
tagline: "Objective OHLCV-derived liquidity-zone labeling layer for the management observer: where price sits relative to likely resting-order pools, has liquidity been swept, did price reject or accept."
status: "note-only"
created: 2026-06-02
updated: 2026-06-02
source: "Operator direction 2026-06-02 to translate transcript liquidity-zone concepts into objective OHLCV predicates that feed the management observer. Inherits the true_zone_liquidity_sweep_reference framework and the closed-negative entry-strategy lessons from PDH_PDL / ROUND_VWAP / objective-level family multistart."
node_type: "management-observer-input / state-router"
markets: ["MNQ"]
timeframe: "RTH intraday with prior-day daily context"
consumes:
  - "1-second OHLCV via nb_lib.data.load_mnq_1s"
  - "prior-day RTH high/low/close"
  - "current-day opening range (09:30-09:45 ET)"
  - "running RTH session high/low"
  - "round-number levels (25/50/100 pt)"
  - "5-bar fractal swing pivots on completed 1-minute bars"
  - "running session VWAP"
  - "running session ATR(20) on 5-minute bars"
emits:
  - "zone_price"
  - "zone_type"
  - "zone_side"
  - "normalized_location_fields"
  - "cohort_support"
  - "historical_sweep_rate"
  - "historical_rejection_rate"
  - "historical_acceptance_rate"
  - "confidence"
  - "management_context"
implementation: "../../scripts/diagnostic_liquidity_zone_prior_router.py"
validation: "descriptive-diagnostic-first (read-only); overlay-experiment later"
related_artifacts:
  - "../candidates/true_zone_liquidity_sweep_reference.md"
  - "../candidates/premium_discount_sweep_shift_continuation.md"
  - "../candidates/opening_range_width_switch.md"
  - "../candidates/objective_level_liquidity_sweep_reversal_family.md"
  - "../candidates/pdh_pdl_liquidity_sweep_reversal.md"
  - "../candidates/round_number_vwap_liquidity_sweep_reversal.md"
  - "opening_range_rejection_state_router.md"
  - "realized_volatility_management_router.md"
  - "../_MANAGEMENT_OBSERVER_MEMORY_LAYER.md"
tags:
  - composition-node
  - liquidity-zones
  - management-observer-input
  - sweep
  - reclaim
  - acceptance
  - descriptive-diagnostic
  - not-a-strategy
---

# Liquidity Zone Prior Router

## 1. Why This Node Exists

The 2026-06-02 transcript intake and earlier `true_zone_liquidity_sweep_reference` already supplied the conceptual framework: price targets, sweeps, rejects, or accepts liquidity at certain chart locations, and the useful sequence is

```text
inducement / visible pool -> sweep -> displacement -> later mitigation/retest
```

Three project facts shape how this node must be built:

1. **Direct trading from these zones has been tried and largely failed.**
   PDH_PDL sweep-reversal, round-VWAP sweep-reversal, opening-range
   liquidity sweep, round-number rejection microfade, and the broader
   objective-level family are all closed-negative or
   tested-informational-rejected. The component-useful exception is
   ORWS opening-range failed-break-reversion, which is preserved as a
   state router (`opening_range_rejection_state_router.md`) rather
   than a deployable entry.

2. **The 2026-06-02 transcript explicitly cautioned that "Discretionary
   chart concepts (premium/discount, supply-demand zones, liquidity
   sweep, market shift) should not enter the research pipeline unless
   translated into objective predicates and tested against cheap
   baselines."** This node is exactly that translation, scoped to feed
   the management observer rather than an entry restart.

3. **The management observer is the consumer.** The observer wants
   computable language for `inside_contraction`, `sweep_against_entry`,
   `reclaim_in_entry_direction`, `accepted_against_entry`. Those
   require objective zone definitions first. The router supplies the
   zone layer; the observer combines zone events with trade state.

This is therefore an **input layer for management research**, not a
new entry strategy and not a resurrection of the closed-negative
sweep-reversal entries.

## 2. What This Node Is

A composition node that:

- Computes objective candidate liquidity zones from completed
  1-second OHLCV at any decision timestamp.
- Tags each zone with a normalized location coordinate, a type, and
  a side (buy-side / sell-side liquidity).
- Optionally — after the descriptive diagnostic has measured
  per-zone-type sweep/rejection/acceptance rates against cheap
  controls — attaches historical-rate metadata so the observer can
  weight which zones to take seriously.

## 3. What This Node Is Not

This node is not:

- A standalone alpha. Direct trading from these zones is not
  authorized.
- A revival of closed-negative liquidity-sweep entries
  (PDH_PDL, round-VWAP, objective-level family, round-number-rejection,
  opening-range-liquidity-sweep, premium-discount-sweep-shift).
- A claim about true order-book liquidity. We cannot see real resting
  orders; this is an **estimated liquidity-zone prior** built from
  chart locations where the operator transcript suggests stops and
  orders cluster.
- Permission to consume sealed OOS (`2026-02-01+`).
- A parameter sweep over zone definitions. All zone parameters are
  pre-committed in Section 5 below and not tuned after measurement.
- A trendline-first node. Trendline liquidity is excluded from v1
  because line fitting is easy to overfit; the design note in
  Section 5.E preserves it for a future explicit-rule version.

## 4. Boring-Zone Order (pre-committed)

The taxonomy is intentionally boring-first. Most-objective zone
types are included in v1; subjective / fit-prone zone types are
deferred or excluded.

| v1 | Zone type | Why included now |
|---|---|---|
| Yes | Prior day high / low / close (PDH / PDL / PDC) | Computed from prior trading day's RTH OHLC; fully objective |
| Yes | Opening range high / low (OR_H / OR_L) | Defined as 09:30-09:45 ET high/low; available by 09:45 |
| Yes | Round numbers within current range (25 / 50 / 100 pt grid) | Pure arithmetic; no parameters |
| Yes | Swing high/low (5-bar fractal on completed 1-minute bars) | One pre-committed lookback; not swept |
| Yes | Equal high / equal low within 1-tick tolerance | Single pre-committed tolerance; cluster-anchored |
| Note-only (v2) | Strong high/low after BOS, not yet traded through | Needs an objective BOS definition; deferred to v2 |
| Note-only (v2) | Support / resistance shelf from repeated touches | Needs touch-count and recency parameters; deferred |
| Note-only (v2) | Swept-liquidity displacement zone | Defined only AFTER a sweep+displacement event observed; chained |
| Excluded (deferred) | Trendline-like aligned pivots | Line-fitting risk; revisit only with pre-committed rule |

Note on the v2 set: "Note-only" means the node spec records the
shape and predicate plan, but v1 implementation does NOT emit them.
A future v2 may add them after the v1 descriptive diagnostic
establishes whether the v1 zones beat cheap baselines.

## 5. Objective predicates (pre-committed parameters)

The parameters below are LOCKED for v1. The descriptive diagnostic
in Section 8 uses these unchanged. Re-tuning any threshold after
seeing the diagnostic output is forbidden under the project's
post-hoc-tuning discipline.

### 5.A Prior-day H/L/C (PDH / PDL / PDC)

- Computed from the **completed prior RTH session** only.
- PDH = max high over prior RTH session bars.
- PDL = min low over prior RTH session bars.
- PDC = last close of prior RTH session.
- Side: PDH is sell-side liquidity (stops of longs from prior day);
  PDL is buy-side liquidity; PDC is two-sided.

### 5.B Opening range (OR_H / OR_L)

- Computed from RTH open bar 09:30:00 inclusive to 09:45:00 exclusive
  (the first 15 minutes of RTH).
- OR_H = max high of those 1-minute bars.
- OR_L = min low of those 1-minute bars.
- Side: OR_H is sell-side (stops of shorts placed during OR);
  OR_L is buy-side.

### 5.C Round numbers

- Grid: 25-point levels for fine resolution, 50-point and 100-point
  levels emitted separately as priority tags.
- "In current range" = within ±2 × ATR(20) (5-min ATR as of current
  bar) of the running session close. Limits cardinality.
- Side: above current price = sell-side; below = buy-side.

### 5.D Swing highs / lows (5-bar fractal)

- Defined on **completed 1-minute RTH bars**.
- Swing high at bar i = `high[i]` is the strict maximum of
  `high[i-2..i+2]` (the conventional 5-bar fractal). A swing high is
  only emitted at bar i+2's close — i.e., causally available 2
  minutes after the pivot bar.
- Swing low symmetric.
- Side: swing high = sell-side; swing low = buy-side.

### 5.E Equal highs / equal lows

- Detected from 5-bar fractal swing pivots only (Section 5.D).
- Tolerance: two swing pivots are "equal" if their prices are
  within **1 tick** of each other (MNQ tick = 0.25 points).
- Cluster: two or more pivots within tolerance form an equal-high
  (sell-side) or equal-low (buy-side) cluster.
- Cluster price = mean of the cluster's pivot prices.
- This is one pre-committed tolerance, not a swept band.

### 5.F Trendline liquidity (excluded from v1; future design)

Reserved for v2 IF and only IF a strict, pre-committed line-fitting
rule is adopted (e.g., "least-squares fit to ≥3 swing pivots whose
residual from the fitted line is ≤0.25 × ATR; fitted line must be
tested at least once after construction"). The risk that fitted
lines spuriously look meaningful in random walks is real; v1 does
not emit them.

## 6. Normalization (coordinates for the management observer)

Raw MNQ prices over two years are not stationary; the observer
cannot use absolute price. Every emitted zone gets a normalized
location bundle:

| Field | Definition |
|---|---|
| `ticks_from_rth_open` | `(zone_price - rth_open) / tick_size` |
| `ticks_from_vwap` | `(zone_price - session_vwap) / tick_size` |
| `pts_from_or_high` | `zone_price - OR_H` (signed) |
| `pts_from_or_low` | `zone_price - OR_L` (signed) |
| `pct_of_or` | `(zone_price - OR_L) / (OR_H - OR_L)`; in [0, 1] if inside OR |
| `atr_normalized_distance_from_close` | `(zone_price - current_close) / atr_5min` |
| `pts_from_pdh` | `zone_price - PDH` (signed) |
| `pts_from_pdl` | `zone_price - PDL` (signed) |
| `pts_from_pdc` | `zone_price - PDC` (signed) |
| `pts_to_nearest_25` | distance to nearest 25-pt multiple |
| `pts_to_nearest_50` | distance to nearest 50-pt multiple |
| `pts_to_nearest_100` | distance to nearest 100-pt multiple |
| `time_of_day_bucket` | open / midmorning / midday / afternoon / close |

VWAP, ATR(20)-5min, and the session high/low are running causal
fields computed from completed bars only. The observer should never
read raw `zone_price` for cross-day comparison; it should read the
normalized fields.

## 7. Cohorting (hierarchical priors, not hard buckets)

Per the prompt: hierarchical priors with shrinkage, NOT tiny
disjoint buckets. The cohort chain (most-shrunken → most-specific):

1. **Global prior** — pooled rate across all in-sample sessions.
2. **Weekday prior** — by day of week (Mon-Fri).
3. **Event-type prior** — FOMC / NFP / CPI / OPEX flagged sessions
   separately from baseline sessions. Event calendar source:
   `nb_lib/calendar.py` if it exposes one, else pre-committed event
   list.
4. **Contract-cycle prior** — week within contract cycle if data
   supports it (see Section 9).
5. **Current-session context** — running session state at the
   decision timestamp (vol regime, OR width regime, OR-state per
   `opening_range_rejection_state_router`).

Combining rule: posterior rate = weighted average of priors with
weights proportional to denominator size at each level. Avoid using
the most-specific bucket alone unless its denominator is ≥30 events.
This is the same hierarchical-prior discipline the project uses
elsewhere; it avoids the Section-10 anti-pattern of "every cell
looks predictive on tiny n."

## 8. First Descriptive Diagnostic (read-only, no parameter sweep)

Pre-committed in this section. The diagnostic asks ONE question per
zone type:

> When this zone forms and is observable, what is the probability
> that price subsequently sweeps it, rejects it, accepts it, or
> never trades to it within the same RTH session, and how do these
> rates compare to controls?

### 8.A Window

- In-sample only: 2024-08-01 → 2026-01-31 (inclusive). OOS
  (2026-02-01 onward) is NOT consumed.
- The diagnostic uses the same partition the management-observer
  research uses: first 60% of unique trading days = DISCOVERY,
  last 40% = HOLDOUT. Pre-committed before computing rates.

### 8.B Outcome definitions (pre-committed)

For each zone observable at a decision timestamp T:

| Outcome | Definition |
|---|---|
| `targeted` | Price subsequently touches `zone_price` within ±0.25 tick before session close |
| `swept` | Price trades through `zone_price` by ≥2 ticks in the side-of-liquidity direction before session close |
| `rejected` | Conditional on `swept` at time T_s: within 5 minutes after T_s, price closes back inside (`above` for sell-side zone, `below` for buy-side zone) by ≥1 tick. Mutually exclusive with `accepted` |
| `accepted` | Conditional on `swept` at time T_s: 5 minutes after T_s, price has NOT closed back inside by ≥1 tick. Mutually exclusive with `rejected` |
| `displacement_in_sweep_direction` | Conditional on `swept` at T_s: 1 minute after T_s, 1-min realized range in the sweep direction ≥ 1.0 × ATR(20)-5min |

Time bounds (5 min rejection window, 1 min displacement window) are
**pre-committed** and not swept. They mirror the management observer's
existing 120s/300s vocabulary.

### 8.C Controls (pre-committed before any rate is computed)

The zone earns belief only by beating cheap controls:

1. **Random-level control**: per session, sample N random prices
   uniformly between the running RTH low and high, where N = number
   of zones observed that day. Compute the same outcomes for these
   random levels. If a zone type's sweep rate is within 5 pp of the
   random-level rate, it has no marginal information.
2. **Distance-matched random control**: for each observed zone,
   sample a random level at the same `ticks_from_vwap` distance
   (matched within 5 ticks). This controls for the trivial effect
   that levels near VWAP are touched more often.
3. **Cheap structural baseline**: for swing-high / swing-low zones,
   compare against **all** 5-bar fractal pivots vs the subset that
   later qualifies as "swept zones" — does the swept-then-mitigated
   subset beat the all-pivot baseline?
4. **Round-number control**: for any zone within 5 ticks of a round
   number, also tag it with the round-number control rate at the same
   normalized location. A zone passes only if it beats the
   round-number-only baseline for the same location.

If a zone type's rate falls inside the control envelope, that zone
type is recorded as **not marginally informative** and the router
emits it as a structural label only (no `confidence` boost).

### 8.D Output of the first diagnostic

A single JSON file:

```text
nb_lib/probe_results/liquidity_zone_prior_router_v1_diagnostic.json
```

containing:

- per-zone-type outcome rates (global, discovery, holdout)
- per-cohort outcome rates (weekday × zone type, event × zone type)
- per-control rates (random-level, distance-matched random,
  round-number control)
- per-zone-type "marginal information" verdict (beats controls / does
  not beat controls)
- n at every cell

### 8.E What the first diagnostic explicitly does NOT do

- Does not produce P&L or any trade simulation.
- Does not run a parameter search.
- Does not emit a recommended action or counterfactual.
- Does not consume OOS.
- Does not iterate after seeing results.

## 9. Contract-overlap policy

The existing `nb_lib.data.load_mnq_1s` decodes Databento DBN files
covering MNQ. The store has date-range partitions
(`2024-08-01_to_2024-10-01.dbn.zst`, etc.) — not separately-symboled
contract files. The loader concatenates by timestamp and dedupes by
`out[~out.index.duplicated(keep="first")]` which means **the first
contract encountered for each timestamp wins**. The Databento
extraction is presumed to have used the front-month / dominant-volume
convention upstream.

What the v1 router assumes:

- One active contract per timestamp/day, supplied by the existing
  loader.
- No additional roll handling is performed by this node.
- If roll-week artifacts produce wider-than-usual ranges or
  contract-handoff price gaps, those appear at the OHLCV level and
  are observable via the standard ATR-percentile / range-percentile
  classification.

What the v1 router records as a known risk:

- If the underlying Databento extraction silently included
  overlapping contract series, prior-day H/L would be computed from
  a mixed contract and could be off by the roll spread. This has
  NOT been verified end-to-end as of 2026-06-02.

Mitigation (planned, not implemented in v1):

- A `contract_cycle_week` cohort field (Section 7, level 4)
  computed from a pre-committed roll calendar. If the descriptive
  diagnostic shows zone behavior near roll dates differs materially
  from non-roll weeks, that is the trigger to revisit the loader's
  contract-overlap policy.

## 10. Candidate Output Contract

```yaml
node_id: liquidity_zone_prior_router
timestamp: datetime
lookahead_clean: true

inputs:
  current_close: float
  current_vwap: float
  atr_5min: float
  rth_open: float
  prior_day_high: float
  prior_day_low: float
  prior_day_close: float
  or_high: float | null
  or_low: float | null
  session_high: float
  session_low: float
  completed_1min_bars: count

zone:
  zone_id: string
  zone_price: float
  zone_type: pdh | pdl | pdc | or_high | or_low |
             round_25 | round_50 | round_100 |
             swing_high | swing_low |
             equal_high | equal_low |
             swept_displacement_zone   # v2
  zone_side: buy_side | sell_side | two_sided
  zone_formed_ts: datetime
  zone_observed_ts: datetime

normalized_location:
  ticks_from_rth_open: float
  ticks_from_vwap: float
  pts_from_or_high: float
  pts_from_or_low: float
  pct_of_or: float | null
  atr_normalized_distance_from_close: float
  pts_from_pdh: float
  pts_from_pdl: float
  pts_from_pdc: float
  pts_to_nearest_25: float
  pts_to_nearest_50: float
  pts_to_nearest_100: float
  time_of_day_bucket: open | midmorning | midday | afternoon | close

cohort_support:
  global_prior_n: int
  weekday_prior_n: int
  event_prior_n: int
  applied_cohort_chain: list[string]

historical_rates:  # populated only after diagnostic in Section 8 completes
  historical_target_rate: float | null
  historical_sweep_rate: float | null
  historical_rejection_rate: float | null  # conditional on sweep
  historical_acceptance_rate: float | null # conditional on sweep
  historical_displacement_rate: float | null
  beats_controls: bool | null

confidence:
  cohort_denominator: int
  control_envelope_distance_pp: float | null
  v1_confidence: low | medium | high

management_context:
  observer_label:
    inside_contraction | near_buy_side_pool | near_sell_side_pool |
    pool_swept | pool_swept_reclaimed | pool_swept_accepted |
    no_nearby_pool
  trade_state_hooks:
    - sweep_against_entry        # consumer responsibility
    - reclaim_in_entry_direction # consumer responsibility
    - accepted_against_entry     # consumer responsibility
```

The `management_context.observer_label` is the bridge to the
management observer's vocabulary (per `_PROJECT_ALTITUDE_MAP.md`
Section 6 transcript-intake observable predicates). The
`trade_state_hooks` are flags the observer combines with trade-state
(side, entry, MFE/MAE) to produce the `sweep_against_entry` /
`reclaim_in_entry_direction` / `accepted_against_entry` labels —
they are NOT trade-aware here in the node.

## 11. Lookahead discipline

Every field MUST be computed from completed bars at or before the
decision timestamp:

- 1-second bar at second S is "completed" only at second S+1's
  arrival; the bar's close is observable at S+1.
- 1-minute bar at minute M is completed at minute M+1's open; bar
  is observable from M+1 onward.
- 5-bar fractal swing pivot at bar i is observable only at bar
  i+2's close, i.e., 2 minutes after the pivot.
- Equal-high / equal-low clusters become observable when the second
  qualifying pivot becomes observable.
- PDH/PDL/PDC are observable from the next session's RTH open onward.

The diagnostic in Section 8 enforces this by sampling the zone's
`zone_observed_ts` (when it became causally available), not
`zone_formed_ts`.

## 12. Validation Plan (overlay path, NOT entry strategy)

After the descriptive diagnostic confirms (or refutes) marginal
information vs controls, the validation path is **overlay** — the
node is not deployable on its own:

1. Tag each historical trade from a current bridge-substrate
   producer (G2 3c, v2a 15c) with the zone state at the trade's
   entry timestamp and at 120s / 300s checkpoints.
2. Compare baseline trade outcomes vs the subset of trades that
   were entered into / managed inside a "near-pool" state.
3. The management-observer believe-it-bar applies (per
   `_MANAGEMENT_OBSERVER_MEMORY_LAYER.md` Section 12): pre-commit,
   day-level partition, both partitions must improve.

The descriptive diagnostic (Section 8) is the GATE for the overlay
step. If zones do not beat cheap baselines descriptively, the
overlay is not run.

## 13. Hard Rules

- No trading from zones in this design.
- No tuning of zone parameters after the descriptive diagnostic.
- Trendline liquidity is excluded from v1.
- v2 zone types (strong-high-after-BOS, support-shelf,
  swept-displacement) are added only after a v1 marginal-information
  finding justifies the additional complexity.
- OOS sealed.
- Day-level partition for any rate comparison.
- Hierarchical-prior shrinkage; cells with <30 events fall back
  toward parent prior.
- All zone rates earn belief only after beating at least three of
  the four Section 8.C controls.

## 14. First Descriptive Diagnostic Results (2026-06-02)

The v1 descriptive diagnostic
(`nb_lib/scripts/diagnostic_liquidity_zone_prior_router.py`) ran
end-to-end on the full in-sample window:

- Output:
  `nb_lib/probe_results/liquidity_zone_prior_router_v1_diagnostic.json`
- Window: 2024-08-01 .. 2026-01-31, in-sample only, OOS untouched.
- Eligible days: 379 (out of 380 trading days; first day has no
  prior-day H/L/C).
- Day-level discovery/holdout split: first 60% of unique trading
  days = DISCOVERY, last 40% = HOLDOUT (pre-committed; identical
  to management-observer split rule).

### Headline result: rejection rate given sweep

For each zone type, what fraction of swept zones see price close
back inside by ≥1 tick within 5 minutes after sweep?

| Zone | DISC rej\|swept | HOLD rej\|swept | n_swept DISC / HOLD | Pattern |
|---|---:|---:|---|---|
| **or_low**  | **89.9%** | **92.0%** | 168 / 112 | Very strong reject |
| **or_high** | **90.8%** | **88.3%** | 173 / 111 | Very strong reject |
| **pdl**     | **82.4%** | **79.6%** |  74 /  49 | Strong reject |
| **pdh**     | 71.3% | 65.2% |  94 /  66 | Moderate reject |
| pdc         | 27.4% | 14.5% | 124 /  76 | Mostly accepted (passes through) |
| random_control | 50.3% | 52.0% | 1120 / 715 | Null baseline ~50% |

All three "reject" zones (or_low, or_high, pdl, pdh) beat the
random-control null on both partitions, with the same sign and
magnitude order. The strongest zones (OR_H, OR_L) reject ~30-40pp
above null. The PDH/PDL asymmetry (PDL stronger than PDH) is itself
a useful directional signal.

### Cross-validates ORWS R1 in a different framework

The ~90% OR rejection rate reproduces the
`opening_range_width_switch` R1 finding (79.5% failed-break
reversion within 30 min) from a different angle: this diagnostic
measures within 5 min, not 30 min, AND uses the 1-tick reclaim
threshold instead of "any close back inside the OR." The agreement
across two independent measurement frameworks strengthens the
underlying claim.

### PDC is a through-level, not a reject-level

PDC (prior-day close) shows the OPPOSITE pattern: only 22.5%
rejection on aggregate, 27.4% / 14.5% by partition. Price more
often accepts beyond PDC than rejects from it. This is consistent
with PDC being a two-sided "fair-value anchor" rather than an
inducement-style stop pool. Observer use: a PDC sweep is weak
information; an OR or PDL sweep is much stronger information.

### Three implementation issues found during the diagnostic

1. **`target_rate == sweep_rate` for every zone.** The v1 `targeted`
   definition (any bar with the zone in its range ±0.25 tick) is
   satisfied whenever `swept` (≥2 ticks through) is satisfied,
   because MNQ tick size (0.25 pts) is small relative to typical
   1-second bar range. The target metric as v1-defined adds nothing
   beyond the sweep metric. A v2 should redefine `targeted` more
   strictly (e.g., "price touched within 1 tick without sweeping ≥2
   ticks") or drop the target field.

2. **Round-number zones emitted ZERO observations.** The v1 spec
   defined the round-number band as `±2 × ATR(20) on 5-min bars`,
   computed at OR end (09:45 ET). At 09:45 only 3 completed 5-min
   bars exist; the 20-bar ATR is `None`, so no round-number zones
   emit. **The round-number arm of the diagnostic did not actually
   run.** Fix for v2: use prior-day daily ATR(20) for the band,
   OR a fixed point-band, OR require fewer 5-min bars.

3. **Random-level control has sampling bias.** Random levels sampled
   uniformly between session-low and session-high at OR end sit
   inside already-visited price territory by construction. Their
   sweep rate (80.7%) exceeds every real zone's sweep rate — not
   because they're informationally richer, but because they sample
   from "easy-to-hit" levels. The rejection-given-sweep comparison
   is still clean (both zones and controls use the same gating),
   but the raw sweep-rate "beats controls" verdict is misleading.
   A v2 needs distance-matched random controls (Control 2 from
   Section 8.C of this spec, which v1 did NOT implement).

### Honest interpretation

- **Zone identification works.** OR_H/OR_L/PDH/PDL produce coherent,
  partition-consistent, control-beating rejection rates after
  sweep. These zones DO carry information beyond the random null.
- **PDC is a different kind of level** and should be tagged as
  through-prone rather than reject-prone in observer output.
- **The full random-level beats-controls comparison is broken** by
  the sampling-bias issue. The descriptive evidence stands on
  rejection-rate-given-sweep, not on raw sweep-rate vs random.
- **Round numbers are untested** because the ATR-band logic emitted
  zero zones. Pending v2 fix.
- **v2 zone types** (5-bar swings, equal highs/lows, strong-after-BOS,
  support shelf, swept-displacement) are still SPEC'd but NOT
  measured. The strongest signal from v1 (OR rejection rate) does
  not depend on them.

### Recommended next steps (operator decision)

1. **v2 patch**: fix targeted-vs-sweep distinction, fix round-number
   ATR-band fallback, add distance-matched random control. These
   are bug fixes to v1, not new search.
2. **Add 5-bar swing and equal-high/low zones** with the v1
   pre-committed parameters. The descriptive scaffold is in place.
3. **First overlay experiment**: tag G2 / v2a bridge-substrate
   trades with zone state at entry and at 120s/300s checkpoints.
   Ask whether "near a sell-side pool" (PDH or OR_H within 0.25 ×
   ATR above current price) predicts management outcome differently
   than the bare poor-entry-triage diagnostic. Day-level partition;
   same believe-it bar as management-observer Section 10A.
4. **Do NOT pursue zone-as-entry** — the closed-negative entry
   results (PDH_PDL, ROUND_VWAP, OBJ-LEVEL family) are unchanged
   by this descriptive finding. The diagnostic is for the observer
   layer.

## 14B. v2 Diagnostic Addendum (2026-06-02): three patches + corrected verdict

The v1 issues documented in Section 14 (target-vs-sweep equivalence,
round-number zero emission, control sampling bias) have been patched
in a separate v2 script that preserves v1 behavior:

- v2 implementation: `nb_lib/scripts/diagnostic_liquidity_zone_prior_router_v2.py`
- v2 JSON output:    `nb_lib/probe_results/liquidity_zone_prior_router_v2_diagnostic.json`
- v2 run log:        `nb_lib/probe_results/liquidity_zone_prior_router_v2_diagnostic_run.log`

### Patches applied

**Patch 1 — target-vs-sweep distinction.** v2 redefines outcomes:

- `reached`: any subsequent bar comes within 1 tick of the zone
  (range touches the ±1-tick band around `zone_price`).
- `swept`: trade through by ≥2 ticks in side-of-liquidity direction.
- `target_only` = `reached` AND NOT `swept` (mutually exclusive).

A side-effect of removing the v1 short-circuit (v1 only checked
sweep when `targeted` was True): v2 sweep counts are now larger
than v1 sweep counts because v1 was implicitly gating sweep on the
loose v1-targeted criterion. The v2 sweep numbers are the
unconditioned truth. This matters for the PDH/PDL verdict below.

**Patch 2 — round-number band.** v2 uses prior-day daily ATR(20)
loaded from `atr_history.csv`: `band_pts = 0.15 × prior_day_atr20`.
Fallback (if missing): 40pt fixed band. Both are pre-committed and
not tuned. In practice: ATR was available for 379/379 eligible
days, so the fallback never fired. Round_50 emitted **724**
observations (~1.9 per day); round_100 emitted **357** (~0.94 per
day). The v1 "round numbers emitted ZERO" bug is fixed.

**Patch 3 — distance-matched random controls.** v2 adds Control 2
from Section 8.C: for each emitted zone, one control level placed
at the zone's signed `ticks_from_vwap` distance ± 5 ticks
(uniform random within the band). VWAP is the cumulative
RTH-VWAP at OR end. Side mirrors the zone's side (apples-to-apples
sweep gating). v1's in-range random control is retained for
continuity but the distance-matched control is now the honest
baseline.

### Headline result: rejection-rate-given-sweep against the v2
distance-matched control

This is the prompt's key question.

| Zone | rej\|sw % | n_swept | v2-ctrl rej\|sw | margin | verdict |
|---|---:|---:|---:|---:|---|
| **round_50** | **93.9%** | 623 | 73.5% | **+20.4pp** | beats |
| **round_100** | **93.9%** | 311 | 73.5% | **+20.3pp** | beats |
| **or_low** | **90.4%** | 281 | 73.5% | **+16.8pp** | beats |
| **or_high** | **89.8%** | 284 | 73.5% | **+16.2pp** | beats |
| pdl | 65.8% | 152 | 73.5% | **−7.8pp** | **loses** |
| pdh | 53.4% | 206 | 73.5% | **−20.1pp** | **loses** |
| pdc | 11.9% | 379 | 73.5% | −61.7pp | loses (through-prone, as expected) |

The v2 distance-matched control's own rejection-given-sweep is
**73.5%** (far higher than v1's 51% in-range control). That
73.5% is the honest baseline: random levels at the same VWAP
distance as the real zones get rejected after sweep ~73% of the
time, simply because the geometric placement near typical sweep
distances biases toward reverting back through. This was the
sampling-bias issue v1 documented.

### Partition consistency (DISCOVERY / HOLDOUT)

| Zone | DISC rej\|sw | n_sw | HOLD rej\|sw | n_sw |
|---|---:|---:|---:|---:|
| or_high | 90.8% | 173 | 88.3% | 111 |
| or_low | 89.3% | 169 | 92.0% | 112 |
| round_50 | 93.3% | 404 | 95.0% | 219 |
| round_100 | 93.2% | 205 | 95.3% | 106 |
| pdh | 54.5% | 123 | 51.8% | 83 |
| pdl | 66.3% | 92 | 65.0% | 60 |
| pdc | 15.0% | 227 | 7.2% | 152 |
| v2 dist-matched ctrl | 74.6% | 1391 | 71.8% | 843 |
| v1 in-range ctrl | 41.8% | 1362 | 37.9% | 912 |

Both partitions tell the same story. OR levels and round numbers
beat the v2 control by 16-22pp in both partitions; PDH/PDL fall
below the v2 control in both partitions; PDC remains through-prone
in both partitions.

### Target_only is essentially empty across all zones

For every zone type, `target_only_rate` is ≤0.3%. When a bar comes
within 1 tick of any zone (PDH/PDL/PDC/OR/round), it almost always
also sweeps by ≥2 ticks within the same evaluation. MNQ ticks
(0.25 points) are simply too small relative to typical 1-second
bar range for a "touch without sweep" outcome to be common. The
target_only field IS now distinct from sweep (v1 had them
trivially identical), but it carries almost no observations. It
remains a valid v2 field; it just doesn't add much information.

### What changed from v1 (and why)

| Zone | v1 rej\|sw | v2 rej\|sw | Δ | Reason |
|---|---:|---:|---:|---|
| or_high | 89.8% | 89.8% | 0pp | sweep population unchanged |
| or_low | 90.7% | 90.4% | -0.3pp | tiny |
| pdh | 68.8% | 53.4% | -15.4pp | v2 sweep population larger (160→206); v1 was gating on loose targeted |
| pdl | 81.3% | 65.8% | -15.5pp | same reason as pdh |
| pdc | 22.5% | 11.9% | -10.6pp | same reason; pdc sweep is now 100% (full session range almost always covers both sides of pdc) |
| round_50 | n/a (zero obs) | 93.9% | — | round-number band fix |
| round_100 | n/a | 93.9% | — | round-number band fix |

The v1 sweep population for PDH/PDL was a subset gated by v1's
loose `targeted` check. That gating turned out to select for
more-reject-prone outcomes, biasing v1 rejection rates upward.
Once removed in v2, PDH/PDL rejection rates fell into the
neighborhood of the distance-matched control. This is the gas
leaking out of the v1 PDH/PDL claim.

### Honest interpretation

- **OR_H / OR_L survive the corrected control.** Rejection-given-
  sweep is partition-consistent (~89-92% on both partitions)
  and 16-17pp above the distance-matched control. This is the
  cleanest finding the diagnostic has produced. It cross-validates
  the ORWS R1 result (79.5% reversion within 30 min) in a tighter
  framework (5 min, ≥1-tick reclaim).
- **Round numbers survive the corrected control.** Rejection-given-
  sweep is ~94% on both partitions, 20pp above the distance-matched
  control. This is a NEW finding made possible by the v2 round-band
  fix. n_swept = 623 (round_50) + 311 (round_100) → plenty.
- **PDH / PDL do NOT survive the corrected control.** PDH falls
  20pp below the distance-matched control; PDL falls ~8pp below.
  The v1 finding that PDH/PDL "show meaningful liquidity zones"
  was a control-bias artifact. The v2 distance-matched control
  (a level at the same VWAP distance as PDH/PDL) is rejected
  after sweep MORE often than PDH/PDL themselves are. Retracting
  the v1 PDH/PDL claim is the honest move.
- **PDC remains through-prone.** 11.9% rejection (88.1% acceptance).
  This is even more extreme than v1's 22.5%, again because v2 has
  a larger swept population. As a label for the observer, PDC =
  "fair-value anchor, expect through-trading."
- **Closed-negative entry candidates are NOT revived.** PDH_PDL
  liquidity-sweep-reversal was already closed-negative as an
  entry strategy; this descriptive update REINFORCES that closure
  rather than weakening it. The observer-context use of PDH/PDL
  also looks weaker than it did under v1.

### Verdict per the prompt's mapping

The prompt defined three verdicts:

- `descriptive-diagnostic-v2-confirmed`: corrected controls
  preserve the v1 pattern → not appropriate (PDH/PDL did not
  survive).
- `descriptive-diagnostic-v2-partial`: OR/PD levels still look
  useful but controls weaken the conclusion → **this is the
  honest fit**. OR_H/OR_L, round_50, round_100 still beat the
  corrected control by 16-20pp; PDH/PDL do not survive.
- `descriptive-diagnostic-v2-failed`: corrected controls erase
  the edge → not appropriate (OR and round-numbers survive
  clearly).

**Verdict: `descriptive-diagnostic-v2-partial`.**

Carried forward as informative-vs-distance-matched-control zone
types (both partitions, n_swept ≥ 280):

- `or_high`, `or_low`, `round_50`, `round_100`

Retracted as informative (do NOT carry forward as a strong
observer signal):

- `pdh`, `pdl`

Retained as a "through-prone" label (not "reject-prone"):

- `pdc`

### Trial-budget note (per _CANDIDATE_SUPPORT_STACK.md §4)

This is one diagnostic run on an existing trade-data corpus, not
a search over multiple policies. No parameter tuning was performed
after seeing results: the three patches were pre-specified by the
v1 Section 14 self-report and the prompt; band parameters and
control geometry were locked before running v2. The descriptive
diagnostic does not gate any candidate verdict; it informs the
observer-context layer per Section 12 (overlay validation
deferred to a future operator decision).

### Recommended next steps (operator decision; not taken here)

1. Stop here on the descriptive arm. The router has both a
   confirmed signal (OR levels, round numbers) and a documented
   retraction (PDH/PDL). The observer can consume this as-is.
2. If overlay validation is later authorized: tag G2 / v2a bridge
   trades with `near_sell_side_pool` / `near_buy_side_pool` /
   `pool_swept_reclaimed` states from the SURVIVING zone types
   only (OR_H/OR_L, round_50, round_100). Day-level partition,
   inherits Section 12 believe-it-bar. Do NOT include PDH/PDL in
   the first overlay since they did not survive the v2 control.
3. Continue to defer trendline liquidity (Section 5.F).
4. v2 zone types not yet measured (5-bar swings, equal-highs/lows,
   BOS-strong, support-shelf, swept-displacement) remain spec'd
   but not built; their priority drops because round_50/round_100
   already explain most of what "non-OR/non-PD reject-prone
   levels" look like.

## 15. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-06-02 | `note-only` | Designed as management-observer input layer per operator 2026-06-02 transcript-intake direction. Boring-zone v1 taxonomy locked: PDH/PDL/PDC, OR_H/OR_L, round numbers, 5-bar fractal swings, equal highs/lows within 1-tick tolerance. Trendlines excluded. Strong-after-BOS / support shelf / swept-displacement zones deferred to v2. Pre-committed parameters in Section 5; pre-committed diagnostic protocol in Section 8; pre-committed controls in Section 8.C. Descriptive diagnostic ready for implementation; overlay validation deferred until descriptive evidence exists. |
| 2026-06-02 | `descriptive-diagnostic-v1-complete` | v1 descriptive diagnostic ran end-to-end on 2024-08-01..2026-01-31 in-sample, OOS sealed. 1,895 zone observations + 2,274 random-control observations across 379 eligible days. Headline: rejection-rate-given-sweep is the cleanest metric and clearly differentiates zones from null: OR_H/OR_L ~90%, PDL ~80%, PDH ~70%, PDC ~25% (through-prone), random-control ~51%. Results partition-consistent (both DISCOVERY and HOLDOUT show same sign and magnitude order). Three implementation issues identified and documented in Section 14: target_rate==sweep_rate (target metric too loose), round-number zones emitted ZERO (ATR-band logic requires 20×5-min bars unavailable at OR end), random-level control has sampling bias (sweep-rate comparison invalid but rejection-rate-given-sweep comparison clean). Round-number arm did not actually run; pending v2 fix. v2 zone types (swings, equal-highs/lows, BOS-strong, support-shelf, swept-displacement) still SPEC'd but not measured. Output JSON: `nb_lib/probe_results/liquidity_zone_prior_router_v1_diagnostic.json`. Verdict: zones DO carry information beyond random null on rejection-after-sweep; descriptive evidence exists; overlay validation against G2/v2a bridge substrate is the recommended next step but requires operator decision. |
| 2026-06-02 | `descriptive-diagnostic-v2-partial` | v2 patches applied: target-vs-sweep distinction (reached / swept / target_only mutually meaningful), round-number band from prior-day daily ATR(20) at 0.15× multiplier (724 round_50 + 357 round_100 observations across 379 eligible days; ATR available all 379 days; fallback band never fired), and distance-matched random control (one matched control per zone at ±5 ticks of zone's signed ticks-from-VWAP distance). v2 distance-matched control's rejection-given-sweep is 73.5% — much higher than v1's in-range control's 51% — confirming the v1 sampling-bias issue. Against the v2 control: OR_H/OR_L (~90%, +16-17pp), round_50/round_100 (~94%, +20pp) survive with partition consistency. PDH (-20pp), PDL (-8pp) FAIL to beat the distance-matched control; v1 PDH/PDL claim is RETRACTED as a control-bias artifact. PDC remains through-prone (11.9% rejection). Surviving observer signals: OR_H, OR_L, round_50, round_100. Retracted: PDH, PDL. Retained-as-label: PDC (through-prone). Output JSON: `nb_lib/probe_results/liquidity_zone_prior_router_v2_diagnostic.json`. Overlay validation deferred to operator decision; if pursued, use only the surviving zone types. |
| 2026-06-02 | `overlay-mixed` | First overlay experiment ran against the G2/v2a bridge substrate. Pre-committed contract: tag each trade by proximity to a SURVIVING reject-prone zone (or_high, or_low, round_50, round_100; PDH/PDL excluded per v2 retraction) within 1R of the entry price in favorable or adverse direction. Pre-committed believe-it bar: n≥20 per population per partition; \|WR-gap\|≥0.10 same sign on both partitions; \|$gap\|≥$50 same sign on both partitions. Day-level partition. Results: G2 (n=118) shows DIRECTION-CONSISTENT but UNDERPOWERED separation on both flags — pool_in_favor (DISC WRgap +0.159, HOLD +0.111) and pool_against (DISC WRgap +0.163, HOLD +0.071). Positive WR-gap = flagged trades have LOWER WR than baseline (consistent reading: near-reject-prone-zone trades on G2 fare worse, either by clipping winners short of TP or by the zone-side stop-out path). v2a (n=40) does NOT replicate the G2 pattern; flag-direction signs flip between partitions. Combined (n=158) preserves G2's direction. NO cell clears the believe-it bar (holdout $gap collapses for both flags; flagged-n is below 20 in multiple cells). Top verdict: **overlay-mixed**. The router's zone definitions show consistent observational direction on G2 but the magnitude weakens out-of-discovery, so this is not yet a basis for any management action. Output JSON: `nb_lib/probe_results/overlay_liquidity_zone_router_v2_g2_v2a.json`. Trial-budget tally: 1 overlay contract × 3 substrates = 3 trials (per `_CANDIDATE_SUPPORT_STACK.md` §4). |
