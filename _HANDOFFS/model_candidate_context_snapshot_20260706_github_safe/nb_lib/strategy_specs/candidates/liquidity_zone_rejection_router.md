---
name: "Liquidity Zone Rejection Router"
tagline: "Trade rejection only at objective zones that beat distance-matched controls; use acceptance as the devil's-advocate stand-down."
status: "tested-informational-rejected"
created: 2026-06-30
updated: 2026-06-30
source: "Synthesizes sneaky-pivot level response with liquidity_zone_prior_router_v2 diagnostic evidence."

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-12:00 ET primary"
hold_duration: "intraday"

signal_type: "liquidity-zone rejection router"
indicators: ["opening range high/low", "round-number levels", "sweep/reclaim state"]
timeframes_used: ["1-minute", "5-minute", "15-minute optional", "1-second fills"]

brackets: "structural stop / next objective target"
position_sizing: "fixed contracts for screen"

canonical_spec: null
implementation: null
related_candidates:
  - "sneaky_pivot_15m_level_reversal"
  - "opening_range_width_switch"
  - "opening_range_response_tree"
  - "prior_day_overnight_level_response_continuation"

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
  - rejection
  - liquidity-zone
  - screen-required
---

# Liquidity Zone Rejection Router

## 1. Thesis

This is the better "yin-yang" home for the sneaky-pivot idea.

Instead of forcing sneaky-pivot onto C2 VWAP reclaim, this candidate
uses objective liquidity zones as the shared battleground:

```text
At some public levels, a sweep is usually rejected. At other levels, a
sweep is accepted. A strategy should not blindly fade every touch; it
should trade only the zones with empirical rejection behavior and stand
down when the acceptance branch is active.
```

The external sneaky-pivot transcript contributes the execution pattern:
wait for a level probe, require a rejection/confirmation candle, then
enter on the break back away from the level. The internal
`liquidity_zone_prior_router_v2` diagnostic contributes the devil's
advocate: not all levels deserve a fade.

## 2. Existing Evidence

The descriptive diagnostic
`nb_lib/probe_results/liquidity_zone_prior_router_v2_diagnostic.json`
already measured zone behavior against distance-matched random controls.
It did not run P&L and did not build a strategy.

Key rejection-rate-given-swept results:

| Zone | n swept | Rejection given swept | Matched-control rejection | Margin | Diagnostic verdict |
|---|---:|---:|---:|---:|---|
| OR high | 284 | 89.8% | 73.5% | +16.2 pp | beats |
| OR low | 281 | 90.4% | 73.5% | +16.8 pp | beats |
| Round 50 | 623 | 93.9% | 73.5% | +20.4 pp | beats |
| Round 100 | 311 | 93.9% | 73.5% | +20.3 pp | beats |
| PDH | 206 | 53.4% | 73.5% | -20.1 pp | loses |
| PDL | 152 | 65.8% | 73.5% | -7.8 pp | loses |
| Prior close | 379 | 11.9% | 73.5% | -61.7 pp | loses |

Interpretation:

- OR high/low and round-number zones are viable rejection candidates.
- PDH/PDL should not be automatically faded in this construction.
- Prior close is an acceptance/magnet zone, not a rejection zone.

## 3. Mechanism

- **Level-attention is real.** OR high/low and round numbers are
  repeatedly swept and reclaimed more often than matched controls.
- **Rejection is the active branch.** A sweep through a rejection-heavy
  zone followed by reclaim identifies failed initiative and trapped
  breakout flow.
- **Acceptance is the devil's advocate.** If price sweeps and then
  accepts beyond the zone, the fade is invalid. The strategy stands
  down rather than fighting accepted auction direction.
- **Targetability is native.** Target is the next opposing objective
  level: OR midpoint/opposite OR edge, VWAP, or nearest round level,
  depending on the branch spec. No target, no trade.

## 4. First Screen Translation

First screen should be cheap and proxy-level, not a full realsim build.

Candidate zones:

- `or_high`
- `or_low`
- `round_50`
- `round_100`

Excluded from first screen:

- `pdh`
- `pdl`
- `pdc`

They are excluded because the existing diagnostic says they do not
support rejection versus matched controls. This is not parameter tuning;
it is respecting prior descriptive evidence.

### Short Rejection

