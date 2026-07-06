---
name: "Needle Drop Adaptive Management Classifier"
tagline: "Default-bracket entry that adapts in-flight brackets by deterministic classification against wiki strategy references."
status: "untested-ideation"
created: 2026-05-12
updated: 2026-05-12
source: "Operator brainstorm 2026-05-12: adaptive management framework using wiki strategies as deterministic classifiers; concept preserved per Path A defer-build decision."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-16:00 ET; exact entry window TBD"
hold_duration: "intraday"

# Signal characteristics
signal_type: "adaptive-management-meta-strategy"
indicators: ["ClassifierStrategySet", "ATR(20) on 5-minute bars", "strategy-specific indicators TBD"]
timeframes_used: ["1-second", "1-minute", "5-minute", "strategy-dependent"]

# Execution
brackets: "volatility-adaptive"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: null
implementation: null
related_candidates:
  - "vwap_stretch_snapback.md"
  - "atr_regime_pullback_continuation.md"
  - "vwap_band_acceptance_regime.md"
  - "developing_swing_trail_vol_cap.md"

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
  - volatility-adaptive
  - fixed-risk-dollar
  - regime-conditional
  - methodology-case-study
---

# Needle Drop Adaptive Management Classifier

## 1. Thesis

This candidate tests whether adaptive bracket management can help where
fixed brackets have failed. The tested-rejected fleet establishes a
hard baseline: several MNQ intraday continuation and breakout strategies
failed Apex 50K eval around the trailing-drawdown floor, and PRJ_3's raw
signal diagnostic showed no intrinsic edge after the lookahead fix.

The needle-drop idea is not "the wiki strategies have edge." It is:
enter with a baseline bracket, then classify the live market state
against deterministic reference patterns drawn from wiki strategy
entries. If the current state resembles a known pattern, adapt the
in-flight brackets conservatively to that pattern's management logic.
The wiki strategies act as reference lenses, not as proven alpha.

## 2. Mechanism (what edge it captures)

- **Adaptive management rather than adaptive entry.** The core test is
  whether changing stops and targets after entry improves outcomes more
  than fixed 25/10/80-style management.
- **Deterministic state classification.** Each eligible wiki strategy is
  converted into a lookahead-clean predicate. No machine learning or
  learned pattern matching is used.
- **Conservative bracket adjustment.** Default behavior is tighten-only:
  stops, TP1, TP2, and BE triggers can move closer, but risk cannot be
  loosened mid-trade.
- **Reference-pattern diversity.** The classifier can recognize
  reversion, trend, level-acceptance, range, and volatility-regime
  states if those wiki entries are precise enough to serve as rules.
- **Falsifiable counter-hypothesis.** If entry quality is the true
  binding constraint, adaptive management should not rescue the result.

## 3. Signal logic (entry conditions)

The baseline entry signal is intentionally TBD. Spec drafting must pick
exactly one of these before any test:

- **Generic extreme entry.** Enter when a 1-minute bar reaches a
  pre-committed percentile extreme from a session anchor such as VWAP.
- **Reuse a precise wiki entry.** For example, reuse
  `vwap_stretch_snapback.md` once its entry condition is fully specced.
- **Wide-net entry.** Any eligible wiki strategy entry predicate can
  trigger the initial trade.

After entry, the classifier runs against the active wiki strategy set.
At each classification moment, it evaluates each eligible strategy's
deterministic entry/state predicate using only data available at that
moment. Matching strategies are candidates for bracket adaptation.

Open design decisions that must be locked before testing:

- Classification frequency: every 1-second bar, every N seconds, or
  event-driven on significant price movement.
- Eligible wiki strategy set: all candidates, only spec-drafted entries,
  or only entries with fully mechanical predicates.
- Tie-breaker when multiple strategies match: maturity order, signal
  family order, or alphabetical deterministic order.

## 4. Exit logic (stops, targets, time-based exits)

Initial default bracket before any classification adjustment:

- Stop: 25 points.
- BE arm trigger: +6 points, symmetric by direction.
- BE offset: +0.25 ticks from entry, subject to tick-size cleanup during
  spec drafting.
- TP1: +10 points, closes 50 percent of position.
- TP2: +80 points, closes remaining 50 percent.

Default adaptive rule:

- Stop: may move closer to entry, never farther away.
- TP1: may move closer to entry, never farther away.
- TP2: may move closer to entry, never farther away.
- BE arm: may trigger sooner if the matched strategy specifies an
  earlier BE rule.

If classification reverses from long-favoring to short-favoring or the
reverse while in a trade, the conservative default is immediate exit.
If no classifier matches, the trade remains on default brackets.

The 80-point TP2 is a known open concern. It may function more like an
EOD runner than a realistic target, and should be explicitly calibrated
or intentionally preserved before any implementation.

## 5. Position sizing

Use fixed dollar risk, not fixed 15-contract sizing. Initial proposed
risk is TBD, likely $300-$600 per trade depending on the final default
stop. Contract count is:

`risk_dollars / (stop_points x $2)`

The result is capped by Apex MNQ contract limits. If a classifier moves
the stop tighter after entry, position size is not increased mid-trade.

## 6. Required indicators / data

Base requirements:

- MNQ 1-second OHLCV, with lookahead-clean 1-minute and 5-minute
  derivations.
- TradingCalendar for RTH, half-days, and EOD flat timing.
- Apex compliance via ComplianceTracker.
- BAND_B friction model unless superseded by a pre-committed execution
  rule.

Classifier requirements depend on the active wiki strategy set. A
practical implementation likely needs:

- Wiki entry parser for YAML frontmatter and body sections.
- Manual or semi-manual registry mapping strategy names to executable
  predicates.
- Bracket-spec registry mapping strategy names to stop/target/BE rules.
- Adjustment engine that applies the tighten-only rule to an active
  TradeLifecycle.

Important caveat: most candidate wiki entries are not precise enough to
be executed directly. They are research notes, not runnable predicates.

## 7. Differentiation (vs already-tested strategies)

