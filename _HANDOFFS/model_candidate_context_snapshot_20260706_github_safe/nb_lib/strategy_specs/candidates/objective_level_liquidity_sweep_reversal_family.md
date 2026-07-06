---
name: "Objective-Level Liquidity Sweep Reversal Family"
tagline: "One sweep/reclaim mechanism applied to PDH/PDL, opening range, and round/VWAP levels with per-level attribution."
status: "tested-informational-rejected"
created: 2026-05-24
updated: 2026-05-24
source: "Option B synthesis from PDH/PDL sparse R4 probe: broaden objective level family rather than loosen single-level filters."

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:35-15:30 ET"
hold_duration: "intraday"

signal_type: "liquidity-sweep-reversal-family"
indicators: ["previous day high/low", "opening range high/low", "round numbers", "RTH VWAP", "volume MA(20)"]
timeframes_used: ["1-second source", "1-minute derived"]

brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"

canonical_spec: "nb_lib/strategy_specs/canonical/objective_level_liquidity_sweep_reversal_family_spec_FINAL.md"
implementation: "nb_lib/scripts/objective_level_liquidity_sweep_reversal_family_canonical_alpha.py"
related_candidates:
  - "pdh_pdl_liquidity_sweep_reversal"
  - "opening_range_liquidity_sweep_reversal"
  - "round_number_vwap_liquidity_sweep_reversal"
  - "true_zone_liquidity_sweep_reference"

test_results:
  in_sample_n: 233
  in_sample_pnl_dollars: -11555.20
  in_sample_pf: 0.75
  in_sample_win_rate: 0.326
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: "3/12 active; aggregate rejected"

tags:
  - rth-only
  - intraday
  - liquidity-sweep
  - objective-level
  - opening-range
  - previous-day-levels
  - round-number
  - vwap-based
  - volume-confirmation
  - composition-node
  - per-branch-attribution
  - ohclv-testable
---

# Objective-Level Liquidity Sweep Reversal Family

## 1. Thesis

The strict PDH/PDL liquidity sweep candidate was clean but sparse. This
family keeps the same sweep/reclaim/volume mechanism and broadens only
the objective level set: previous-day high/low, opening-range high/low,
and round-number/VWAP confluence levels.

The thesis is not that any single level family is enough. The thesis is
that liquidity sweeps are a reusable objective-level response pattern,
and the useful unit may be the family with per-level attribution rather
than PDH/PDL alone.

Counter-hypothesis: this becomes round-number microfade in disguise.
That is why level-family tags are mandatory. The test must show whether
round/VWAP, OR, or PDH/PDL actually contributes, rather than hiding weak
branches inside an aggregate.

## 2. Mechanism

All branches use the same mechanism:

- An objective level attracts stops and breakout orders.
- Price sweeps beyond the level by a bounded amount.
- Price reclaims/rejects back through the level.
- The reclaim/rejection bar shows volume expansion.
- Entry is delayed until the reversal bar break, not taken at the
  initial level touch.

Level families:

- `PDH_PDL`: prior completed RTH high and low.
- `OPENING_RANGE`: 09:30-09:45 ET range high and low.
- `ROUND_VWAP`: 25-point round handles near RTH VWAP.

## 3. R4 Probe Result

R4 v1.2 probe completed on 2026-05-24.

Report:
`C:/VMShare/NT8lab/nb_lib_objective_level_liquidity_sweep_family_r4_probe_report.md`

JSON:
`nb_lib/probe_results/objective_level_liquidity_sweep_reversal_family_r4_probe.json`

Headline:

- 30 structural signals over 23 trading days.
- 23 valid fill-guard-passing entries.
- 15 long / 15 short.
- Sparsity class: moderate.
- Extrapolated 30-120 passing signals per 60 trading days.

Per-family attribution:

| Level family | Structural signals | Passing fill guards |
|---|---:|---:|
| `PDH_PDL` | 5 | 3 |
| `OPENING_RANGE` | 7 | 4 |
| `ROUND_VWAP` | 18 | 16 |

Interpretation: broadening the level family fixed the frequency issue,
but most of the count came from `ROUND_VWAP`. Any FINAL spec must
preserve attribution and explicitly compare against prior round-number
failure modes.

## 4. Signal Logic

Use 1-minute bars derived from MNQ 1-second OHLCV. All signals are
evaluated on completed bars. Volume context uses prior bars only:
`volume >= 1.5 * SMA(volume, 20).shift(1)`.

Common long rule:

- Price sweeps below an objective support level by 2-20 ticks.
- The bar closes back above the level.
- The reclaim bar is bullish or closes in the upper 40% of its range.
- Volume confirmation passes.
- Entry stop is reclaim bar high + 1 tick.
- Stop is sweep low - 1 tick.

Common short rule:

- Price sweeps above an objective resistance level by 2-20 ticks.
- The bar closes back below the level.
- The rejection bar is bearish or closes in the lower 40% of its range.
- Volume confirmation passes.
- Entry stop is rejection bar low - 1 tick.
- Stop is sweep high + 1 tick.

Level-specific windows:

- `PDH_PDL`: scan 09:35-15:30 ET.
- `OPENING_RANGE`: OR forms 09:30-09:45 ET; scan 09:45-12:00 ET.
- `ROUND_VWAP`: scan 09:45-15:30 ET; 25-point round handles within 16
  pts of RTH VWAP.

## 5. Required Spec Work Before Implementation

- Commit overlap precedence for same-bar multi-family signals.
- Decide whether the strategy can take multiple level-family signals per
  day or must use a first-signal-wins rule.
- Commit stop-band guard and risk dollars.
- Commit fixed 2R versus VWAP target. The R4 probe used 2R geometry only.
- Preserve `level_family`, `level_label`, `setup`, and `direction` in all
  trade records.
- Require a per-level-family performance table in any multistart report.

## 6. Methodology Note

This candidate exists because Option B was cleaner than loosening the
PDH/PDL parameters after a sparse result. The R4 probe kept the same
sweep-depth and volume thresholds as the strict PDH/PDL probe and
changed only the objective level set.

This is entry-design, not a FINAL spec. It is eligible for FINAL spec
drafting because R4 frequency is now moderate, but no P&L edge has been
measured.

## 7. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-24 | entry-design | Family candidate created after strict PDH/PDL R4 was sparse. Broadened objective levels without loosening sweep/volume thresholds. R4 family probe passed frequency: 30 structural / 23 passing over 23 trading days, moderate sparsity class. |
| 2026-05-25 | spec-drafted-final | FINAL informational spec drafted at `nb_lib/strategy_specs/canonical/objective_level_liquidity_sweep_reversal_family_spec_FINAL.md`. Branch tags and per-level attribution are mandatory through implementation and multistart reporting. |
| 2026-05-25 | tested-informational-rejected | Implementation + 12-start multistart completed. Aggregate rejected: 233 trades, -$11,555.20, PF 0.75, 9/12 failed starts. Branch attribution preserved: `OPENING_RANGE` positive (+$2,069.30, PF 1.40, n=32) as a registry-review lead; `ROUND_VWAP` drove losses (-$11,807.30, PF 0.64, n=159). Report: `C:/VMShare/NT8lab/nb_lib_objective_level_liquidity_sweep_reversal_family_multistart_informational_report.md`. |
