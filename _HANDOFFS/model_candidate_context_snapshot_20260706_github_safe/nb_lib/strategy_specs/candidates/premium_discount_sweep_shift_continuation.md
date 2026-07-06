---
name: "Premium/Discount Sweep-Shift Continuation"
tagline: "Trade with higher-timeframe bias only after price reaches premium/discount location, sweeps liquidity, then shifts lower-timeframe structure."
status: "phase-0-proxy-inconclusive"
created: 2026-06-02
updated: 2026-06-02
source: "Transcript intake: routine / simplified mechanical trade plan; later clarified by operator screenshots showing 4H swing range, premium/discount, supply-zone ranking, and 1H sweep/shift structure."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "10:30-14:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "trend-continuation"
indicators: ["EMA(8/21) on 15-minute bars", "rolling 4-hour range", "1-minute liquidity sweep", "1-minute structure shift"]
timeframes_used: ["1-second", "1-minute", "15-minute"]

# Execution
brackets: "structure-based"
position_sizing: "fixed-risk-dollar"

# Cross-references
canonical_spec: null
implementation: "../../scripts/diagnostic_pdssc_premium_discount_sweep_shift_r1.py"
related_candidates:
  - "opening_range_liquidity_sweep_reversal"
  - "failed_orb_fade"
  - "lunch_compression_break"

# Test status
test_results:
  in_sample_n: 12
  in_sample_pnl_dollars: null
  in_sample_pf: null
  in_sample_win_rate: 0.25
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: null

tags:
  - rth-only
  - intraday
  - trend-continuation
  - transcript-derived
  - phase-0
  - liquidity-sweep
  - structure-shift
  - not-visual-reproduction
---

# Premium/Discount Sweep-Shift Continuation

## 1. Thesis

The transcript argues that entries should not be taken merely because a
lower-timeframe pattern appears. Price must first be in a higher-timeframe
location that makes the trade direction sensible. For a bearish bias, the
candidate waits for price to pull back into premium; for a bullish bias,
it waits for discount. Only then does it look for a liquidity sweep and a
lower-timeframe market shift.

This is a text-only reconstruction. It does **not** claim to reproduce
the instructor's visual supply/demand boxes. Instead, it tests the
mechanical version the project can actually falsify using current MNQ
OHLCV data.

Visual clarification added 2026-06-02: the first proxy below is now known
to be too generic. The intended method is not "rolling range + EMA trend."
It is a hierarchical structure workflow:

1. Identify the higher-timeframe directional context first. In the
   operator screenshots this is a 4-hour downtrend, with the visible
   range anchored to the most recent meaningful lower high and lower low.
2. Draw premium/discount across that active 4H swing range.
3. Identify multiple supply zones inside the range and rank them by
   location. The zones near premium/extreme supply matter more; zones
   near equilibrium or discount are lower quality or invalid for shorts.
4. Only after price mitigates a selected HTF point of interest, drop to a
   lower timeframe (shown as 1H in the screenshots) and wait for liquidity
   sweep plus structure shift.

The first R1 diagnostic should therefore be read as a failed **crude
proxy**, not as a falsification of the visual method itself.

Daily-bias transcript intake added 2026-06-02: the useful addition is a
five-step bias scaffold that can be converted into objective labels:

1. Mark the higher-timeframe range and premium/discount location.
2. Mark obvious liquidity magnets, especially prior-day high/low and
   equal highs/lows.
3. Identify phase narrative: continuation with higher-timeframe trend
   versus pullback/counter-HTF phase.
4. Pick the target before entry: opposing zone, opposing swing, prior-day
   level, or unfilled imbalance.
5. Define invalidation: the bias is wrong only after a pre-defined break
   and acceptance, not after a wick or one noisy bar.

This is not new evidence for the candidate. It is a better checklist for
future objective predicate design.

## 2. Mechanism

- **Location before trigger.** A lower-timeframe entry model should only
  matter after price reaches a higher-timeframe premium/discount zone.
- **Liquidity event before continuation.** A sweep above/below recent
  local structure may mark a stop-run or failed auction.
- **Liquidity quality matters.** Transcript follow-up on 2026-06-02
  sharpened the "sweep" concept into a taxonomy of likely resting-order
  locations: ordinary swing highs/lows, strong highs/lows that have not
  been traded through, equal highs/lows, trendline liquidity, and obvious
  support/resistance shelves. These should be treated as label candidates,
  not as proof of edge.
- **Inducement before sweep.** The useful mechanical pattern is not
  merely "price swept a high/low." The stronger version is:
  inducement builds a visible liquidity pool, price sweeps that pool,
  displacement follows, and the resulting supply/demand/FVG zone becomes
  the higher-quality point of interest for a later pullback.
- **Structure shift as confirmation.** The candidate does not enter on
  the sweep alone; it waits for a lower-timeframe break in the trade
  direction.
- **Bias alignment.** Longs require bullish higher-timeframe bias and
  discount location. Shorts require bearish higher-timeframe bias and
  premium location.