The tested-rejected fleet used fixed bracket geometry and static
management once a trade was entered. This candidate directly targets
that shared failure mode by making management adaptive after entry.

It differs from PRJ_3 specifically because PRJ_3 used a fractal-pullback
entry and then fixed management. Needle Drop does not assume fractal
levels have edge and does not reuse PRJ_3's proximity-touch pattern as
the core signal. If PRJ_3 is included at all, it is only one possible
classifier reference and its post-lookahead rejection must be marked
clearly.

It differs from batch-1 and batch-2 candidates because those are single
strategy hypotheses. This is a meta-strategy/infrastructure candidate:
the research object is whether deterministic strategy-state
classification improves bracket management. That makes it more flexible
but also much more confounded.

## 8. Required research before spec drafting

- **Entry signal selection.** Pick one initial entry mechanic. Do not
  test multiple and keep the winner.
- **Classifier eligibility.** Catalog all wiki candidates and decide
  which are precise enough to become deterministic predicates.
- **Predicate implementation plan.** Decide whether predicates are
  manually coded from specs or generated from structured metadata. The
  latter is likely too ambitious for v1.
- **Tie-breaker.** Pre-commit one: status maturity, signal family, or
  alphabetical deterministic order.
- **Classification frequency.** Choose continuous, periodic, or
  event-driven evaluation before testing.
- **Default bracket calibration.** Decide whether 25/6/10/80 remains
  intentional or should become ATR-scaled before the first test.
- **Apex interaction.** Verify mid-trade bracket adjustment and
  forced-exit behavior remain consistent with ComplianceTracker and
  trailing drawdown accounting.
- **Validation attribution.** Define what a negative result means,
  because default entry, classifier rules, bracket registry, and market
  state can all be failure sources.

Curve-fit warning: this candidate has many design degrees of freedom.
The only defensible path is one pre-committed v1 test, maybe one
pre-declared variant, then family closure unless the result is
diagnostically clear.

## 9. Source / references

- Operator brainstorm, 2026-05-12.
- Candidate wiki entries in `nb_lib/strategy_specs/candidates/`.
- Tested-rejected strategy entries:
  `variant_1_lifecycle.md`, `noise_brk_canonical_alpha.md`,
  `prj3_canonical_alpha.md`, `ema_trend_canonical_alpha.md`.
- Related adaptive candidates:
  `vwap_band_acceptance_regime.md`,
  `developing_swing_trail_vol_cap.md`,
  `atr_percentile_trend_day_hold.md`.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | Operator brainstorm during wait for vwap_stretch_snapback spec drafting. Path A decision: preserve in wiki, defer build. Concept should be revisited only after current iterations complete and more wiki strategies reach spec-drafted precision. Curve-fit, infrastructure, and confounded-validation risks acknowledged. |
| 2026-05-12 | `untested-ideation` | Counterfactual analysis run against 40 vwap_stretch_snapback in-sample trades. Raw delta -$984 (worsening); bias-decontaminated estimate ≈ +$600 (within noise at n=23 affected). Branch 1/3/4/6 never fired; Branch 2 fired on 23 trades and is effectively the only active branch; Branch 5 was suppressed 88 times by Branch 2 priority. Direction asymmetry deepens (longs cf -$1,425, shorts cf +$441). See `nb_lib_needle_drop_counterfactual_analysis.md`. Status remains `untested-ideation` per family-closure rule (counterfactual is informational, not a v1 test). |
| 2026-05-12 | `spec-drafted-v2` | FINAL spec drafted for needle drop v2 at `../canonical/needle_drop_v2_spec_FINAL.md`. V2 is structurally different from v1 per family closure rule: long-only VWAP entry with 30-minute participation gate, parallel field-by-field specialist composition instead of first-match priority, confidence-conditional management, and bounded runner extension instead of universal tighten-only management. Real edge attempt; OOS-eligible only per Section 13 of the FINAL spec. Library work for mid-trade bracket adjustment and strategy-reason force-exit path is next iteration. |

## 11. Decision Tree v1 Design (added 2026-05-12)

### Methodology framing

This is **v1 of a versioned exploratory design**, not a promoted
strategy spec. The status remains `untested-ideation`. The purpose of
this section is to convert the original classifier-engine idea into a
hardcoded, deterministic decision tree that could later be implemented
as:

`apply_decision_tree(state, current_brackets) -> new_brackets`

No machine learning, no learned pattern matching, and no natural-language
wiki parsing is used in v1. The tree is a manual registry of a small
number of strategy-inspired predicates.

Important methodology caveats:

- Defaults for untested strategies are **INFORMED PRIORS, not
  data-derived**. They are round-number choices or direct translations
  of candidate descriptions.
- The tree structure embeds designer judgment about which market states
  matter. That judgment is a source of selection bias before testing
  even begins.
- Bracket adjustments are **tighten-only**. A proposed adjustment is
  ignored if it would widen risk or move a target farther away than the
  current active bracket.
- This family gets one pre-committed v1 test, possibly one
  pre-declared structurally different variant, then family closure unless
  the result is diagnostically clear. A v2 cannot be a retuned v1; it
  would need different branch conditions or a different reference set.

### V1 design decisions resolved here

For v1, several Section 8 open questions are resolved deliberately:

- **Initial entry signal:** use `vwap_stretch_snapback` as the only
  entry source. It is the only spec-drafted candidate as of 2026-05-12,
  so it is the cleanest lookahead-audited starting point. Needle Drop v1
  tests adaptive management after this entry, not a wide-net entry.
- **Classifier eligibility:** use a hardcoded set of five wiki
  references: `vwap_stretch_snapback`, `round_number_rejection_microfade`,
  `choppiness_impulse_fade`, `atr_ratio_expansion_scalp`, and
  `developing_swing_trail_vol_cap`.
- **Predicate implementation plan:** manually coded predicates only.
  No wiki parser in v1.
- **Tie-breaker:** fixed priority order in the table below. The first
  matching branch wins.
