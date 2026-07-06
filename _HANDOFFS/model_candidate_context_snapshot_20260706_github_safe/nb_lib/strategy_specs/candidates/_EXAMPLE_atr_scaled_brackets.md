---
name: "ATR-Scaled Brackets for PRJ_3 Canonical Alpha (example untested candidate)"
tagline: "Replace PRJ_3's fixed-point stops/targets with ATR-scaled brackets to make them volatility-adaptive"
status: "untested-triage-passed"
created: 2026-05-11
updated: 2026-05-12
source: "Operator hypothesis post-PRJ_3-raw-signal-diagnostic: maybe the fixed-point brackets (25 stop / 10 TP1 / 80 TP2) are mis-scaled for varying regimes; ATR-scaling might rescue per-trade expectancy."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-12:00 ET (3-phase pipeline; identical to PRJ_3 Canonical Alpha)"
hold_duration: "intraday"

# Signal characteristics
signal_type: "pullback"
indicators: ["11-bar fractal (minute bars)", "ATR(?) on daily bars"]
timeframes_used: ["1-second", "1-minute", "daily"]

# Execution
brackets: "atr-scaled"               # KEY DIFFERENCE from PRJ_3 Canonical Alpha
position_sizing: "fixed-contracts"

# Cross-references
canonical_spec: null                 # not drafted yet
implementation: null                 # not implemented yet
related_candidates:
  - "prj3_canonical_alpha.md"        # parent strategy

# Test status (none — untested)
test_results:
  in_sample_n: null
  in_sample_pnl_dollars: null
  in_sample_pf: null
  out_of_sample_tested: false

tags:
  - rth-only
  - intraday
  - pullback
  - atr-scaled
  - example-only
  - awaiting-operator-decisions
---

# ATR-Scaled Brackets for PRJ_3 Canonical Alpha (example untested candidate)

> **Note:** filename prefixed with `_EXAMPLE_` — this entry exists
> primarily as a worked example of the schema for an untested
> candidate. It also preserves the design context for an actual
> iteration that was deferred mid-design. If the operator later
> wants to pick up the ATR-scaled brackets idea, this file is the
> starting point; rename it to `atr_scaled_brackets_prj3.md` and
> move forward.

## 1. Thesis

PRJ_3 Canonical Alpha's post-lookahead-fix raw signal diagnostic
showed mean **-$176/trade** on 8 real pre-FAILED trades with fixed
25-pt stops, 10-pt TP1, 80-pt TP2. The hypothesis: the fixed-point
brackets might be **mis-scaled for varying volatility regimes**.
A 25-pt stop in a quiet regime is too tight (many full-stop hits
that would have run to TP under wider stops); in a volatile regime
the same 25-pt stop is too tight in a different way (stop hit
before any meaningful favorable move). ATR-scaling the brackets
adapts them to the prevailing regime.

This is a parameter-replacement candidate, not a new signal. The
signal pipeline (trend → fractal → pullback → confirmation → T+2
entry) stays identical to PRJ_3 Canonical Alpha. Only the bracket
construction changes.

## 2. Mechanism

- **Volatility-regime adaptation.** A fixed stop is "too wide" in
  quiet regimes (gives up edge to slippage) and "too tight" in
  volatile regimes (gets stopped on noise before signal can play
  out). ATR-scaled stops sized to a multiple of recent volatility
  stay proportional.
- **Reward:risk ratio preservation across regimes.** With ATR-
  scaled TP1 and TP2 (same multiples of ATR), the strategy's R:R
  shape is regime-invariant — winners are bigger when ATR is
  larger, losers are also bigger, but the ratio holds.
- **Edge survives volatility but not direction.** If PRJ_3's
  underlying signal has true edge in some regime, ATR-scaling
  prevents fixed brackets from being a regime-specific bug. If
  the signal has no edge in any regime (per the raw signal
  diagnostic), ATR-scaling won't rescue it. The candidate's value
  is bounded by the signal's underlying edge.

## 3. Signal logic (entry conditions)

**Identical to PRJ_3 Canonical Alpha's three phases.** Trend
direction in [9:30, 10:00); 11-bar minute fractal in same window;
asymmetric proximity wait in [10:00, 12:00); single-bar green/red
confirmation; T+2-second entry at confirming bar's right-edge +
2 seconds.

No changes to signal logic.

## 4. Exit logic

