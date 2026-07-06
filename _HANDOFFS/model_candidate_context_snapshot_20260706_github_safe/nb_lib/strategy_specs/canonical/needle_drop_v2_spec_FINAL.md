---
status: "spec-drafted-final"
---

# Needle Drop V2 - Canonical Strategy Specification (FINAL)

**Strategy ID**: `needle_drop_v2`
**Status**: FINAL SPEC DRAFTED, not implemented, not tested
**Created**: 2026-05-13
**Canonical path**: `nb_lib/strategy_specs/canonical/needle_drop_v2_spec_FINAL.md`
**Candidate lineage**: `nb_lib/strategy_specs/candidates/needle_drop_adaptive_management_classifier.md`

Needle Drop V2 is a structurally different second design in the Needle
Drop family. It is not v1 with tuned thresholds. V1 used a priority-order
classifier over multiple wiki patterns, tighten-only bracket updates, and
a two-sided VWAP snapback entry. V2 uses a single long-only VWAP snapback
entry source, a higher-timeframe participation gate, and a parallel
field-by-field management composer driven by confidence state.

All values below are pre-committed informed priors unless explicitly
identified as inherited from a prior FINAL spec. They are not calibrated
performance parameters.

---

## 0. Outcome Priors And Scope Acknowledgments

### 0.1 Priors

Needle Drop V2 is a real edge attempt, but its priors are modest. The
project has seven tested-rejected strategies in the current fleet,
including both continuation and mean-reversion concepts. V1's
counterfactual showed limited signal and branch dominance rather than a
clear management edge.

Pre-test priors:

| Outcome | Prior | Meaning |
|---|---:|---|
| No edge / account failure | 0.55 | Strategy fails Apex 50K EOD eval or PF < 1.0 |
| Weak in-sample only | 0.25 | PF 1.0 to 1.5, not OOS-eligible |
| OOS-eligible edge | 0.12 | PF >= 1.5 with sufficient trade count and attribution |
| Implementation or realism blocker | 0.08 | Mid-trade management API or logging proves insufficient |

These are not statistical claims. They are methodology priors used to
keep the result interpretation sober.

### 0.2 Scope

This spec defines strategy behavior only. It assumes a later library
iteration will add:

- Mid-trade bracket adjustment support to `TradeLifecycle`.
- Strategy-reason force exits that are distinct from compliance exits.
- Event logging for each management proposal and each accepted bracket
  change.

No source code is drafted here.

### 0.3 Structural Difference From V1

V2 differs from v1 on four architecture axes:

1. **Coordination mechanism**: v1 used first-match-wins priority order.
   V2 evaluates specialists in parallel and composes proposed changes by
   bracket field.
2. **Entry source**: v1 used two-sided VWAP snapback. V2 is long-only
   and requires a higher-timeframe participation gate.
3. **Risk invariant**: v1 was tighten-only for every field. V2 keeps
   stop and TP1 conservative, but permits bounded TP2 widening only in a
   high-confidence runner state.
4. **State axis**: v1 matched discrete wiki branches. V2 computes a
   deterministic confidence score from thesis alignment, momentum
   quality, and time decay.

These are structural changes under the family closure rule. Thresholds
inside this spec must not be tuned after seeing the in-sample result.

---

## 1. Strategy Thesis

Needle Drop V2 tests whether a rejected but direction-asymmetric VWAP
snapback entry becomes viable when paired with deterministic management
that distinguishes "mean reversion completed" from "runner still
healthy."

The underlying market idea is narrow:

- Downside VWAP stretches in MNQ sometimes snap back when the broader
  intraday environment remains constructive.
- The original two-sided VWAP strategy failed overall, but the in-sample
  failure was direction-asymmetric: longs made money while shorts lost
  enough to fail the account.
- V1 management was too blunt. It mostly capped winners through one
  dominant branch and did not let favorable long trades extend.

V2 therefore tests a deliberately constrained version:

- Long entries only.
- Trade only when the higher-timeframe session state is not bearish.
- Take partial profit at a nearby structural level.
- Let the runner extend beyond VWAP only when confidence remains high.
- Exit or tighten when confidence collapses.

The counter-hypothesis is equally important: the long-only observation may
be post-result noise, and no management layer may rescue a weak entry.
OOS reservation is the control for that bias.

---

## 2. Entry Signal And Timing

### 2.1 Market And Session

