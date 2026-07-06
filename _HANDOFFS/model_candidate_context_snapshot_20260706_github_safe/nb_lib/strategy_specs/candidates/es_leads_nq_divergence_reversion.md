---
name: "ES-Leads-NQ Divergence Reversion"
tagline: "Fade NQ when it overreacts relative to ES."
status: "phase-0-inadmissible-closed"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: pairs and spread trading; common statistical arbitrage framework."

# Market and timing
markets: ["MNQ", "ES/MES"]
session: "RTH"
time_of_day: "09:45-15:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "statistical-arbitrage"
indicators: ["RTHReturn", "BetaAdjustedSpreadZScore", "ThirtyMinuteHighLow"]
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
  - cross-asset
  - data-acquisition-required
---

# ES-Leads-NQ Divergence Reversion

## 1. Thesis

NQ and ES are highly correlated, but NQ can overshoot because of tech
beta and thinner liquidity at the margin. When NQ diverges sharply from
ES intraday without ES confirmation, NQ may snap back toward the
beta-adjusted index spread.

This candidate trades MNQ only, but the signal is cross-index relative
value rather than outright MNQ price action.

## 2. Mechanism (what edge it captures)

- Tracks RTH returns for MNQ and ES or MES.
- Computes a beta-adjusted NQ-minus-ES spread z-score.
- Requires ES to refuse confirmation of NQ's extension.
- Enters after a local 1-minute reversal candle rather than at the
  spread extreme.

## 3. Signal logic (entry conditions)

Track 5-minute returns from RTH open for MNQ and ES/MES. Compute spread
z-score as NQ return minus beta-adjusted ES return. Short MNQ when the
spread z-score is greater than +2 and ES is not making new 30-minute
highs. Long MNQ when the spread z-score is below -2 and ES is not making
new 30-minute lows.

Enter after a 1-minute reversal candle in the reversion direction.

## 4. Exit logic (stops, targets, time-based exits)

Stop if the spread expands to z-score 3. TP when the spread mean-reverts
to z-score 0.5. Time exit after 60 minutes if unresolved. A price-based
catastrophe stop on MNQ may be required for implementation safety.

## 5. Position sizing

Use fixed MNQ dollar risk, likely reduced from single-instrument
strategies because spread divergences can persist. Contract count should
be capped by Apex limits.

## 6. Required indicators / data

MNQ and ES/MES synchronized 1-minute or 5-minute OHLCV data, beta
estimate, RTH return series, and spread z-score. ES/MES data is not
currently in the project store and requires acquisition before testing.

## 7. Differentiation (vs already-tested strategies)

The tested strategies were MNQ-only and derived direction from MNQ's own
morning price behavior. This candidate uses cross-asset confirmation and
mean reversion of a relative spread, so it can reject MNQ-only moves that
do not have broad index confirmation.

## 8. Required research before spec drafting

- **ES data status (updated 2026-05-12):** ES 1-minute data IS
  present in the Databento store at
  `databento/ES/ohlcv-1m/` (596,235 bars,
  2024-07-31 → 2026-04-14). Coverage aligns with MNQ 1-second
  store including the same 9 missing-day gaps. Data layer is
  NOT a blocker. The store contains full-size `ES.c.0`, not
  `MES`; usable as a proxy for spread/divergence purposes.
- **Library blocker:** no `load_es_1m()` helper exists in nb_lib.
  Implementation requires either: (a) author strategy-local
  loader, or (b) wait for a separate iteration to add the
  library helper. Suggest (b) if other ES-using candidates
  emerge.
- **Methodology blocker:** spread z-score and beta estimation
  helpers are not in nb_lib. Could be inlined or promoted to
  library if N≥3 ES-spread candidates accumulate.
- Decide whether beta is fixed, rolling, or precomputed outside the test
  window.
- Define z-score lookback without OOS leakage.
- Decide how spread stops translate into MNQ execution stops.
- Verify that divergences are frequent enough after excluding catalyst
  windows.

## 9. Source / references

Pairs trading and index relative-value frameworks. This is a common
statistical-arbitrage concept; no proprietary source is claimed.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | untested-ideation | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch. |
| 2026-05-12 | untested-ideation | 2026-05-12: data layer unblocked (ES 1m data exists in store); library loader still needed. |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.4 R1-first triage applied (Phase B: first cross-asset class).** Built ES 1-min loader (~10-line `load_es_1m()` helper in diagnostic script; no new nb_lib primitive added per Phase B scope). R1 evidence diagnostic measured MNQ/ES beta=1.0 spread z-score reversion rate over 156 days. **167 z>+2 raw signals (94 blocked by ES confirming) + 178 z<-2 raw signals (125 blocked) → 75 qualifying events** after ES-not-confirming filter + reversal candle + stop band. **30 reverted 1R within 30min (40.0%)**, 34 hit stop first, 11 neither. Direction: 32L / 43S. Median 8.0 min to revert. **R1 verdict: NOT MET** at 40% (well below 60% threshold, below 50% null). **First STRUCTURALLY NOVEL class tested under R1-first triage — also fails.** Cross-asset stat-arb hypothesis on MNQ intraday is empirically refuted: ES-NQ divergence DOES occur (345 raw signals) and the ES-not-confirming filter DOES select for genuine idiosyncratic MNQ moves (56-70% filter rate) — but the surviving signals continue more often than they revert. Three plausible reasons documented in closure: (1) MNQ idiosyncratic moves are momentum-driven not exhaustion-driven; (2) z-score signal lag; (3) beta=1.0 may be wrong. 10-pattern R1 result: 1 MET (ORWS), 9 NOT MET. **Phase C decision point reached** — empirical case for v1.5 calibration / v2.0 rethink is now decisive. Diagnostic: `nb_lib/probe_results/es_leads_nq_divergence_reversion_r1_diagnostic.json`. Phase B closure + decision-point report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_4_phase_b_closure_and_decision_point.md`. |