- **Classification frequency:** evaluate once per completed 1-minute bar
  while a trade is open, plus once immediately after entry brackets are
  initialized. This matches the granularity of most branch predicates and
  avoids noisy every-second churn.
- **Default bracket calibration:** preserve the brainstorm defaults
  (25 stop / BE at +6 / TP1 at +10 / TP2 at +80) for v1, but size by
  fixed dollar risk. These defaults are intentionally not calibrated.

### Shared state inputs

The future implementation should build a `state` object containing at
least:

- `ts`: current completed 1-minute bar right-edge timestamp.
- `direction`: `long` or `short`.
- `entry_price`, `current_price`, `mfe_pts`, `mae_pts`.
- `current_brackets`: active stop, TP1, TP2, BE arm, and BE offset.
- `atr_5m_20`: most recent completed 5-minute ATR(20), Wilder.
- `atr_percentile_60`: ATR percentile over trailing 60 RTH sessions.
- `atr_ratio_5_30`: ATRRatio(5,30) on 1-minute bars.
- `choppiness_14`: ChoppinessIndex(14) on 5-minute bars.
- `session_vwap`, `session_stdev`, and `stretch_sigma`.
- `last_1m` and `prior_1m` OHLCV bars.
- `last_confirmed_5m_swing_high` and `last_confirmed_5m_swing_low`, if
  available.
- Nearest 50/100-point round-number levels around current price.

All inputs must be computed lookahead-clean from bars whose right edge is
less than or equal to `ts`.

### Tighten-only application rule

Every branch proposes a complete or partial bracket update. The update
is filtered through the same rule:

```text
For a long:
- proposed_stop is accepted only if proposed_stop > current_stop
  and proposed_stop < current_price.
- proposed_tp1 is accepted only if proposed_tp1 <= current_tp1
  and proposed_tp1 > current_price.
- proposed_tp2 is accepted only if proposed_tp2 <= current_tp2
  and proposed_tp2 > current_price.
- proposed_be_arm is accepted only if proposed_be_arm <= current_be_arm.

For a short:
- proposed_stop is accepted only if proposed_stop < current_stop
  and proposed_stop > current_price.
- proposed_tp1 is accepted only if proposed_tp1 >= current_tp1
  and proposed_tp1 < current_price.
- proposed_tp2 is accepted only if proposed_tp2 >= current_tp2
  and proposed_tp2 < current_price.
- proposed_be_arm is accepted only if proposed_be_arm <= current_be_arm.
```

If a proposed target would already be behind current price, it becomes an
immediate market exit candidate rather than a new limit target. This
must be explicit in implementation so the tree cannot silently create
invalid bracket ordering.

### Tree structure

Branches are evaluated in this exact order. First match wins.

| Priority | Branch | Reference | Condition | Tighten-only adjustment |
|---:|---|---|---|---|
| 1 | Opposite stretch reversal | `vwap_stretch_snapback` | Long: `stretch_sigma >= +1.5` and last 1m candle closes red after making a higher high than prior close. Short: `stretch_sigma <= -1.5` and last 1m candle closes green after making a lower low than prior close. | Force exit at current bar close. This says the trade has rotated into the opposite VWAP-stretch state. |
| 2 | VWAP snapback management | `vwap_stretch_snapback_spec_FINAL.md` | Trade is still between entry and VWAP, and `abs(stretch_sigma) >= 1.0`. | Stop to 1.0 x ATR(20) from current price if tighter. TP1 to nearest 50-point psychological level between current price and VWAP. TP2 to VWAP at signal moment or current VWAP, whichever is closer to current price. BE arm to half the distance from entry to TP1. |
| 3 | Round-number rejection capture | `round_number_rejection_microfade.md` | Current price is within 8 points of a 50/100-point level and last 1m candle rejects that level against the open trade direction. | TP1 to the nearest 25-point subdivision back inside the range. TP2 to the nearest 50-point subdivision back inside the range. Stop to 2 ticks beyond the rejection extreme if tighter. |
| 4 | Rotational chop compression | `choppiness_impulse_fade.md` | `choppiness_14 >= 62` and `atr_percentile_60 <= 0.55`. | TP1 to 0.5 x ATR(20) from current price in trade direction. TP2 to 0.75 x ATR(20). Stop to 0.7 x ATR(20) from current price if tighter. BE arm to +0.4 x ATR(20) if sooner. |
| 5 | Volatility expansion risk-off | `atr_ratio_expansion_scalp.md` | `atr_ratio_5_30 >= 1.35` or `atr_percentile_60 >= 0.75`. | Stop to 0.8 x ATR(5) on 1-minute bars if tighter. TP1 to 1.0 x ATR(5). TP2 to 1.4 x ATR(5). BE arm to +0.5 x ATR(5). |
| 6 | Structure trail once profitable | `developing_swing_trail_vol_cap.md` | `0.40 <= atr_percentile_60 <= 0.80`, `mfe_pts >= initial_risk_pts`, and a confirmed favorable 5-minute swing exists. | Long: stop to last confirmed 5m swing low if tighter. Short: stop to last confirmed 5m swing high if tighter. Targets unchanged. |
| 7 | Default | Needle Drop base | No branches match. | Keep current brackets unchanged. |

### Pseudocode

```text
def apply_decision_tree(state, current_brackets):
    if opposite_stretch_reversal(state):
        return force_exit("needle_drop_opposite_stretch")

    if vwap_snapback_management(state):
        proposal = brackets_from_vwap_snapback(state)
        return tighten_only(state.direction, current_brackets, proposal)

    if round_number_rejection_capture(state):
        proposal = brackets_from_round_number_rejection(state)
        return tighten_only(state.direction, current_brackets, proposal)

    if rotational_chop_compression(state):
        proposal = brackets_from_choppiness_impulse_fade(state)
        return tighten_only(state.direction, current_brackets, proposal)

    if volatility_expansion_risk_off(state):
        proposal = brackets_from_atr_ratio_expansion_scalp(state)
        return tighten_only(state.direction, current_brackets, proposal)

    if structure_trail_once_profitable(state):
        proposal = brackets_from_developing_swing_trail(state)
        return tighten_only(state.direction, current_brackets, proposal)

    return current_brackets
```

