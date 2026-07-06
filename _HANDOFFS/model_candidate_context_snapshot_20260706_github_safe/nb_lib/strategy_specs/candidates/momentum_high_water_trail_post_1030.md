---
name: "Momentum High-Water Trail Past 10:30"
tagline: "Ride morning momentum past the typical 10:30 ET exhaustion by trailing from the high-water mark."
status: "untested-ideation"
created: 2026-05-14
updated: 2026-05-14
source: "Operator direction 2026-05-14; trader-art observation about 10:30 ET morning-momentum exhaustion pattern. Filename chosen to make the post-10:30 high-water trail mechanic explicit."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:35-15:58 ET; entry before 10:20, high-water transition at 10:30"
hold_duration: "intraday"

# Signal characteristics
signal_type: "trend-continuation"
indicators: ["OpeningRange(5m)", "VWAP", "ATR(20) on 5-minute bars", "VolumeRatio(1m/20m)", "5m swing detector"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "high-water-trailing"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: null
implementation: null
related_candidates:
  - "atr_percentile_trend_day_hold.md"
  - "mnq_news_like_impulse_pullback.md"

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
  - trend-continuation
  - high-water-trail
  - morning
  - fixed-risk-dollar
---

# Momentum High-Water Trail Past 10:30

## 1. Thesis

This candidate tests a trader-art observation about the morning session:
many RTH momentum moves exhaust around 10:30 ET as the opening auction,
early institutional execution, and first-hour discretionary flow begin
to fade. A simple time exit at 10:30 protects against that common fade,
but it also throws away the minority of momentum days that continue
cleanly through late morning and into the afternoon.

The locked thesis is: **if morning momentum has built enough favorable
high-water mark by 10:30, do not exit just because the clock says
10:30. Instead, convert the trade from ordinary momentum management to
a high-water-anchored trail.** For longs, the high-water mark is the
best price reached between entry and 10:30. For shorts, it is the lowest
favorable price reached by 10:30. The post-10:30 stop/trail is anchored
to that favorable excursion so the trade can continue with substantially
reduced give-back risk.

The counter-hypothesis is serious: most morning moves really do fade
around 10:30, and a trailing mechanism may simply turn a clean time exit
into a delayed stop-out. The strategy assumes enough continuation cases
exist to justify keeping the runner alive after the fade window. That
assumption is unproven and must be tested later; this wiki entry only
records the candidate.

## 2. Mechanism (what edge it captures)

- **Opening-flow momentum.** The first 30-60 minutes can contain real
  directional pressure from overnight inventory resolution, cash-session
  order flow, and macro/news digestion.
- **10:30 as exhaustion risk.** Around 10:30 ET, opening participation
  often thins and early momentum can mean-revert. The strategy treats
  10:30 as a risk-transition point, not an automatic exit.
- **High-water mark as proof of survival.** A trade that has built
  meaningful favorable excursion by 10:30 has already proven more than a
  marginal open-drive pop. The trail uses that favorable path as the
  risk anchor.
- **Hard exit replaced by controlled optionality.** Time-exiting at
  10:30 captures no continuation tail. High-water trailing keeps the
  tail open while forcing the trade to defend its morning gains.
- **Continuation-class skepticism preserved.** Six prior continuation
  candidates failed. This candidate is not "another momentum entry"; its
  specific hypothesis is that the 10:30 transition rule changes the
  distribution of winners by preserving continuation tails while cutting
  morning-fade failures.

## 3. Signal logic (entry conditions)

The entry should stay lean. A future Phase 0/1 may revise or reject the
specific predicates, but the candidate's starting design is:

- **Entry window:** 09:35:00-10:20:00 ET. No new entries after 10:20
  because the trade needs enough time to build high-water progress before
  the 10:30 transition.
- **Opening range reference:** define the 09:30-09:35 high/low using
  completed 1-minute bars.
- **Long momentum predicate:** price closes above the 09:30-09:35 high,
  closes above session VWAP, and the breakout 1-minute bar has volume at
  least 1.5x the trailing 20 completed 1-minute bars.
- **Short momentum predicate:** symmetric close below the 09:30-09:35
  low, below session VWAP, with the same volume condition.
- **Volatility sanity guard:** ATR(20) on completed 5-minute bars must
  be positive and within a pre-committed valid range. This is a data
  sanity guard, not a regime optimizer.
- **Direction handling:** two-sided by default. Long and short morning
  momentum are both allowed unless a later Phase 0 admissibility check
  rejects symmetry.
- **Lookahead rule:** every predicate uses completed bars only. A
  1-minute close at 09:42 becomes knowable at 09:43:00; entry fills on
  the first eligible 1-second bar strictly after the signal timestamp.

The predicate count is intentionally modest: opening-range break, VWAP
side, volume participation, and ATR sanity. This is more selective than
round-number's overly broad rejection predicate but avoids the
multi-layer regime stack that made chop-fade sparse.

## 4. Exit logic (the core differentiator)

### Pre-10:30 Management

- **Initial stop:** opposite side of the 09:30-09:35 opening range, or
  1.25 x ATR(20) on 5-minute bars from entry, whichever is closer after
  pre-commitment in a future spec.
- **TP1:** optional. Candidate default is one partial at +1.0R, closing
  50% of contracts, to reduce exposure before the 10:30 transition.
- **TP2:** no fixed TP2 before 10:30. The post-10:30 high-water trail is
  the runner mechanism.
- **BE arm:** if used, it should not arm before +1.0R or before TP1.
  This explicitly addresses the round-number failure mode: an early BE
  stop can make later structural trailing proposals look like widening
  and become inert. The future spec may also choose no BE arm before
  10:30, relying instead on the high-water transition.

### At-10:30 Transition

Transition timestamp: **10:30:00 ET**, evaluated after the completed
1-minute bar ending at 10:30 is available.

For a long:

```text
high_water = max(highs from entry_ts through 10:30 completed bar)
transition_anchor = high_water
```

For a short:

```text
low_water = min(lows from entry_ts through 10:30 completed bar)
transition_anchor = low_water
```

Implementation note: a protective stop cannot always be placed literally
at the high-water price for a long, because current price may already be
below that level at 10:30. Therefore the thesis is operationalized as a
**high-water-anchored protective trail**:

- Long proposed stop: `high_water - trail_offset`.
- Short proposed stop: `low_water + trail_offset`.
- If current price has already crossed the proposed protective stop at
  10:30, exit immediately on the next eligible 1-second bar.
- If high-water is not meaningfully favorable versus entry, exit at
  10:30 rather than pretending the trade earned a runner.

Candidate default for "meaningfully favorable": at least +0.75R by
10:30. This is an informed prior for future Phase 0 review, not a tested
parameter.

### Post-10:30 Trail Mechanic

The candidate default is an ATR high-water trail:

```text
trail_offset = max(0.75 x ATR(20) on completed 5-minute bars, 6 points)
long_stop = max(previous_stop, running_high_water - trail_offset)
short_stop = min(previous_stop, running_low_water + trail_offset)
```

Update cadence:

- Evaluate once per completed 1-minute bar after 10:30.
- Stop only tightens, never widens.
- Running high-water/low-water updates only on new favorable extremes.

Alternative future spec choice: use the v2.4 5-minute swing detector
instead of ATR offset, but that must explicitly avoid the BE conflict
seen in round-number rejection.

### Time Exit

- Mandatory Apex EOD flat at 15:58:30 ET.
- Optional earlier time exit after 14:30 if the post-10:30 trail has not
  advanced for a defined period. This remains a research question.

## 5. Position sizing

Use fixed-risk-dollar sizing:

```text
risk_dollars = 300
point_value = 2 dollars per MNQ point per contract
stop_pts = abs(entry_price - initial_stop)
contracts = floor(risk_dollars / (stop_pts * point_value))
contracts = clamp(contracts, 1, 15)
```

Skip conditions for future spec drafting:

- Stop distance below 5 points: too tight for BAND_B friction and MNQ
  opening noise.
- Stop distance above 35 points: too wide for Apex 50K survival under a
  $300 risk budget.
- Less than 1 contract after sizing.
- Current compliance state not active.

The $300 risk figure is an informed prior. It is chosen because a $2K
trailing floor cannot tolerate repeated $600-$900 losses from fixed
15-contract morning systems. Seven full $300 losses can still breach
the floor, so Phase 0 must address cluster-loss risk before this
candidate can become admissible.

## 6. Required indicators / data

- MNQ 1-second OHLCV from the Databento store.
- 1-minute bars derived from 1-second data for opening-range,
  breakout, volume ratio, and high-water tracking.
- 5-minute ATR(20), Wilder smoothing, for stop/trail offsets and sanity
  checks.
- Session VWAP, RTH-anchored.
- Optional: v2.4 5-minute swing detector if a future spec chooses a
  swing-based post-10:30 trail instead of ATR high-water trail.
- TradingCalendar for RTH windows, half-days, and EOD flat.

No external news feed, order flow, ES data, or options data is required.

## 7. Differentiation (vs already-tested strategies)

This candidate is still a continuation strategy. That is a major concern
because six continuation-class candidates have already failed. It must
not be promoted just because it sounds different.

Specific differences:

- **Variant 1 / noise_brk:** those entered a 9:36 noise-band breakout
  and used fixed brackets. This candidate enters only if opening-range
  momentum also agrees with VWAP and volume participation, then changes
  management at 10:30 instead of treating the whole day with static
  brackets.
- **PRJ_3:** PRJ_3 used fractal-pullback continuation and failed after
  lookahead removal. This candidate does not use fractal proximity or
  pullback confirmation; it tests whether early momentum that survives
  to 10:30 should be trailed rather than time-exited.
- **ema_trend:** ema_trend waited until 11:10 for EMA trend state and
  had no 10:30 transition. This candidate is explicitly about the
  pre-10:30/post-10:30 boundary.
- **atr_regime parent / tight-target fork:** those tested ATR-regime
  pullback entries and bracket geometry. This candidate tests a
  time-of-day management transition, not another ATR-regime entry
  classifier.
- **round_number_rejection_microfade:** round-number's adaptive
  management was design-dead because BE armed before structure trail
  could tighten. This candidate names that failure mode and treats BE
  timing as a design constraint.

The honest argument for this candidate is narrow: fixed-bracket
continuation may have failed partly because it did not distinguish
ordinary morning momentum from momentum that built enough favorable
excursion by the 10:30 exhaustion window. If that distinction is false,
this candidate should be rejected quickly.

## 8. Required research before spec drafting

Before Phase 0 admissibility or any spec drafting, answer:

- **10:30 behavior diagnostic:** characterize unconditional MNQ price
  behavior around 10:30 after morning momentum. No P&L; just measure
  continuation vs fade after pre-10:30 high-water progress.
- **Apex survival thesis:** estimate typical initial stop distances,
  $300 risk effect, and cluster-loss exposure. Explain why this does not
  repeat the 5-11 loss sequences that killed prior candidates.
- **Signal-frequency expectation:** define expected in-sample signal
  count range with rationale. Too sparse would look like chop-fade; too
  broad would look like round-number Phase 1.
- **Direction symmetry:** defend two-sided operation. If long and short
  10:30 behavior differ structurally, Phase 0 must say how asymmetry is
  handled.
- **Management lifecycle compatibility:** prove the 10:30 transition
  occurs while trades are still open often enough to matter, and that
  BE/TP1 choices do not preclude the high-water trail.
- **Trail choice:** decide whether post-10:30 trail is ATR high-water,
  swing-based, fixed-distance, or a hybrid. Only one should be
  pre-committed.
- **Half-day handling:** decide whether the strategy skips half-days,
  because 10:30 exists but the afternoon tail is shortened.

## 9. Source / references

- Operator direction, 2026-05-14: trader-art observation that 10:30 ET
  often marks morning-momentum exhaustion, but high-water progress by
  that time may identify moves worth trailing rather than exiting.
- Internal methodology references:
  `nb_lib_forward_iteration_plan_post_8fleet.md` and the 8-fleet matrix
  therein.
- General market-structure context: intraday volume and volatility
  commonly follow a U-shaped pattern, with heavy open/close activity and
  thinner midday participation. No peer-reviewed citation is claimed in
  this entry; this candidate records trader-art folklore for later
  empirical testing.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-14 | `phase-0-inadmissible` | Phase 0 admissibility check completed. Verdict: INADMISSIBLE because Apex survival thesis and signal-frequency tolerance are not met; edge thesis, management lifecycle, and direction handling are partially met. Candidate remains `untested-ideation`; no Phase 1 preflight. See `C:/VMShare/NT8lab/nb_lib_phase0_momentum_high_water_trail_post_1030.md`. |
| 2026-05-14 | `untested-ideation` | Wiki entry authored from operator direction. 10:30 high-water trail mechanic recorded as a continuation-class candidate addressing prior morning-momentum failure modes. Awaiting Phase 0 admissibility check before any test commitment. |
| 2026-05-14 | `phase-0-bypass` | **Operator authorized Phase 0 bypass for informational multistart testing.** FINAL spec drafted at `../canonical/momentum_high_water_trail_post_1030_spec_FINAL.md` with explicit bypass framing (Sections 7.5 / 13.2 / 15). All wiki Section 8 deferred items resolved at the spec level. R2 gap addressed via daily loss limit (2 losses/day); R4 gap addressed via mechanism-derived signal-count expectation (60-180 trades across 12 monthly starts). Strategy does NOT graduate from this iteration regardless of multistart outcome. OOS slot remains sealed for this candidate. Wiki body content unchanged per bypass contract. |
| 2026-05-14 | `tested-informational-rejected` | **Multistart informational test executed and closed.** 12-start (Aug 2024 - Jul 2025) × 42-trading-day windows. Results: 14 trades total (spec expected 60-180), 0/12 starts profitable, PF=0.00, total P&L -$3,412.00. Core-mechanism dead: only 1 trade reached 10:30 still open and force-exited (`mhw_no_high_water_at_10_30`); zero post-10:30 trail tightenings. Phase 0 R4 (signal frequency) confirmed; R2 (cluster losses) untestable at this trade volume. Candidate **closed** as `tested-informational-rejected`. No wiki revision, no Phase 0 re-run, no Phase 1 preflight. Report at `C:/VMShare/NT8lab/nb_lib_mhw_multistart_informational_report.md`. OOS slot remains sealed. 9-fleet failure pattern. |
