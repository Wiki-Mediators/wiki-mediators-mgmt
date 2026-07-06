---
name: "Round Number Rejection Microfade"
tagline: "Fade failed 1-bar sweeps of 50/100-point psychological levels with short, level-anchored targets."
status: "tested-rejected"
created: 2026-05-12
updated: 2026-05-14
source: "Operator Phase 1 direction 2026-05-13; round-number rejection as standalone entry mechanism following choppiness_impulse_fade closure."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-15:30 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "level-rejection"
indicators: ["RoundLevelGrid(50)", "ATR(20) on 5-minute bars"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "fixed-point"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: "../canonical/round_number_rejection_microfade_spec_FINAL.md"
implementation: "../../scripts/round_number_rejection_microfade_canonical_alpha.py"
related_candidates: []

# Test status (only populated when status >= tested-*)
test_results:
  in_sample_n: 23
  in_sample_pnl_dollars: 327.50
  in_sample_pf: 1.11
  in_sample_win_rate: 0.174
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
  - level-based
  - fixed-point
  - fixed-risk-dollar
  - microfade
---

# Round Number Rejection Microfade — Phase 1 Entry Signal Design

This document specifies the entry signal only. It is not a full FINAL
strategy spec. Phase 2 will extend this entry design into a canonical
strategy spec with v2.4-style adaptive management if Phase 1 preflight
passes.

## 0. Outcome Priors And Scope Acknowledgments

### 0.1 Priors

Pre-test priors for the eventual full strategy:

| Outcome | Prior | Meaning |
|---|---:|---|
| No edge / account failure | 0.50 | Round-number rejection has no exploitable edge after friction; the contested-edge counter-hypothesis wins |
| Weak in-sample only | 0.30 | A modest in-sample effect that does not clear OOS or Apex constraints |
| OOS-eligible edge | 0.12 | Round-number microstructure produces a durable, friction-survivable signal |
| Signal design blocker | 0.08 | Signal too sparse, too dense, or pathologically clustered |

These are methodology priors, not statistical estimates. The 0.50 base
rate reflects that round-number effects in liquid futures markets are
contested in the literature.

### 0.2 Scope

Phase 1 covers:

- Round-level identification.
- Sweep + rejection detection.
- Entry trigger predicates.
- Initial static brackets sufficient for entry-only validation.
- Fixed-risk-dollar sizing and runtime assertions.

Phase 2 will add (consuming v2.4 management primitives per
`nb_lib_v2_4_management_infrastructure_report.md`):

- Adaptive specialists (if any).
- Mid-trade `apply_bracket_update` integration.
- Strategy `force_exit_strategy` triggers.
- Management event attribution.
- Full pass/fail criteria for PF, account survival, and OOS trigger.

No management mechanics are designed in this document beyond a simple
static bracket scaffold.

## 1. Strategy Thesis

Round Number Rejection Microfade tests whether brief sweeps of 50-point
psychological levels on MNQ that fail to hold beyond the level produce
short-lived mean-reversion opportunities on the inside of the level.

The intended edge is microstructural: 50-point levels (and especially
100-point levels as a subset) attract resting limit orders, stop
placements, and discretionary attention. A 1-minute bar that pokes
through the level and closes back on the inside is evidence that the
breakout failed — the move did not attract follow-through. Inside that
1-minute window, a small fade with a stop just beyond the rejection
extreme and a target at the next inside subdivision is a finite
expression of the failed-breakout idea.

The counter-hypothesis is equally important and possibly more accurate:
**round-number behavior in liquid futures markets is widely known and
likely arbitraged**. If true, this candidate fails like the contested
literature predicts. Phase 1's job is to test the entry signal's
mechanical viability before committing Phase 2 resources to a thesis
whose edge is contested at the literature level.

The thesis is FALSIFIABLE in two senses:
1. If the signal-frequency preflight produces too few signals, the
   mechanism is structurally narrow even before edge is measured.
2. If Phase 2 in-sample PF falls below 1.0 and the account FAILs (as
   the seven prior canonical alphas did), the thesis is empirically
   refuted at this granularity.

## 2. Entry Signal And Timing

### 2.1 Market And Session

- Market: MNQ continuous front-month futures.
- Session: RTH only.
- Entry evaluation window: 09:45:00 through 15:30:00 US/Eastern.
- No new entries on half-days in Phase 1.
- Maximum accepted trades: four per RTH day (Section 8.4 caps).

The window opens at 09:45 to skip the first 15 minutes of opening-range
discovery (where round-level behavior is dominated by overnight
positioning rather than microstructure rejection). The window closes at
15:30 — 30 minutes before EOD-flat at 15:58:30 — to give microfade
trades time to reach target or be cleanly exited before compliance EOD.

### 2.2 Derived Bars And Lookahead Rule

All bars derive from the 1-second OHLCV source.

- 1-minute bars: primary signal evaluation bar (rejection candle).
- 5-minute bars: ATR(20) for risk-guard validation only.

Bars are left-labeled half-open intervals. At decision timestamp `T`, a
derived bar is usable only if:

```text
bar.left_edge + bar_duration <= T
```

For a 1-minute signal evaluated at `T = 10:23:00`, the last usable
1-minute bar is `[10:22:00, 10:23:00)`. The entry fill, if any, is on
the first 1-second bar strictly after `T`.

### 2.3 Round-Level Identification

The round-level grid is the **50-point integer grid**. 100-point levels
are a natural subset (every 100-multiple is a 50-multiple), so no
separate 100-grid logic is needed. The grid is anchored at price 0; on
MNQ at typical prices (18,000–22,000), this produces levels at
18,000 / 18,050 / 18,100 / ... etc.

At each completed 1-minute bar B, two reference levels are computed
from price-only data:

```text
level_above = ceil(B.close / 50) * 50
level_below = floor(B.close / 50) * 50
```

Both are usable; one or both may be relevant depending on which side of
the level the rejection appears on.

The grid is fixed and uses 50.0 as the spacing constant. No regime
gating, no time-varying spacing, no learned level selection.

### 2.4 Approach Detection (Sweep Requirement)

For a rejection to qualify, the bar must have actually penetrated the
level — a passing touch is insufficient. The minimum sweep depth is **1
tick (0.25 points)** beyond the level.

For a SHORT setup (selling a failed upside sweep of `L = level_above`):

```text
B.high >= L + 0.25
```

For a LONG setup (buying a failed downside sweep of `L = level_below`):

```text
B.low <= L - 0.25
```

The sweep-depth requirement is a single-tick threshold, not an
ATR-scaled one, because round-level behavior is anchored to the
absolute tick grid, not to a volatility regime.

### 2.5 Rejection Identification (Close-Back-Inside)

The rejection trigger is **a single 1-minute bar that pokes through the
level and closes back on the inside**. No multi-bar pattern; no body-
direction requirement; no separate "wick length" condition.

For SHORT (rejection of `L = level_above` after sweep above):

```text
B.high >= L + 0.25     (Section 2.4 sweep)
B.close < L            (closed back below the level)
```

For LONG (rejection of `L = level_below` after sweep below):

```text
B.low <= L - 0.25      (Section 2.4 sweep)
B.close > L            (closed back above the level)
```

**Methodology note**: this is intentionally one bar, not a multi-bar
pattern. Adding a "close > open" body requirement or a "high <
prior_high" pullback rule would compound conjunctive filters. The
chop-fade binding-constraint analysis showed those compound stacks
produce sparse event classes. The "high >= L + 0.25 AND close < L"
condition is *intrinsically rejection-shaped* — a bar that sweeps above
the level and closes back below is structurally a failed-breakout
signature. No further pattern stacking is needed at Phase 1.

### 2.6 Entry Trigger Conditions

Short entry predicate (all true at signal moment T = right edge of bar B):

```text
session_in_window == True             (Section 2.1)
B.high >= level_above + 0.25          (Section 2.4)
B.close < level_above                 (Section 2.5)
abs(B.close - level_above) <= 8.0     (Section 2.6 proximity guard)
```

Long entry predicate (symmetric):

```text
session_in_window == True
B.low <= level_below - 0.25
B.close > level_below
abs(level_below - B.close) <= 8.0
```

The **proximity guard** (`|close - L| <= 8.0`) ensures the bar's close
sits in a band 8 points wide on the inside of the level. Bars that
sweep the level and close far away (e.g., 20 points back inside) are
not "rejections" — they are mid-move continuations whose level-touch is
incidental. 8 points is approximately 1/3 of typical MNQ 5-min ATR; an
informed-prior round number.

Boundary rules:

- All comparisons use `>=` and `<=` per spec.
- If both long and short predicates fire on the same timestamp (would
  require simultaneous sweeps of `level_above` and `level_below`,
  geometrically rare but possible on wide-range bars): skip with
  reason `ambiguous_two_sided_signal`.

### 2.7 Direction Handling

Phase 1 is two-sided. This honors the methodology concern raised by
needle drop v2's long-only post-result selection (which inherited the
vwap result's direction asymmetry). Round-number rejection is, in
theory, symmetric: psychological levels should reject in either
direction.

If signal-frequency preflight reveals strong direction imbalance, that
is a Phase 2 or post-test finding. It is NOT a Phase 1 design lever.

### 2.8 Entry Fill Semantics

Use the established T+1 second pattern:

```text
signal_ts = right edge of completed 1-minute rejection bar
entry_ts = first 1-second bar strictly after signal_ts
entry_price = entry bar open with BAND_B entry friction
```

Assertions:

```python
assert entry_ts > signal_ts
assert signal_ts.time() >= time(9, 45)
assert signal_ts.time() <= time(15, 30)
```

If no eligible 1-second bar exists after the signal timestamp within
RTH, skip the trade.

## 3. Risk And Position Sizing

### 3.1 Fixed Dollar Risk

```text
risk_dollars = 300.00
point_value = 2.00 dollars per MNQ point per contract
```

The lower-than-Needle-Drop risk reflects microfade trade scale: short
stops produce high contract counts under fixed-risk sizing; a smaller
risk-dollar caps per-trade exposure.

### 3.2 Initial Stop Distance

For a SHORT setup (faded sweep above level L):

```text
sweep_extreme = B.high        (the 1-min rejection bar's high)
raw_stop_pts = sweep_extreme - entry_price + 0.50
```

For a LONG setup:

```text
sweep_extreme = B.low
raw_stop_pts = entry_price - sweep_extreme + 0.50
```

The `+ 0.50` (2 ticks) is a buffer beyond the rejection extreme. If
price re-tests and exceeds the extreme by more than the buffer, the
"failed breakout" thesis has itself failed — get out.

### 3.3 Position Size Formula And Bounds

```text
raw_contracts = floor(risk_dollars / (raw_stop_pts * point_value))
contracts = clamp(raw_contracts, min=1, max=15)
```

Skip if `raw_contracts < 1`.

### 3.4 Risk Guards

Skip the trade if any of:

```text
raw_stop_pts < 2.0          (rejection bar too small; not a real sweep)
raw_stop_pts > 6.0          (rejection bar too large; not a microfade)
contracts < 1
contracts > 15
atr_5m_20 <= 0 or NaN       (indicator warmup)
Compliance state != ACTIVE
```

The 2.0–6.0 point band on stop distance is the heart of the "micro"
qualifier: a rejection bar with high - close > 6.0 means the bar's
range is wide and the trade is no longer a tight-stop microfade.

### 3.5 Apex Compliance

Use `ComplianceTracker` with the Apex 50K EOD eval preset. The outer
strategy loop must stop opening new trades after `AccountState.FAILED`.

## 4. Adaptive Layers In Phase 1

### 4.1 No Regime Gate

Phase 1 has **no chop/trend/volatility regime gate**. The round-level
proximity (Section 2.6 proximity guard) acts as the natural selector —
it pre-filters to bars at meaningful zones in price action. Adding a
chop or trend filter on top would compound conjunctive predicates
unnecessarily.

This is a DELIBERATE choice informed by the chop-fade binding
constraint analysis: each conjunctive predicate is a multiplicative
filter. Predicate count should be the minimum that captures the
thesis, not a maximalist coverage of regime conditions.

### 4.2 Phase 2 Management Deferred

No confidence score, parallel composer, runner ceiling, force-exit
logic, or specialist attribution is specified in Phase 1. Phase 2 may
add such mechanics if signal-frequency preflight passes and operator
chooses to invest in the build.

## 5. Initial Bracket Geometry (Phase 1 Static Scaffold)

The microfade targets are short and anchored to **inside subdivisions
of the 50-point grid**: 25-point subdivisions toward the level's inside
direction.

### 5.1 Stop Placement

Per Section 3.2:

```text
short_stop = entry_price + raw_stop_pts
long_stop = entry_price - raw_stop_pts
```

### 5.2 TP1 (First Subdivision)

The next 25-point subdivision inside the level:

For SHORT (faded sweep of level_above):

```text
short_tp1 = level_above - 25.0
```

For LONG (faded sweep of level_below):

```text
long_tp1 = level_below + 25.0
```

TP1 closes 50% of contracts, rounded down. If position size is 1
contract, TP1 is disabled and TP2 manages the full position.

If the distance from entry to TP1 is less than `0.50 * raw_stop_pts`
(R:R below 0.5), skip the trade. Friction is too large relative to the
target.

### 5.3 TP2 (Second Subdivision)

For SHORT:

```text
short_tp2 = level_above - 50.0
```

For LONG:

```text
long_tp2 = level_below + 50.0
```

TP2 is the next 50-point subdivision inside — typically another round
level itself, which may itself act as support/resistance. The trade
closes its remaining 50% there.

### 5.4 BE Arm

```text
be_arm_pts = 0.60 * raw_stop_pts
be_offset_pts = 0.0
```

The 0.60×R BE arm fires earlier than the typical 0.75×R because
microfade trades resolve quickly — if the trade has moved meaningfully
toward TP1, getting BE protection in place is more valuable than
preserving optionality for further adverse excursion.

This is a static scaffold. Phase 2 may replace it with adaptive
management.

## 6. Indicators, Data, And Assumed Library

### 6.1 Required Indicators

- 5-minute ATR(20), Wilder smoothing (for Section 3.4 risk-guard
  validation — confirms ATR warmup completed and value is positive).
- Round-level grid (50-point spacing, computed price-only; no library
  primitive needed beyond `math.floor` / `math.ceil`).

No ChoppinessIndex, ATRPercentile, ATRRatio, or VWAP/SessionStdev are
required at Phase 1. This is a deliberate departure from the chop-fade
and vwap_stretch_snapback regime-gated approaches.

### 6.2 Data Source

MNQ 1-second OHLCV from the project Databento store. Derive 1-minute
and 5-minute bars from the 1-second source using left-labeled half-open
intervals.

No ES, options, order-flow, or external event data is required.

### 6.3 Assumed Lifecycle API

Phase 1 only requires standard `TradeLifecycle` bracket behavior. The
v2.4 adaptive management primitives are not used by the Phase 1 static
scaffold. Phase 2 is expected to consume:

- `apply_bracket_update` (if regime-conditional bracket updates are
  designed)
- `force_exit_strategy` (if a confidence-collapse or invalidation
  signal is designed)
- management event logger (for Section 7.3 attribution if Phase 2 uses
  specialists)
- 5-minute swing detector (only if Phase 2 uses structure-trail
  management — unlikely for microfade)

### 6.4 FILL_ASSUMPTIONS Entry

Phase 2 should add a strategy-specific fill assumption key:

```text
FILL_ASSUMPTIONS["round_number_rejection_microfade"] = BAND_B
```

Until then, Phase 1 assumes the project default BAND_B friction.

## 7. Pre-Committed Pass Criteria (Phase 1 Entry-Only)

These are signal-shape expectations, not full performance thresholds.

### 7.1 Signal Frequency Expectation

Expected in-sample accepted-signal count:

```text
60 <= accepted_entries <= 220
```

The expected range is **wider on both ends** than chop-fade's 40–180
because round-level visits occur multiple times per day on MNQ at
typical prices, and the predicate stack is intentionally leaner. If
fewer than 60 accepted signals fire, the proximity guard or sweep-
depth requirement may be too restrictive. If more than 220 fire,
per-day or per-level cooldown may need tightening (Section 8.4
parameters are first-revision targets if so).

### 7.2 Direction Balance Expectation

Because Phase 1 is two-sided:

```text
0.35 <= long_trade_share <= 0.65
```

If the signal is outside this range, Phase 2 must explicitly review
whether the imbalance is structural (e.g., MNQ's tendency toward
upside trend in the in-sample window biased rejection toward the
short side) or a bug.

### 7.3 Full Pass Criteria Deferred

PF thresholds, win-rate expectations, Apex survival criteria,
specialist attribution, and OOS trigger rules are Phase 2 scope. They
must be locked in the FINAL spec before any full in-sample test.

## 8. Mechanics

### 8.1 Evaluation Cadence

Evaluate entry predicates once per completed 1-minute bar during the
09:45–15:30 entry window.

### 8.2 Time Exit

Microfade trades resolve quickly. The Phase 1 static scaffold uses:

```text
time_exit = entry_ts + 20 minutes
```

Exit reason:

```text
"round_number_microfade_time_exit"
```

20 minutes is **half** the chop-fade time exit. Phase 2 may revise
this — but per the microfade thesis, trades that haven't resolved
within 20 minutes are no longer "fades of a fresh rejection."

### 8.3 EOD Flat

No position may remain open past the existing EOD flat deadline.
Strategy time exit should normally occur before EOD compliance flat.

### 8.4 Per-Day Limits And Cooldown

After an accepted trade exits:

```text
cooldown_after_trade = 15 minutes
```

The 15-minute cooldown is shorter than chop-fade's 45-minute because
microfade trades fire more often and resolve faster.

Per-day limits:

```text
maximum 4 accepted trades per RTH day
maximum 3 long, 3 short  (i.e., total cap binds first at 4)
```

Per-level limit (anti-duplicate-fade safeguard):

```text
no fade on the same level_above OR level_below within 30 minutes of
the prior fade on that level
```

This prevents repeatedly fading the same level after a failed first
fade — a "second touch" might be a genuine new signal, but a "third
touch within 30 minutes" is the strategy fighting the level instead
of fading it.

### 8.5 Runtime Assertions

Entry-side assertions:

```python
assert signal_ts < pd.Timestamp("2026-02-01", tz="America/New_York")
assert last_1m.name + pd.Timedelta(minutes=1) == signal_ts
assert atr_5m_20 > 0
assert last_5m.name + pd.Timedelta(minutes=5) <= signal_ts
assert raw_stop_pts >= 2.0 and raw_stop_pts <= 6.0
assert contracts >= 1 and contracts <= 15
assert direction in ("long", "short")
assert level in {level_above, level_below}
assert (level % 50) == 0  # 50-point grid integrity
```

## 9. HARD-HALT Conditions

Phase 1 halts on:

1. **HARD-HALT-OOS-LEAK**: any data timestamp >= 2026-02-01 is used
   for design, in-sample signal counts, or indicator history.
2. **HARD-HALT-LOOKAHEAD**: any predicate reads an incomplete 1-minute
   or 5-minute bar.
3. **HARD-HALT-ACCOUNT-FAILED-CONTINUE**: a new trade opens after the
   compliance tracker is FAILED.
4. **HARD-HALT-SPEC-DRIFT**: thresholds differ from this document
   during implementation without an explicit spec revision.
5. **HARD-HALT-MANAGEMENT-CREEP**: Phase 1 implementation adds
   adaptive management behavior before the Phase 2 spec exists.
6. **HARD-HALT-DIRECTION-BUG**: long/short predicates both fire on the
   same timestamp and the implementation enters anyway.
7. **HARD-HALT-LEVEL-GRID-DRIFT**: the strategy uses a level spacing
   other than 50.0 without spec revision (no 25-point microgrid, no
   100-point coarser grid).

## 10. Open Questions Deferred (Phase 2 Scope)

Deferred to Phase 2:

- Adaptive management specialist set (if any).
- Whether the static 20-minute time exit should be replaced with a
  confidence-driven exit.
- Whether a regime gate could meaningfully tighten Phase 2 in-sample
  performance without re-introducing chop-fade's predicate-stack
  sparseness.
- Whether the proximity guard (`|close - L| <= 8`) should be
  ATR-scaled rather than fixed.
- Whether a second-touch / N-touch counting mechanism per level adds
  value vs. the simple "fade first qualifying rejection" approach.
- Full pass criteria including PF threshold, account survival, and
  OOS trigger.
- Whether 100-point levels should receive special treatment
  (heavier weighting, separate target geometry) vs treating them as
  the natural subset of 50-pt levels they are.

## 15. Selection Bias Notes

This design is influenced by:

1. **The 7-fleet failure pattern** (continuation + breakout + mean-
   reversion candidates all failing Apex eval). Round-number rejection
   is a structurally different family from any of the seven — it
   anchors to absolute price levels rather than volatility, momentum,
   or trend indicators.

2. **The chop-fade closure** (mechanism produced 8/11/19 signals at
   three threshold values; binding-constraint analysis identified
   compound predicate stacks as the structural cause). This design
   deliberately uses **only 4 conjunctive predicates** per direction
   (session window + sweep + close-back-inside + proximity), down from
   chop-fade's 7+. The intent is to demonstrate that lean predicate
   design produces viable signal frequency.

3. **The needle drop v2 long-only post-result selection.** This Phase
   1 stays two-sided to avoid repeating that pattern. Round-number
   rejection is theoretically symmetric.

4. **Round-number effects are CONTESTED in the literature.** This is
   acknowledged in Section 1 thesis. The 0.50 base-rate prior in
   Section 0.1 reflects the lit-literature uncertainty.

All thresholds (50-pt grid, 0.25-pt sweep depth, 8.0-pt proximity,
2.0–6.0-pt stop band, $300 risk dollars, 15-contract cap, 20-min time
exit, 15-min cooldown, 30-min per-level cooldown, 4-per-day cap) are
informed priors. No threshold may be tuned after a signal-frequency
run or in-sample result; the single-revision discipline applies.

## 16. Status History

| Date       | Status               | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-05-12 | `untested-ideation`  | Created as untested-ideation by Codex 5.5 CLI batch 2 (dynamic adaptive intraday focus).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 2026-05-13 | `entry-design`       | Phase 1 entry signal designed following chop-fade closure. Lean 4-predicate stack chosen deliberately to address chop-fade's compound-predicate sparseness finding. Phase 2 full FINAL spec with v2.4-style management pending signal-frequency preflight result.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 2026-05-13 | `spec-drafted-final` | FINAL spec drafted. Phase 2 management framework added; Phase 1 entry preserved. See `../canonical/round_number_rejection_microfade_spec_FINAL.md`. Three specialists (time_to_resolution, volatility_shock, structure_trail); parallel field-by-field composition; strict tighten-only invariant. v2.4 primitives consumed. 8.0 pt proximity guard preserved per operator choice (2 design revisions remaining under Option 2 discipline).                                                                                                                                                                                                                                                                                                     |
| 2026-05-14 | `tested-rejected`    | In-sample test FAILED. 23 trades over 6 active days (2024-08-01 to 2024-08-08); account FAILED via compliance_drawdown on trade 23. PF 1.11, win rate 17.4%, total P&L $+327.50 (positive but well below spec edge threshold). Six of seven spec Section 7 pass criteria failed (PF, n, account state, attribution 30%, attribution 2-of-3 specialists, direction asymmetry 218%). Management was design-dead: 2 of 3 specialists never fired; structure_trail made 7 proposals all correctly rejected as widening (BE arm fired before structure_trail could tighten further). OOS slot NOT consumed (Section 7.5 requires all 6 conditions; this run met 0). 8-fleet Apex-eval-failure pattern. See `nb_lib_rnrm_insample_results_report.md`. |