### Wiki strategy references and parameter status

`vwap_stretch_snapback` is **spec-drafted**. Use the FINAL spec's
actual mechanics:

- Stretch threshold: 2.0 sigma for entry, but v1 management branch can
  use 1.0 sigma because the trade is already open.
- Stop: 1.0 x ATR(20) on 5-minute bars.
- TP1: nearest 50-point psychological level between entry/current price
  and VWAP, falling back to midpoint if no level exists.
- TP2: VWAP.
- BE arm: halfway from entry to TP1.

The following references are `untested-ideation`; **PARAMETERS ARE
INFORMED PRIORS, not data-derived**:

- `round_number_rejection_microfade`: 8-point proximity to a 50/100
  level, 25/50-point target subdivisions, 2-tick stop beyond rejection
  extreme. Reasoning: round-level edge, if it exists, should be local
  and fast; wider parameters would turn a microfade into a generic
  mean-reversion trade.
- `choppiness_impulse_fade`: Choppiness >= 62 and ATR percentile <=
  0.55; 0.5/0.75 ATR targets and 0.7 ATR stop. Reasoning: rotational
  regimes should harvest smaller targets and not hold for 80-point
  runners.
- `atr_ratio_expansion_scalp`: ATRRatio(5,30) >= 1.35 or ATR percentile
  >= 0.75; 0.8/1.0/1.4 x ATR(5) management. Reasoning: fast volatility
  expansion is hostile to loose fixed brackets; compress the management
  horizon.
- `developing_swing_trail_vol_cap`: ATR percentile between 0.40 and
  0.80 and MFE >= 1R before swing trail activates. Reasoning: structure
  trailing needs enough movement to form swings but not so much
  volatility that every swing is noise.

### Open questions addressed

- **Entry signal selection:** resolved to `vwap_stretch_snapback` only
  for v1.
- **Classifier eligibility:** resolved to five hardcoded references.
- **Predicate implementation plan:** resolved to manual predicates.
- **Tie-breaker:** resolved to fixed priority order.
- **Classification frequency:** resolved to completed 1-minute bars.
- **Default bracket calibration:** resolved to preserve 25/6/10/80 for
  v1, while acknowledging it is uncalibrated.
- **Apex interaction:** partially resolved by no mid-trade size increase,
  tighten-only risk, and immediate-exit handling for invalid targets.

### Open questions deferred

- **Whether the default brackets are sensible long-term.** V1 preserves
  them to isolate adaptive management, but the 80-point TP2 remains a
  known concern.
- **Whether candidate predicates should eventually be generated from
  wiki metadata.** V1 rejects this as too much infrastructure.
- **Whether untested-ideation strategies should influence live
  management.** V1 uses them as informed-prior references only; future
  testing may show this was too noisy.
- **Validation attribution.** A negative result will still be
  confounded: entry signal, branch predicates, priority order, and
  bracket geometry can all be responsible.
- **Confirmed swing primitive.** Branch 6 requires a lookahead-clean
  5-minute swing detector. If no such helper exists at implementation
  time, Branch 6 should be omitted rather than improvised.

### Implementation notes for future spec drafter

- Do not implement a wiki parser in v1. Hardcode predicates and bracket
  proposals in a strategy-local registry.
- Log every decision-tree evaluation with timestamp, current branch,
  branch inputs, current brackets, proposed brackets, and accepted
  tighten-only changes. Without this log, post-test attribution will be
  nearly impossible.
- Runtime assertions should enforce monotonic tightening: stop risk
  cannot increase, target distance cannot increase, BE arm cannot become
  later.
- If multiple branches could match, do not merge them. First-match
  priority order is the tie-breaker.
- If v1 fails, do not retune thresholds. Either close the family or
  design a structurally different v2 with different references and
  branch logic before any new test.

### 11.X.1 Runnable predicates

The predicates below are the implementation-ready form of the v1 branch
conditions. Every predicate returns `False` if a required state input is
missing or NaN. Threshold comparisons use inclusive boundaries
(`>=`, `<=`) unless a strict inequality is needed for bar direction.

Helper assumptions:

```python
def is_valid_number(value) -> bool:
    return value is not None and not pd.isna(value)

def has_ohlc_bar(bar) -> bool:
    return (
        bar is not None
        and is_valid_number(bar.open)
        and is_valid_number(bar.high)
        and is_valid_number(bar.low)
        and is_valid_number(bar.close)
    )
```

Branch 1: opposite stretch reversal.

```python
def opposite_stretch_reversal(state) -> bool:
    if not has_ohlc_bar(state.last_1m) or not has_ohlc_bar(state.prior_1m):
        return False
    if not is_valid_number(state.stretch_sigma):
        return False

    if state.direction == "long":
        return (
            state.stretch_sigma >= 1.5
            and state.last_1m.close < state.last_1m.open
            and state.last_1m.high > state.prior_1m.close
        )

    if state.direction == "short":
        return (
            state.stretch_sigma <= -1.5
            and state.last_1m.close > state.last_1m.open
            and state.last_1m.low < state.prior_1m.close
        )

    return False
```

Branch 2: VWAP snapback management.

```python
def vwap_snapback_management(state) -> bool:
    required = [
        state.current_price,
        state.session_vwap,
        state.stretch_sigma,
        state.atr_5m_20,
    ]
    if not all(is_valid_number(value) for value in required):
        return False
    if state.atr_5m_20 <= 0:
        return False

    if state.direction == "long":
        return (
            state.current_price < state.session_vwap
            and state.stretch_sigma <= -1.0
        )

    if state.direction == "short":
        return (
            state.current_price > state.session_vwap
            and state.stretch_sigma >= 1.0
        )

    return False
```

Branch 3: round-number rejection capture.

