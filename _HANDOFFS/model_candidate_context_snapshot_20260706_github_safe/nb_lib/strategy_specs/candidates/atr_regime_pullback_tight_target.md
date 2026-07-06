---
name: "ATR Regime Pullback — Tight Single Target"
tagline: "Same regime-filtered pullback entry as the rejected parent, but a single 1.5xATR target with no partial, no BE arm, no runner — isolates entry edge from trail-management."
status: "tested-rejected"
created: 2026-05-12
updated: 2026-05-12
source: "Fork of atr_regime_pullback_continuation (tested-rejected 2026-05-12). Bracket geometry redesigned from first principles about MNQ intraday continuation magnitude."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-14:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "trend-continuation"
indicators: ["EMA(20)", "EMA(50)", "VWAP", "ATR(20)", "ATRPercentile"]
timeframes_used: ["1-minute", "5-minute", "30-minute"]

# Execution
brackets: "atr-scaled"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: "../canonical/atr_regime_pullback_tight_target.md"
implementation: "../../scripts/atr_regime_pullback_tight_target_canonical_alpha.py"
related_candidates:
  - atr_regime_pullback_continuation.md

# Test status (only populated when status >= tested-*)
test_results:
  in_sample_n: 9
  in_sample_pnl_dollars: -1140.40
  in_sample_pf: 0.45
  in_sample_win_rate: 0.333
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: null

# Tags for organization
tags:
  - rth-only
  - intraday
  - trend-continuation
  - multi-timeframe
  - atr-scaled
  - fixed-risk-dollar
  - single-target
  - no-partial
  - bracket-geometry-fork
---

# ATR Regime Pullback — Tight Single Target

## 0. Provenance and methodology disclosure

This candidate is a deliberate fork of
`atr_regime_pullback_continuation.md` (status `tested-rejected`,
2026-05-12). The parent failed twice on the in-sample bucket: a
single-run test (n=15, $-1,656, PF 0.30) and a 12-start multistart
(0/12 accounts pass, mean $-1,720, stdev $313 — tight clustering
indicating uniform no-edge, not start-date sensitivity).

The decision to fork (vs. close the line and let the parent's
`tested-rejected` status stand) was made deliberately and at
methodology cost:

- **Cost.** This consumes a second in-sample bucket slot on a
  closely related hypothesis. The parent's per-trade failure data
  has already been examined (the exit-reason breakdown is the
  observation that motivated the fork). A pure no-leak fork is
  therefore not achievable — the operator has already seen *that*
  the original bracket geometry didn't work, even if not exactly
  *how* to fix it.
- **Mitigation.** The new bracket geometry (Section 4) is
  designed from **first-principles claims about MNQ intraday
  continuation magnitude** that are independent of the parent's
  observed exit-reason percentages. The choice should be defensible
  even if the parent had failed in a different distribution. The
  rationale is documented in Section 4 before any reference to
  the parent's per-trade data.
- **Bucket accounting.** If this candidate is taken through
  spec-drafting and in-sample testing, it should be counted as
  the second of two in-sample uses on the
  `atr_regime_pullback_*` family. A third attempt within this
  family would constitute methodology overrun and should be
  refused without explicit operator override.

## 1. Thesis

Same regime-filtered pullback continuation as the parent, with one
hypothesis change: **the parent's exit geometry, not its entry
mechanism, is what failed.** If the entry mechanism (multi-timeframe
trend alignment + ATR-regime gate + pullback-and-reversal on
5-min/1-min) has any edge, a single tight target with no partials
should reveal it. If the entry has no edge, a tight single target
will not save it — and the family is closed.

The candidate is therefore a **clean entry-edge test**: by
removing partials, break-even arming, and the 2.5xATR runner, the
exit logic becomes a single decision and the result attributable
to the entry mechanism alone.

## 2. Mechanism (what edge it captures)

- **Mechanism 1 (carried from parent).** Multi-timeframe trend
  alignment (30-min trend + 5-min pullback + 1-min reversal) is
  a stronger filter than single-timeframe pullback signals such
  as PRJ_3. Falsifiable.
- **Mechanism 2 (carried from parent).** ATR-percentile-band
  gating restricts trades to volatility regimes where directional
  structure tends to hold; extreme-vol and dead-vol days are
  excluded. Falsifiable.
- **Mechanism 3 (NEW).** Intraday MNQ trend-continuation
  expectancy is concentrated in the **first 1-2 ATR** of favorable
  excursion; beyond that, marginal excursion is dominated by
  mean-reversion noise. A 1.5xATR single target captures the bulk
  of the expectancy without exposing the position to runner-
  retracement risk. Falsifiable: if the strategy still loses at
  this geometry, the entry mechanism, not the target geometry,
  is the limiting factor.

## 3. Signal logic (entry conditions)

**Unchanged from parent.** Re-stated here for completeness:

For longs:

- 30-minute trend qualification: close above EMA(50) on 30-min,
  agreement with VWAP direction.
- 5-minute pullback: price retraces to dynamic reference (EMA20
  or VWAP — operator pre-commit which one in spec drafting).
- 1-minute reversal: reversal candle in direction of 30-min
  trend (operator pre-commit candle definition mechanically
  to avoid lookahead).
- ATR regime gate: 5-min ATR(20) within pre-committed percentile
  band (above median, below pre-committed extreme percentile).
- Session window: 09:45-14:30 ET.

Shorts are symmetric.

**Same entry, same filters, same regime gate.** Only the exit
logic changes from the parent.

## 4. Exit logic (stops, targets, time-based exits)

**This is the only change vs. parent.** All four values below
are pre-committed before any reference to parent's per-trade
data:

- **Stop: 1.0 x ATR(20)** beyond pullback low (long) / high
  (short). Slightly tighter than parent's 1.25x.
- **Target: 1.5 x ATR(20).** Single fixed target. Reflects the
  Mechanism-3 claim that intraday MNQ continuation expectancy is
  in the first 1-2 ATR.
- **No TP1, no BE arm, no runner, no partial close.**
- **EOD flat at 14:30 ET** (one minute before session window
  close, same convention as parent).

R:R is 1.5:1. Breakeven win rate ~40%.

**Rationale (pre-committed; written before re-examining parent's
exit-reason breakdown):**

1. The parent's 2.5xATR TP2 is far enough from entry that MNQ
   intraday continuation rarely reaches it without significant
   retracement first. Mid-trade retracement either trips the BE
   stop (a partial-win turned scratch) or the original stop
   (a full loss when BE not yet armed). This is a structural
   issue with the geometry, not a tunable parameter.
2. Partial-fill mechanics (TP1 + runner + BE arm) introduce three
   independent decisions per trade: where TP1 fills, when BE
   arms, and whether the runner ever clears 2.5xATR. Each of
   these is a source of expectancy leakage. Collapsing to one
   decision removes three failure modes at once.
3. Short-horizon trend literature (Carver, Clenow's short-term
   systems, public futures-systems writeups) consistently finds
   intraday trend expectancy is captured within the first 1-2
   ATR of favorable excursion. 1.5xATR sits at the upper end of
   that range, providing reasonable R while remaining inside the
   high-expectancy zone.
4. The asymmetric R:R (1.5:1) is preferred over symmetric
   (1.0:1) because trend-continuation entries that survive the
   regime gate should produce a positive directional excursion
   on average; allocating more upside than downside captures
   that asymmetry. R:R further out (2.0:1+) re-introduces the
   parent's "rarely reached" problem.

**Not chosen and why:**

- Time-stop-based (no fixed TP, exit at fixed-time): valid
  alternative; deferred because it adds a hyperparameter
  (the time window) that would need its own pre-commit. If this
  candidate fails, time-stop is the next-logical successor and
  is worth its own candidate file.
- Symmetric tight bracket (1.0xATR stop / 1.0xATR target): too
  vulnerable to commission + slippage drag at MNQ tick size on
  fixed-risk sizing.
- Wider stop (1.5xATR) + same target: reduces R:R below 1:1 and
  increases per-trade dollar loss on stops, accelerating
  Apex-floor pressure.

## 5. Position sizing

**Unchanged from parent.** Fixed dollar risk per trade: risk
dollars divided by stop dollars, capped by the Apex contract
limit. The tier classifier and vol multiplier from the parent's
FINAL spec carry over.