- Market: MNQ continuous front-month futures.
- Data source: 1-second OHLCV store.
- Session: RTH only.
- Entry evaluation window: 09:45:00 through 14:45:00 US/Eastern.
- New entries are disabled on half-days unless the implementation has a
  verified half-day EOD-flat deadline from `TradingCalendar`.
- Maximum trades: one accepted entry per calendar trading day.

### 2.2 Derived Bars

All derived bars are built from 1-second source bars.

- 1-minute bars: half-open intervals `[minute, minute + 1min)`, labeled
  by left edge.
- 5-minute bars: half-open intervals `[ts, ts + 5min)`, labeled by left
  edge.
- 30-minute bars: half-open intervals `[ts, ts + 30min)`, labeled by
  left edge.

At decision timestamp `T`, a derived bar is usable only if:

```text
bar.left_edge + bar_duration <= T
```

This right-edge rule is mandatory for lookahead cleanliness.

### 2.3 Higher-Timeframe Participation Gate

V2 is long-only and should not fade downside stretches during a clear
bearish intraday regime.

At the signal decision timestamp, the last completed 30-minute bar must
satisfy:

```text
last_30m.close >= session_vwap_30m
EMA20_30m >= EMA50_30m
```

Both conditions are required. If either value is unavailable due to
warmup, the day is skipped.

Rationale: this gate is an informed-prior response to vwap's observed
short-side failure and to the general fleet pattern of morning
continuation failure. It is not data-derived proof of edge.

### 2.4 Long VWAP Stretch Rejection Signal

Compute session VWAP and session standard deviation on completed
1-minute bars from RTH open through the signal bar.

Definitions:

```text
stretch_sigma = (last_1m.close - session_vwap) / session_stdev
```

A long setup is valid when all conditions are true:

```text
time_in_window == True
participation_gate == True
session_stdev > 0
stretch_sigma <= -2.0
last_1m.close > last_1m.open
last_1m.close > prior_1m.high
last_1m.low < prior_1m.low
```

Plain English: price is stretched at least 2 session standard deviations
below VWAP, prints a rejection candle, closes above the prior 1-minute
high, and the broader 30-minute environment is not bearish.

### 2.5 Entry Fill

The signal timestamp is the right edge of the confirming 1-minute bar.
Entry uses `resolve_entry_fill` semantics:

```text
entry_ts = first 1-second bar strictly after signal_ts
entry_price = entry bar open plus BAND_B entry slippage
```

The entry must satisfy:

```python
assert entry_ts > signal_ts
assert entry_ts.date() == signal_ts.date()
```

If no 1-second bar exists strictly after the signal timestamp within RTH,
skip the trade.

---

## 3. Risk And Position Sizing

### 3.1 Fixed Dollar Risk

V2 uses fixed-dollar risk, not fixed contracts.

```text
risk_dollars = 400.00
point_value = 2.00 dollars per MNQ point per contract
```

Initial stop distance is ATR-derived in Section 5. Position size:

```text
raw_contracts = floor(risk_dollars / (initial_stop_pts * point_value))
contracts = clamp(raw_contracts, min=1, max=20)
```

If `raw_contracts < 1`, skip the trade.

The max of 20 MNQ is below the Apex eval contract limit and matches a
conservative PA Level 1 ceiling. This is an informed-prior choice to keep
V2 from repeating the tested fleet's 15-contract fixed-risk distortion
when volatility changes.

### 3.2 Risk Guards

Skip the trade if:

```text
initial_stop_pts < 8
initial_stop_pts > 60
contracts < 1
contracts > 20
```

The lower bound avoids oversized contract counts from tiny stops. The
upper bound avoids signals where the stop is too wide for Apex 50K EOD
constraints.

### 3.3 Compliance

The strategy must use `ComplianceTracker` with Apex 50K EOD eval rules.
The outer strategy loop must not call `trade_one_day` or open a new trade
after the tracker enters `AccountState.FAILED`.

Any violation of this rule is a HARD-HALT.

---

## 4. Adaptive Layers

V2 has three adaptive layers. They are intentionally few and explicit.

### 4.1 Layer A: Entry Regime Gate

The 30-minute participation gate in Section 2.3 is a regime-conditional
entry filter. It is evaluated once before entry and never changes an open
trade.

Adaptive source: level/regime state via 30-minute VWAP and EMA alignment.

### 4.2 Layer B: Confidence-Conditional Management

