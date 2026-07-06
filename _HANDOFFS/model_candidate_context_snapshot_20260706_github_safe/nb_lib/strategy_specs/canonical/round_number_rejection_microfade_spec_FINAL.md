---
status: "spec-drafted-final"
---

# Round Number Rejection Microfade — Canonical Strategy Specification (FINAL)

**Strategy ID**: `round_number_rejection_microfade`
**Status**: FINAL SPEC DRAFTED, not implemented, not tested
**Created**: 2026-05-13
**Canonical path**: `nb_lib/strategy_specs/canonical/round_number_rejection_microfade_spec_FINAL.md`
**Candidate lineage**: `nb_lib/strategy_specs/candidates/round_number_rejection_microfade.md`

Round Number Rejection Microfade is a new candidate family (not a v2 of
an existing strategy). It tests whether brief 1-minute sweeps of
50-point psychological levels on MNQ that fail to hold beyond the level
produce short-lived mean-reversion opportunities on the inside of the
level. Phase 1 (entry design) was preflighted at 1,465 accepted signals
over the in-sample window with 50.4% long share and clean distribution
across all measured dimensions. Phase 2 (this spec) extends Phase 1
with v2.4 adaptive management primitives focused on friction mitigation
and time-bounded thesis enforcement, the two dominant risks at the
preflight-projected trade rate.

All values below are pre-committed informed priors unless explicitly
identified as inherited from a prior spec. They are not calibrated
performance parameters.

---

## 0. Outcome Priors And Scope Acknowledgments

### 0.1 Priors (updated with preflight evidence)

Preflight evidence for Phase 1 entry mechanics:
- Signal count: 1,465 over in-sample window (~3 trades/day average).
- Direction balance: 50.4% long (perfectly symmetric).
- Distribution: clean per-month, per-weekday, per-bucket; no clustering.
- Edge-sensitivity: no edge-bound predicates.
- Friction risk: ~$10,250 in commission alone over the in-sample window.

Pre-test priors for the full Phase 2 strategy:

| Outcome | Prior | Meaning |
|---|---:|---|
| No edge / account failure | 0.55 | Round-number rejection thesis is contested in literature; high trade rate exacerbates friction; account fails |
| Weak in-sample only | 0.20 | PF in [1.00, 1.50]; not OOS-eligible |
| OOS-eligible edge | 0.10 | PF >= 1.50 with sufficient n + management attribution |
| Implementation or realism blocker | 0.10 | Management mechanics fail to fire; or friction model surfaces issues not in preflight |
| Signal count materially different in implementation | 0.05 | Mid-trade management filters change the effective trade count vs preflight |

These are methodology priors, not statistical estimates. The 0.55 base
rate reflects:
1. The contested empirical status of round-number effects in liquid
   futures.
2. The 7-fleet failure pattern across prior canonical alphas (none
   reached PF >= 1.50 in-sample).
3. The friction concern: at the preflight-projected rate, gross edge
   must exceed ~$7 per trade (commission alone) before any net
   profitability surfaces.

### 0.2 Scope

This spec defines strategy behavior only. It assumes the v2.4 library
primitives (`apply_bracket_update`, `force_exit_strategy`, management
event logger, 5-minute swing detector) are available — they landed in
nb_lib v2.4 per `nb_lib_v2_4_management_infrastructure_report.md`.

No new source code is drafted here. No new library primitives are
required. A separate strategy-implementation iteration consumes this
spec.

Iteration budget under Option 2 discipline: **2 design revisions
remaining** after this Phase 2 spec lands. If in-sample results expose
a structural issue, the operator may choose to apply a revision
(Iteration 2 of 2) and re-run; if a third issue emerges, the candidate
closes.

### 0.3 Structural difference from previous strategies

This is a NEW family, not a v2. The family-closure rule does not bind
this design to be structurally different from anything specific. The
distinct family attributes:

| Axis | Round-number microfade | Prior strategies |
|---|---|---|
| Anchor | Absolute price levels (50-pt grid) | Volatility (ATR), indicator (VWAP, EMA), or fractal swings |
| Signal class | Level-rejection (mean-reversion) | Continuation (NB / PRJ_3 / ema_trend / atr_regime), mean-reversion vs VWAP (vwap_stretch_snapback), chop-fade (closed) |
| Decision granularity | 1-minute primary, 1-second execution | 5-min primary (atr_regime / chop-fade), 1-min primary (vwap / needle_drop_v2) |
| Adaptive layer count | 3 specialists + no global confidence score | needle_drop_v2 had 4 specialists + multi-component confidence score |
| Trade rate | High (~3/day average) | Low (NB ~1.5/day; PRJ_3 ~0.02/day; chop-fade ~0.03/day at 58.0) |
| Bracket invariant | Strict tighten-only (no widening) | needle_drop_v2 had bounded TP2 widening |