```python
def round_number_rejection_capture(state) -> bool:
    if not has_ohlc_bar(state.last_1m) or not has_ohlc_bar(state.prior_1m):
        return False
    if not is_valid_number(state.nearest_round_level):
        return False

    distance_to_level = abs(state.current_price - state.nearest_round_level)
    if distance_to_level > 8.0:
        return False

    if state.direction == "long":
        return (
            state.last_1m.high >= state.nearest_round_level
            and state.last_1m.close < state.nearest_round_level
            and state.last_1m.close < state.last_1m.open
        )

    if state.direction == "short":
        return (
            state.last_1m.low <= state.nearest_round_level
            and state.last_1m.close > state.nearest_round_level
            and state.last_1m.close > state.last_1m.open
        )

    return False
```

Branch 4: rotational chop compression.

```python
def rotational_chop_compression(state) -> bool:
    required = [
        state.choppiness_14,
        state.atr_percentile_60,
        state.atr_5m_20,
    ]
    if not all(is_valid_number(value) for value in required):
        return False
    return (
        state.choppiness_14 >= 62.0
        and state.atr_percentile_60 <= 0.55
        and state.atr_5m_20 > 0.0
    )
```

Branch 5: volatility expansion risk-off.

```python
def volatility_expansion_risk_off(state) -> bool:
    has_ratio = is_valid_number(state.atr_ratio_5_30)
    has_percentile = is_valid_number(state.atr_percentile_60)
    has_atr_1m = is_valid_number(state.atr_1m_5) and state.atr_1m_5 > 0.0
    if not has_atr_1m:
        return False

    ratio_trigger = has_ratio and state.atr_ratio_5_30 >= 1.35
    percentile_trigger = has_percentile and state.atr_percentile_60 >= 0.75
    return ratio_trigger or percentile_trigger
```

Branch 6: structure trail once profitable.

```python
def structure_trail_once_profitable(state) -> bool:
    required = [
        state.atr_percentile_60,
        state.mfe_pts,
        state.initial_risk_pts,
    ]
    if not all(is_valid_number(value) for value in required):
        return False
    if not (0.40 <= state.atr_percentile_60 <= 0.80):
        return False
    if state.mfe_pts < state.initial_risk_pts:
        return False

    if state.direction == "long":
        return is_valid_number(state.last_confirmed_5m_swing_low)
    if state.direction == "short":
        return is_valid_number(state.last_confirmed_5m_swing_high)
    return False
```

Branch 7: default.

```python
def default_branch(state) -> bool:
    return True
```

### 11.X.2 State input computation

All state inputs are evaluated at `state.ts`, the right-edge timestamp of
the most recent completed 1-minute bar. A branch whose required inputs
are unavailable returns `False`; one bad indicator does not disable the
whole tree.

```text
state.ts:
- Source: 1-minute bar right-edge.
- Rule: first evaluation timestamp after entry is the first 1-minute
  boundary strictly greater than entry_ts.
- Warmup: no evaluation if there is no completed 1-minute bar.

state.direction:
- Source: active TradeLifecycle direction.
- Values: "long" or "short" only.
- Warmup: none.

state.entry_price:
- Source: actual entry fill price after entry friction.
- Rule: constant for the trade.

state.current_price:
- Source: last completed 1-minute close at state.ts.
- Rule: state.current_price = state.last_1m.close.

state.mfe_pts / state.mae_pts:
- Source: running trade state.
- Rule: measured in favorable/adverse points from entry using completed
  bars only. For long, MFE uses high-entry and MAE uses entry-low; for
  short, MFE uses entry-low and MAE uses high-entry.

state.initial_risk_pts:
- Source: entry_price to initial stop distance.
- Rule: constant for the trade; positive float.

state.current_brackets:
- Source: active bracket state after all prior tighten-only updates.
- Fields: stop, tp1, tp2, be_arm_pts, be_offset_pts.
```

Indicator fields:

```text
state.atr_5m_20:
- Source: 5-minute bars derived from 1-second source.
- Indicator: ATR(20), Wilder smoothing.
- Evaluation: last completed 5-minute bar where bar.name + 5min <=
  state.ts.
- Warmup: None/NaN until ATR warmup completes; dependent predicates
  return False.

state.atr_1m_5:
- Source: 1-minute bars.
- Indicator: ATR(5), Wilder smoothing.
- Evaluation: last completed 1-minute bar at state.ts.
- Warmup: None/NaN until five completed 1-minute bars exist.

state.atr_percentile_60:
- Source: 5-minute ATR(20), compared to trailing 60 RTH sessions.
- Evaluation: percentile value available at the same completed 5-minute
  bar used for state.atr_5m_20.
- Warmup: None/NaN until lookback completes.

state.atr_ratio_5_30:
- Source: 1-minute bars.
- Indicator: ATRRatio(5,30).
- Evaluation: last completed 1-minute bar at state.ts.
- Warmup: None/NaN until 30-bar long ATR warmup completes.

state.choppiness_14:
- Source: 5-minute bars.
- Indicator: ChoppinessIndex(14).
- Evaluation: last completed 5-minute bar where bar.name + 5min <=
  state.ts.
- Warmup: None/NaN until 14 completed 5-minute bars exist.
```

VWAP and bar fields:

```text
state.session_vwap:
- Source: 1-minute bars with volume, session anchored at RTH open.
- Evaluation: value at state.ts using only bars whose right-edge <=
  state.ts.
- Warmup: None/NaN before sufficient session bars exist.

state.session_stdev:
- Source: 1-minute closes since RTH open.
- Evaluation: value at state.ts using only bars whose right-edge <=
  state.ts.
- Warmup: None/NaN or zero during early-session warmup.

state.stretch_sigma:
- Formula: (state.current_price - state.session_vwap) /
  state.session_stdev.
- Rule: None if session_stdev is None, NaN, or <= 0.

state.last_1m:
- Source: 1-minute bar with right-edge == state.ts.
- Assertion: state.last_1m.name + 1min == state.ts.

state.prior_1m:
- Source: 1-minute bar immediately before state.last_1m.
- Assertion: state.prior_1m.name + 1min == state.last_1m.name.
```

