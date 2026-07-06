---
status: "tested-positive-bridge"
---

# Savor-Wilson v2a Canonical Alpha - Strategy Specification (FINAL bridge)

**Strategy ID**: `savor_wilson_v2a_canonical_alpha`  
**Status**: FINAL bridge to nb_lib; tested-positive under per-trade empirical canonical  
**Lineage**: Legacy active-fleet v2a member from trader-frame v5, originally validated by `v2a_adapter.py` and `v2a_canonical_v2_pertrade.py`.  
**Implementation**: `nb_lib/scripts/v2a_canonical_alpha.py`  
**Candidate record**: `nb_lib/strategy_specs/candidates/savor_wilson_v2a_canonical_alpha.md`  
**Date**: 2026-05-27

---

## 0. Methodology Note

This is a bridge specification, not a new strategy discovery iteration.
The goal is to make the old catalyst-day fleet member discoverable and
runnable on the current `nb_lib` surface.

The nb_lib implementation is self-contained and does not import the root
adapter. It preserves the known v2a mechanics so the first validation
question is whether the old fleet member reproduces inside `nb_lib`.

## 1. Thesis

FOMC, NFP, and monthly OPEX sessions create afternoon volatility windows
where a simple long-only entry plus adaptive lifecycle management can
capture outsized catalyst moves while breakeven and trailing behavior
limit failed attempts.

## 2. Signal Logic

Eligible dates come from `savor_wilson_v2_calendar.json`:

- FOMC: enter long at 14:30 ET.
- NFP: enter long at 14:00 ET.
- OPEX: enter long at 14:00 ET.

The strategy has no additional directional signal filter in this
canonical bridge.

## 3. Exit Logic

- Initial stop: 25 points below entry.
- Breakeven arm: MFE >= 6 points.
- Trail arm: MFE >= 20 points.
- Trail ratchet: use completed minute close as candidate swing low;
  when price rallies 5 points above that candidate, raise stop to
  candidate low minus 2 points.
- EOD flat: 16:00 ET if no stop/trail/BE exit fired.

## 4. Execution Parameters

Empirical full-sample parameters:

| Parameter | Value |
|---|---:|
| Entry slippage | 0.50 pt |
| Stop overshoot | 0.63 pt |
| MAE multiplier | 1.20x |
| Commission | $0.35/contract/side |
| Contracts | 15 |

Full-sample stop overshoot is used because Band C-specific calibration
evidence was too thin for a separate v2a-window estimate.

## 5. Current nb_lib Result

Run date: 2026-05-27. Window: 2024-08-01 through 2026-01-31. OOS sealed
at 2026-02-01.

| Metric | Value |
|---|---:|
| Trades | 40 |
| Net P&L | +$4,239.00 |
| Profit factor | 1.73 |
| Win rate | 25.0% |
| Max drawdown | $2,244.00 |
| Exit mix | full_stop 6 / be_stop 24 / trail_stop 10 |

The result matches `v2a_canonical_v2_pertrade_outputs/v2a_canonical_v2_pertrade_report.md`
on headline metrics.

## 6. Management-System Relevance

v2a is a good management-system substrate because its edge is already
mostly lifecycle-shaped: BE survival, trail arming, and catalyst-window
path behavior matter more than a rich entry predicate. It is useful for
testing whether observer diagnostics can distinguish full-stop, BE-stop,
and trail-stop paths early enough to improve management without clipping
the few large catalyst winners.

## 7. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-04 | active-fleet-legacy | Trader-frame v5 records v2a as active catalyst-day fleet member under per-trade empirical canonical. |
| 2026-05-27 | FINAL bridge | Added nb_lib-native bridge implementation and canonical wiki record; rerun matches per-trade empirical canonical exactly. |
