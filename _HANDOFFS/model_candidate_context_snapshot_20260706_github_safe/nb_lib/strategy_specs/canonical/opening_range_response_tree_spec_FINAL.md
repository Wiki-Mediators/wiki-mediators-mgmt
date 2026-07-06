---
status: "spec-drafted-final-bypass"
---

# Opening Range Response Tree FINAL Spec

**Strategy ID:** `opening_range_response_tree`  
**Status:** SPEC-DRAFTED-FINAL-BYPASS  
**Created:** 2026-05-21  
**Canonical path:** `nb_lib/strategy_specs/canonical/opening_range_response_tree_spec_FINAL.md`  
**Candidate lineage:** `nb_lib/strategy_specs/candidates/opening_range_response_tree.md`  
**Bypass authorization:** Operator decision 2026-05-21 to skip R4 and proceed directly to informational FINAL spec, implementation, and multistart for the composition-node variant.

---

## Methodology Disclosure

This is a **bypass / informational** spec. The normal R4 and v1.4 gates
were intentionally skipped. Results from this spec:

1. Do not consume OOS.
2. Do not graduate the candidate.
3. Must be read primarily by branch attribution, not only aggregate PF.
4. May reject the idea, preserve a useful branch as registry evidence, or
   justify a clean non-bypass re-run through the standard gates.

The core question is whether one opening-range level can act as a
composition node with useful branch-specific signal: failed-break
reversal, break-hold continuation, or expansion breakout.

---

## 0. Scope And Priors

This is a two-sided opening-range response tree on MNQ RTH. It permits at
most one structural entry per day across all branches.

| Outcome | Prior | Meaning |
|---|---:|---|
| Frequency failure | 0.20 | One-trade-per-day tree is too sparse |
| Aggregate no edge | 0.35 | Branches blend into negative expectancy |
| One branch useful | 0.30 | Attribution reveals a registry-useful sub-signal |
| Strong informational edge | 0.10 | Aggregate PF >= 1.50 with account survival |
| Implementation blocker | 0.05 | Branch conflict or fill semantics issue |

---

## 1. Branch Thesis

The opening range high/low is a shared objective level. The candidate
does not assume a single response to that level. It classifies the first
qualified post-OR interaction into one of three branches:

- `sweep_reversal`: price trades beyond OR boundary and closes back
  inside the range, implying a failed break / stop sweep.
- `break_hold_continuation`: price accepts beyond OR boundary, pulls
  back toward the boundary, and holds without closing back inside.
- `expansion_breakout`: after 10:30 ET, price breaks beyond OR boundary
  with a wide expansion bar.

The experiment is composition-node instrumentation. A weak aggregate can
still be informative if one branch carries positive expectancy and the
others drag.

---

## 2. Entry Signal

```text
instrument: MNQ
session: RTH
primary timeframe: 2-minute bars from 1-second OHLCV
opening range: 09:30:00-10:00:00 ET
scan window: 10:00:00-13:00:00 ET
max structural entries/day: 1 across all branches
```

All bar predicates use completed 2-minute bars. ATR values used by a
current decision are the value available before the current bar by using
`atr14_prior = atr14.shift(1)`.

### Branch A: Sweep-Reversal

Predicates:

1. After 10:00 ET, a completed 2-minute bar trades beyond an OR boundary.
2. OR-high sweep: bar high > OR-high and bar close < OR-high and close
   remains inside the OR.
3. OR-low sweep: bar low < OR-low and bar close > OR-low and close
   remains inside the OR.
4. Entry is stop-market in the fade direction:
   - OR-high sweep: short at reclaim bar low - 1 tick.
   - OR-low sweep: long at reclaim bar high + 1 tick.

Stop:

- Short: reclaim bar high + 1 tick.
- Long: reclaim bar low - 1 tick.

Management:

- TP1 1.0R, TP2 2.0R, BE arm 1.25R, max hold 30 minutes.

### Branch B: Break-Hold Continuation

Predicates:

1. A completed bar closes beyond the OR boundary.
2. Price pulls back toward the broken boundary within `0.25 * atr14_prior`.
3. No completed bar closes back inside the OR after acceptance.
4. Hold bar closes back in the break direction off the level:
   - Long: close > prior high and close > OR-high.
   - Short: close < prior low and close < OR-low.