Every completed 1-minute bar after entry, compute:

```text
confidence = 0.4 * thesis_alignment
           + 0.4 * momentum_quality
           + 0.2 * time_decay
```

All components are in `[0.0, 1.0]`.

#### Thesis Alignment

For this long-only strategy:

```text
target_anchor = signal_vwap
progress = (current_price - entry_price) / (target_anchor - entry_price)
```

If `target_anchor <= entry_price`, thesis alignment is 0 and the trade is
not eligible for runner extension.

Otherwise:

```python
if current_price < entry_price - 0.50 * atr_5m_20:
    thesis_alignment = 0.0
elif progress >= 1.00:
    thesis_alignment = 0.25
elif progress >= 0.75:
    thesis_alignment = 0.60
elif progress >= 0.00:
    thesis_alignment = 1.00
else:
    thesis_alignment = 0.50
```

Rationale: confidence in the original snapback thesis is highest while
the trade is moving from entry toward VWAP. Once VWAP is reached, the
mean-reversion thesis is mostly satisfied; confidence in further movement
must come from momentum, not the original stretch.

#### Momentum Quality

Use the last five completed 1-minute bars ending at evaluation timestamp.

```text
favorable_count = number of bars where close > prior_close
momentum_quality = favorable_count / 5
```

If fewer than five completed 1-minute bars exist after entry,
use all available completed bars. If zero exist, `momentum_quality = 0.5`.

#### Time Decay

```text
minutes_since_entry = (state.ts - entry_ts).total_seconds() / 60
time_decay = 0.5 ** (minutes_since_entry / 20.0)
```

The 20-minute half-life is an informed prior. It makes a 5-minute trade
fresh, a 20-minute trade half-stale, and a 40-minute trade mostly stale.

#### Confidence Bands

| Confidence | Mode | Management intent |
|---:|---|---|
| `>= 0.70` | high | Preserve or extend runner if momentum confirms |
| `0.40 <= c < 0.70` | standard | Keep brackets, allow normal BE behavior |
| `0.20 <= c < 0.40` | defensive | Tighten stop and cap TP2 |
| `< 0.20` | invalidated | Force exit |

### 4.3 Layer C: Volatility Shock Defense

At each management evaluation:

```text
vol_shock = atr_percentile_60 >= 0.85 or atr_ratio_5_30 >= 1.35
```

If `vol_shock` is true and the trade has not reached TP1, V2 must not
widen TP2 and must allow defensive stop tightening. If TP1 has fired,
runner extension is disabled for that evaluation.

Adaptive source: volatility-regime state. This is defensive only.

### 4.4 Parallel Specialist Composer

V2 uses four management specialists:

1. `confidence_manager`
2. `vwap_completion_manager`
3. `volatility_shock_manager`
4. `structure_trail_manager`

All specialists evaluate at every management timestamp. Each may return a
proposal:

```python
BracketProposal(
    stop_price=None,
    tp1_price=None,
    tp2_price=None,
    be_arm_pts=None,
    force_exit=False,
    exit_reason=None,
    specialist_id=None,
)
```

Composition rules for long-only V2:

```text
force_exit: accepted if any specialist proposes force_exit
stop_price: highest proposed stop above current stop and below current price
tp1_price: lowest proposed TP1 above current price and at or below current TP1
tp2_price:
  - if runner_extension_allowed: highest valid TP2 up to runner ceiling
  - otherwise: lowest valid TP2 above current price and at or below current TP2
be_arm_pts: lowest valid BE arm above 0 and at or below current BE arm
```

This field-by-field composition is the main coordination change from v1.
No specialist can silently suppress another specialist's proposal because
of priority order. The event log must record every proposal and whether it
was accepted or rejected.

---

## 4.5 Per-Direction-Per-Day Dedup

V2 is long-only, so the dedup rule is:

```text
maximum one accepted long trade per RTH trading day
```

If a signal occurs and the trade is skipped for data warmup, risk bounds,
or compliance state, later signals may still be considered. Once a trade
is accepted, no further entries are allowed that day.

Any short entry is a HARD-HALT.

---

## 5. Bracket Geometry

### 5.1 Initial Brackets

All initial brackets are computed at entry from values available at the
signal timestamp or entry timestamp.

```text
initial_stop_pts = 1.00 * atr_5m_20_at_signal
stop_price = entry_price - initial_stop_pts
```