Level fields:

```text
state.last_confirmed_5m_swing_high / swing_low:
- Source: completed 5-minute bars only.
- Confirmation rule for v1: 3-bar swing, center bar has high greater
  than both neighbors for swing high, or low lower than both neighbors
  for swing low.
- Lookahead rule: a swing centered at bar i is confirmed only after bar
  i+1 is complete. At state.ts, the confirming bar right-edge must be <=
  state.ts.
- Warmup: None until at least three completed 5-minute bars exist.

state.nearest_round_level:
- Source: price-only derived level.
- Formula: nearest multiple of 50.0 points to state.current_price.
- If equidistant, choose the level in the adverse direction of the open
  trade: above price for long, below price for short.

state.round_level_above / state.round_level_below:
- Formula: ceil(current_price / 50.0) * 50.0 and
  floor(current_price / 50.0) * 50.0.
```

### 11.X.3 Bracket adjustment formulas

All proposal functions recompute from live state at each evaluation. The
tighten-only filter decides which proposed fields are accepted.

Shared helpers:

```python
@dataclass
class BracketProposal:
    stop: float | None = None
    tp1: float | None = None
    tp2: float | None = None
    be_arm_pts: float | None = None
    force_exit: bool = False
    exit_reason: str | None = None

def midpoint(a: float, b: float) -> float:
    return (a + b) / 2.0

def round_to_tick(price: float) -> float:
    return round(price / 0.25) * 0.25

def first_round_level_between(low: float, high: float) -> float | None:
    first = math.ceil(low / 50.0) * 50.0
    if first < high:
        return first
    return None

def last_round_level_between(low: float, high: float) -> float | None:
    last = math.floor(high / 50.0) * 50.0
    if last > low:
        return last
    return None
```

Branch 1 has no bracket proposal; it returns force exit:

```python
def proposal_opposite_stretch_reversal(state) -> BracketProposal:
    return BracketProposal(
        force_exit=True,
        exit_reason="needle_drop_opposite_stretch",
    )
```

Branch 2:

```python
def brackets_from_vwap_snapback(state) -> BracketProposal:
    if state.direction == "long":
        proposed_stop = state.current_price - 1.0 * state.atr_5m_20
        proposed_tp1 = first_round_level_between(
            state.current_price, state.session_vwap
        )
        if proposed_tp1 is None:
            proposed_tp1 = midpoint(state.current_price, state.session_vwap)
        proposed_tp2 = state.session_vwap
    else:
        proposed_stop = state.current_price + 1.0 * state.atr_5m_20
        proposed_tp1 = last_round_level_between(
            state.session_vwap, state.current_price
        )
        if proposed_tp1 is None:
            proposed_tp1 = midpoint(state.current_price, state.session_vwap)
        proposed_tp2 = state.session_vwap

    proposed_tp1 = round_to_tick(proposed_tp1)
    proposed_tp2 = round_to_tick(proposed_tp2)
    proposed_stop = round_to_tick(proposed_stop)
    proposed_be_arm = abs(proposed_tp1 - state.entry_price) / 2.0

    return BracketProposal(
        stop=proposed_stop,
        tp1=proposed_tp1,
        tp2=proposed_tp2,
        be_arm_pts=proposed_be_arm,
    )
```

Branch 3:

```python
def brackets_from_round_number_rejection(state) -> BracketProposal:
    if state.direction == "long":
        proposed_stop = state.last_1m.low - 0.50
        proposed_tp1 = state.nearest_round_level - 25.0
        proposed_tp2 = state.nearest_round_level - 50.0
    else:
        proposed_stop = state.last_1m.high + 0.50
        proposed_tp1 = state.nearest_round_level + 25.0
        proposed_tp2 = state.nearest_round_level + 50.0

    proposed_be_arm = abs(proposed_tp1 - state.entry_price) / 2.0
    return BracketProposal(
        stop=round_to_tick(proposed_stop),
        tp1=round_to_tick(proposed_tp1),
        tp2=round_to_tick(proposed_tp2),
        be_arm_pts=proposed_be_arm,
    )
```

Branch 4:

```python
def brackets_from_choppiness_impulse_fade(state) -> BracketProposal:
    if state.direction == "long":
        proposed_stop = state.current_price - 0.7 * state.atr_5m_20
        proposed_tp1 = state.current_price + 0.5 * state.atr_5m_20
        proposed_tp2 = state.current_price + 0.75 * state.atr_5m_20
    else:
        proposed_stop = state.current_price + 0.7 * state.atr_5m_20
        proposed_tp1 = state.current_price - 0.5 * state.atr_5m_20
        proposed_tp2 = state.current_price - 0.75 * state.atr_5m_20

    return BracketProposal(
        stop=round_to_tick(proposed_stop),
        tp1=round_to_tick(proposed_tp1),
        tp2=round_to_tick(proposed_tp2),
        be_arm_pts=0.4 * state.atr_5m_20,
    )
```

Branch 5:

```python
def brackets_from_atr_ratio_expansion_scalp(state) -> BracketProposal:
    atr = state.atr_1m_5
    if state.direction == "long":
        proposed_stop = state.current_price - 0.8 * atr
        proposed_tp1 = state.current_price + 1.0 * atr
        proposed_tp2 = state.current_price + 1.4 * atr
    else:
        proposed_stop = state.current_price + 0.8 * atr
        proposed_tp1 = state.current_price - 1.0 * atr
        proposed_tp2 = state.current_price - 1.4 * atr

    return BracketProposal(
        stop=round_to_tick(proposed_stop),
        tp1=round_to_tick(proposed_tp1),
        tp2=round_to_tick(proposed_tp2),
        be_arm_pts=0.5 * atr,
    )
```

Branch 6:

```python
def brackets_from_developing_swing_trail(state) -> BracketProposal:
    if state.direction == "long":
        proposed_stop = state.last_confirmed_5m_swing_low
    else:
        proposed_stop = state.last_confirmed_5m_swing_high

    return BracketProposal(stop=round_to_tick(proposed_stop))
```