- **Bias must include invalidation.** A future version should not log
  "bullish" or "bearish" without also logging the level or state that
  invalidates that bias. Acceptance beyond the invalidation level should
  be defined before measurement.

## 3. Signal logic

Phase-0 proxy definitions:

- Higher timeframe = 15-minute bars.
- Trend bias = EMA(8) vs EMA(21) plus EMA(21) slope over four 15-minute
  bars.
- Swing range = rolling prior 16 x 15-minute bars, roughly four hours,
  excluding the active 15-minute bar.
- Premium/discount = top/bottom quartile of that rolling range.
- Lower-timeframe liquidity = 1-minute sweep of the prior 20-minute high
  or low by at least 2 ticks, closing back through the swept level.
- Market shift = within five minutes of the sweep, a close through the
  opposite 10-minute local structure level in the intended direction.

Short setup:

1. 15-minute bias is bearish.
2. Current minute trades in the top quartile of the prior four-hour
   range.
3. A 1-minute bar sweeps above the prior 20-minute high by at least
   2 ticks and closes back below that high.
4. Within five minutes, a 1-minute close breaks below the pre-sweep
   10-minute local low.

Long setup is symmetric.

## 4. Exit logic

Phase-0 R1 diagnostic only:

- Stop for short = sweep high + 1 tick.
- Stop for long = sweep low - 1 tick.
- 1R continuation target = entry +/- stop distance.
- R1 asks whether the 1R continuation target is hit within 30 minutes
  before the structure stop.

No TP1/TP2, BE, trailing, or Apex lifecycle logic is introduced until R1
evidence exists.

## 5. Position sizing

Not used in Phase 0. A future full strategy would use fixed-dollar risk
based on actual structure-stop distance.

## 6. Required indicators / data

- MNQ 1-second bars for stop/target ordering.
- 1-minute bars for sweep and market-shift detection.
- 15-minute bars for EMA bias and rolling four-hour range.
- No external data.

The current text source does not provide exact visual supply/demand box
coordinates, so those are represented by rolling-range premium/discount
location only.

## 7. Differentiation

This differs from previously tested opening-range fade/sweep candidates
because the opening range is not the anchor. It is a more general
location-then-trigger framework:

- higher-timeframe trend and price location first;
- lower-timeframe liquidity sweep second;
- lower-timeframe market shift third.

It also differs from `ema_trend_canonical_alpha` because EMA is only a
bias filter, not the entry trigger.

## 8. Required research before spec drafting

- Does the translated sweep-shift setup clear R1 continuation evidence?
  **Initial answer: no.** The strict text-only proxy produced only 4
  qualifying events in the first Phase-0 slice and only 1 reached 1R
  continuation before stop.
- Does premium/discount location add anything over the sweep-shift trigger
  alone?
- Is the 15-minute EMA/range proxy too crude compared with the transcript's
  4-hour structure concept?
- If R1 passes, should the next test compare aggressive sweep entry vs
  conservative pullback-after-shift entry?

Post-R1 interpretation: do not promote this strict proxy. If this idea is
ever revisited, the next legitimate experiment is not parameter tweaking
inside this result. It would need a separately pre-committed comparison
between:

- sweep-shift trigger without the premium/discount location gate;
- premium/discount location with a less restrictive structure-shift
  definition;
- a visual-review-assisted zone-labeling dataset, if the operator wants
  to preserve the transcript's actual drawn-box logic.

Visual-method follow-up now preferred over blind tuning:

- Replace EMA bias with objective BOS/pivot bias.
- Replace rolling four-hour range with an active swing range from the
  most recent confirmed HTF impulse leg.
- Add daily-bias phase labels:
  - pro-HTF continuation;
  - counter-HTF pullback;
  - mid-range/equilibrium chop;
  - invalidated / reset.
- Replace generic premium/discount touch with a ranked HTF zone:
  extreme-zone first, mid-premium second, equilibrium/discounter zones
  excluded for shorts.
- Replace generic "prior 20-minute high/low sweep" with a liquidity-pool
  label:
  - ordinary swing high/low;
  - equal highs/lows within a pre-committed tick tolerance;
  - strong high/low: pivot that led to BOS and has not been traded
    through since;
  - trendline liquidity: at least three aligned swing points, treated
    cautiously because line fitting is easy to overfit;
  - support/resistance shelf: repeated tests of a horizontal level
    within a pre-committed tolerance.
- Add a separately logged "swept-liquidity zone" label only when the
  sweep is followed by displacement in the intended direction. This is
  not allowed to be used for entry at the sweep itself unless
  pre-committed; its main value is ranking later pullback zones.
- Preserve lower-timeframe sequence: mitigation -> sweep of local swing
  high/low -> market shift through the opposite local swing.
- Pre-define target and invalidation fields even in diagnostics:
  target_zone_type = prior_day_level | opposing_swing | opposing_zone |
  imbalance_fill; invalidation_type = acceptance_beyond_protected_high_low
  | reclaim_against_bias. These fields may be descriptive at first, but
  they should be logged so later observer work can score whether the bias
  plan was correct.