The structural novelty is the **absolute-level anchor** plus the
**friction-dominated regime** (high trade rate) — neither of which has
been tested in the project.

---

## 1. Strategy Thesis

Round-number rejection microfade tests whether 1-minute bars that
sweep 50-point psychological levels on MNQ and close back on the
inside of the level produce **short-lived, level-anchored
mean-reversion opportunities** that the strategy can capture with
small, fast-resolving brackets.

The market thesis:

- 50-point levels (and especially 100-point multiples as a natural
  subset) attract resting limit orders, stop placements, and
  discretionary attention.
- A 1-minute bar that pokes through the level and closes back on the
  inside is structural evidence that the breakout failed: the move
  did not attract follow-through.
- The trade thesis is a small fade with stop just beyond the
  rejection extreme and target at the next inside subdivision (25
  points) or next round level (50 points).
- The thesis is intrinsically TIME-BOUNDED: if the fade hasn't
  resolved within ~5-7 minutes, the rejection is being re-tested or
  the level is breaking down. Either way, the original thesis is
  invalidated.

The counter-hypothesis is serious:

- Round-number effects in liquid futures markets are contested in the
  literature. Some research shows weak effects; some shows none.
- At the preflight-projected trade rate, **friction is the dominant
  risk**: ~$7/trade commission × ~1,465 trades = ~$10,250 baseline
  cost. Gross edge must exceed this before net profitability appears.
- The 7-fleet failure pattern suggests methodology-level structural
  difficulty across multiple signal classes at this granularity.

The thesis is FALSIFIABLE in two senses:

1. If in-sample PF is below 1.0 or the account FAILs (as 7 prior
   canonical alphas did), the round-number microfade thesis is
   empirically refuted.
2. If in-sample PF >= 1.50 but OOS fails, the in-sample result was
   selection on the high-trade-rate noise.

---

## 2. Entry Signal And Timing

Entry mechanics are **PRESERVED VERBATIM from Phase 1**. The 8.0 pt
proximity guard is LOCKED for this iteration despite preflight Section
E identifying it as the loosest predicate. Tightening it is reserved
for Iteration 2 if needed.

### 2.1 Reference to Phase 1 spec

The complete entry specification lives at
`nb_lib/strategy_specs/candidates/round_number_rejection_microfade.md`
Sections 2.3–2.6 plus 3.4 (risk guards) plus 8.4 (per-day limits).

Brief recap (no normative authority — Phase 1 spec is the source of truth):

- **Session**: 09:45–15:30 ET, RTH only, no half-days.
- **Round-level grid**: 50-point spacing; 100-pt as natural subset.
- **Sweep depth**: `>= 0.25 pt` beyond the level (1 tick).
- **Close-back-inside**: 1-min bar's `close` on the inside of the
  level after the sweep.
- **Proximity guard**: `|close - level| <= 8.0 pt` (LOCKED).
- **Risk-guard band**: `raw_stop_pts in [2.0, 6.0]`.
- **Two-sided**: long and short setups symmetric.
- **Entry fill**: T+1 second pattern, BAND_B entry slippage.

### 2.2 What carries forward unchanged

The Phase 1 4-predicate stack per direction is locked:
1. Session window
2. Sweep depth (`>= 0.25 pt`)
3. Close-back-inside the level
4. Proximity guard (`<= 8.0 pt`)

Plus risk-guard band on `raw_stop_pts` (Section 3.4 of Phase 1).
Plus ambiguous-two-sided-signal skip rule.

No entry-side modifications in Phase 2.

---

## 3. Risk And Position Sizing

PRESERVED from Phase 1 unchanged. Fixed-dollar risk, fixed contract
bounds. Adaptive logic is in BRACKETS only, never in sizing.

### 3.1 Fixed Dollar Risk

```text
risk_dollars = 300.00
point_value = 2.00 dollars per MNQ point per contract
```

### 3.2 Initial Stop Distance

Per Phase 1 Section 3.2. For SHORT: `raw_stop_pts = sweep_extreme -
entry_price + 0.50`. For LONG: symmetric. The 0.50 buffer is 2 ticks
beyond the rejection extreme.

### 3.3 Position Size Formula And Bounds

```text
raw_contracts = floor(risk_dollars / (raw_stop_pts * point_value))
contracts = clamp(raw_contracts, min=1, max=15)
```

### 3.4 Risk Guards

Per Phase 1 Section 3.4. Skip if `raw_stop_pts < 2.0` or `> 6.0`,
`contracts < 1` or `> 15`, `atr_5m_20 <= 0` or NaN, compliance not
ACTIVE.

### 3.5 Apex Compliance

