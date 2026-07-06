---
name: "Sneaky Pivot 15m Level Reversal"
tagline: "Use prior-session range and outer swing levels as objective reversal anchors, then enter on a 15m rejection-confirmation break."
status: "screen-failed-pre-build"
created: 2026-06-30
updated: 2026-07-02
source: "External transcript archived at nb_lib/strategy_specs/source_artifacts/sneaky_pivot_transcript_20260630.md"

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-11:30 ET primary; no entries after 12:00 ET unless separately pre-committed"
hold_duration: "intraday"

signal_type: "level-response mean-reversion"
indicators: ["prior-session high/low", "confirmed swing high/low", "15m candles"]
timeframes_used: ["15-minute", "1-second fills"]

brackets: "structural level target / structural setup stop"
position_sizing: "fixed contracts for screen"

canonical_spec: null
implementation: null
related_candidates:
  - "prior_day_overnight_level_response_continuation"
  - "ten_fifteen_opening_drive_state_router"
  - "c2_midmorning_targetability_mean_reversion_screen"

test_results:
  in_sample_n: null
  in_sample_pnl_dollars: null
  in_sample_pf: null
  in_sample_win_rate: null
  out_of_sample_tested: false

tags:
  - rth-only
  - intraday
  - level-response
  - mean-reversion
  - targetability
  - screen-required
---

# Sneaky Pivot 15m Level Reversal

## 1. Thesis

The transcript describes a deliberately simple discretionary strategy:
draw the previous day's high/low plus the next outer swing high/low,
then trade only when price reaches one of those levels and prints a
three-candle rejection sequence on the 15-minute chart.

The MNQ translation is not "buy because the chart looks close enough."
The testable thesis is narrower:

```text
Early RTH probes into prior-session extremes or adjacent outer swing
levels sometimes exhaust, and a completed 15m rejection candle followed
by a break of that candle can produce a tradable rotation back toward
the opposing objective level.
```

This is a level-response / targetability candidate. The target is not a
static 30/60 bracket; it is the next objective level across the range.

## 2. Mechanism

- **Prior-session levels concentrate attention.** PDH/PDL and nearby
  outer swings are visible reference points where stops, breakout
  orders, and failed-break participants may cluster.
- **The first 15-30 minutes reveal which side is being tested.** A
  strong opening candle into one of those levels creates an objective
  location for response, instead of a random mid-range fade.
- **The sneaky candle is rejection evidence.** The second completed 15m
  candle must show that the level is being defended before entry is
  allowed.
- **The third-candle break is the execution trigger.** Entry occurs only
  when price breaks the sneaky candle in the reversal direction.
- **The opposing level provides targetability.** If there is no
  reachable opposing level with acceptable reward/risk, there is no
  trade.

## 3. Objective Signal Translation

Candidate screen should use one trade per day maximum until proven
otherwise.

### Levels Frozen Before Entry

- `range_high`: prior RTH high.
- `range_low`: prior RTH low.
- `swing_high`: nearest confirmed swing high above `range_high`, using
  only bars completed before the current RTH open.
- `swing_low`: nearest confirmed swing low below `range_low`, using
  only bars completed before the current RTH open.

The transcript allows using the opening 15m candle high/low when the
daily structure is too wide. Treat that as a separate future variant,
not part of the first screen, unless explicitly pre-committed.

### Long Setup

- First completed 15m RTH candle probes the lower level zone:
  `range_low` or `swing_low`.
- "Probe" must be objective, for example low touches/breaches the level
  or comes within a pre-committed tolerance such as `0.25 * ATR_15m`.
- Sneaky candle: the next completed 15m candle closes in the reversal
  direction and closes back above the tested level or above the first
  candle midpoint.
- Entry trigger: buy when a later 15m candle breaks above the sneaky
  candle high. For a cheap screen, use the next 1-second open after that
  break.
- Stop: below the lowest low of the setup sequence, tick-rounded worse
  for the position.
- Target: nearest upper objective level in this order: `range_high`,
  then `swing_high`, provided it clears targetability.

### Short Setup

Mirror the long setup:

- First completed 15m RTH candle probes `range_high` or `swing_high`.
- Sneaky candle closes in the reversal direction and back below the
  tested level or below the first candle midpoint.