TP1:

```text
tp1_price = nearest 50-point psychological level strictly between
            entry_price and signal_vwap
```

If no 50-point level exists strictly between entry and signal VWAP:

```text
tp1_price = entry_price + 0.50 * (signal_vwap - entry_price)
```

TP2:

```text
tp2_price = signal_vwap
```

BE arm:

```text
be_arm_pts = 0.50 * (tp1_price - entry_price)
```

Validation:

```python
assert stop_price < entry_price < tp1_price <= tp2_price
assert initial_stop_pts > 0
assert be_arm_pts > 0
```

If validation fails, skip the trade and log the skip reason.

### 5.2 TP1 Fill

TP1 closes 50% of open contracts, rounded down. If contract count is 1,
TP1 is disabled and the whole position is managed as a single runner.

### 5.3 Runner Ceiling

V2 permits bounded TP2 widening only for the runner.

At entry:

```text
runner_ceiling = min(
    entry_price + 2.50 * initial_stop_pts,
    signal_vwap + 0.75 * atr_5m_20_at_signal
)
```

TP2 may never be widened above `runner_ceiling`.

Rationale: v1 often capped winners, but unrestricted widening turns a
VWAP reversion strategy into an undefined trend-following strategy. The
ceiling gives the runner space without erasing the original thesis.

### 5.4 Runner Extension Eligibility

Runner extension is allowed only when all conditions are true:

```text
tp1_fired == True
confidence >= 0.70
momentum_quality >= 0.80
vol_shock == False
current_price < runner_ceiling
minutes_since_entry <= 45
```

If eligible:

```text
proposed_tp2 = runner_ceiling
```

If not eligible, TP2 can only tighten.

### 5.5 Defensive Tightening

When `0.20 <= confidence < 0.40`:

```text
proposed_stop = max(current_stop, current_price - 0.50 * atr_5m_20_live)
proposed_tp2 = min(current_tp2, current_price + 0.75 * atr_5m_20_live)
proposed_be_arm_pts = min(current_be_arm_pts, 0.25 * initial_stop_pts)
```

All live ATR values use the last completed 5-minute bar at the
evaluation timestamp.

### 5.6 Confidence Collapse Exit

When `confidence < 0.20`, propose:

```text
force_exit = True
exit_reason = "needle_drop_v2_confidence_exit"
```

Exit semantics are defined in Section 8.5.

### 5.7 Structure Trail

After TP1 has fired, the structure trail manager may propose:

```text
proposed_stop = last_confirmed_5m_swing_low - 0.25
```

The swing low must be confirmed by two completed 5-minute bars on each
side. It is usable only if the right edge of the confirming bar is at or
before the evaluation timestamp.

The proposal is accepted only if:

```text
current_stop < proposed_stop < current_price
```

---

## 6. Indicators, Data, And Assumed Library API

### 6.1 Required Indicators

| Field | Source | Rule |
|---|---|---|
| `session_vwap` | 1-minute RTH bars | completed bars only |
| `session_stdev` | 1-minute closes | completed bars only |
| `stretch_sigma` | close, VWAP, stdev | completed signal bar |
| `atr_5m_20` | 5-minute bars | Wilder ATR(20), completed bars |
| `atr_percentile_60` | daily/session ATR history | 60 prior sessions only |
| `atr_ratio_5_30` | 5-minute ATR short/long | completed bars only |
| `EMA20_30m` | 30-minute close | completed bars only |
| `EMA50_30m` | 30-minute close | completed bars only |
| `last_confirmed_5m_swing_low` | 5-minute bars | two-bar confirmation |

Any NaN value required for entry causes a skip. Any NaN value required
for a management specialist causes that specialist to return no proposal
for that evaluation.

### 6.2 Required State Object

The strategy implementation should construct a management state at each
completed 1-minute evaluation:

```python
NeedleDropV2State(
    ts,
    entry_ts,
    signal_ts,
    entry_price,
    current_price,
    signal_vwap,
    current_brackets,
    initial_stop_pts,
    runner_ceiling,
    tp1_fired,
    contracts_open,
    atr_5m_20,
    atr_percentile_60,
    atr_ratio_5_30,
    last_1m,
    recent_1m_bars,
    last_confirmed_5m_swing_low,
    minutes_since_entry,
    compliance_state,
)
```

### 6.3 Assumed Mid-Trade Adjustment API