Use `ComplianceTracker` with Apex 50K EOD eval rules. Outer loop must
not call `trade_one_day` after `AccountState.FAILED`.

---

## 4. Adaptive Layers

Round-number microfade has **three adaptive layers**, deliberately few.
The HARD-HALT-MAXIMALIST-MANAGEMENT bound (>6 specialists, >20
informed-prior parameters) is well respected — this spec uses 3
specialists and 11 informed-prior management parameters.

### 4.1 Layer A: Entry-side level proximity

Phase 1's round-level proximity guard (`|close - level| <= 8.0 pt`) is
a regime-conditional filter — the level itself is the regime. Phase 1
established this; Phase 2 inherits unchanged.

### 4.2 Layer B: Time-bounded thesis enforcement

Microfade is intrinsically time-bounded. If a fade hasn't reached TP1
within a small number of minutes, the rejection is being re-tested or
the level is breaking down, and the original thesis is invalidated.

This is implemented as a specialist (Section 4.4 below).

### 4.3 Layer C: Volatility shock defense

Same defensive pattern as needle drop v2: tighten stop if ATR ratio
expands or ATR percentile spikes. Round-number microfade is especially
vulnerable to this regime change because chop-to-trend transitions are
the classic level-rejection failure mode.

### 4.4 Parallel specialist composer

Three management specialists evaluate **in parallel field-by-field**
at every management timestamp. This matches needle drop v2's
composition mechanism, which already has library support via
`apply_bracket_update`.

**Specialist set**:

1. **`time_to_resolution_manager`**: force-exit if the trade has not
   reached TP1 within `MAX_MINUTES_TO_TP1 = 7` minutes. Captures the
   "microfade thesis is time-bounded" invariant. If TP1 has fired,
   this specialist becomes inactive (the runner has its own time
   handling per Section 8.2).

2. **`volatility_shock_manager`**: defensive tightening when ATR
   regime shifts. If `atr_ratio_5_30 >= 1.30` OR `atr_percentile_60
   >= 0.85`, propose tightening the stop to within `0.75 *
   raw_stop_pts` of current price (if tighter than current stop).
   Does not propose TP changes.

3. **`structure_trail_manager`**: post-TP1 only. Uses the v2.4
   5-minute swing detector. After TP1 fires, the manager proposes
   trailing the runner's stop to the most recent confirmed 5-min
   swing low (long) or swing high (short), but only if the swing is
   closer to current price than the current stop.

State representation per specialist (Section 4.5).

### 4.5 State representation

Each specialist receives a `MicrofadeManagementState` dict at every
evaluation. Fields required:

```python
@dataclass
class MicrofadeManagementState:
    ts: pd.Timestamp                 # current 1-second bar timestamp
    entry_ts: pd.Timestamp
    direction: int                   # +1 long, -1 short
    entry_price: float
    current_price: float             # most recent 1-second bar close
    minutes_since_entry: float
    tp1_fired: bool
    contracts_open: int
    current_brackets: dict           # stop_price, tp1_price, tp2_price, be_arm_pts
    initial_stop_pts: float
    raw_stop_pts: float              # = initial_stop_pts (preserved)
    level: float                     # the round level being faded
    atr_5m_20: float
    atr_ratio_5_30: float
    atr_percentile_60: float
    last_confirmed_5m_swing_high: float | None
    last_confirmed_5m_swing_low: float | None
```

All state inputs must be computed lookahead-clean (right-edge <= ts).

### 4.6 Composition rules

Per-field combination at each management timestamp:

```text
force_exit: True if ANY specialist proposes force_exit
stop_price (long):  TIGHTEST of proposed stops above current stop and below current price
stop_price (short): TIGHTEST of proposed stops below current stop and above current price
tp1_price (long):   LOWEST proposed TP1 above current price and at or below current TP1
tp1_price (short):  HIGHEST proposed TP1 below current price and at or above current TP1
tp2_price (long):   LOWEST proposed TP2 above current price and at or below current TP2
tp2_price (short):  HIGHEST proposed TP2 below current price and at or above current TP2
be_arm_pts:         LOWEST proposed be_arm above 0 and at or below current be_arm_pts
```

**Tighten-only invariant**: every accepted field change must be a
TIGHTENING vs current. Widening is NOT permitted at any time on any
field for any reason. This is a stricter invariant than needle drop v2
(which permitted bounded TP2 widening for runner extension) because the
microfade thesis does not extend — there is no "let it run further"
scenario for round-level fades.

### 4.7 Specialist evaluation cadence

Specialists evaluate once per completed 1-minute bar after entry, plus
on every 1-second bar for `time_to_resolution_manager`'s force-exit
trigger only. The 1-second cadence for the time check is necessary
because the time bound (`MAX_MINUTES_TO_TP1 = 7`) does not align with
1-minute boundaries.

