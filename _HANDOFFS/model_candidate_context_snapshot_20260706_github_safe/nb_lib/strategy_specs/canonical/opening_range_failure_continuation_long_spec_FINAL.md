---
status: "spec-drafted-final-bypass"
---

# Opening Range Failure Continuation Long FINAL Spec

**Strategy ID:** `opening_range_failure_continuation_long`  
**Status:** SPEC-DRAFTED-FINAL-BYPASS  
**Created:** 2026-05-21  
**Canonical path:** `nb_lib/strategy_specs/canonical/opening_range_failure_continuation_long_spec_FINAL.md`  
**Candidate lineage:** `nb_lib/strategy_specs/candidates/opening_range_failure_continuation_long.md`  
**Bypass authorization:** Operator decision 2026-05-21 to skip R4 and proceed directly to informational FINAL spec, implementation, and multistart for the highest-confidence candidate.

---

## Methodology Disclosure

This is a **bypass / informational** spec. The normal R4 and v1.4 gates
were intentionally skipped. Results from this spec:

1. Do not consume OOS.
2. Do not graduate the candidate.
3. May reject the idea, preserve it as registry-useful, or justify a
   clean non-bypass re-run through the standard gate.

The core question is whether "trade the hold, not the break" improves
over naive opening-range breakout behavior.

---

## 0. Scope And Priors

This is a long-only opening-range continuation candidate.

| Outcome | Prior | Meaning |
|---|---:|---|
| Sparse / frequency failure | 0.25 | Break-and-hold is too selective |
| No edge / Apex failure | 0.35 | Holds are not predictive |
| Weak positive / registry-useful | 0.25 | Some edge, not standalone |
| Strong informational edge | 0.10 | PF >= 1.50 and account survival |
| Implementation blocker | 0.05 | Stop-entry or OR geometry issue |

---

## 1. Thesis

The opening range high is an objective level watched by intraday traders.
This candidate does not buy the first break. It waits for a confirmed
break above OR-high, then a pullback toward OR-high that does not close
back inside the range, then a hold bar that closes back above the prior
bar's high.

The edge claim is selectivity: failed breakouts re-enter the range; good
breakouts defend the prior range high as support.

---

## 2. Entry Signal

```text
instrument: MNQ
session: RTH
primary timeframe: 2-minute bars from 1-second OHLCV
opening range: 09:30:00-10:00:00 ET
scan window: 10:00:00-11:00:00 ET
direction: long only
max structural entries/day: 1
```

Predicates:

1. Compute OR-high and OR-low from completed 2-minute bars in the
   09:30-10:00 window.
2. After 10:00, require a completed 2-minute bar to close above OR-high.
3. After that break, require price to pull back to within
   `0.25 * ATR14` of OR-high.
4. Any completed bar close below OR-high invalidates the setup for the day.
5. Once pullback has occurred, a hold bar qualifies when it closes above
   the prior bar's high and remains above OR-high.
6. Entry is stop-market at hold-bar high + one MNQ tick, armed at
   `signal_ts + 1 second`.
7. Entry order expires after three 2-minute bars.

All bar predicates use completed bars only.

---

## 3. Indicators

Required:

- 2-minute OHLCV bars.
- ATR14 on 2-minute bars using Wilder smoothing.
- Opening range high/low.

EMA8 was noted in the candidate as optional context and is deliberately
not included in this first bypass implementation.

---

## 4. Risk And Position Sizing

```text
risk_dollars = 300
point_value = 2.0
tick_size = 0.25
max_contracts = 12
stop_band = [5, 35] points
daily_loss_limit = 2 realized losses
```

Initial stop:

```python
initial_stop = OR_high - 0.50
```

Contracts:

```python
contracts = floor(300 / (stop_pts * 2.0))
contracts = min(contracts, 12)
skip if contracts < 1
```

The [5, 35] stop band is intentionally tighter than wide-state reversal
because this is a defended-level continuation setup, not a wide-state
exhaustion bar.

---

## 5. Bracket And Management

No adaptive specialists. Static lifecycle:

```python
TP1 = 1.00R
TP2 = 2.25R
TP1 close fraction = 0.50
BE arm = 1.50R
BE offset = 0.25 pt
runner trail = fixed MFE at 1.25R
max hold = 30 minutes
```

Time exit reason:

```text
opening_range_failure_continuation_time_exit_30m
```

---

## 6. Informational Pass Criteria

This bypass cannot graduate. Informational interpretation:

| Verdict | Conditions |
|---|---|
| Frequency failure | n < 80 across 12 starts |
| Informational rejected | PF < 1.05 or repeated Apex failure |
| Registry-useful | PF [1.05, 1.50), positive P&L, failed starts <= 2 |
| Strong informational | PF >= 1.50, n >= 80, failed starts <= 1 |

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
attribution, exit reasons, and Apex failure count.

---

## 8. OOS Guard

Implementation must assert loaded data remains before 2026-02-01 for
in-sample runs. This branch is not OOS-eligible regardless of result.

---

## 9. HARD-HALT Conditions

- HARD-HALT-OOS-LEAK.
- HARD-HALT-SHORT-SIDE-ADDITION: short sibling is separate.
- HARD-HALT-EXTRA-FILTERS: no EMA8 or volume additions in this bypass.
- HARD-HALT-STOP-BAND-DRIFT: do not widen beyond [5, 35] without a new spec.
- HARD-HALT-GRADUATION: positive bypass result cannot graduate directly.

---

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-21 | spec-drafted-final-bypass | FINAL bypass spec drafted for direct implementation + 12-start informational multistart. |
