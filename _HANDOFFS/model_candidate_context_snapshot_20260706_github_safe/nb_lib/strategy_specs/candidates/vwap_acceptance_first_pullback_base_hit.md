---
name: "VWAP Acceptance First-Pullback Base Hit"
tagline: "Trade the first accepted VWAP pullback after a morning drive, targeting a return to the impulse extreme."
status: "phase-0-inadmissible-closed"
created: 2026-05-25
updated: 2026-05-25
source: "Codex-invented candidate 2026-05-25. Designed after ORWS v2 timing failure, tight-opening base-hit negative result, and repeated MNQ fade failures. Core idea: stop fading strong accepted flow; test first pullback continuation after VWAP acceptance."

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-12:00 ET"
hold_duration: "intraday"

signal_type: "vwap-acceptance-continuation"
indicators: ["RTH VWAP", "ATR(14) 1-min", "EMA(8) 1-min", "opening drive high/low", "volume MA(20)"]
timeframes_used: ["1-second source", "1-minute derived"]

brackets: "structure anchored base-hit"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
  - "vwap_stretch_snapback"
  - "opening_range_width_switch_v2_base_hit"
  - "tight_opening_window_breakout_long"
  - "mnq_news_like_impulse_pullback"

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

admissibility:
  r1_edge_thesis:
    r1_diagnostic_convention_version: "v1.1"
    r1_diagnostic_script: "nb_lib/scripts/diagnostic_vafp_vwap_pullback_continuation_r1.py"
    r1_diagnostic_output: "nb_lib/probe_results/vwap_acceptance_first_pullback_base_hit_r1_diagnostic.json"
    r1_diagnostic_window: ["2024-08-01", "2025-01-31"]
    r1_lookahead_minutes: 60
    r1_mechanism_class: "moderate"
    r1_n_qualifying_events: 49
    r1_low_confidence: false
    r1_compound_filter_over_restrictive: false
    r1_reversion_rate: 0.5306122448979592
    r1_neither_rate: 0.0
    r1_verdict: "NOT MET"
  r2_apex_survival:
    risk_dollars_per_trade: 250
    expected_stop_distance_pts_range: [6, 28]
    expected_loss_dollars_per_trade: 250
    worst_plausible_cluster_n: 5
    worst_plausible_cluster_dollars: 1250
    cluster_vs_floor_ratio: 0.625
    favorable_first_week_independent: false
    r2_variance_probe_version: null
    r2_variance_probe_script: null
    r2_variance_probe_output: null
    r2_variance_pf_simulated: null
    r2_variance_win_rate: null
    r2_variance_max_consecutive_losses: null
    r2_variance_max_running_drawdown_dollars: null
    r2_variance_trailing_dd_breach: null
    r2_variance_verdict: null
  r4_signal_frequency:
    probe_convention_version: "v1.2"
    probe_script: null
    probe_output: null
    probe_window_start: null
    probe_window_end: null
    probe_n_signals_observed: null
    probe_signals_passing_fill_guards: null
    probe_attrition_rate: null
    probe_p95_drift_pts: null
    probe_low_confidence_attrition: null
    probe_n_long: null
    probe_n_short: null
    probe_distinct_days_with_signal: null
    expected_signals_per_60_trading_days: null
    sparsity_class: null
    sparsity_class_rationale: null

tags:
  - rth-only
  - intraday
  - vwap-based
  - trend-continuation
  - pullback
  - base-hit
  - objective-level
  - ohclv-testable
  - two-sided
---

# VWAP Acceptance First-Pullback Base Hit

## 0. Admissibility Summary

- **R1 (edge thesis)**: NOT MET. R1 v1.1 diagnostic over 2024-08-01 to 2025-01-31 found 49 qualifying first VWAP-pullback events; only 26 reached the drive-extreme/1R-capped target before stop, a 53.1% target-first rate. This is below the 60% floor, with sufficient sample and no over-restrictive compound-filter flag.
- **R2 (Apex survival)**: Initial thesis uses $250 risk per trade, expected stops in the 6-28 point range, and one trade per direction per day. A five-loss cluster is $1,250, 62.5% of the Apex 50K EOD $2K floor. This is safer than the $300 risk used by several recent candidates but still large enough to avoid micro-sizing noise.
- **R3 (management lifecycle)**: No adaptive specialists in v1. Exit should be simple: fixed base-hit target at the impulse extreme or 1R, whichever is nearer, with a hard time exit.
- **R4 (signal frequency)**: Not run. The candidate closed at R1, so R4 is intentionally skipped.
- **R5 (direction handling)**: Two-sided by design. Longs require above-VWAP acceptance and a VWAP hold; shorts require below-VWAP acceptance and a VWAP rejection. Any direction restriction would need a separate regime-router argument, not post-hoc filtering.