The later library iteration must provide an API equivalent to:

```python
lifecycle.apply_bracket_update(
    ts=state.ts,
    stop_price=new_stop_or_none,
    tp1_price=new_tp1_or_none,
    tp2_price=new_tp2_or_none,
    be_arm_pts=new_be_arm_or_none,
    reason="needle_drop_v2",
    metadata={...},
)
```

Required behavior:

- Validate bracket ordering before accepting the update.
- Reject any update that would create an immediate impossible bracket.
- Log previous values, proposed values, accepted values, specialist ids,
  and rejection reasons.
- Preserve existing partial-fill state.
- Do not change public entry/exit fill conventions.

### 6.4 Assumed Strategy Force-Exit API

The later library iteration must provide an API equivalent to:

```python
lifecycle.force_exit_strategy(
    ts=state.ts,
    exit_reason="needle_drop_v2_confidence_exit",
    exit_price_source="next_1s_open",
    metadata={...},
)
```

This must be separate from compliance force exits. It closes the full
remaining open quantity, or the runner if TP1 already fired.

---

## 7. Pre-Committed Pass Criteria

### 7.1 In-Sample Verdict Thresholds

Use the in-sample window defined by the project methodology:

```text
2024-08-01 through 2026-01-31
```

Verdict thresholds:

| Verdict | Criteria |
|---|---|
| Edge candidate | PF >= 1.50, n >= 20, account not FAILED |
| Weak/noise | 1.00 <= PF < 1.50 or n < 20 with positive P&L |
| Rejected | PF < 1.00 or account FAILED |

The account state criterion is mandatory. A strategy that shows PF >=
1.50 but fails Apex 50K EOD eval is not deployable and must be marked
"edge but not Apex-deployable" rather than OOS-ready.

### 7.2 Trade Count Minimum

`n >= 20` is required for any meaningful in-sample conclusion. If fewer
than 20 trades fire, the result is inconclusive unless the account fails.

### 7.3 Specialist Attribution

The implementation report must include:

- Number of evaluations per specialist.
- Number of proposals per specialist.
- Number of accepted field changes per specialist.
- P&L of trades where each specialist affected at least one bracket.
- P&L of trades with no accepted management changes.

Minimum contribution for V2 to be considered a management success:

```text
At least 25% of completed trades must have at least one accepted
management update, and at least two of four specialists must contribute
accepted updates on at least 10% of trades.
```

If PF >= 1.50 but all benefit comes from entry selection and management
barely fires, the strategy may still be an edge candidate, but the Needle
Drop management thesis is not confirmed.

### 7.4 Direction Asymmetry

V2 is long-only. Therefore long-vs-short disparity is not applicable.

Replacement check:

```text
Any short trade count > 0 is HARD-HALT.
```

The results report must still state that direction asymmetry was handled
by disabling shorts, and this choice is a post-result design risk.

### 7.5 OOS Trigger

OOS validation is allowed only if all are true:

```text
in_sample_pf >= 1.50
in_sample_n >= 20
account_state != FAILED
specialist_attribution_minimum_met == True
no HARD-HALT fired
```

If any condition fails, OOS remains sealed.

### 7.6 Halt And Review Conditions During Implementation

Implementation must halt if:

- The spec constants cannot be pinned exactly in tests.
- Mid-trade update API requires a public signature change outside the
  planned library work.
- The strategy needs OOS data to compute any in-sample indicator.
- Management update logging cannot distinguish proposal vs acceptance.
- The implementation discovers v2 is behaviorally identical to v1 for
  material trades.

---

## 8. Mechanics

### 8.1 Evaluation Cadence

Management evaluates once per completed 1-minute bar after entry.

If entry fills at `10:23:01`, the first management evaluation is at
`10:24:00`, using the completed bar `[10:23:00, 10:24:00)`.

There is no immediate post-entry management evaluation.

### 8.2 Time Exit

Force exit any remaining position at the earlier of:

```text
entry_ts + 60 minutes
15:58:30 ET on full RTH days
12:58:30 ET on half-days, if half-day trading is enabled
```

Exit reason:

```text
"needle_drop_v2_time_exit"
```

### 8.3 EOD Flat

The strategy must also use the existing EOD compliance check. Strategy
time exit should normally occur before compliance EOD flat. If compliance
flat fires first, log it as compliance, not strategy exit.

### 8.4 Cooldown