Branch 7:

```python
def brackets_from_default(state) -> BracketProposal:
    return BracketProposal()
```

### 11.X.4 Runtime assertions

These assertions fire in production-path code at each decision-tree
evaluation and after each accepted proposal.

```python
def assert_state_integrity(state) -> None:
    assert state.ts is not None
    assert state.direction in ("long", "short")
    assert state.entry_price > 0.0
    assert state.current_price > 0.0
    assert state.initial_risk_pts > 0.0
    assert state.mfe_pts >= 0.0
    assert state.mae_pts >= 0.0
    assert has_ohlc_bar(state.last_1m)
    assert state.last_1m.name + pd.Timedelta(minutes=1) == state.ts
    if state.prior_1m is not None:
        assert state.prior_1m.name + pd.Timedelta(minutes=1) == state.last_1m.name

    if state.atr_5m_20 is not None and not pd.isna(state.atr_5m_20):
        assert state.atr_5m_20 > 0.0
    if state.atr_1m_5 is not None and not pd.isna(state.atr_1m_5):
        assert state.atr_1m_5 > 0.0
    if state.atr_percentile_60 is not None and not pd.isna(state.atr_percentile_60):
        assert 0.0 <= state.atr_percentile_60 <= 1.0
```

```python
def assert_tighten_only(direction, old, new) -> None:
    if direction == "long":
        assert new.stop >= old.stop
        assert new.tp1 <= old.tp1
        assert new.tp2 <= old.tp2
        assert new.be_arm_pts <= old.be_arm_pts
    else:
        assert new.stop <= old.stop
        assert new.tp1 >= old.tp1
        assert new.tp2 >= old.tp2
        assert new.be_arm_pts <= old.be_arm_pts
```

```python
def assert_bracket_ordering(state, brackets) -> None:
    if state.direction == "long":
        assert brackets.stop < state.current_price
        assert state.current_price < brackets.tp1 <= brackets.tp2
    else:
        assert brackets.stop > state.current_price
        assert state.current_price > brackets.tp1 >= brackets.tp2
```

Additional edge-case assertions:

```python
assert not (proposal.force_exit and proposal.exit_reason is None)
assert not (proposal.force_exit and any([
    proposal.stop is not None,
    proposal.tp1 is not None,
    proposal.tp2 is not None,
]))
assert new_brackets.stop is not None
assert new_brackets.tp1 is not None
assert new_brackets.tp2 is not None
assert new_brackets.be_arm_pts is not None
```

If a proposed target is already crossed at evaluation time, do not pass
it through `assert_bracket_ordering`. Convert it to an immediate
strategy exit with reason `needle_drop_target_crossed`.

### 11.X.5 Branch 1 force-exit semantics

Branch 1 is a strategy-management exit, not a compliance violation.

Specific decisions:

- Exit reason: `needle_drop_opposite_stretch`.
- Exit timestamp: first available 1-second bar strictly after
  `state.ts`, normally `state.ts + 1 second`.
- Exit price: that 1-second bar close, with the same exit friction model
  used by normal lifecycle market exits.
- Lifecycle handling: route through the same force-exit path used by
  compliance callbacks if available, but record the exit reason as a
  strategy reason, not `compliance_*`.
- Partial-fill state: if TP1 has already fired, close only the remaining
  runner contracts. If TP1 has not fired, close the full open position.
- Trade CSV: `exit_reason = "needle_drop_opposite_stretch"`; include
  `needle_drop_branch = "opposite_stretch_reversal"` in strategy extras
  or execution log.
- Logging: log the branch input values (`stretch_sigma`, last_1m OHLC,
  prior_1m close, current brackets) before the exit record.

The exit is one second after the completed 1-minute evaluation bar
because the signal is only knowable at `state.ts`. Filling at the 1-minute
close itself would repeat the PRJ_3 left-edge/right-edge mistake in a
new form.

### 11.X.6 First evaluation moment

V1 precision decision: **skip immediate post-entry decision-tree
evaluation**. The existing text's "once immediately after entry brackets
are initialized" is superseded for v1 precision by this rule.

First evaluation:

```text
entry_ts = signal_ts + 1 second
first_eval_ts = first 1-minute boundary strictly greater than entry_ts
```

Example:

```text
signal_ts = 10:23:00
entry_ts = 10:23:01
first_eval_ts = 10:24:00
```

Rationale: all branches are defined against completed 1-minute or
completed 5-minute state. Evaluating immediately after entry would reuse
the same signal bar that produced entry and add churn without new
information. It also creates a special-case path that later implementers
could mishandle.

Evaluation cadence after first evaluation:

```text
Evaluate at every completed 1-minute boundary while position is open.
Do not evaluate after EOD-flat time or after lifecycle has exited.
Do not evaluate on a timestamp where state.last_1m is missing.
```

### 11.X.7 Multi-evaluation interactions

Each evaluation is independent. At each evaluation timestamp:

1. Build fresh `state` from completed bars and current lifecycle state.
2. Evaluate branches in fixed priority order.
3. First matching branch produces a proposal.
4. Apply the tighten-only filter.
5. Commit accepted bracket changes to the active lifecycle.
6. Log branch, proposal, accepted fields, and resulting brackets.

Cross-evaluation rules:

- Brackets are monotonic. Once a stop or target tightens, later branches
  cannot loosen it.
- Branches can differ across evaluations. Branch 2 can tighten TP1 at
  minute 5, Branch 4 can tighten TP1 further at minute 10, and Branch 6
  can tighten the stop at minute 20.
- If Branch 6 moves a long stop to a 5-minute swing low and a later
  confirmed swing low is higher, the stop moves higher again. If the
  later swing low is lower, it is ignored.
- If a required indicator is NaN at one evaluation, only predicates that
  require that indicator return False. Other branches remain eligible.
- If a proposal would make TP1 and TP2 cross or collapse out of order,
  reject the invalid field. If ordering still fails after rejection,
  keep prior brackets and log `needle_drop_invalid_proposal`.