### Methodology Pipeline Order

This candidate is closed at R1. It should not proceed to R4 or FINAL spec without a new thesis.

R1 result:

- Diagnostic: `nb_lib/scripts/diagnostic_vafp_vwap_pullback_continuation_r1.py`
- Output: `nb_lib/probe_results/vwap_acceptance_first_pullback_base_hit_r1_diagnostic.json`
- Window: 2024-08-01 to 2025-01-31
- Lookahead: 60 minutes (moderate-resolution v1.1 default)
- Events: 49
- Target-first: 26/49 = 53.1%
- Verdict: NOT MET

## 1. Thesis

The project has repeatedly found that fading obvious strength on MNQ is dangerous: round-number fades, wide-state reversals, liquidity-sweep fades, and several opening-range response branches all lost money or produced severe Apex path risk. This candidate reverses that posture. It does not ask "has price gone too far?" It asks "has price accepted one side of VWAP, pulled back, and held?"

VWAP is an institutional intraday reference. When the morning drive pushes away from VWAP and price remains accepted on one side, a first pullback into the VWAP/EMA area can function as a participation reset: early longs or shorts take profit, late chasers get tested, and continuation traders get a defined-risk entry. The base-hit target is deliberately modest: return to the opening-drive extreme, not a large trend-day runner.

Counter-hypothesis: VWAP pullbacks are often where the opening move dies. A VWAP touch after a drive may be the start of balance rotation, not a continuation reset. The R1 diagnostic must answer this before any implementation time is spent.

## 2. Mechanism

- **Accepted flow**: VWAP separates accepted intraday value from rejected excursions. Sustained closes above VWAP suggest buyers are willing to transact above the session mean; sustained closes below VWAP suggest sellers have control.
- **First pullback reset**: The first pullback after a drive is cleaner than later pullbacks because fewer prior failed attempts have polluted the level.
- **Defined structural risk**: The pullback low/high gives a natural stop; the drive extreme gives an objective base-hit target.
- **Base-hit design**: The strategy intentionally avoids a large runner. Recent work showed that "be right a little" sometimes deserves testing, but only where the mechanism supports it. Here the target is the already-proven impulse extreme, not an arbitrary 2R target.
- **Anti-fade posture**: It is explicitly the opposite of the failed "strong move must reverse" family. It trades continuation only after a pullback confirms acceptance.

## 3. Signal Logic

Use 1-minute bars derived from MNQ 1-second OHLCV. All decisions use completed 1-minute bars. For left-labeled bars, a bar timestamped `10:14:00` is not available until `10:15:00`; any stop-entry fill must occur no earlier than `10:15:01`.

### Common Definitions

- RTH VWAP starts at 09:30 ET.
- Opening-drive window: 09:30-10:00 ET.
- Scan window: 09:45-12:00 ET.
- `EMA8` is computed on 1-minute closes.
- `ATR14` is computed on 1-minute OHLC.
- Volume context uses `SMA(volume, 20).shift(1)`.

### Long Setup

Pre-committed predicates:

- Opening-drive high is set by the highest high from 09:30-10:00 ET.
- By 10:00 ET, price has at least two completed 1-minute closes above RTH VWAP.
- The drive distance from VWAP to opening-drive high is at least `0.75 * ATR14`.
- First qualifying pullback after 09:45:
  - Bar low touches or comes within `0.20 * ATR14` of VWAP.
  - Bar closes above VWAP.
  - Bar closes above or back through EMA8, or the following completed bar closes above the pullback bar high.
  - Pullback low remains above VWAP by no more than one tick of violation tolerance; deeper completed close below VWAP invalidates long setup for the day.
- Entry: buy stop at pullback-confirmation bar high + 1 tick.
- Stop: pullback low - 1 tick.
- Target: opening-drive high, capped at 1R if the drive high is farther than 1R.

### Short Setup

Symmetric predicates:

- Opening-drive low is set by the lowest low from 09:30-10:00 ET.
- By 10:00 ET, price has at least two completed 1-minute closes below RTH VWAP.
- The drive distance from VWAP to opening-drive low is at least `0.75 * ATR14`.
- First qualifying pullback after 09:45:
  - Bar high touches or comes within `0.20 * ATR14` of VWAP.
  - Bar closes below VWAP.
  - Bar closes below or back through EMA8, or the following completed bar closes below the pullback bar low.
  - Completed close above VWAP invalidates short setup for the day.