The other two specialists (volatility and structure trail) need
indicator updates at 5-minute granularity; evaluating them more
frequently than 1-minute would not reveal new state.

---

## 5. Bracket Geometry

Phase 1 had simple static brackets. Phase 2 replaces them with the
following structure that supports adaptive specialist proposals.

### 5.1 Initial Brackets

Computed at entry from values available at signal timestamp:

**Stop**: per Phase 1 Section 3.2, `entry_price ± raw_stop_pts`.

**TP1** (next 25-pt subdivision inside the level):

```text
For SHORT (faded sweep of level_above L):
    tp1_price = L - 25.0
For LONG (faded sweep of level_below L):
    tp1_price = L + 25.0
```

TP1 closes 50% of contracts, rounded down. If `contracts == 1`, TP1
is disabled and the full position becomes the runner.

**TP2** (next 50-pt subdivision inside the level — typically the next
round level itself):

```text
For SHORT: tp2_price = L - 50.0
For LONG:  tp2_price = L + 50.0
```

**BE arm**:

```text
be_arm_pts = 0.60 * raw_stop_pts
be_offset_pts = 0.0
```

The 0.60×R BE arm is earlier than the typical 0.75×R because microfade
trades resolve quickly and protective BE matters more than upside
optionality.

Validation:

```python
assert stop_price < entry_price < tp1_price <= tp2_price  # long
assert stop_price > entry_price > tp1_price >= tp2_price  # short
assert raw_stop_pts > 0
assert be_arm_pts > 0
```

If validation fails, skip the trade.

### 5.2 TP1 Fill

50% of contracts close at TP1 (rounded down). Remainder is the runner.
If contracts == 1, no partial possible; runner is the full position.

### 5.3 Runner geometry

Microfade does NOT use a fixed-MFE runner trail. After TP1 fires:
- The runner has a TP2 target at the next 50-pt subdivision.
- The runner's stop ratchets to BE+offset (BE-only-runner mode;
  `runner_trail_distance_pts = None` in lifecycle API).
- The `structure_trail_manager` specialist may further tighten the
  runner's stop to the most recent confirmed 5-min swing low/high.

### 5.4 Adaptive bracket update rules

Per specialist (proposals only — composition rules in Section 4.6
determine which fields actually update):

**`time_to_resolution_manager`**:

```python
if not state.tp1_fired and state.minutes_since_entry >= 7.0:
    return BracketProposal(force_exit=True,
                           exit_reason="microfade_time_invalidated",
                           specialist_id="time_to_resolution")
```

**`volatility_shock_manager`**:

```python
vol_shock = (state.atr_ratio_5_30 >= 1.30
             or state.atr_percentile_60 >= 0.85)
if vol_shock:
    proposed_stop = state.current_price + (
        -state.direction * 0.75 * state.raw_stop_pts
    )  # for long: below current; for short: above current
    return BracketProposal(stop_price=proposed_stop,
                           specialist_id="volatility_shock")
```

**`structure_trail_manager`** (post-TP1 only):

```python
if not state.tp1_fired:
    return BracketProposal()  # no proposal pre-TP1
if state.direction > 0:
    proposed_stop = state.last_confirmed_5m_swing_low
else:
    proposed_stop = state.last_confirmed_5m_swing_high
if proposed_stop is None:
    return BracketProposal()
return BracketProposal(stop_price=proposed_stop,
                       specialist_id="structure_trail")
```

### 5.5 Bracket update validation

Every proposal goes through `lifecycle.apply_bracket_update(...)` per
the v2.4 library API. The library handles:
- Atomic all-or-nothing acceptance.
- Ordering validation (stop < entry < tp1 <= tp2 for long).
- Latency model (effective at first bar > ts).
- Event logging.

The strategy never modifies bracket state directly. All updates flow
through the library.

### 5.6 Tighten-only rule

Strict tighten-only on all fields. Widening is FORBIDDEN. This is the
strictest invariant in the project — needle drop v2 permitted bounded
TP2 widening; round-number microfade does not.

### 5.7 Strategy force-exit conditions

Conditions that fire `lifecycle.force_exit_strategy(...)`:

1. **`microfade_time_invalidated`**: `time_to_resolution_manager`
   fires if not at TP1 within 7 minutes.
2. **`microfade_eod_buffer`**: standard Section 8.3 time exit
   (Section 8.2 cap of 20 min OR EOD-flat deadline minus 90 seconds,
   whichever earlier).

No other force-exit triggers in Phase 2.

---

## 6. Indicators, Data, And Assumed Library API

### 6.1 Required indicators