**ATR-scaled** brackets (replace PRJ_3's fixed values):

- **Stop:** `STOP_ATR_MULT × ATR(N)` instead of 25 fixed points.
- **TP1:** `TP1_ATR_MULT × ATR(N)` instead of 10 fixed.
- **TP2:** `TP2_ATR_MULT × ATR(N)` instead of 80 fixed.
- **BE arm:** `BE_ARM_ATR_MULT × ATR(N)` instead of 6 fixed.
- **BE delay, MIN_HOLD, EOD flat:** unchanged from PRJ_3.

**Specific multipliers are TBD per operator decision.** Initial
candidates (no implementation yet):
- STOP_ATR_MULT: 0.25 (yields ~25pt stop at ATR ~100pt — matches
  PRJ_3's fixed default at the current ATR regime).
- TP1_ATR_MULT: 0.10 (yields ~10pt TP1).
- TP2_ATR_MULT: 0.80 (yields ~80pt TP2).
- BE_ARM_ATR_MULT: 0.06 (yields ~6pt arm).

These keep the strategy's R:R shape identical to PRJ_3 at "current"
ATR but scale proportionally for other regimes.

## 5. Position sizing

15 MNQ at entry, TP1 closes 7, runner 8. Identical to PRJ_3
Canonical Alpha. Fixed (no ATR-scaling of contracts).

## 6. Required indicators / data

- **ATR(N) on daily RTH bars** — period N is an open question (see
  Section 8). Computed lookahead-free: strictly prior days, no
  intraday peeking. Built from the 1-second store inline (using
  the noise_brk family's `session_high_low` + half-day-excluded
  pattern, then fed into `nb_lib.indicators.ATR`).
- **11-bar minute fractal** — inherited from PRJ_3 Canonical Alpha;
  inline in the strategy script.
- **Asymmetric proximity, single-bar confirmation** — inherited.
- **Bar resolutions:** 1-second + 1-minute + daily (the new tier).
- **Calendar:** half-day-aware for daily-bar exclusion + EOD flat.

## 7. Differentiation

vs **PRJ_3 Canonical Alpha**: same signal pipeline; **only the
bracket construction differs**. ATR-scaled vs fixed-point.

vs **VP_VABounce Phase 1.5**: VP_VABounce used a *dynamic TP
threshold* (1-minute favorable bar range > 0.75 × 14-day ATR) as
a signal filter, not as the bracket size. This candidate uses ATR
for bracket sizing.

vs **noise_brk Canonical Alpha**: noise_brk uses ADR(20) for the
*entry threshold* (signal-firing condition), not for exit
brackets. This candidate flips the application: same kind of
volatility input, different consumer.

## 8. Required research before spec drafting

The pre-investigation report
`nb_lib_atr_iteration_pre_investigation.md` (2026-05-11) answered
six structural questions and left five open questions that need
operator decisions before this candidate can become a FINAL spec:

- **H.1 — BAND_B friction calibration scope.** Is BAND_B
  RTH-calibrated or session-wide? No documentation in `empirical.py`.
  If the ATR-scaled iteration would ever consider overnight fills,
  this must be answered. (Strategy is RTH-only entry; less acute
  but still worth confirming.)
- **H.2 — VP_VABounce lookahead context.** The pre-investigation
  found the live `vp_vabounce_phase1_5.py` code IS lookahead-free
  (strictly prior days for daily ATR; explicit forward-shift for
  intraday ATR). The "VP_VABounce caused a lookahead bug" framing
  may refer to a pre-Phase-1.5 version. Confirm with operator
  whether there's specific context this iteration should be aware
  of.
- **H.3 — ATR smoothing.** `nb_lib.indicators.ATR` supports Wilder
  (default), SMA, EMA. Fleet precedent: noise_brk uses simple
  mean for ADR; VP_VABounce uses simple mean for 14-day ATR.
  Wilder is the conventional ATR smoothing. **Operator decision.**
- **H.4 — ATR period.** VP_VABounce uses 14. noise_brk uses 20.
  Wilder's original ATR uses 14. **Operator decision.**
- **H.5 — Range definition.** True Range (with prior-close gap)
  vs RTH-only range (no gap). Fleet precedent is RTH-only range.
  **Operator decision.**

Until H.1–H.5 are answered, the candidate is stuck at
`untested-triage-passed`. With them answered, the candidate becomes
`spec-drafted` once a FINAL spec is written.

## 9. Source / references

- Pre-investigation report:
  `nb_lib_atr_iteration_pre_investigation.md`
- Parent strategy: `prj3_canonical_alpha.md` (this candidate file)
  and `../canonical/prj3_canonical_alpha.md` (FINAL spec)
- Raw signal diagnostic that motivated the hypothesis:
  `nb_lib_prj3_raw_signal_diagnostic_report.md` Section D
  (showing -$176/trade pre-FAILED real-trades expectancy)
- Library primitive: `nb_lib.indicators.atr.ATR` (already exists;
  streaming; Wilder/SMA/EMA)
- Precedents: `nb_lib/scripts/noise_brk_canonical_alpha.py:build_adr_per_day`
  (daily-range aggregation pattern) and
  `vp_vabounce_phase1_5.py:build_daily_atr14` (prior-days-only ATR
  pattern)

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-10 | (implicit `untested-ideation`) | Operator raised hypothesis post-raw-signal-diagnostic. No file created yet. |
| 2026-05-11 | `untested-triage-passed` | Pre-investigation report answered six structural questions. Five open decisions (H.1-H.5) need operator input. |
| 2026-05-12 | `untested-triage-passed` (example) | Wiki entry created as worked example. Marked `_EXAMPLE_` to avoid being mistaken for an active triage-passed candidate; remove the underscore prefix when actually picking the iteration up. |