- Entry: sell stop at pullback-confirmation bar low - 1 tick.
- Stop: pullback high + 1 tick.
- Target: opening-drive low, capped at 1R if the drive low is farther than 1R.

### Caps

- Maximum one long and one short structural setup per day.
- If both directions qualify on the same day, first confirmed setup wins and the opposite side is skipped unless flat and at least 30 minutes have passed.
- No new entries after 12:00 ET.

## 4. Exit Logic

Base v1 exit:

- Initial stop at pullback extreme +/- one tick.
- Target is the opening-drive extreme, capped at 1R.
- Same-second target/stop ambiguity uses adverse-first resolution.
- Max hold: 30 minutes.
- EOD flat: 15:58:30 ET if somehow still open.
- No trailing stop, no partials, no adaptive specialists for first test.

The "target capped at 1R" rule is important. It prevents rare distant drive extremes from converting a base-hit candidate into a hidden runner strategy.

## 5. Position Sizing And Apex Survival Rationale

Initial risk: `$250` per trade.

Position size:

```text
contracts = floor(250 / (stop_points * 2.0))
cap = 10 MNQ contracts
skip if contracts < 1
```

Skip if stop distance is below 6 points or above 28 points. The lower guard avoids micro-noise around VWAP; the upper guard avoids Apex damage on oversized pullback bars.

Worst plausible cluster: five consecutive losses. That is `$1,250`, 62.5% of the $2K Apex trailing drawdown cushion. The strategy can still fail if the first week clusters losses before any wins, so favorable-first-week independence is not assumed. The safer risk size is a response to the project pattern: candidates may have weak edge but die through path variance.

Daily loss limit: two realized losing exits per RTH date across this candidate.

## 6. Required Indicators / Data

All required data exists in the current store:

- MNQ 1-second OHLCV.
- Derived 1-minute OHLCV.
- RTH VWAP from 09:30 ET cumulative typical-price volume.
- EMA(8) on 1-minute closes.
- ATR(14) on 1-minute bars.
- Volume SMA(20), shifted one bar for lookahead cleanliness.

No footprint, bid/ask, Level II, or external news feed is required.

## 7. Differentiation

- Versus `vwap_stretch_snapback`: this does not fade VWAP stretch. It requires VWAP acceptance and trades continuation after the first pullback.
- Versus `opening_range_width_switch_v2_base_hit`: this does not use the opening range as the reversion target. It uses VWAP as the acceptance boundary and the impulse extreme as the base-hit target.
- Versus `tight_opening_window_breakout_long`: this does not chase a fresh breakout bar. It waits for a pullback to the session value reference after acceptance.
- Versus `mnq_news_like_impulse_pullback`: this removes the news/proxy-catalyst layer and uses the session VWAP acceptance test as the structural gate.
- Versus failed wide/fade families: this is continuation-first, not contrarian by default.

## 8. Required Research Before Spec Drafting

- R1 diagnostic: among qualifying first VWAP pullbacks, how often is the impulse extreme retested before the structural stop within 30 minutes?
- Direction attribution in R1: does the long/short split diverge materially?
- R4 frequency: does "first pullback only" create sparse signals, or does VWAP produce enough daily opportunities?
- Stop distribution: verify `[6, 28]` points is realistic rather than aspirational.
- Compare target choices in diagnostic only as labels, not tuning: drive extreme, 0.75R, 1R cap.
- Confirm VWAP calculation convention matches the replay frontend and indicator docs.

## 9. Source / References

This is a Codex-authored synthesis from project lessons rather than a transcript import. It uses a common intraday market concept: VWAP as an institutional reference and pullbacks to VWAP as continuation tests. This is trader-art, not academic proof. The project-specific empirical motivation is stronger than the external citation base: repeated MNQ fade attempts have failed, while the surviving weak leads tend to avoid catastrophic counter-flow fading.

The candidate is intentionally cheap to test with current OHLCV data. It should not be believed until R1 and R4 diagnostics exist.

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-25 | `untested-ideation` | Codex-invented candidate added to wiki. Continuation-first VWAP acceptance pullback with base-hit target to opening-drive extreme capped at 1R. No diagnostics run yet; pending R1 evidence diagnostic before any spec work. |
| 2026-05-25 | `phase-0-inadmissible-closed` | R1 v1.1 diagnostic completed. 127 eligible days, 49 qualifying events, target-first rate 53.1% (long 50.0%, short 57.1%), neither 0.0%, low-confidence false, compound-filter-over-restrictive false. Verdict NOT MET, below 60% floor. Closed at R1; no R4/spec/implementation. |