| Field | Source | Rule |
|---|---|---|
| Round-level grid | price-only | 50-pt spacing; computed with floor/ceil at each bar |
| `atr_5m_20` | 5-min bars | Wilder ATR(20), completed bars only |
| `atr_percentile_60` | 5-min ATR(20) over 60 RTH sessions | completed bars only |
| `atr_ratio_5_30` | 5-min ATR(5) / ATR(30) | completed bars only |
| `last_confirmed_5m_swing_low/high` | 5-min bars | v2.4 swing detector; confirmation right-edge <= state.ts |

ATR ratio uses 5-min bars (not 1-min as some prior strategies) because
the management evaluation timeframe is 1-minute primary plus 5-minute
indicators for regime signals.

### 6.2 Data Source

MNQ 1-second OHLCV from project Databento store. Derive 1-min and
5-min bars via `to_minutes` and `to_five_min` per project convention.

### 6.3 Assumed Library API (v2.4)

This strategy consumes the following v2.4 primitives:

```python
# Per spec Section 4.6 + 5.5:
result = lifecycle.apply_bracket_update(
    ts=state.ts,
    stop_price=new_stop_or_none,
    tp1_price=new_tp1_or_none,
    tp2_price=new_tp2_or_none,
    be_arm_pts=new_be_arm_or_none,
    reason="microfade_<specialist_id>",
    metadata={...},
)

# Per spec Section 5.7:
result = lifecycle.force_exit_strategy(
    ts=state.ts,
    exit_reason="microfade_time_invalidated",
    metadata={...},
)

# Per spec Section 14.1 attribution:
logger.log_management_proposal(...)
logger.log_bracket_update_accepted(...)
logger.log_bracket_update_rejected(...)
logger.log_strategy_force_exit(...)

# Per Section 6.1:
swings = detect_5m_swings(bars_5m, confirmation_pattern="5_bar_pivot")
```

All four primitives landed in nb_lib v2.4. No new library work
required.

### 6.4 FILL_ASSUMPTIONS extension

```text
FILL_ASSUMPTIONS["round_number_rejection_microfade"] = BAND_B
```

This is a 1-line additive change to `nb_lib/trade_record.py`'s
`FILL_ASSUMPTIONS` set, done by the implementation iteration.

---

## 7. Pre-Committed Pass Criteria

### 7.1 In-sample verdict thresholds

In-sample window: 2024-08-01 through 2026-01-31.

| Verdict | Criteria |
|---|---|
| **Edge candidate** | PF >= 1.50 AND n >= 200 AND account state != FAILED AND specialist attribution met |
| **Weak/noise** | 1.00 <= PF < 1.50 OR (n >= 200 AND PF >= 1.50 but attribution not met) |
| **Rejected** | PF < 1.00 OR account FAILED |

The n >= 200 minimum is meaningfully high because the preflight
projected 1,465 raw accepted signals; if the actual implementation
produces <200 trades, the management filtering is far more aggressive
than expected and the strategy is materially different from what was
preflighted.

PF >= 1.50 is the standard OOS-eligible bar across the project.

### 7.2 Trade count minimum

`n >= 200` is required. If fewer, the result is inconclusive UNLESS
the account FAILed (which is a definitive rejection regardless of n).

### 7.3 Specialist attribution requirements

The implementation report must include:

- Number of evaluations per specialist.
- Number of proposals per specialist.
- Number of accepted field changes per specialist.
- Force-exit events per specialist.
- P&L of trades affected by each specialist.
- P&L of trades with no accepted management changes.

Minimum attribution to validate the management thesis:

```text
At least 30% of completed trades must have at least one accepted
management update (proposal accepted AND latency-applied).
At least 2 of 3 specialists must contribute accepted updates on at
least 10% of trades.
```

If PF >= 1.50 but attribution fails (e.g., only `volatility_shock`
fires and the other two contribute nothing), the strategy may still
be an edge candidate, but the **microfade adaptive management thesis
is not confirmed**. In that case the result is "edge from entry; not
from management."

### 7.4 Direction asymmetry tolerance

Phase 1 preflight showed 50.4% long share. Acceptable Phase 2
direction P&L asymmetry:

```text
abs(long_total_pnl - short_total_pnl) / abs(total_pnl) <= 0.65
```

If asymmetry exceeds 65%, flag in results report. Strategy is not
rejected on direction asymmetry alone, but the report must call it
out and the operator must decide whether OOS is justified.

### 7.5 OOS trigger conditions

OOS validation may run only if ALL are true:

```text
in_sample_pf >= 1.50
in_sample_n >= 200
account_state != FAILED
specialist_attribution_minimum_met == True
no HARD-HALT fired during implementation or test
direction_pnl_asymmetry <= 0.65
```

If any condition fails, OOS remains sealed. The candidate moves to
`tested-rejected` (or `tested-weak` if PF in [1.00, 1.50] with
attribution met).