- Zone type is sell-side: OR high or round level above current price.
- Price sweeps above the zone by at least 2 ticks.
- Within a fixed reclaim window, a completed bar closes back below the
  zone by at least 1 tick.
- Optional sneaky-pivot confirmation: the reclaim bar must have a
  rejection wick or be followed by a break of its low.
- Entry short on the next 1-second fill after confirmation.
- Stop above the sweep extreme plus buffer.
- Target nearest opposing objective below entry that clears
  targetability.

### Long Rejection

Mirror the short setup:

- Zone type is buy-side: OR low or round level below current price.
- Price sweeps below the zone by at least 2 ticks.
- Completed bar closes back above the zone by at least 1 tick.
- Optional sneaky-pivot confirmation: rejection wick or break of the
  reclaim bar's high.
- Entry long on the next 1-second fill after confirmation.
- Stop below the sweep extreme plus buffer.
- Target nearest opposing objective above entry that clears
  targetability.

## 5. Devil's-Advocate Rules

This is the core complement to sneaky-pivot.

Do not fade if any of the following are true:

- Price closes beyond the zone and holds beyond it for the whole reclaim
  window.
- A second completed bar accepts beyond the swept side before reclaim.
- The targetability gate cannot identify a reachable opposing level.
- The candidate zone is a known acceptance/magnet zone from prior
  evidence, especially prior close.

The job of the devil's advocate is not to create a continuation trade
yet. In the first screen, acceptance means **no fade**. A later
continuation branch can be tested only if the rejection branch earns a
build.

## 6. Exit Logic

First screen:

- Stop: structural sweep extreme plus a fixed tick/point buffer.
- Target: nearest opposing objective level.
- Time exit: flat by 12:00 or 15:55, pre-commit before screen.
- No BE/trail/partials.

## 7. Why This Fits Better Than C2

C2's anchor was VWAP stretch; sneaky-pivot's anchor is objective
horizontal structure. Overlaying sneaky levels on C2 improved PF but
collapsed the sample.

This candidate starts where the level evidence is already strongest:
OR high/low and round numbers. It also avoids blindly fading PDH/PDL,
which the prior diagnostic showed are not rejection-favorable.

## 8. Required Screen

Before any build:

- Produce a proxy trade list from in-sample data only
  (`2024-08-01` through `2026-01-31`).
- Use fixed parameters from the diagnostic where possible:
  sweep >= 2 ticks, reclaim >= 1 tick, reclaim window = 5 minutes.
- Add only one execution confirmation choice before running:
  either completed 1m reclaim close, or reclaim close plus 15m/sneaky
  break confirmation. Do not test both unless counted as separate
  trials.
- Run the five-axis mechanism screen.
- Report per-zone attribution: OR high, OR low, round 50, round 100.

Build only if the rejection branch clears frequency/power and
concentration. A positive aggregate where one zone carries all net is
not enough.

## 9. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-06-30 | `untested-ideation-screen-required` | Created as the better complement to sneaky-pivot: liquidity-zone rejection where prior descriptive evidence beats controls, with acceptance as stand-down. |
| 2026-06-30 | `tested-informational-rejected` | Three trials run in-session, all DO_NOT_BUILD. **Trial #1** (rejection on OR/round zones, `probe_liquidity_zone_rejection_router_screen.py`): t=−3.12, mean −$7.36/trade, every zone independently negative — geometry of structural sweep stops vs. nearest-objective targets is structurally broken. **Trial #2** (continuation on OR/round, `probe_liquidity_zone_continuation_branch_screen.py`): t=−0.14, breakeven noise; round_50 marginally positive (PF 1.20, n=223) but too thin to clear multiplicity bar. **Trial #3** (continuation on PDH/PDL/PDC, `probe_liquidity_zone_continuation_pdhpdlpdc_screen.py`): t=−1.53 with extreme negative skew (−10.5) and kurtosis 205.6; classic pennies-in-front-of-steamroller profile, single worst loss −$2,852. Pre-committed Pattern-9 trial budget for this family is exhausted. **CONTEXT preserved**: the descriptive level-mechanics signal (90%+ rejection rate at OR/round, ~88% acceptance at PDC) is REAL price-action evidence; the conversion from descriptive signal to tradeable edge does not survive the geometry of any of the three tested mechanizations on MNQ RTH first hour. |
