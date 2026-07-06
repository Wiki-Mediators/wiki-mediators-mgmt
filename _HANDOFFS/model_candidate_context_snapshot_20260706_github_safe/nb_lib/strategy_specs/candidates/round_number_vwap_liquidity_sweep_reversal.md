---
name: "Round-Number VWAP Liquidity Sweep Reversal"
tagline: "Fade round-number sweeps only when VWAP context and volume-confirmed rejection align."
status: "phase-0-inadmissible-closed"
created: 2026-05-21
updated: 2026-05-21
source: "Operator request 2026-05-21 to build three liquidity-sweep strategies from True Zone transcript plus project lessons."

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-15:30 ET"
hold_duration: "intraday"

signal_type: "liquidity-sweep-reversal"
indicators: ["round numbers", "RTH VWAP", "volume MA(20)", "ATR(14) optional"]
timeframes_used: ["1-second source", "1-minute derived"]

brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"

canonical_spec: null
implementation: null
related_candidates:
  - "true_zone_liquidity_sweep_reference"
  - "round_number_rejection_microfade"
  - "pdh_pdl_liquidity_sweep_reversal"
  - "opening_range_liquidity_sweep_reversal"

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

tags:
  - rth-only
  - intraday
  - liquidity-sweep
  - round-number
  - vwap-based
  - volume-confirmation
  - ohclv-testable
---

# Round-Number VWAP Liquidity Sweep Reversal

## 0. Role In The Three-Strategy Liquidity-Sweep Batch

This is Strategy 3 of the OHLCV-first liquidity-sweep batch. It deliberately revisits the round-number idea, but with the lesson from `round_number_rejection_microfade`: generic round-number rejection was too broad and failed through loss clustering. This version requires a true sweep and a context filter.

The creative twist is confluence: the level is only interesting when a large round number sits near RTH VWAP or when price is stretched from VWAP and sweeps a round number before rejecting. The goal is to avoid every-touch microfading.

## 1. Thesis

Round numbers attract visible orders and stops, but they are too common to trade blindly. This candidate waits for price to sweep a large round number, fail to hold beyond it, and reject with volume confirmation. VWAP provides context: either the sweep occurs near fair value where two-sided flow is likely, or it occurs after a stretch where rejection back toward VWAP is plausible.

Long thesis: price sweeps below a round number, reclaims it on elevated volume, and is either near VWAP support or stretched below VWAP enough for mean reversion.

Short thesis: price sweeps above a round number, rejects below it on elevated volume, and is either near VWAP resistance or stretched above VWAP enough for mean reversion.

Counter-hypothesis: this is still round-number microfade in disguise and will overtrade unless R4 proves the confluence gates reduce frequency.

## 2. Mechanism

- Round numbers concentrate obvious orders and stops.
- VWAP is a widely watched intraday fair-value anchor.
- Sweeping a round number triggers liquidity.
- Failure to hold beyond the round number suggests trapped breakout flow.
- Volume expansion on reclaim/rejection confirms an active response.

## 3. Entry Logic

Use 1-minute bars derived from 1-second OHLCV.

Round-number grid:

- First candidate grid: 25-point handles.
- Larger grid variant: 50-point handles.
- Do not test both in the same first spec unless R4 is explicitly a comparison probe.

Context gate, choose one before FINAL spec:

- Near-VWAP mode: round number is within 8-16 points of RTH VWAP.
- VWAP-stretch mode: price is at least 20 points away from RTH VWAP and sweep direction is away from VWAP.

Long:

- Price trades below a selected round number by at least 2 ticks.
- Price closes back above the round number.
- Reclaim candle volume >= `1.5 * SMA(volume, 20)`.
- VWAP context gate passes.
- Entry stop is reclaim candle high + 1 tick.
- Stop is sweep low - 1 tick.

Short:

- Price trades above a selected round number by at least 2 ticks.
- Price closes back below the round number.
- Rejection candle volume >= `1.5 * SMA(volume, 20)`.
- VWAP context gate passes.
- Entry stop is rejection candle low - 1 tick.
- Stop is sweep high + 1 tick.

Maximum one trade per round-number level per day, maximum two trades per day.

## 4. Exit Logic

First baseline should be simple:

- Fixed 2R, or
- VWAP touch if using VWAP-stretch mode.

Do not mix both target modes in the first P&L test.

## 5. Position Sizing And Apex Survival Rationale

Use fixed-risk-dollar sizing and a strict daily loss cap. This candidate inherits the round-number overactivity warning. R4 must prove that VWAP context plus sweep/reclaim reduces trade count enough to avoid another loss-cluster failure.

Initial stop band should likely start at `[5, 35]`, not `[5, 50]`, because round-number sweeps should be tighter than wide-state reversals. If R4 shows stops routinely exceed 35 points, that is probably a warning sign rather than a reason to widen immediately.

## 6. Required Indicators / Data

This candidate is OHLCV-testable:

- MNQ 1-second OHLCV.
- Derived 1-minute OHLCV.
- RTH VWAP.
- 1-minute volume SMA(20).
- Round-number grid.

No footprint data is required for the first version.

## 7. Differentiation

This differs from `round_number_rejection_microfade` in three ways:

1. It requires a liquidity sweep and reclaim/rejection, not a generic touch.
2. It requires volume confirmation.
3. It requires VWAP context to avoid trading every round number.

If those three changes do not materially reduce overactivity and loss clustering, the round-number family should remain closed for now.

## 8. Required Research Before Spec Drafting

- R4 v1.2 probe with 25-point grid and one VWAP context mode.
- Count raw round sweeps versus volume-confirmed VWAP-context signals.
- Stop-distance distribution.
- Same-day clustering and direction balance.
- Compare against the prior round-number failure mode explicitly.

## 9. Source / References

Source is the operator's True Zone liquidity-sweep transcript synthesis, combined with project evidence that plain round-number rejection failed. The strategy exists only because it is structurally different: sweep-first, volume-confirmed, VWAP-contextual.

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-21 | untested-ideation | Strategy 3 of three OHLCV-first liquidity-sweep candidates. Round-number idea rebuilt as sweep/reclaim + volume + VWAP context after earlier round-number microfade failure. Awaiting R4 probe before spec drafting. |
| 2026-05-25 | `phase-0-inadmissible-closed` | **v1.5 R1-first triage sweep applied.** R1 diagnostic measured 25-pt round-number sweep + reclaim + volume×1.5 + near-VWAP context reversion. **69 qualifying events (38L/31S); 27 reverted 1R within 30min (39.1%)**, 40 hit stop first, 2 neither. **R1 verdict: NOT MET** at 39.1% — 13.5pp below OR-LSR (52.6%) in same liquidity-sweep family, and 40.4pp below ORWS base. **Same family failure pattern as OR-LSR**: filter-augmented variants underperform the unfiltered base. The wiki's counter-hypothesis ("this is still round-number microfade in disguise and will overtrade unless R4 proves the confluence gates reduce frequency") is empirically validated — the VWAP confluence gate works as a filter but the surviving signals don't have reversion edge. Candidate CLOSED at R1 gate. **Confirms liquidity-sweep family-wide R1 failure**: pdh_pdl (R4-sparse 3/23d) + opening_range (R1 52.6%) + round_number_vwap (R1 39.1%) — all three OHLCV-first liquidity-sweep candidates closed. Diagnostic: `nb_lib/probe_results/round_number_vwap_liquidity_sweep_reversal_r1_diagnostic.json`. Combined sweep closure report: `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_5_sweep_closures.md`. |