### 7.6 Halt and review conditions during implementation

Implementation must halt and consult the operator if:

- The spec constants cannot be pinned exactly in tests.
- Mid-trade update API requires a public signature change outside
  v2.4's API (should not happen; v2.4 is sufficient by design).
- Strategy needs OOS data to compute any in-sample indicator.
- Management update logging cannot distinguish proposal vs
  acceptance.
- The strategy generates a materially different signal count from
  preflight (e.g., <300 or >2000 in-sample trades) without
  identifiable cause (could indicate a predicate-drift bug).

---

## 8. Mechanics

### 8.1 Evaluation cadence

- Entry predicates: once per completed 1-minute bar in the entry
  window.
- Management specialists: once per completed 1-minute bar after
  entry, plus 1-second cadence ONLY for
  `time_to_resolution_manager`'s force-exit clock.

### 8.2 Time exit

The Phase 1 static scaffold's 20-minute time exit is REPLACED by:

```text
Force exit any remaining position at the EARLIER of:
- entry_ts + 20 minutes (Phase 1 cap; preserved)
- microfade_time_invalidated trigger (7-min no-TP1 trigger;
  Section 4.4)
- 15:58:30 ET (EOD-flat compliance)
```

Exit reason for time exits:

```text
"microfade_time_exit"        for the 20-min cap (post-TP1)
"microfade_time_invalidated" for the 7-min pre-TP1 trigger
```

### 8.3 EOD Flat

Standard compliance EOD-flat at 15:58:30 ET on regular days (90-sec
buffer before close). Strategy time exits should normally fire before
compliance EOD-flat.

### 8.4 Cooldowns and per-day limits

PRESERVED from Phase 1 Section 8.4 unchanged:

- Per-level 30-min cooldown (no re-fade of the same level for 30 min
  after a fade).
- Per-trade 15-min cooldown (no new trade for 15 min after an exit).
- Max 4 trades per RTH day.
- Max 3 long, 3 short per day.

### 8.5 Strategy force-exit semantics

For `microfade_time_invalidated`, `microfade_time_exit`, and any other
strategy-decision exit (none currently planned beyond these two):

- Exit on the next available 1-second bar STRICTLY AFTER the
  management decision timestamp.
- Apply BAND_B exit friction (TP-class slippage = 0 per BAND_B; no
  adverse overshoot since these are voluntary).
- If TP1 has fired, close only the runner.
- If TP1 has not fired, close the full open position.
- Record `exit_reason` exactly as the strategy reason string.
- Record `strategy_exit=True` in metadata.

### 8.6 Runtime assertions

At minimum, in production code path (not just tests):

```python
assert state.ts > state.entry_ts
assert state.current_price > 0
assert state.entry_price > 0
assert state.initial_stop_pts > 0
assert state.compliance_state.name != "FAILED"
assert state.current_brackets.stop_price != state.current_brackets.tp1_price
assert state.minutes_since_entry >= 0
```

After every accepted bracket update via `apply_bracket_update`:

```python
assert new_stop is None or current_stop <= new_stop < state.current_price  # long
assert new_tp1 is None or state.current_price < new_tp1 <= current_tp1
assert new_tp2 is None or new_tp1 <= new_tp2 <= current_tp2
assert new_be_arm_pts is None or 0 < new_be_arm_pts <= current_be_arm_pts
```

(Symmetric inequalities for short.)

Any assertion failure is HARD-HALT, not silent skip.

---

## 9. HARD-HALT Conditions

Implementation or test must halt on:

1. **HARD-HALT-OOS-LEAK**: any row with timestamp >= 2026-02-01 used
   for in-sample indicator warmup or results.
2. **HARD-HALT-LOOKAHEAD**: any predicate or specialist reads a
   derived bar whose right edge is after the decision timestamp.
3. **HARD-HALT-API-MISSING**: any v2.4 library method behaves
   differently from this spec's expectation. (Should not happen; v2.4
   landed clean per the v2.4 report.)
4. **HARD-HALT-SPEC-DRIFT**: implementation constants differ from
   this FINAL spec without a new spec revision.
5. **HARD-HALT-REGRESSION**: existing nb_lib tests fail after the
   strategy implementation iteration.
6. **HARD-HALT-ACCOUNT-FAILED-CONTINUE**: outer strategy loop opens a
   new trade after `AccountState.FAILED`.
7. **HARD-HALT-UNLOGGED-MANAGEMENT**: a bracket proposal or accepted
   update occurs without event logging sufficient for Section 7.3
   attribution.
8. **HARD-HALT-LEVEL-GRID-DRIFT**: the strategy uses a level spacing
   other than 50.0 (no 25-pt microgrid; no 100-pt coarser grid) per
   Phase 1 inheritance.