5. Entry is stop-market with trend:
   - Long: hold bar high + 1 tick.
   - Short: hold bar low - 1 tick.

Stop:

- Long: OR-high - 0.50.
- Short: OR-low + 0.50.

Management:

- TP1 1.0R, TP2 2.25R, BE arm 1.5R, max hold 35 minutes.

### Branch C: Expansion Breakout

Predicates:

1. Time is 10:30 ET or later.
2. A completed 2-minute bar closes beyond the OR boundary.
3. The same bar's range is at least `1.5 * atr14_prior`.
4. Entry is stop-market with trend:
   - Long: breakout bar high + 1 tick.
   - Short: breakout bar low - 1 tick.

Stop:

- Long: max(OR midpoint, entry - 1.0 * atr14_prior), rounded to tick.
- Short: min(OR midpoint, entry + 1.0 * atr14_prior), rounded to tick.

Management:

- TP1 1.0R, TP2 2.25R, BE arm 1.5R, max hold 40 minutes.

---

## 3. Precedence And Conflict Rules

The tree evaluates completed bars from 10:00 ET through 13:00 ET. The
first valid branch signal takes the day. Later signals are not traded in
this bypass implementation.

Within a bar:

1. Sweep-reversal is checked first.
2. Break-hold continuation is checked second.
3. Expansion breakout is checked third.

This deliberately lets the earliest reclaim event beat later continuation
logic if both are somehow possible on the same completed bar.

---

## 4. Risk And Position Sizing

```text
risk_dollars = 300
point_value = 2.0
tick_size = 0.25
max_contracts = 12
stop_band = [5, 40] points
daily_loss_limit = 2 realized losses
```

Contracts:

```python
contracts = floor(300 / (stop_pts * 2.0))
contracts = min(contracts, 12)
skip if contracts < 1
```

The [5, 40] stop band is wider than the single continuation test because
this tree includes reversal and expansion branches with wider structural
bars.

---

## 5. Indicators And Data

Required:

- 1-second OHLCV source data.
- 2-minute derived OHLCV bars.
- Opening range high/low from 09:30-10:00 ET.
- ATR14 on 2-minute bars using Wilder smoothing.
- Optional EMA8 context is not used in the bypass implementation.

No footprint, delta, or order-flow data is required.

---

## 6. Informational Pass Criteria

This bypass cannot graduate. Informational interpretation:

| Verdict | Conditions |
|---|---|
| Frequency failure | aggregate n < 80 across 12 starts |
| Branch frequency failure | no branch has n >= 30 |
| Informational rejected | aggregate PF < 1.05 and no branch PF >= 1.05 with positive P&L |
| Branch registry-useful | a branch has PF [1.05, 1.50), positive P&L, and no severe Apex failure concentration |
| Strong informational | aggregate PF >= 1.50, n >= 80, failed starts <= 1 |

The branch table is the key output.

---

## 7. Multistart Configuration

```text
starts: monthly 2024-08-01 through 2025-07-01
window length: 42 trading days
account: fresh Apex 50K EOD ComplianceTracker per start
friction: BAND_B
OOS: sealed from 2026-02-01
```

Report aggregate P&L, PF, trade count, per-start breakdown, direction
attribution, branch attribution, branch-by-direction attribution, exit
reasons, and Apex failure count.

---

## 8. OOS Guard

Implementation must assert loaded data remains before 2026-02-01 for
in-sample runs. This branch is not OOS-eligible regardless of result.

---

## 9. HARD-HALT Conditions

- HARD-HALT-OOS-LEAK.
- HARD-HALT-BRANCH-RETUNING: do not remove a branch after seeing the
  result inside this bypass.
- HARD-HALT-EXTRA-FILTERS: no EMA, volume, VWAP, delta, or time filters
  beyond this spec.
- HARD-HALT-GRADUATION: positive bypass result cannot graduate directly.

---

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-21 | spec-drafted-final-bypass | FINAL bypass spec drafted for direct implementation + 12-start informational multistart. |
