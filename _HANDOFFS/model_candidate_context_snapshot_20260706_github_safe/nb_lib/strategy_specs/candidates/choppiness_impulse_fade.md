---
name: "Choppiness Impulse Fade"
tagline: "Fade short impulse moves back toward a rotational range mean when the market is explicitly choppy."
status: "closed"
created: 2026-05-12
updated: 2026-05-13
source: "Operator Phase 1 direction 2026-05-13; entry signal design for chop-regime impulse mean reversion."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:15-14:45 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "mean-reversion"
indicators: ["ChoppinessIndex(14)", "ATR(20)", "ATRPercentile(60 sessions)", "ATRRatio(5,30)", "Donchian range over 12 completed 5-minute bars"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "atr-scaled"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: null
implementation: null
related_candidates: []

# Test status (only populated when status >= tested-*)
test_results:
  in_sample_n: null
  in_sample_pnl_dollars: null
  in_sample_pf: null
  in_sample_win_rate: null
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: null

# Tags for organization (recommended controlled vocabulary in README)
tags:
  - rth-only
  - intraday
  - mean-reversion
  - range-bound
  - regime-conditional
  - atr-scaled
  - fixed-risk-dollar
---

# Choppiness Impulse Fade - Phase 1 Entry Signal Design

This document specifies the entry signal only. It is not a full FINAL
strategy spec. Phase 2 will extend this entry design into a canonical
strategy spec with v2-style adaptive management.

## 0. Outcome Priors And Scope Acknowledgments

### 0.1 Priors

Pre-test priors for the eventual full strategy:

| Outcome | Prior | Meaning |
|---|---:|---|
| No edge / account failure | 0.50 | Chop-fade fails like prior fleet or is crushed by trend transitions |
| Weak in-sample only | 0.25 | Entry looks plausible but does not clear OOS or account constraints |
| OOS-eligible edge | 0.15 | Choppy-regime impulse fade shows durable signal |
| Signal design blocker | 0.10 | Frequency too low, clustered, or too directionally imbalanced |

These are methodology priors, not statistical estimates.

### 0.2 Scope

Phase 1 covers:

- Entry regime gate.
- Impulse definition.
- Reversal trigger.
- Initial static brackets sufficient for entry-only validation.
- Entry-side risk sizing and runtime assertions.

Phase 2 will add:

- Adaptive management specialists.
- Mid-trade bracket updates.
- Strategy force exits.
- Management event attribution.
- Full pass/fail criteria for PF, account survival, and OOS trigger.

No management mechanics are designed in this document beyond a simple
static bracket scaffold.

## 1. Strategy Thesis

Choppiness Impulse Fade tests whether short impulse moves in an already
rotational MNQ session tend to mean-revert toward the local range mean.
The signal does not use VWAP as the anchor. The anchor is the rolling
chop range: the midpoint of the last 60 minutes of completed 5-minute
bars.

The intended edge is behavioral and microstructural: in a choppy regime,
breakout attempts often lack follow-through. A fast three-minute push
toward the edge of the local range can attract late momentum entries
just as range participants fade the move. The strategy waits for a small
reversal candle before entering so it is fading a stalled impulse, not
blindly stepping in front of strength.

The counter-hypothesis is serious: retail chop-fade systems often fail
because choppiness is lagging and regimes change exactly when the fade
fires. If a choppy session transitions into trend, the signal will enter
against the new direction and can cluster losses. This risk is why the
entry includes a volatility-expansion veto and conservative sizing.

## 2. Entry Signal And Timing

### 2.1 Market And Session

- Market: MNQ continuous front-month futures.
- Session: RTH only.
- Entry evaluation window: 10:15:00 through 14:45:00 US/Eastern.
- No new entries on half-days in Phase 1.
- Maximum accepted trades: two per day total, one long and one short.

The window skips the first 45 minutes, where opening range discovery can
turn "chop" indicators stale, and avoids the late close window where
positioning flows can dominate range behavior.

### 2.2 Derived Bars And Lookahead Rule

All bars derive from the 1-second OHLCV source.

- 1-minute bars: primary impulse and reversal trigger.
- 5-minute bars: ChoppinessIndex, ATR, ATR percentile, ATR ratio, and
  rolling chop range.

Bars are left-labeled half-open intervals. At decision timestamp `T`, a
derived bar is usable only if:

```text
bar.left_edge + bar_duration <= T
```

For a 1-minute signal evaluated at `T = 10:23:00`, the last usable
1-minute bar is `[10:22:00, 10:23:00)`. The entry fill, if any, is on
the first 1-second bar strictly after `T`.

### 2.3 Regime Gate

The regime gate must be true before any impulse setup is considered.

Use the most recent completed 5-minute bar at `T`.

```text
choppiness_5m_14 >= 58.0
0.20 <= atr_percentile_60 <= 0.65
atr_ratio_5_30 <= 1.20
```

Definitions:

- `choppiness_5m_14`: ChoppinessIndex(14) on completed 5-minute bars.
- `atr_percentile_60`: current 5-minute ATR(20) ranked against the
  prior 60 RTH sessions.
- `atr_ratio_5_30`: ATRRatio(5,30) on completed 1-minute bars.

Rationale:

- `58.0` is informed-prior. The conventional ChoppinessIndex chop floor
  is 61.8 (Fibonacci-derived). The original Phase 1 value, 62.0, was
  inherited from needle drop v1's management-trigger context: a
  management-state classifier, not an entry threshold. Preflight
  empirically showed 62.0 was mechanically too restrictive when
  repurposed as an entry threshold: 8 signals in 469 days versus 40-180
  expected. The revised 58.0 floor captures chop conditions just below
  the conventional floor. This is design correction based on
  predicate-frequency evidence, not performance tuning; no P&L was
  observed in the preflight.
- The ATR percentile band excludes dead regimes below 20th percentile
  and trend-shock regimes above 65th percentile.
- The ATR ratio cap vetoes fresh volatility expansion, where a fade is
  most likely to be early.

### 2.4 Chop Range Anchor

Build the local chop range from the last 12 completed 5-minute bars
(60 minutes):

```text
range_high = max(high over last 12 completed 5-minute bars)
range_low = min(low over last 12 completed 5-minute bars)
range_mid = (range_high + range_low) / 2
range_half = (range_high - range_low) / 2
range_height = range_high - range_low
```

Range validity:

```text
1.25 * atr_5m_20 <= range_height <= 4.00 * atr_5m_20
```

This avoids fading in a range too tight to pay friction or a range so
wide that "chop" may simply be volatile two-way trend.

### 2.5 Impulse Detection

Use the last three completed 1-minute bars ending at decision timestamp
`T`.

Short fade impulse:

```text
three_bar_move = last_1m.close - close_3_bars_ago
three_bar_move >= 0.60 * atr_5m_20
last_1m.close >= range_mid + 0.35 * range_half
```

Long fade impulse:

```text
three_bar_move = close_3_bars_ago - last_1m.close
three_bar_move >= 0.60 * atr_5m_20
last_1m.close <= range_mid - 0.35 * range_half
```

The impulse must move price into the outer half of the rolling chop
range. This makes the setup a range-edge fade rather than generic
counter-momentum.

### 2.6 Entry Trigger Conditions

The actual trigger is a one-minute reversal candle after the impulse.

Short entry predicate:

```text
regime_gate == True
range_valid == True
short_impulse == True
last_1m.close < last_1m.open
last_1m.close < prior_1m.close
last_1m.high >= max(high of prior two 1-minute bars)
```

Long entry predicate:

```text
regime_gate == True
range_valid == True
long_impulse == True
last_1m.close > last_1m.open
last_1m.close > prior_1m.close
last_1m.low <= min(low of prior two 1-minute bars)
```

Boundary rules:

- Threshold comparisons use `>=` and `<=`.
- If any indicator is NaN, the predicate is false.
- If both long and short predicates are true on the same timestamp, skip
  the timestamp and log `ambiguous_two_sided_signal`.

### 2.7 Direction Handling

Phase 1 is two-sided. This is a deliberate methodology choice.

Needle Drop V2 used long-only selection after observing VWAP direction
asymmetry. That may be defensible for that family, but repeating a
direction-restricted design here would import post-result bias into a
new candidate. Chop-fade should be symmetric in theory: impulses toward
either edge of a rotational range can fail.

The Phase 1 expectation is not that longs and shorts have identical
performance. The expectation is that signal generation is not wildly
one-sided before any test. Section 7 defines the balance expectation.

### 2.8 Entry Fill Semantics

Use the established T+1 second pattern.

```text
signal_ts = right edge of completed 1-minute reversal bar
entry_ts = first 1-second bar strictly after signal_ts
entry_price = entry bar open with BAND_B entry friction
```

Assertions:

```python
assert entry_ts > signal_ts
assert signal_ts.time() >= time(10, 15)
assert signal_ts.time() <= time(14, 45)
```

If no eligible 1-second bar exists after the signal timestamp, skip the
trade.

## 3. Risk And Position Sizing

### 3.1 Fixed Dollar Risk

Use fixed-risk-dollar sizing:

```text
risk_dollars = 350.00
point_value = 2.00 dollars per MNQ point per contract
```

The lower-than-Needle-Drop risk is intentional. Mean-reversion losses can
cluster when chop turns into trend.

### 3.2 Initial Stop Distance

For a short setup:

```text
impulse_extreme = max(high over last three completed 1-minute bars)
raw_stop_distance = impulse_extreme - entry_price + 0.25 * atr_5m_20
```

For a long setup:

```text
impulse_extreme = min(low over last three completed 1-minute bars)
raw_stop_distance = entry_price - impulse_extreme + 0.25 * atr_5m_20
```

Validity:

```text
0.50 * atr_5m_20 <= raw_stop_distance <= 1.25 * atr_5m_20
```

If the raw distance is below the lower bound, use the lower bound. If it
is above the upper bound, skip the trade. The stop should be beyond the
impulse extreme, but not so far that the signal has poor Apex geometry.

### 3.3 Position Size Formula And Bounds

```text
raw_contracts = floor(risk_dollars / (stop_distance_pts * point_value))
contracts = clamp(raw_contracts, min=1, max=12)
```

Skip the trade if `raw_contracts < 1`.

### 3.4 Risk Guards

Skip if:

- `atr_5m_20 <= 0` or NaN.
- `stop_distance_pts <= 0`.
- `range_height <= 0`.
- Entry price is already beyond the stop.
- TP1 would be on the wrong side of entry.
- Compliance state is not ACTIVE.

### 3.5 Apex Compliance

Use `ComplianceTracker` with the Apex 50K EOD eval preset. The outer
strategy loop must stop opening new trades after `AccountState.FAILED`.

## 4. Adaptive Layers In Phase 1

### 4.1 Entry Regime Gate

The only Phase 1 adaptive layer is the entry regime gate:

```text
choppiness_5m_14 >= 58.0
0.20 <= atr_percentile_60 <= 0.65
atr_ratio_5_30 <= 1.20
```

This is Level 2 regime-conditional adaptation under the methodology
repertoire. Every threshold is an informed prior and must not be tuned
after seeing results.

### 4.2 Phase 2 Management Deferred

No confidence score, parallel composer, runner ceiling, force-exit
logic, or specialist attribution is specified in Phase 1. Phase 2 may
replace the static brackets below with v2-style adaptive management.

## 5. Initial Bracket Geometry (Phase 1 Static Scaffold)

### 5.1 Stop Placement

Use the stop distance from Section 3.2.

```text
long_stop = entry_price - stop_distance_pts
short_stop = entry_price + stop_distance_pts
```

### 5.2 TP1

TP1 targets the rolling range midpoint.

```text
long_tp1 = range_mid
short_tp1 = range_mid
```

TP1 closes 50% of contracts, rounded down. If position size is 1
contract, TP1 is disabled and TP2 manages the full position.

If the distance from entry to `range_mid` is less than `0.50R`, skip the
trade. Friction is too large relative to the first target.

### 5.3 TP2

TP2 targets the opposite inner quartile of the rolling chop range.

For long:

```text
tp2 = range_mid + 0.35 * range_half
```

For short:

```text
tp2 = range_mid - 0.35 * range_half
```

The target is intentionally modest. Phase 1 is not trying to harvest a
trend runner from a chop-fade entry.

### 5.4 BE Arm

Break-even arms after favorable movement of:

```text
be_arm_pts = 0.75 * stop_distance_pts
be_offset_pts = 0.0
```

This is a static scaffold. Phase 2 may replace it with adaptive
management.

## 6. Indicators, Data, And Assumed Library

### 6.1 Required Indicators

- ChoppinessIndex(14) on completed 5-minute bars.
- ATR(20), Wilder smoothing, on completed 5-minute bars.
- ATRPercentile(60 sessions) based on ATR(20).
- ATRRatio(5,30) on completed 1-minute bars.
- Rolling 12-bar 5-minute high/low range.

### 6.2 Data Source

Use MNQ 1-second OHLCV from the project Databento store. Derive 1-minute
and 5-minute bars from the 1-second source using left-labeled half-open
intervals.

No ES, GC, order-flow, options, or external event data is required in
Phase 1.

### 6.3 Assumed Lifecycle API

Phase 1 only requires standard `TradeLifecycle` bracket behavior. The
v2.4 adaptive management primitives are not used by the Phase 1 static
entry scaffold, but Phase 2 is expected to consume:

- `apply_bracket_update`
- `force_exit_strategy`
- management event logger
- 5-minute swing detector

### 6.4 FILL_ASSUMPTIONS Entry

Phase 2 should add a strategy-specific fill assumption key:

```text
FILL_ASSUMPTIONS["choppiness_impulse_fade"] = BAND_B
```

Until then, Phase 1 assumes the project default BAND_B friction.

## 7. Pre-Committed Pass Criteria (Phase 1 Entry-Only)

These are signal-shape expectations, not full performance thresholds.

### 7.1 Signal Frequency Expectation

Expected in-sample signal count:

```text
40 <= accepted_entries <= 180
```

Fewer than 40 suggests the entry is too narrow for a meaningful Phase 2
strategy. More than 180 suggests overtrading in chop and likely excessive
friction exposure.

### 7.2 Direction Balance Expectation

Because Phase 1 is two-sided:

```text
0.35 <= long_trade_share <= 0.65
```

If the signal is outside this range, Phase 2 must explicitly review
whether the imbalance is structural or a bug.

### 7.3 Full Pass Criteria Deferred

PF thresholds, win-rate expectations, Apex survival criteria,
specialist attribution, and OOS trigger rules are Phase 2 scope. They
must be locked in the FINAL spec before any full in-sample test.

## 8. Mechanics

### 8.1 Evaluation Cadence

Evaluate entry predicates once per completed 1-minute bar during the
entry window.

### 8.2 Time Exit

Phase 1 static scaffold uses:

```text
time_exit = entry_ts + 30 minutes
```

Exit reason:

```text
"chop_fade_time_exit"
```

Phase 2 may revise this.

### 8.3 EOD Flat

No position may remain open past the existing EOD flat deadline. Strategy
time exit should normally occur before EOD compliance flat.

### 8.4 Cooldown Between Trades

After an accepted trade exits, no new trade may open for:

```text
45 minutes
```

Additionally:

- Maximum one long per day.
- Maximum one short per day.
- Maximum two total trades per day.

### 8.5 Runtime Assertions

Entry-side assertions:

```python
assert signal_ts < pd.Timestamp("2026-02-01", tz="America/New_York")
assert last_1m.name + pd.Timedelta(minutes=1) == signal_ts
assert last_5m.name + pd.Timedelta(minutes=5) <= signal_ts
assert atr_5m_20 > 0
assert 0.0 <= atr_percentile_60 <= 1.0
assert choppiness_5m_14 >= 0
assert range_high > range_low
assert stop_distance_pts > 0
assert contracts >= 1
assert direction in ("long", "short")
```

## 9. HARD-HALT Conditions

Phase 1 halts on:

1. **HARD-HALT-OOS-LEAK**: any data timestamp >= 2026-02-01 is used for
   design, in-sample signal counts, or indicator history.
2. **HARD-HALT-LOOKAHEAD**: any predicate reads an incomplete 1-minute
   or 5-minute bar.
3. **HARD-HALT-ACCOUNT-FAILED-CONTINUE**: a new trade opens after the
   compliance tracker is FAILED.
4. **HARD-HALT-SPEC-DRIFT**: thresholds differ from this document during
   implementation without an explicit spec revision.
5. **HARD-HALT-MANAGEMENT-CREEP**: Phase 1 implementation adds adaptive
   management behavior before the Phase 2 spec exists.
6. **HARD-HALT-DIRECTION-BUG**: long/short predicates both fire on the
   same timestamp and the implementation enters anyway.

## 10. Open Questions Deferred

Deferred to Phase 2:

- Adaptive management specialist set.
- Confidence score components, if any.
- Parallel composer mechanics.
- Runner ceiling logic.
- Strategy force-exit triggers.
- Management attribution requirements.
- Full PF/account/OOS pass criteria.
- Whether static Phase 1 brackets should be replaced entirely or used as
  the initial bracket before adaptation.

## 15. Selection Bias Notes

This design is influenced by the 7-fleet failure pattern: continuation
and breakout-style entries have repeatedly failed, so this candidate
tests a different signal family. That is a legitimate research pivot,
but it is still post-result ideation.

It is also influenced by the VWAP mean-reversion failure. To avoid
turning this into a VWAP patch, this entry uses the rolling chop range
as the anchor and does not reuse VWAP's psychological-level target
algorithm.

The design stays two-sided specifically to avoid repeating Needle Drop
V2's long-only post-result selection. If future evidence shows strong
direction asymmetry, that is a Phase 2 or post-test finding, not a
reason to pre-filter one side in this Phase 1 entry design.

All thresholds are informed priors. No threshold may be tuned after a
signal-frequency run or in-sample result.

The Phase 1 chop threshold was revised from 62.0 to 58.0 on 2026-05-13
following a signal-frequency preflight that found the original value
mechanically too restrictive. This is design correction based on
predicate-frequency evidence, not performance tuning; no P&L was
observed. Per single-revision discipline, no further threshold iteration
on this mechanism will occur regardless of re-preflight outcome.

## 16. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | Created as untested-ideation by Codex 5.5 CLI batch 2, focused on dynamic adaptive intraday strategies. |
| 2026-05-13 | `entry-design` | Phase 1 entry signal designed. Phase 2 full FINAL spec with v2-style management pending. |
| 2026-05-13 | `entry-design (revised)` | Chop threshold revised from 62.0 to 58.0 based on signal-frequency preflight finding. Phase 1 design otherwise unchanged. |
| 2026-05-13 | closed | Candidate closed after binding constraint analysis. Mechanism produces sparse signals on MNQ at 5-min granularity per compound predicate stack. Operator pivot to different candidate. |