9. **HARD-HALT-WIDENING**: any bracket update widens (vs tightens) a
   field. Tighten-only is strict per Section 5.6.
10. **HARD-HALT-ENTRY-MODIFICATION**: any deviation from Phase 1
    entry predicates (preserved verbatim).
11. **HARD-HALT-PROXIMITY-GUARD-DRIFT**: the 8.0 pt proximity guard
    changed without spec revision.

---

## 10. Open Questions Deferred

### 10.1 Whether the 8.0 pt proximity guard is right

Deferred to Iteration 2 (under Option 2 discipline if needed). The
preflight identified substantial headroom; tightening to e.g. 4.0 pt
would materially reduce signal count and may improve trade quality.
This is the most likely target if Iteration 2 fires.

### 10.2 Whether the 7-min time invalidation is right

Deferred. The 7 minutes is an informed prior. If results show many
trades exiting via time-invalidation that would have eventually
reached TP1 given more time, this may need extension. If too few
exit via time-invalidation, the specialist is design-dead.

### 10.3 Whether structure_trail is materially active

Deferred. Round-number rejections may resolve too quickly for
confirmed 5-min swings to form before TP1 fires. If
`structure_trail_manager` fires <5% of post-TP1 trades, it's
effectively design-dead and a future spec revision could remove it.

### 10.4 Whether the tighten-only invariant is too strict

Deferred. If results show many trades reaching TP2 just-barely and
the strategy would have benefited from extension, a bounded-widening
mechanism similar to needle drop v2's runner ceiling could be
considered in a future iteration.

### 10.5 Whether the 30-min per-level cooldown is right

Deferred. The preflight showed this cooldown filtered 33.9% of raw
signals — heavily binding. If implementation results show that the
"second-touch" of a level (after the cooldown) is systematically a
worse fade than the first, the cooldown could be lengthened.

---

## 11. Wiki References And Informed-Prior Status

Preserved from Phase 1 (entry):

| Reference | Status | Usage |
|---|---|---|
| `round_number_rejection_microfade.md` Phase 1 | entry-design | Entry predicates 2.3-2.6, risk guards 3.4, per-day limits 8.4 |
| `needle_drop_v2_spec_FINAL.md` | spec-drafted | Parallel composer pattern (Section 4.6 here) |
| `vwap_stretch_snapback_spec_FINAL.md` | tested-rejected | 16-section format reference; BAND_B convention; T+1s entry pattern |
| `nb_lib_v2_4_management_infrastructure_report.md` | (v2.4 library) | API consumed |
| `nb_lib_round_number_rejection_microfade_preflight_report.md` | (preflight) | Signal-count expectations + edge sensitivity findings |

New informed priors introduced by Phase 2 management:

| Parameter | Value | Source |
|---|---:|---|
| `MAX_MINUTES_TO_TP1` | 7.0 | Time-bounded thesis; informed prior |
| `volatility_shock.atr_ratio_threshold` | 1.30 | Slightly lower than needle drop v2's 1.35 due to higher MNQ chop sensitivity at microfade scale |
| `volatility_shock.atr_pct_threshold` | 0.85 | Matches needle drop v2 |
| `volatility_shock.stop_tighten_x_risk` | 0.75 | New (tighten stop to 75% of original raw_stop_pts above current price) |
| Tighten-only invariant | strict | Mechanism-appropriate (microfade does not extend) |
| Specialist count | 3 | Per "deliberate, not maximalist" framing |
| Attribution min (Section 7.3) | 30% trades, 2 of 3 specialists | Informed prior; first project use of these specific thresholds |
| n minimum (Section 7.2) | 200 | Anchored to preflight projection of ~1,465 |

11 informed-prior management parameters total. Well below the
HARD-HALT-MAXIMALIST-MANAGEMENT threshold of 20.

---

## 12. FILL_ASSUMPTIONS Extension

Round-number microfade inherits BAND_B friction:

- Entry slippage per existing primitive convention (0.5 pt).
- Stop overshoot per BAND_B (1.16 pt).
- TP slippage 0.0 per BAND_B.
- Commission $0.35 per side per contract.

**Bracket update latency** (per v2.4 library + needle drop v2 spec
Section 12):

```text
Bracket update latency in backtest: effective at the first 1-second
bar strictly after the management evaluation timestamp.
```

If price crosses the OLD bracket before the update-effective bar, the
old bracket wins. If price crosses the NEW bracket only after the
update is effective, the new bracket applies. This prevents
same-timestamp bracket rewrites from creating unrealistic fills.

Strategy-decision force exits (via `force_exit_strategy`) use TP-class
friction (no adverse overshoot). Voluntary exits do not incur the
stop-class slippage; commission still applies.

