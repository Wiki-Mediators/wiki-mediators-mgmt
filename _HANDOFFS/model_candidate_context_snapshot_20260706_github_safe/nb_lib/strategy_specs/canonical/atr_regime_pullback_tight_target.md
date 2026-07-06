---
status: "tested-rejected"
---

# ATR Regime Pullback Tight-Target Canonical Alpha — Strategy Specification (FINAL)

**Strategy ID**: atr_regime_pullback_tight_target
**Version**: 1.0
**Status**: tested-rejected (in-sample run 2026-05-12; all 4 pre-committed pass criteria failed)
**Lineage**: nb_lib-native, fork of `atr_regime_pullback_continuation` (tested-rejected 2026-05-12)
**Date created**: 2026-05-12
**Date updated**: 2026-05-12
**Authors**: Strategic Claude + operator
**Library version**: nb_lib v2.3 (post simulator-extension + atr_regime parent iteration; tests 310/310)
**Verification trail**: candidate wiki entry
`nb_lib/strategy_specs/candidates/atr_regime_pullback_tight_target.md` →
this FINAL spec → upcoming implementation iteration.

---

## 0. Methodology framing (read first)

### 0.1 What this iteration tests

A single hypothesis: **the parent strategy's failure was driven by
exit geometry, not entry mechanism.** All entry, regime-gate,
pullback, reversal, tier, and sizing logic carry over UNCHANGED
from the parent. Only the bracket geometry changes:

| Element | Parent | This fork |
|---|---|---|
| Stop distance | 1.25 × ATR | **1.0 × ATR** |
| TP1 distance | 0.75 × ATR (50% close) | **none** |
| TP2 / target | 2.50 × ATR (runner) | **1.5 × ATR (full close)** |
| BE arm trigger | 0.50 × ATR | **none (disabled)** |
| Partial close | yes (50% at TP1) | **no** |
| Runner | yes (BE-only) | **no** |
| Decisions per trade | 4 (TP1, BE arm, TP2, stop) | **2 (target, stop)** |

If the entry mechanism has any edge, a single tight target with no
partials should reveal it. If the entry has no edge, the
single-decision exit will fail too — and the family is closed.

### 0.2 Bucket-discipline cost

This iteration consumes the SECOND in-sample bucket slot for the
`atr_regime_pullback_*` strategy family. The parent
(`atr_regime_pullback_continuation`) consumed the first slot and
ended `tested-rejected` (single-run + 12-start multistart both
uniform no-edge). A third fork within this family is NOT permitted
without explicit operator override.

The parent's per-trade failure data has already been examined (the
exit-reason breakdown of 37.6% full_stop / 28.6% BE-stop / 25.3%
TP1→BE / 4.1% TP2 is what motivated the fork). Therefore a pure
no-leak fork is not achievable. The new bracket parameters are
designed from first-principles claims about MNQ intraday
continuation magnitude (Section 10 below) that are independent of
the parent's specific exit-reason percentages.

### 0.3 Expected outcome priors (honest, adjusted from parent)

- **70%**: no in-sample edge. If the entry mechanism truly lacked
  edge in the parent, removing the bracket complexity will not
  rescue it. This is the dominant prior given the parent's 0/12
  multistart.
- **15%**: in-sample edge surfaces. Bracket geometry was indeed
  the binding constraint. Mandatory held-out OOS validation
  follows (Section 13).
- **10%**: in-sample shows surface-level improvement (PF moves
  from 0.30 toward 1.0 but still loses) — partial vindication of
  the geometry hypothesis without genuine edge. Treat as
  `tested-rejected` confirming the entry mechanism, not the
  brackets, is the failure source.
- **5%**: in-sample edge with execution issues; bracket mechanics
  break in some specific way.

The 70% prior is HIGHER than the parent's 60% because we already
have direct evidence the family fails uniformly across 12 fresh
starts. The fork's only chance is the specific hypothesis that
geometry, not entry, was the binding constraint.

### 0.4 Infrastructure value (regardless of outcome)

Even if no edge, this iteration validates:

- **Single-decision exit pattern** as a reusable lifecycle
  configuration (`use_runner=False`, default
  `tp1_close_contracts`, large `be_arm_pts` sentinel)
- **Diff-fork pattern** for candidate → canonical → script
  forking, where the unchanged portions of a tested-rejected
  parent are inherited with the changed portions documented
  explicitly

---

## 1. Spec metadata

- **Name**: ATR Regime Pullback Tight-Target Canonical Alpha
- **Strategy ID**: atr_regime_pullback_tight_target
- **Version**: 1.0
- **Created**: 2026-05-12
- **Updated**: 2026-05-12
- **Status**: tested-rejected
- **In-sample window**: 2024-08-01 → 2026-01-31 (RTH sessions
  only, US/Eastern)
