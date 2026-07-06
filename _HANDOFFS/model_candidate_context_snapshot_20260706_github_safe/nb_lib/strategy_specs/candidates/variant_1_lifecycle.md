---
name: "PRJ_3 Variant 1 (Lifecycle)"
tagline: "First nb_lib-native noise-band breakout at 9:36 ET; same signal logic as noise_brk Canonical Alpha"
status: "tested-rejected"
created: 2026-05-09
updated: 2026-05-12
source: "Built as the first nb_lib-native strategy; intended to exercise the TradeLifecycle composition pattern. Spec same as noise_brk family."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-09:36 ET (signal window); 09:36 entry"
hold_duration: "intraday"

# Signal characteristics
signal_type: "breakout"
indicators: ["ADR(20)"]
timeframes_used: ["1-second"]

# Execution
brackets: "fixed-point"
position_sizing: "fixed-contracts"

# Cross-references
canonical_spec: null                 # Variant 1 doesn't have its own FINAL spec; see noise_brk's
implementation: "../../scripts/prj3_lifecycle_variant.py"
related_candidates:
  - "noise_brk_canonical_alpha.md"   # functionally identical strategy

# Test status
test_results:
  in_sample_n: 5
  in_sample_pnl_dollars: -2010.00
  in_sample_pf: 0.05
  in_sample_win_rate: 0.20            # 1W / 4L
  out_of_sample_tested: false
  multistart_pass_rate: null

tags:
  - rth-only
  - intraday
  - breakout
  - fixed-brackets
  - tested-rejected
  - post-j3-fix
---

# PRJ_3 Variant 1 (Lifecycle)

## 1. Thesis

The first nb_lib-native strategy build. Same edge thesis as noise_brk
Canonical Alpha — by 9:36 ET, six minutes after the cash open, the
overnight risk-premium unwind has resolved enough that a one-sided
break of a volatility-scaled noise band (ADR(20) × 0.25 anchored to
the 9:30 RTH open) is an actionable directional signal. Variant 1
was built to exercise the library's composition pattern; its signal
logic is functionally identical to noise_brk Canonical Alpha's.

## 2. Mechanism

- **Overnight risk-premium unwind.** Globex-hour positioning resolves
  against US-hour participation in the first 5-10 minutes of the
  cash session.
- **ADR(20)-scaled noise band.** Quarter of trailing 20-day RTH
  range; adapts to volatility regime.
- **Single-sided break filter.** Days where both bands break in
  the first six minutes are rotational/whipsaw — strategy filters
  them out via the most-recent-break tiebreak.

## 3. Signal logic (entry conditions)

Signal evaluates at 11:10:00... wait, no. **Variant 1's signal is at
9:36:00 ET** (same as noise_brk Canonical Alpha). At 9:36:00:
- Compute `upper_band = open_9_30 + 0.25*ADR(20)` and `lower_band`
  symmetrically.
- Track `session_high_so_far` and `session_low_so_far` in
  [9:30:00, 9:36:00).
- If only upper broken → LONG; only lower broken → SHORT;
  both broken → most-recent-break tiebreak; neither → no trade.

Entry at 9:36:00 second-bar OPEN via `resolve_entry_fill`'s
fill-at-exactly-time-T pattern (Pattern 2 from
`nb_lib/execution.py`).

## 4. Exit logic (stops, targets, time-based exits)

- **Stop:** entry ± 32 points (BAND_B applies 1.16pt overshoot on stop hit).
- **TP1:** entry ± 10 points, closes 7 of 15 contracts (partial).
- **TP2:** entry ± 80 points, closes runner (8 contracts).
- **BE arming:** after MFE ≥ 6 points, BE arms after 3-bar delay;
  stop moves to entry.
- **MIN_HOLD:** 10 bars after entry, TP1/TP2 are non-live; stop +
  compliance still active.
- **EOD flat:** 15:58:30 ET (90s before 16:00 close;
  calendar-aware for half-days).
- **Apex 50K EOD eval compliance:** DLL ($1K), drawdown floor
  ($2K), contract limit, news blackout, EOD.

## 5. Position sizing

- 15 MNQ contracts at entry. TP1 closes 7; runner = 8.
- Fixed contracts (no scaling).

## 6. Required indicators / data

- **Indicators:** ADR(20) — RTH-only daily ranges, prior-days-only,
  half-day-excluded.
- **Bar resolutions:** 1-second only.
- **Calendar:** half-day awareness for ADR exclusion + EOD flat
  timing.
- **External:** none.

## 7. Differentiation

Variant 1 is **the original of the noise_brk family** — it was the
first build of this strategy on nb_lib. noise_brk Canonical Alpha
is a re-spec of the same strategy with cleaner methodology framing
+ extended window (2026-05-04 vs Variant 1's 2026-01-31). The two
produce identical numbers on identical windows; they're best
understood as one strategy with two specifications.

The key difference vs PRJ_3 Canonical Alpha: noise-band breakout
(6-minute scanning window) vs fractal-pullback (30 + 120 minute
multi-phase pipeline). Different signal mechanism.

## 8. Required research before spec drafting

N/A — this strategy was built before the wiki existed. Treated as
retrospective documentation.

## 9. Source / references

- Implementation: `nb_lib/scripts/prj3_lifecycle_variant.py`
- Build report: `nb_lib/scripts/prj3_lifecycle_variant.py` docstring
  + git history (no dedicated build report — this was the first
  iteration that established the build-report pattern that later
  strategies use).
- Methodology debt closure: `nb_lib_j3fix_report.md` (post-J#3-fix
  baseline established).
- Related candidate: `noise_brk_canonical_alpha.md` (same strategy,
  different framing).
- Related spec: `../canonical/noise_brk_canonical_alpha.md` (noise_brk
  family's FINAL spec; closest applicable spec for Variant 1).

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-09 | `tested-rejected (pre-J#3-fix)` | First build; pre-J#3-fix baseline n=92, $-7,453.50, PF 0.20 — these numbers are NOT authoritative (synthetic-in-methodology post-FAILED records polluted the trade list). |
| 2026-05-09 | `tested-rejected (post-J#3-fix)` | Methodology debt J#3 fix landed across all three nb_lib-native scripts. Variant 1 outer loop got the `tracker.state == FAILED → break` guard. New authoritative baseline: **n=5, $-2,010.00, PF 0.05**. Strategy fails Apex 50K eval after 5 real trades. |
| 2026-05-12 | `tested-rejected` (retrospective) | Wiki entry created. Strategy joins the "4 strategies, 0 positive Apex baselines" cohort. |
