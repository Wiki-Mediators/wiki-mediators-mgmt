---
name: "First Loss Reversal Day"
tagline: "Trade reversal after early directional failure and volatility exhaustion."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: opening-drive failure concepts from discretionary futures trading."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-14:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "intraday-reversal"
indicators: ["VWAP", "RTHOpen", "ATR(20) on 5-minute bars", "MorningRange"]
timeframes_used: ["1-minute", "5-minute"]

# Execution
brackets: "volatility-adaptive"
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
  - opening-failure
  - fixed-risk-dollar
---

# First Loss Reversal Day

## 1. Thesis

Some days punish early trend traders. If the first directional push
fails and volatility contracts afterward, the market may rotate back
through the open or VWAP as early positions unwind.

This candidate is explicitly anti-breakout. It waits for an early
impulse to fail before entering in the opposite direction.

## 2. Mechanism (what edge it captures)

- Identifies the first meaningful opening impulse.
- Requires the impulse to retrace through RTH open or VWAP.
- Waits for reversal confirmation after early directional failure.
- Avoids days where the early range is already too large.

## 3. Signal logic (entry conditions)

From 9:30 to 10:15 ET, identify the first impulse direction as a move
greater than 0.5 x ATR(20) on 5-minute bars. Require that impulse to
fully retrace back through RTH open or VWAP by 11:00 ET.

Enter opposite the original impulse on a 5-minute close through VWAP.
Skip if the session range is already greater than 1.5 x daily ATR.

## 4. Exit logic (stops, targets, time-based exits)

Stop beyond the failed impulse extreme. TP1 is the opposite side of the
morning range midpoint. TP2 is the opposite morning range boundary. Time
exit by 14:00 ET.

## 5. Position sizing

Use fixed dollar risk based on the failed impulse extreme stop distance,
capped by Apex contract limits.

## 6. Required indicators / data

MNQ 1-minute and 5-minute bars, VWAP, RTH open, morning range, and
ATR(20). All required market data appears available in the current MNQ
store.

## 7. Differentiation (vs already-tested strategies)

The rejected strategies generally followed early direction or pullback
continuation. This candidate waits for that early direction to fail,
then trades the reversal back through the session anchor with
volatility-adaptive stops.

## 8. Required research before spec drafting

- Define "first impulse" when both directions move more than the
  threshold.
- Define volatility exhaustion or decide to omit it from v1.
- Verify no lookahead in identifying the impulse and retrace.
- Check whether reversal entries are frequent enough after range and
  catalyst filters.

## 9. Source / references

Opening-drive failure concepts from discretionary futures trading.
Widely known idea; any edge likely depends on strict mechanical
definition and filtering.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | untested-ideation | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch. |
| 2026-05-25 | `phase-0-inadmissible-closed` | **R1-first triage applied (new methodology pattern post-PDCRF closure).** R1 evidence diagnostic measured failed-impulse-reversal rate over 107 in-sample days (2024-08-01 to 2025-01-31). **82 first-impulse events detected; 51 qualifying after retrace + stop-band filter; 23 reverted 1R within 30 min (45.1%)**, 12 hit stop first (23.5%), 16 neither in window (31.4% — high, indicating slow-resolution mechanism). Short reversion 40.0% (6/15); long 47.2% (17/36). Median minutes to revert: 10.0. **R1 verdict: NOT MET** (45.1% < 60% threshold). Below 50% null but above PDCRF's 38.9%. Caveat documented: 30-min lookahead may undercount this candidate's slow-resolution mechanism (TP1 at morning-range-midpoint, time exit at 14:00 ET); extending lookahead post-hoc would be discipline-failure. **Candidate CLOSED at Phase 0 R1 gate** — no R4 probe, no FINAL spec, no implementation. **R1-first triage validated** across two consecutive closures (PDCRF + FLRD); saving ~6-10 hours of downstream pipeline per candidate. 13-pattern update; second candidate closed at cheapest gate. Diagnostic: `nb_lib/probe_results/first_loss_reversal_day_r1_diagnostic.json`. Report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_2_first_loss_reversal_day_closure.md`. |