- **OOS reserved window**: 2026-02-01 → 2026-05-04 (DO NOT load
  during in-sample work)
- **Library version**: nb_lib v2.3 (tests 310/310 after parent's
  `FILL_ASSUMPTIONS` enum extension)
- **Data source**: `load_seconds` (matches parent and
  tested-fleet convention)
- **Account preset**: `apex_50k_eod_eval` (Rithmic variant) initially;
  optional eval → PA transition mid-stream

---

## 2-9. Inherited sections (UNCHANGED from parent canonical)

The following sections are **inherited verbatim** from the parent
canonical spec at
`nb_lib/strategy_specs/canonical/atr_regime_pullback_continuation.md`.
No re-derivation, no re-tuning. The implementation MUST read those
sections from the parent file.

| Inherited section | Topic | Parent file location |
|---|---|---|
| 2 | Signal window definitions per timeframe | Section 2 |
| 3 | Phase 0 — multi-timeframe bar prep + lookahead audit | Section 3 |
| 4 | Phase 1 — 30-min trend qualification | Section 4 |
| 5 | Phase 2 — 5-min regime gates | Section 5 |
| 6 | Phase 3 — 5-min pullback detection | Section 6 |
| 7 | Phase 4 — 1-min reversal candle | Section 7 |
| 8 | Phase 5 — watch window + entry timing | Section 8 |
| 9 | Position sizing (tier classifier, vol mult, Mechanic 1/2) | Section 9, with one change in 9.7 below |

### 9.7 OVERRIDE — Contract sizing with new stop distance

Identical to parent Section 9.7 *except* the stop-distance constant:

```python
stop_distance_pts = 1.0 * atr_5m  # was 1.25 in parent; spec Section 10 below
risk_per_contract = stop_distance_pts * POINT_VALUE  # $2/pt for MNQ
contracts = max(1, int(round(risk_dollars / risk_per_contract)))
contracts = min(contracts, tracker.preset["max_contracts_mnq"])
```

The tighter 1.0×ATR stop produces slightly larger contract counts
for the same risk-dollar budget. Dollar-risk per trade is
conserved by design.

---

## 10. TradeLifecycle parameters (CHANGED — the only meaningful divergence)

### 10.1 Brackets (single-target, locked at signal moment)

ATR = `atr_5m` value at signal moment T (parent Section 5; last
completed 5-min bar). The same ATR value is used for both stop
and target; bracket distances are locked at T and do NOT update
during the trade (no trailing).

For LONG entry at `entry_price`:

- **Stop**: `entry_price - 1.0 × ATR`
- **Target**: `entry_price + 1.5 × ATR` (single decision; full
  close)
- **No TP1.** (Single target = TP1 in lifecycle API terms.)
- **No BE arm.** Disabled via large sentinel
  (`be_arm_pts = 10 × ATR`, never reached before target/stop
  fires).
- **No runner.** `use_runner=False` → full exit at first target
  touch.

For SHORT entry: symmetric (`-` ↔ `+`).

R:R is 1.5:1. Theoretical breakeven win rate ~40%.

### 10.2 Friction (BAND_B parameters)

**UNCHANGED from parent**: `stop_overshoot=1.16 pt`,
`tp_slippage=0.0 pt`, `commission_per_contract_per_side=$0.35`.

### 10.3 Lifecycle API mapping

Because `nb_lib.lifecycle.TradeLifecycle` exposes a TP1/TP2/BE/runner
API, the single-target geometry maps to:

```python
life = TradeLifecycle(
    entry_ts=entry_ts,
    entry_price=entry_price,
    direction=direction_int,
    stop_price=entry_price - direction_int * 1.0 * atr_5m,
    tp1_pts=1.5 * atr_5m,        # this is the SINGLE target
    tp2_pts=10.0 * atr_5m,       # sentinel; unreachable; not used
    be_arm_pts=10.0 * atr_5m,    # sentinel; never armed
    be_offset=0.0,
    use_runner=False,            # full exit at "TP1" (our target)
    # tp1_close_contracts: omit (None) → defaults to contract_count = full close
    session_close_time=session_close,
    eod_flat_seconds_before_close=EOD_FLAT_SECONDS_BEFORE_CLOSE,
    compliance_check=compliance_check,
    contract_count=contracts,
    point_value=POINT_VALUE,
    empirical_params=EMPIRICAL_PARAMS,
    on_entry=on_entry,
    # on_partial_fill: omit (no partials in single-target mode)
    on_exit=on_exit,
    calendar=calendar,
    logger=logger,
)
```