- If a proposal target is already crossed by current price, convert to
  immediate exit on the next 1-second bar with reason
  `needle_drop_target_crossed`.
- If Branch 1 force-exit matches, no later branches are evaluated at
  that timestamp.

Example interaction:

```text
10:24 Branch 2 matches:
- TP1 tightens from +10 fixed points to nearest round level.
- TP2 tightens from +80 fixed points to VWAP.

10:31 Branch 4 matches:
- Proposed TP1 is even closer because chop regime emerged.
- Tighten-only accepts smaller TP1/TP2 and maybe closer stop.

10:44 Branch 6 matches:
- MFE >= 1R and new swing low confirmed for long.
- Stop ratchets up to swing low if above existing stop.

10:52 Branch 5 matches:
- ATRRatio jumps, but proposed stop is below current stop.
- Stop proposal rejected; TP proposals may still be accepted if tighter.
```

This interaction model intentionally does not try to remember which
branch "owns" the trade. The active brackets are the state. The branch
tree only proposes monotonic changes.

### 11.X.8 Switching cooldown logic

#### 11.X.8.1 Motivation

V1 evaluates once per completed 1-minute bar, so it already has a
natural 60-second gap between decision-tree evaluations. That cadence is
enough to prevent bracket-switching thrash in the current design.

This explicit cooldown rule is documented for future-proofing. If a
future implementation changes the tree to sub-minute, event-driven, or
every-second evaluation, unbounded switching can create two problems:
live broker order modifications may still be in flight for 1-3 seconds,
and backtest behavior can become "managed to death" by many individually
valid tighten-only changes that are incoherent in sequence.

#### 11.X.8.2 Cooldown rule

New state field:

```python
state.last_switch_ts  # timestamp of last accepted bracket change, or None
```

V1 constant:

```python
MIN_SECONDS_BETWEEN_SWITCHES = 30
```

The 30-second value is an informed-prior operational default, not a
calibrated parameter. It is long enough to avoid broker-modification
thrash in live-style execution and short enough that defensive management
does not become stale on a normal intraday trade.

Cooldown decision:

```python
def cooldown_elapsed(state) -> bool:
    if state.last_switch_ts is None:
        return True
    elapsed = (state.ts - state.last_switch_ts).total_seconds()
    return elapsed >= MIN_SECONDS_BETWEEN_SWITCHES
```

If cooldown has not elapsed, opportunistic adjustments are skipped.
Defensive stop tightening and force exits are handled by the bypass rules
below.

#### 11.X.8.3 Bypass rules

Cooldown applies by field, not by branch.

- Force exit: always bypasses cooldown.
- Stop tightening: always bypasses cooldown because it is defensive.
- TP1 tightening: respects cooldown.
- TP2 tightening: respects cooldown.
- BE arm adjustment: respects cooldown.

Implementation-ready filter:

```python
def apply_cooldown_filter(state, proposal):
    """Filter a BracketProposal before tighten_only is applied.

    Force exits always pass through.
    Stop tightening always passes through because it reduces risk.
    TP1, TP2, and BE-arm changes require cooldown elapsed.
    """
    if proposal.force_exit:
        return proposal

    if state.last_switch_ts is None:
        is_elapsed = True
    else:
        elapsed = (state.ts - state.last_switch_ts).total_seconds()
        is_elapsed = elapsed >= MIN_SECONDS_BETWEEN_SWITCHES

    filtered = BracketProposal()

    # Defensive adjustment: allowed even inside cooldown.
    filtered.stop = proposal.stop

    # Opportunistic / management adjustments: gated by cooldown.
    if is_elapsed:
        filtered.tp1 = proposal.tp1
        filtered.tp2 = proposal.tp2
        filtered.be_arm_pts = proposal.be_arm_pts

    return filtered
```

Order of operations:

```text
raw proposal -> cooldown filter -> tighten-only filter -> bracket commit
```

The cooldown filter should not decide whether a stop is actually tighter.
It simply allows the stop field through. The tighten-only filter remains
the authority on whether the proposed stop reduces risk.

#### 11.X.8.4 `last_switch_ts` update rule

`last_switch_ts` updates only after an accepted change reaches the active
lifecycle bracket state.

Specific rule:

```python
def update_last_switch_ts_if_changed(state, old_brackets, new_brackets):
    changed = (
        new_brackets.stop != old_brackets.stop
        or new_brackets.tp1 != old_brackets.tp1
        or new_brackets.tp2 != old_brackets.tp2
        or new_brackets.be_arm_pts != old_brackets.be_arm_pts
    )
    if changed:
        state.last_switch_ts = state.ts
```

Details:

- Any accepted bracket change updates `last_switch_ts`: stop, TP1, TP2,
  or BE arm.
- Defensive-only stop tightening updates `last_switch_ts` because the
  trade state changed materially.
- A rejected proposal does not update `last_switch_ts`.
- A force exit does not update `last_switch_ts`; the trade ends and no
  future evaluations occur.
- An immediate `needle_drop_target_crossed` exit does not update
  `last_switch_ts` for the same reason.

#### 11.X.8.5 Integration with v1's 1-minute cadence

For v1:

- Evaluation cadence is once per completed 1-minute bar.
- Consecutive evaluations are normally 60 seconds apart.
- `MIN_SECONDS_BETWEEN_SWITCHES = 30` means cooldown is always elapsed
  between normal v1 evaluations.
- Therefore the cooldown is effectively dormant in v1.

Even though it is dormant, the future implementation should still carry
the state field and filter. That keeps the behavior explicit and protects
later variants that might evaluate every second or on event triggers.

#### 11.X.8.6 Open question deferred

The exact cooldown duration is a design parameter. V1 uses 30 seconds.
Reasonable alternatives are 15, 20, or 60 seconds, but none are
calibrated from data here.

Do not tune cooldown duration after seeing v1 results. Changing 30
seconds to another value because the first test would have improved is
curve-fitting. A different cooldown may only appear in a structurally
different v2 that is pre-declared before testing, with the family-closure
rule still applying.