Follow-up completed 2026-06-02:

- `structure_30m_5m` profile used local TVB tick binaries, built 1-second
  bars manually, then derived 30-minute structure and 5-minute sweep/shift.
  Result: 131 eligible days, 1,950 location bars, 363 sweeps, 12 full
  sweep+shift events, 3 continuation / 0 stop / 9 neither. R1 continuation
  rate = 25.0%, verdict `NOT_MET`.
- `visual_4h_1h` profile used the same local tick binaries, built 4-hour
  structure and 1-hour sweep/shift to match the screenshots more closely.
  Result: 126 eligible days, 193 location bars, 49 sweeps, but **0 full
  sweep+shift events**. Verdict `NOT_MET` for denominator failure.

Interpretation: the screenshots improved the conceptual translation, but
the objective MNQ implementation still does not produce an admissible
candidate on the available TVB tick-vault fallback window. The 30m/5m
adaptation is not wrong-way (0 stops), but it is too slow/sparse for R1
continuation. The 4H/1H faithful version is too sparse to trade at all
under the objective definition.

Important data-source caveat: the structure follow-up used the local TVB
tick-vault folders because the current runtime could not decode the
canonical Databento DBN store. The tick-vault coverage is shorter and is
not the project's primary research source. Treat this as a proxy
inconclusive result, not a final full-dataset viability closure.

## 9. Source / references

- 2026-06-02 transcript intake: routine / simplified mechanical trade
  plan.
- 2026-06-02 transcript/image intake: liquidity concepts and inducement
  taxonomy. Useful additions: resting liquidity behind highs/lows that
  have not been traded through; equal highs/lows; trendline and
  support/resistance liquidity; inducement as bait that builds liquidity;
  higher-quality zones are those that sweep liquidity, create
  displacement, and can later be mitigated.
- 2026-06-02 transcript intake: daily-bias checklist. Useful additions:
  daily bias means "likely next move plus why"; bias requires
  invalidation; prior-day high/low and equal highs/lows are first-pass
  liquidity magnets; phase should be labeled as pro-HTF continuation or
  counter-HTF pullback; targets should be selected before entry from
  opposing zones/swings/prior-day levels/imbalances.
- `_METHODOLOGY_INTUITION.md` section 2.7 records the process lesson and
  warns that discretionary chart concepts require objective predicates.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-06-02 | `untested-phase-0` | Candidate created from text-only transcript as an objective proxy, not a visual reproduction. |
| 2026-06-02 | `phase-0-inadmissible-sparse` | R1 diagnostic run: `nb_lib/scripts/diagnostic_pdssc_premium_discount_sweep_shift_r1.py`; output `nb_lib/probe_results/premium_discount_sweep_shift_continuation_r1_diagnostic.json`. In-sample slice only, OOS untouched. 127 eligible days, 515 location-pass minute bars, 82 sweeps after location, but only 4 full sweep+shift events; 1 continuation, 2 stops, 1 neither; continuation rate 25.0%; R1 verdict `NOT_MET`. Strict text-only translation is too sparse and not admissible for spec drafting. |
| 2026-06-02 | `phase-0-inadmissible-sparse` | Operator supplied visual clarification screenshots. Important correction: the intended method is hierarchical 4H structure -> premium/discount -> ranked supply/demand zone -> 1H sweep/shift, not EMA + rolling-range location. Keep the R1 failure attached only to the crude v0.1 proxy. |
| 2026-06-02 | `phase-0-proxy-inconclusive` | Structure follow-up completed with local TVB tick binaries, no new data download, OOS untouched. Script: `nb_lib/scripts/diagnostic_pdssc_structure_v2_r1.py`. `structure_30m_5m`: 12 events, 3 continuation / 0 stop / 9 neither, 25.0% R1, `NOT_MET`. Output: `nb_lib/probe_results/premium_discount_sweep_shift_continuation_v0_2_structure_structure_30m_5m_r1_diagnostic.json`. `visual_4h_1h`: 49 sweeps but 0 full sweep+shift events, denominator failure, `NOT_MET`. Output: `nb_lib/probe_results/premium_discount_sweep_shift_continuation_v0_2_structure_visual_4h_1h_r1_diagnostic.json`. Because TVB tick-vault coverage is short and non-canonical relative to the two-year 1-second OHLCV store, this is a proxy/informational result, not a final full-dataset closure. |
| 2026-06-02 | `phase-0-proxy-inconclusive` | Liquidity/inducement transcript added as concept refinement, not new evidence. The useful update is a testable liquidity-pool taxonomy and the "sweep -> displacement -> later mitigation zone" sequence. Do not use the language of smart money or inducement as evidence by itself; convert it into objective labels before any future diagnostic. |
| 2026-06-02 | `phase-0-proxy-inconclusive` | Daily-bias transcript added as concept refinement, not new evidence. Banked the five-step scaffold: HTF range/premium-discount, liquidity magnets, phase narrative, target selection, and invalidation. Future diagnostics should log bias phase, target zone, and invalidation condition rather than only entry trigger outcome. |