---

## 13. OOS Reservation And Validation Triggers

### 13.1 Reserved window

```text
2026-02-01 through 2026-05-04
```

In-sample script must assert before any results computation:

```python
assert WINDOW_END < pd.Timestamp("2026-02-01", tz="America/New_York")
```

### 13.2 OOS eligibility

Per Section 7.5: all six conditions must be true to consume the OOS
slot.

### 13.3 OOS report requirements

If OOS is triggered, the OOS report must include:

- PF, P&L, trade count, win rate.
- Account outcome.
- Direction P&L breakdown (long / short).
- Management attribution using same specialist metrics as in-sample.
- Degradation ratio vs in-sample.
- Statement that OOS was consumed for round_number_rejection_microfade.

If OOS fails to preserve edge (PF degrades by >50% OR account fails),
the family closes. Do not design a v2 from the OOS result; that would
itself constitute post-result iteration that exceeds the bounded
budget.

---

## 14. Test Plan

### 14.1 Library tests (v2.4 — already passing)

Verify 375/375 still pass before implementation iteration commits any
library changes. (None are expected; v2.4 should be sufficient.)

### 14.2 Strategy constant pinning tests

The implementation iteration must add tests pinning:

- Phase 1 entry constants (50-pt grid, 0.25-pt sweep, 8.0-pt
  proximity, 2.0-6.0-pt stop band)
- `MAX_MINUTES_TO_TP1 = 7.0`
- `volatility_shock.atr_ratio_threshold = 1.30`
- `volatility_shock.atr_pct_threshold = 0.85`
- `volatility_shock.stop_tighten_x_risk = 0.75`
- BE arm = 0.60 × raw_stop_pts
- TP1 = level ± 25, TP2 = level ± 50
- Time exits: 20 min cap (post-TP1) + 7 min pre-TP1 invalidation
- Per-day limits: 4 total, 3 long, 3 short, 15-min cooldown, 30-min
  per-level

### 14.3 Synthetic strategy behavior tests

Minimum synthetic-data tests:

- Long entry fires on round-level downsweep + close-back.
- Short entry fires on round-level upsweep + close-back.
- Entry skips when proximity > 8.0 pt.
- Entry skips when sweep_depth < 0.25 pt.
- Entry skips when raw_stop_pts > 6.0.
- `time_to_resolution_manager` force-exits after 7 min pre-TP1.
- `volatility_shock_manager` tightens stop on ATR ratio >= 1.30.
- `structure_trail_manager` proposes nothing pre-TP1.
- Tighten-only invariant rejects any widening proposal.
- Per-day cap of 4 binds.
- Per-level 30-min cooldown binds.

### 14.4 In-sample run

Run the complete in-sample window once after tests pass. Produce:

- Trade CSV with management attribution columns.
- Management event CSV (proposal / accepted / rejected / applied /
  force-exit events).
- Results report including all Section 7.3 attribution statistics.
- Changelog.

No parameter changes after the run.

---

## 15. Selection Bias Notes

This design is explicitly post-result in two ways:

1. **Round-number microfade was chosen AFTER chop-fade closed.** This
   is a post-result pivot — the candidate was not the first choice.
   The methodology cost is acknowledged.

2. **The 8.0 pt proximity guard is preserved despite preflight
   evidence of substantial headroom.** Iteration 1 of Option 2
   discipline showed mean signal distance from level = 1.86 pt with
   cap at 8.0. The operator chose to preserve the cap for Phase 2 and
   reserve the 2 remaining iterations for post-test problems.

3. **Specialist set choices were informed by needle drop v2 + chop-fade
   binding-constraint findings.** The 3-specialist count is a
   deliberate response to chop-fade's compound-stack lesson and needle
   drop v2's per-specialist attribution lesson.

4. **The friction concern is post-preflight knowledge.** The 1,465
   signal count was unknown at Phase 1 design time. Phase 2's emphasis
   on time-bounded exits and tighten-only invariant is partly a
   response to this finding.

If the in-sample test passes and OOS fails, the family closes per
Section 13.3 — no further iteration is permitted on this candidate.
This bounds the selection-bias surface that compounds across the
pivot + preservation + management-design choices.

---

## 16. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | Created as untested-ideation by Codex 5.5 CLI batch 2. |
| 2026-05-13 | `entry-design` | Phase 1 entry signal designed following chop-fade closure. |
| 2026-05-13 | `spec-drafted-final` | FINAL spec drafted. Phase 2 management framework added (3 specialists: time_to_resolution, volatility_shock, structure_trail; parallel field-by-field composition; strict tighten-only). Phase 1 entry preserved. v2.4 primitives consumed. 2 design revisions remaining under Option 2 discipline. |

End of specification.