API constraints enforced by lifecycle:

- `use_runner=False` + `tp1_close_contracts<contract_count` is
  prohibited (raises ValueError). Solution: leave
  `tp1_close_contracts=None` (defaults to `contract_count`,
  full close at "TP1").
- Trade record's `exit_reason` will be `"tp1"` when the target
  hits (it's literally TP1 in the API; semantically our single
  target). Stop hits remain `"full_stop"`. EOD/compliance exits
  unchanged.

### 10.4 Pre-committed values + rationale (FIRST PRINCIPLES)

The following rationale was committed **before re-examining the
parent's per-trade exit-reason distribution**. It draws on general
claims about MNQ intraday continuation behavior, not on the
specific failure modes of the parent run.

1. **1.0 × ATR stop** (tighter than parent's 1.25):
   - Reduces per-contract dollar loss on stops, easing
     Apex-floor pressure (the parent's 11/12 multistart breaches
     were drawdown-floor failures).
   - Symmetric with the smaller target distance — same ATR
     reference, smaller absolute multiplier.
2. **1.5 × ATR target** (vs. parent's 2.5):
   - Short-horizon trend literature (Carver *Leveraged Trading*;
     Clenow short-term momentum work; futures-systems writeups)
     consistently locates intraday trend expectancy in the first
     1-2 ATR of favorable excursion. 1.5 sits at the upper end
     of that band.
   - Above 2 ATR, marginal favorable excursion is dominated by
     mean-reversion noise on intraday timeframes; runner
     mechanics rely on capturing that excursion, which is
     unreliable at MNQ's typical 5-min ATR (5-15 pts).
3. **No partial close**:
   - Partial-fill mechanics introduce three independent
     decisions per trade (TP1 distance, BE arm trigger, TP2
     distance) and three sources of expectancy leakage.
     Collapsing to one decision isolates entry-edge from
     trail-management.
   - Eliminates the "TP1-fired-then-BE-stops-at-zero" pathway,
     which is a structural attribute of partial-fill systems
     regardless of strategy quality.
4. **No BE arm**:
   - BE arming convolves entry-edge with trail-management. With
     single target, there is no leg to protect after a partial;
     the only way to manage trade is to give it room to either
     hit target or stop.
5. **R:R 1.5:1**:
   - Asymmetric upside preferred over symmetric (1:1) because
     trend-continuation entries surviving the regime gate
     should produce a positive directional excursion *on
     average*; allocating more upside captures that.
   - Wider R:R (2:1+) re-introduces the parent's "rarely
     reached" problem.

**Not chosen and why:**

- **Time-stop-based** (no fixed target, exit at fixed-time): valid
  alternative; deferred because it adds a hyperparameter
  (the time window). If this fork fails, time-stop is a logical
  successor and warrants its own candidate file in a future
  session.
- **Symmetric tight bracket** (1.0 stop / 1.0 target): vulnerable
  to commission + slippage drag at MNQ tick size on fixed-risk
  sizing.
- **Wider stop with same 1.5 target** (e.g., 1.5/1.5): reduces
  R:R to 1:1 and accelerates Apex-floor pressure.

---

## 11. Compliance and EOD handling

**UNCHANGED from parent Section 11.** Same combined compliance
check (DLL + drawdown + EOD), same 90-second EOD-flat buffer,
same optional eval → PA transition logic.

---

## 12. Runtime assertions (CHANGED — bracket-order only)

Per parent Section 12, runtime assertions are required in
production code. Changes for this fork:

### 12.1-12.4: UNCHANGED from parent

Timeframe staleness, indicator sanity, tier classification, and
sizing-bounds assertions remain identical. (Note: the sizing-bounds
range `[$175, $1755]` is unchanged because the risk-dollar
calculation is unchanged; only the stop distance changes contract
count.)

### 12.5 OVERRIDE — Bracket consistency (single-target)

Replaces parent's 4-leg assertion:

```python
target_price = entry_price + direction * 1.5 * atr_5m
stop_price   = entry_price - direction * 1.0 * atr_5m
if side == "long":
    assert stop_price < entry_price < target_price, (
        f"LONG bracket order violation: stop={stop_price}, "
        f"entry={entry_price}, target={target_price}"
    )
else:
    assert stop_price > entry_price > target_price, (
        f"SHORT bracket order violation: stop={stop_price}, "
        f"entry={entry_price}, target={target_price}"
    )
```

### 12.6: UNCHANGED from parent

Trade lifecycle invariants (entry_ts ≥ signal_ts + 60s; exit_ts >
entry_ts).

---

## 13. OOS reservation policy

**UNCHANGED from parent Section 13.** Same in-sample / OOS
boundaries. Same post-test policy. Same `assert_in_sample(df)`
guard at the top of the runner.

If this fork shows in-sample promise (PF ≥ 1.5), mandatory OOS
validation on 2026-02-01 → 2026-05-04 with parameters frozen.
NOTE: an OOS pass on the fork combined with the parent's failure
would be epistemically significant — it confirms the
geometry-was-the-binding-constraint hypothesis and clears the
family for further work.

---

## 14. Stage-by-stage iteration gates

Because this fork inherits Stages A–I and K verbatim from the
parent's implementation, only Stage J (lifecycle integration) and
Stage L (in-sample run) require new implementation work.

### Stage J — TradeLifecycle integration (CHANGED)

- Build `TradeLifecycle` per Section 10.3 mapping.
- Verify `use_runner=False` and `tp1_close_contracts=None`
  (default) combination passes the lifecycle's API constraint.
- HALT-BRACKET-VIOLATION if stop/target order is wrong (Section
  12.5).
- HALT-API-MISCONFIG if lifecycle raises on init due to
  partial-close + use_runner=False mismatch.

### Stage L — In-sample test (parameter-identical to parent)

- Run full 2024-08-01 → 2026-01-31 window.
- Generate results CSV at
  `C:/VMShare/NT8lab/atr_regime_pullback_tight_target_trades.csv`.
- Apply Section 13 OOS guard.
- **Verify trade count matches parent.** Because entry logic is
  identical, n should be 15 ± 1 (allowing for any minor
  precision boundary at the 1.0-vs-1.25 ATR stop interaction
  with watch-window skip; this would only matter if a stop fired
  inside the watch window, which the watch logic doesn't
  consider). If n diverges materially from 15, debug entry
  pipeline before reporting test results.

All other stages (A–I, K) reuse parent script's already-tested
helpers; the fork SHOULD NOT re-implement them.

---

## 15. Expected outcomes (honest priors, recap)

Per Section 0.3:

- **70%**: no in-sample edge. Entry mechanism lacks edge;
  geometry change does not rescue it.
- **15%**: in-sample edge surfaces (PF ≥ 1.5, n ≥ 15). Mandatory
  OOS validation follows; if it survives, the fork has unique
  epistemic value — it isolates entry-edge from
  trail-management.
- **10%**: PF moves from 0.30 toward 1.0 but still loses.
  Partial geometry-was-the-constraint vindication without genuine
  edge. Family CLOSED at `tested-rejected`.
- **5%**: execution mechanic break (e.g., target unreachable on
  most trades, or watch-window skip rate explodes — neither
  expected because watch and entry logic are unchanged).

### 15.1 What signals "genuine edge"

- In-sample PF ≥ 1.5 across n ≥ 15
- Win rate ≥ 40% (the breakeven hurdle at 1.5:1 R:R)
- Apex eval account remains ACTIVE or PASSES (not FAILED) at
  end of in-sample window
- Parent's exit-reason composition (37.6% full_stop) materially
  improves — though this is a CONSEQUENCE check, not a primary
  criterion

### 15.2 What signals "selection bias"

- In-sample PF > 2.0 — this would be SURPRISING given parent's
  PF 0.30 with identical entries; would suggest bracket-only
  hypothesis is correct but warrants extra OOS scrutiny.
- Most P&L concentrated in 1-2 trades — single-target single-
  decision means trade P&L distribution is wider; check top-3
  concentration.

---

## 16. Pre-committed pass criteria for in-sample test

Stated here so they cannot be re-defined post-hoc:

| Criterion | Threshold | Action if met / not met |
|---|---|---|
| Account state at end of in-sample | not FAILED | If FAILED → `tested-rejected`; report exit-reason composition |
| Total P&L | > $0 | If ≤ $0 → `tested-rejected` |
| Profit Factor | ≥ 1.5 | If < 1.5 → `tested-rejected` even if total P&L > $0 (insufficient edge to justify OOS burn) |
| Trade count | ≥ 10 | If < 10 → "insufficient sample"; do NOT promote to OOS |
| Win rate | ≥ 40% | (Informational — at 1.5:1 R:R this is breakeven; below = strategy is losing on selection, not just on bracket) |

A run that clears all four pre-commit criteria proceeds to MANDATORY OOS validation
(Section 13). A run that fails any criterion ends the fork at
`tested-rejected` and closes the `atr_regime_pullback_*` family.

---

**End of spec.** Parameters in Sections 9.7, 10, and 12.5 are
LOCKED. No tuning during implementation or testing. Any deviation
requires a separate iteration with explicit operator sign-off.
