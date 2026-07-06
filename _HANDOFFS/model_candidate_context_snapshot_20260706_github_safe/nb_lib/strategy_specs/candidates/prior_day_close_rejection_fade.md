---
name: "Prior Day Close Rejection Fade"
tagline: "Fade the test of yesterday's RTH close when a completed bar rejects it."
status: "phase-0-inadmissible-closed"
created: 2026-05-20
updated: 2026-05-20
source: "Strategic synthesis 2026-05-20 from session lessons: single precise high-attention level (not a value-area range), signal-at-rejection timing. Distinct from prior_day_value_area_rejection (tested-rejected) by using one RTH close price rather than a value-area band."
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-15:00 ET"
hold_duration: "intraday"
signal_type: "mean-reversion"
indicators: ["prior-day RTH close", "ATR(14) 2-min", "swing detection"]
timeframes_used: ["1-second source", "2-minute derived"]
brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"
canonical_spec: null
implementation: null
related_candidates:
  - "prior_day_value_area_rejection"
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
tags:
  - rth-only
  - intraday
  - mean-reversion
  - level-rejection
  - prior-day-close
  - two-minute
  - objective-level
---

# Prior Day Close Rejection Fade

## 1. Thesis
Prior-day RTH close is a precise, high-attention intraday reference. It
is not the same as official exchange settlement unless settlement data is
added later; this first candidate intentionally uses the OHLCV-available
RTH close. This candidate fades a test-and-rejection of that one precise
level.

Mechanism: when RTH price approaches the prior-day close from one side,
tests it, and a completed 2-minute bar rejects it (wick rejection,
close back on the originating side, no acceptance across the level),
fade away from the level. The signal fires AT the rejection bar (the
start of the fade move), not after extension.

Counter-hypothesis: mean reversion has struggled in this project
(prior_day_value_area_rejection tested-rejected; wide-state reversal
failed twice). Level-rejection at a single price may behave the same as
value-area rejection. The bet is that ONE precise high-attention level
(settlement) behaves differently from a value-area RANGE — that the
specificity is the difference.

## 2. Mechanism (what edge it captures)
- Prior-day close is a precise, objective, universally-watched level
  (one number, not a discretionary zone or a range).
- A clean test-and-reject signals the level is being defended by
  resting orders; price fails to find acceptance across it.
- Signal fires at the rejection bar (start of the fade), reducing the
  fill-drift that hurt signal-after-move candidates.
- Binary test/reject logic is selective — only clean rejections qualify,
  not every approach.

## 3. Signal logic (entry conditions)
- Reference: prior-day RTH close (single price).
- Approach detection: RTH price comes within 0.25 x ATR(14) of
  prior-day close.
- Rejection trigger (short, approaching from below): a completed
  2-minute bar makes a high at/above prior-day close but closes back
  below it by at least a pre-committed wick fraction; no completed bar
  has closed across (accepted above) the level.
- Rejection trigger (long, approaching from above): symmetric.
- Entry: stop-market on break of the rejection bar's far extreme
  (rejection-bar low for short, high for long).
- Two-sided by design (approach can come from either side); direction
  is determined by approach side, not post-hoc selection.
- Maximum two structural signals per day (one per side).
- Bars evaluated on completion; lookback strictly before current bar.

## 4. Exit logic (stops, targets, time-based exits)
- Initial stop: on the far side of prior-day close (the level that must
  hold for the rejection thesis). Pre-commit buffer at spec stage.
- Stop-band guard: reject signal if stop distance < 5 pts or > 40 pts.
- TP1: 1.0R, close half.
- TP2: 2.0R (mean-reversion targets resolve faster; not 2.25R).
- BE arm: 1.25R (mean reversion gives back gains quickly; arm earlier
  than continuation candidates but still not at-entry).
- Max hold: 45 minutes (rejection fades can take time to resolve toward
  target).
- EOD flat by 15:58:30 ET.

## 5. Position sizing
Fixed dollar risk, $300 per trade: contracts = floor(300 / (stop_points
x $2)), capped at 12 MNQ contracts. Skip if contracts < 1. Daily loss
limit: 2 realized losing trades per RTH date.

## 6. Required indicators / data
Prior-day RTH close (single value per session), ATR(14) on 2-minute
bars, swing detection for rejection-bar identification. 2-minute bars
derived from MNQ 1-second OHLCV. No footprint or order-flow dependency
— fully OHLCV-testable.