V2 uses 1-minute cadence. No separate cooldown is required. A future
sub-minute variant would need cooldown logic, but that is outside this
FINAL spec.

### 8.5 Strategy Force-Exit Semantics

For `needle_drop_v2_confidence_exit` and `needle_drop_v2_time_exit`:

- Exit on the next available 1-second bar open strictly after the
  management decision timestamp.
- Apply BAND_B exit friction according to the primitive convention.
- If TP1 has fired, close only the runner.
- If TP1 has not fired, close the full open position.
- Record `exit_reason` exactly as the strategy reason string.
- Record `strategy_exit=True` in metadata if the trade schema supports
  it; otherwise include the flag in `strategy_extras`.

### 8.6 Runtime Assertions

At minimum:

```python
assert state.ts > state.entry_ts
assert state.current_price > 0
assert state.entry_price > 0
assert state.initial_stop_pts > 0
assert state.runner_ceiling > state.entry_price
assert state.compliance_state.name != "FAILED"
assert 0.0 <= confidence <= 1.0
assert state.current_brackets.stop_price < state.current_price
assert state.current_brackets.tp1_price > state.current_price or state.tp1_fired
assert state.current_brackets.tp2_price > state.current_price
```

After composition:

```python
assert new_stop is None or current_stop <= new_stop < state.current_price
assert new_tp1 is None or state.current_price < new_tp1 <= current_tp1
assert new_tp2 is None or state.current_price < new_tp2 <= state.runner_ceiling
assert new_be_arm_pts is None or 0 < new_be_arm_pts <= current_be_arm_pts
```

Any assertion failure is HARD-HALT, not silent skip.

---

## 9. HARD-HALT Conditions

Implementation or test must halt on:

1. **HARD-HALT-OOS-LEAK**: any row with timestamp >= 2026-02-01 is used
   for in-sample indicator warmup, threshold selection, or results.
2. **HARD-HALT-SHORT-TRADE**: any short entry is generated.
3. **HARD-HALT-LOOKAHEAD**: any predicate uses a derived bar whose right
   edge is after the decision timestamp.
4. **HARD-HALT-API-MISSING**: mid-trade bracket adjustment or
   strategy-reason force exit cannot be implemented without changing the
   intended public behavior of existing lifecycle paths.
5. **HARD-HALT-SPEC-DRIFT**: implementation constants differ from this
   FINAL spec without a new spec revision.
6. **HARD-HALT-REGRESSION**: existing nb_lib tests fail after the library
   work or strategy implementation.
7. **HARD-HALT-ACCOUNT-FAILED-CONTINUE**: the outer strategy loop opens a
   new trade after `AccountState.FAILED`.
8. **HARD-HALT-UNLOGGED-MANAGEMENT**: a bracket proposal or accepted
   update occurs without event logging sufficient for attribution.

---

## 10. Open Questions Deferred

### 10.1 Whether Long-Only Is Real Edge Or Selection Bias

Deferred to OOS. The long-only choice is post-result design informed by
the vwap report. There is no clean in-sample way to remove that bias.

### 10.2 Whether TP2 Widening Should Be Larger

Deferred. V2 uses a bounded runner ceiling. Increasing the ceiling after
seeing results would be parameter tuning.

### 10.3 Whether Shorts Can Be Reintroduced

Deferred. Reintroducing shorts would be a different strategy family
because V2's selection-bias control depends on declaring long-only before
test.

### 10.4 Whether Confidence Weights Are Optimal

Deferred permanently for V2. The weights `0.4/0.4/0.2` are informed
priors. Tuning them on in-sample results violates the family rule.

---

## 11. Wiki References And Informed-Prior Status

Referenced wiki/spec materials:

| Reference | Status | Usage |
|---|---|---|
| `vwap_stretch_snapback_spec_FINAL.md` | tested-rejected | Entry concept, VWAP stretch definitions, psychological TP1 convention |
| `needle_drop_adaptive_management_classifier.md` | untested-ideation | Family lineage and v1 contrast |
| `_METHODOLOGY_repertoire.md` | methodology | Adaptive-layer and curve-fit framing |
| `_METHODOLOGY_data_store.md` | methodology | Data availability and OOS guard |

The confidence score, runner ceiling, and specialist composer are new V2
informed-prior design choices. They are not validated by existing wiki
entries.

---

## 12. FILL_ASSUMPTIONS Extension