- Entry trigger: sell when price breaks below the sneaky candle low.
- Stop: above the highest high of the setup sequence.
- Target: nearest lower objective level in this order: `range_low`, then
  `swing_low`, provided it clears targetability.

## 4. Targetability Gate

This candidate should include targetability from the beginning because
the target is intrinsic to the thesis.

Minimum first-screen constraints:

- Candidate target must be strictly in the trade direction.
- Structural risk is distance from entry to setup invalidation stop.
- Target distance / risk must clear a pre-committed floor, suggested
  `R >= 1.0` for the first screen.
- Target distance must be plausible for remaining session movement,
  using an ATR/ADR reachability cap. If no target clears both tests,
  deny the trade.

This is different from bolting targetability onto a weak entry after the
fact. Here the entry only exists because the opposing level is the
expected destination.

## 5. Exit Logic

First screen:

- Stop: setup structural stop as above.
- Target: nearest qualifying opposing objective level.
- Time exit: flat by 15:55 ET.
- No BE, trail, partials, or discretionary cut.

The transcript describes patience and holding while the level remains
valid. That maps to no early BE/trail in the first screen.

## 6. Data Requirements

- 15-minute RTH bars derived from the canonical 1-second MNQ store.
- 1-second data for fill timing and realistic stop/target touches.
- Prior RTH high/low.
- Confirmed swing high/low logic with no future bars after the RTH
  open.
- ATR/ADR history for tolerance and reachability if used.

OOS remains sealed. First screen must use only 2024-08-01 through
2026-01-31.

## 7. Differentiation

Compared with `prior_day_overnight_level_response_continuation`, this is
rejection/reversal, not break-retest continuation.

Compared with `ten_fifteen_opening_drive_state_router`, this is not a
fixed-time state bet. It only trades if price first interacts with an
objective level and then rejects.

Compared with C2/C4 VWAP reclaim, this uses horizontal prior-session
structure and a 15m candle sequence instead of VWAP bands.

## 8. Required Research Before Build

Screen-only first:

- Does the level interaction plus sneaky candle produce enough trades?
  The project needs a materially better rate than 5 trades/month unless
  expectancy is exceptional.
- Does the targetability requirement kill the sample, as it did when
  applied after the fact to first-hour momentum?
- Do upper/lower `range` levels behave differently from outer `swing`
  levels?
- Is the edge reversal-specific, or does it merely re-express the same
  weak intraday direction factor already rejected elsewhere?
- Does using opening-15m high/low as fallback improve frequency, or does
  it turn into another opening-range re-skin?

## 9. Screen Verdict Rules

Before full build, create the cheapest proxy trade list and pass it
through the five-axis mechanism screen.

- Any RED on skew/concentration or frequency/power: do not build.
- Cost-distance must be GREEN because targets are structural and should
  be farther than friction.
- Cross-correlation must be checked against first-hour momentum,
  prior-day level response, VWAP-reclaim, noise-area, and noise_brk.

No parameter rescue if the first objective translation fails. A future
variant must change the mechanism materially, not just tweak tolerance.

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-06-30 | `untested-ideation-screen-required` | Distilled from external "sneaky pivot" transcript. Archived as source artifact. Candidate is not promoted; first step is a cheap screen. |
| 2026-07-02 | `screen-failed-pre-build` | Mechanical screen run (`probe_sneaky_pivot_15m_level_reversal_screen.py`, results at `sneaky_pivot_15m_level_reversal_screen_report.json`, findings at `_worker_reports/TASK_sneaky_pivot_15m_level_reversal_screen_findings.md`). Three hard-gate reds: **frequency-power** (n=66 over 380 days = 3.7/mo, below §8 floor of 5/mo; t=0.14), **skew/concentration** (best-trade share = 307.95% of net; MinTRL 9,472), **regime concentration** (range-level trades alone are net −$304; swing trades alone are net +$543; the positive aggregate is entirely carried by n=8 swing trades — §9 "one bucket carries all" failure). Range_high shorts are the loudest specific loser (n=40, −$1,246, PF 0.688). Cost-distance is GREEN (φ=0.006 — targetability worked) and cross-correlation vs noise_brk is GREEN (Jaccard 0.147), but neither rescues the hard gates. Per §9 last line: no parameter rescue. Any future revival must change the mechanism materially. |