## 7. Differentiation (vs already-tested strategies)
Unlike prior_day_value_area_rejection (tested-rejected, n=14, PF 1.17
but fill-drift attrition), this uses ONE precise settlement price, not a
value-area range. The value-area version suffered because the POC/VA
boundaries were fuzzy and TP-to-POC distances were often negative or
unreachable; a single close price has unambiguous geometry. Unlike
wide-state reversal (tested-dead), this is not fading trend extension —
it is fading a specific-level rejection that can occur in any regime.

The bet: precision of the level (one settlement price vs a value-area
band) changes the fill geometry and the participant behavior enough to
behave differently from the failed value-area version.

## 8. Required research before spec drafting
- R4 probe: how often does RTH price test-and-reject prior-day close per
  session? Could be sparse (some days price never approaches it) or
  dense (gappy days test it repeatedly).
- Pre-commit the wick-rejection fraction and approach-proximity
  threshold before testing.
- Fill-mechanics check: does the rejection-bar break entry suffer the
  same drift attrition that killed the value-area version? Run fill-time
  geometry in the R4 probe.
- Honest concern: this is mean-reversion class, which has failed
  repeatedly. The specificity-of-level hypothesis must be tested, not
  assumed. If R4 + fill mechanics look like the value-area version,
  expect similar rejection.
- Check direction balance (approaches from above vs below) for any
  structural asymmetry.

## 9. Source / references
Strategic synthesis from 2026-05-20 session. Prior-day settlement as a
magnet/rejection level is standard market-profile and auction-theory
folklore; the single-price specificity framing is the deliberate
contrast with the failed value-area-range version.

## 10. Status history
| Date | Status | Notes |
|------|--------|-------|
| 2026-05-20 | untested-ideation | Authored from session-lesson synthesis. Single-settlement-price rejection fade, contrasted against tested-rejected value-area-range version. Mean-reversion class — honest risk that it behaves like prior failures. Pending R4 probe with fill-mechanics for frequency and drift. |
| 2026-05-25 | (probe + Phase 0 review) | **R4 v1.2 probe complete + Phase 0 v2 review.** Probe over 23 days produced **7 signals fired, 6 passing fill guards (14% attrition — low)**. Drift: median 0.75pt, p95 3.00pt (LOWEST IN PROJECT). Direction: 5L/2S = 71% long (exceeds 65% pre-committed bound at n=7). Sparsity: **sparse** (6 over 23 days; band ≤8 = sparse). Extrapolated [7, 32] per 60 trading days. Phase 0 verdict: **CONDITIONALLY ADMISSIBLE (borderline INADMISSIBLE)** — R2/R3 MET; R1 PARTIAL (folklore-grounded; no MNQ close-rejection reversion diagnostic); R4 PARTIAL (sparse but low-attrition is unusual positive); R5 PARTIAL (asymmetry interpretation not pre-committed). **Pipeline halted at Phase 0 gate** pending operator decision: close, resolve R1+R5 lightweight, or continue. Probe at `nb_lib/probe_results/prior_day_close_rejection_fade_r4_probe.json`. Phase 0 report at `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_2_prior_day_close_rejection_fade.md`. |
| 2026-05-25 | `phase-0-inadmissible-closed` | **Path B: R1 evidence diagnostic complete. Verdict REFUTES the thesis.** Diagnostic over 126 in-sample days (2024-08-01 to 2025-01-31) measured 18 qualifying wick-rejection events of prior-day RTH close: **7 reverted 1R within 30min (38.9%)**, 11 hit 1R adverse stop first (61.1%). Short reversion rate 33.3% (4/12); long 50.0% (3/6). Compare to ORWS R1 diagnostic 79.5% reversion — this candidate's 38.9% is well below the 60% NOT MET threshold and below the 50% null. **The single-price specificity hypothesis is empirically refuted**: close-rejections continue more often than they revert. **Verdict updated: R1 NOT MET → INADMISSIBLE.** Candidate **CLOSED at Phase 0 gate** — no FINAL spec, no implementation, no in-sample test. Path B saved ~6-10 hours downstream pipeline work via lightweight diagnostic-first triage. 12th candidate in the project failure pattern; FIRST one closed at R1-evidence gate rather than after spec/implementation. Closure report at `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_2_prior_day_close_rejection_fade_closure.md`. Diagnostic output: `nb_lib/probe_results/prior_day_close_rejection_fade_r1_diagnostic.json`. |