Needle Drop V2 inherits BAND_B friction assumptions:

- Entry slippage per existing primitive convention.
- Stop overshoot per BAND_B.
- TP slippage 0.0 unless the primitive changes globally.
- Commission $0.35 per side per contract.

Extension needed for mid-trade management:

```text
Bracket update latency in backtest: effective at the first 1-second bar
strictly after the management evaluation timestamp.
```

If price crosses the old bracket before the update-effective bar, the old
bracket wins. If price crosses the new bracket only after the update is
effective, the new bracket applies.

This prevents same-timestamp bracket rewrites from creating unrealistic
fills.

---

## 13. OOS Reservation And Validation Triggers

### 13.1 Reserved Window

The reserved OOS window remains:

```text
2026-02-01 through 2026-05-04
```

In-sample scripts must assert:

```python
assert WINDOW_END < pd.Timestamp("2026-02-01", tz="America/New_York")
```

or an equivalent date-only guard before any results are computed.

### 13.2 OOS Eligibility

OOS may be run only if Section 7.5 triggers are met. If OOS is run and
fails to preserve edge, the Needle Drop family closes. Do not design a
third version from the OOS result.

### 13.3 OOS Report Requirements

If OOS is triggered, the OOS report must include:

- PF, P&L, trade count, win rate.
- Account outcome.
- Management attribution using the same specialist metrics as in-sample.
- Degradation ratio versus in-sample.
- Statement that OOS was consumed for Needle Drop V2.

---

## 14. Test Plan

### 14.1 Library Tests

Before strategy implementation:

- Mid-trade bracket update accepts valid stop/TP changes.
- Invalid bracket ordering is rejected.
- Partial-fill state is preserved after update.
- Strategy force exit closes full position pre-TP1.
- Strategy force exit closes runner post-TP1.
- Management event logging captures proposal and acceptance.

### 14.2 Strategy Constant Pinning Tests

Tests must pin:

- Entry window.
- Long-only mode.
- Stretch threshold.
- 30-minute regime gate.
- Risk dollars and contract cap.
- Confidence weights and bands.
- Runner ceiling formula.
- Vol shock thresholds.
- Time exit.
- OOS guard.

### 14.3 Synthetic Strategy Behavior Tests

Minimum synthetic tests:

- Long signal fires with valid VWAP stretch and regime gate.
- Signal skips when 30-minute gate fails.
- Signal skips when TP1/VWAP ordering invalid.
- High-confidence runner widens TP2 up to runner ceiling.
- Defensive confidence tightens stop and caps TP2.
- Confidence collapse force-exits.
- Vol shock blocks runner extension.
- Structure trail moves stop only after confirmed swing low.
- No short trade can be generated.
- No management evaluation uses incomplete bars.

### 14.4 In-Sample Run

Run the complete in-sample window once after tests pass. Produce:

- Trade CSV.
- Management event CSV.
- Results report.
- Changelog.

No parameter changes after the run.

---

## 15. Selection Bias Notes

V2 is explicitly post-result design. These choices came from prior
results:

| Prior result | V2 design response |
|---|---|
| V1 Branch 2 dominated and suppressed Branch 5 | Parallel field-by-field composition replaces priority order |
| V1 capped long winners more than it rescued shorts | Bounded TP2 widening permitted in high-confidence runner state |
| VWAP report showed long/short asymmetry | Shorts disabled; higher-timeframe long gate added |
| V1 inactive branches added complexity without signal | Specialist set reduced and made field-specific |
| Counterfactual was contaminated by TP2 reconstruction bias | V2 requires native event logging and cannot rely on reconstructed TP2 |

This is legitimate only because the OOS window remains sealed. If V2
passes in-sample and fails OOS, the family closes. If V2 fails in-sample,
the family closes without OOS.

The spec must not be edited after implementation starts except for
clerical typo fixes that do not alter behavior.

---

## 16. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | v1 documented | Original Needle Drop classifier wiki entry completed with v1 decision tree and implementation-ready precision subsections. |
| 2026-05-12 | v1 counterfactual reviewed | Counterfactual on vwap trades showed branch dominance, limited signal, and TP2 reconstruction bias. |
| 2026-05-13 | FINAL spec drafted | V2 canonical spec drafted as a structurally different real edge attempt: long-only VWAP entry, 30-minute participation gate, parallel specialist composition, confidence-conditional management, and bounded runner extension. |

End of specification.