Note: the tighter 1.0xATR stop (vs. parent's 1.25x) means smaller
stop dollars, so fixed-risk sizing will produce a slightly
larger contract count for the same risk dollar — within Apex cap.
The dollar-risk per trade is conserved by design.

## 6. Required indicators / data

**Unchanged from parent.** MNQ 1-minute, 5-minute, and 30-minute
bars; EMA20, EMA50, VWAP, ATR(20), and ATR percentile or median
history. All available in nb_lib indicators.

## 7. Differentiation (vs already-tested strategies)

- **vs. parent (`atr_regime_pullback_continuation`,
  tested-rejected):** identical entry + sizing; exit geometry
  collapsed from 4-decision (TP1, BE arm, TP2, stop) to
  2-decision (target, stop). Single-target, no-partial, no-BE,
  no-runner.
- **vs. PRJ_3 Canonical Alpha (tested-rejected):** same
  multi-timeframe alignment and ATR regime gate as parent, both
  of which PRJ_3 lacks. Now also strips PRJ_3's partial-TP
  structure entirely.
- **vs. noise_brk Canonical Alpha (deployed):** different
  signal mechanism (multi-timeframe pullback vs. 9:36 noise-band
  breakout); different time window (09:45-14:30 vs. 9:36 only).
- **vs. ema_trend Canonical Alpha (tested-rejected):** different
  entry timing (pullback-and-reversal vs. EMA-slope trigger);
  multi-timeframe vs. single-timeframe.

The structural novelty of this candidate over the parent is
specifically the **single-decision exit**. That is the
hypothesis being tested.

## 8. Required research before spec drafting

- **Pre-commit reversal-candle definition mechanically.** Same
  open question as parent. Required to avoid lookahead. Candidate
  for FINAL spec: "1-minute close beyond prior 1-minute close
  in trend direction, with bar range >= X% of 5-min ATR."
- **Pre-commit ATR percentile band bounds.** Carry over from
  parent's FINAL spec (do not retune).
- **Pre-commit EMA20 vs. VWAP pullback priority.** Carry over
  from parent's FINAL spec (do not retune).
- **Pre-commit tier classifier + vol multiplier tables.** Carry
  over from parent's FINAL spec (do not retune).
- **Verify trade count.** Parent generated n=15 in-sample over
  the same window. With identical entry, this candidate should
  generate the same set of trade timestamps; the exit logic
  change alters per-trade P&L but not signal count. If the
  signal count diverges, that indicates a regression in the
  entry pipeline and must be debugged before testing.
- **Confirm with operator that this candidate is the second and
  final in-sample slot for the `atr_regime_pullback_*` family.**
  Document that a third fork would not be permitted without
  explicit override.

## 9. Source / references

- Parent: `atr_regime_pullback_continuation.md` (this
  directory).
- Multistart report:
  `../../../nb_lib_atr_regime_multistart_report.md` (Section E
  for exit-reason breakdown; Section I for forward path).
- In-sample rerun report:
  `../../../nb_lib_atr_regime_insample_rerun_report.md`.
- Carver, Robert: *Leveraged Trading* — short-horizon trend
  expectancy decay.
- Clenow, Andreas: *Stocks on the Move* — momentum capture
  windows.
- nb_lib repertoire reference: `_METHODOLOGY_repertoire.md`.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | Forked from `atr_regime_pullback_continuation` (tested-rejected). Bracket geometry collapsed to single 1.5xATR target with 1.0xATR stop; no TP1, no BE arm, no runner. Pre-committed before re-examining parent's per-trade exit-reason data. Treats this candidate as the second of two in-sample slots permitted for the `atr_regime_pullback_*` family. |
| 2026-05-12 | `untested-triage-passed` | Triage-pass: candidate is structurally distinct from parent in the precise dimension being tested (single-decision exit). Open research questions in Section 8 are answerable by inheriting parent's locked parameters. No retuning of regime gate, ATR percentile bounds, tier classifier, or vol multiplier — only bracket geometry changes. Bucket accounting (Section 0) reaffirmed: this is the SECOND and FINAL in-sample slot for the `atr_regime_pullback_*` family. |
| 2026-05-12 | `spec-drafted` | FINAL canonical spec drafted at `../canonical/atr_regime_pullback_tight_target.md` (16 sections, 0-16). Inherits parent canonical Sections 2-9 (entry pipeline) and 11 (compliance) verbatim. Diverges only in Sections 9.7 (stop distance constant), 10 (single-target brackets), and 12.5 (bracket-order assertion). Pre-committed pass criteria locked in Section 16: PF >= 1.5, total P&L > $0, n >= 10, account state != FAILED. |
| 2026-05-12 | `implementation-in-progress` | Strategy script implemented at `../../scripts/atr_regime_pullback_tight_target_canonical_alpha.py` as a fork importing parent's helpers verbatim. Override surface: bracket constants, `build_brackets()`, `trade_one_session()` (single-target lifecycle call, no partials), and `main()`. Dry-run passes. |
| 2026-05-12 | `tested-rejected` | In-sample run COMPLETED. **All 4 pre-committed pass criteria FAILED**: account FAILED via compliance_drawdown breach on 2024-10-17 (trade 9 of 9), total P&L $-1,140.40, PF 0.45, n=9 (< 10 threshold). Win rate 33.3%. Geometry hypothesis PARTIALLY VINDICATED: target-reach rate jumped to 22.2% (2 tp1 hits / 9 trades) from parent's 4.1% TP2 rate — single-target geometry does what it was designed to do. But this did NOT rescue the entry edge. Full_stop rate climbed to 55.6% (vs parent's 37.6%) because tighter 1.0x stop fires more often and no TP1 partial cushion remains. Account failed FASTER (9 trades vs parent's 15) because larger contract counts under tighter stop accelerated drawdown. Conclusion: **entry mechanism, not bracket geometry, was the binding constraint**. The `atr_regime_pullback_*` family is CLOSED. Bucket accounting: this consumed the 2nd and FINAL in-sample slot. See `nb_lib_atr_regime_tight_target_results_report.md`. |
