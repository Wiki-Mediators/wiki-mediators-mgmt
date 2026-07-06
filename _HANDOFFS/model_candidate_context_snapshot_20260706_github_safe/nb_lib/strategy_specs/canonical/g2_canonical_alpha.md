---
status: "tested-positive-bridge"
---

# G2 Canonical Alpha - Strategy Specification (FINAL bridge)

**Strategy ID**: `g2_canonical_alpha`  
**Status**: FINAL bridge to nb_lib; tested-positive under per-trade empirical canonical  
**Lineage**: Legacy active-fleet G2 member from trader-frame v5, originally validated by `g2_adapter.py` and `g2_canonical_v2_pertrade.py`.  
**Implementation**: `nb_lib/scripts/g2_canonical_alpha.py`  
**Candidate record**: `nb_lib/strategy_specs/candidates/g2_canonical_alpha.md`  
**Date**: 2026-05-27

---

## 0. Methodology Note

This is a bridge specification, not a new strategy discovery iteration.
The goal is to make the old fleet member discoverable and runnable on the
current `nb_lib` surface after the PRJ_3 lookahead-safe re-baseline showed
that the trader-frame v5 fleet and the newer library truth must be kept
separate unless explicitly bridged.

The nb_lib implementation is self-contained and does not import the root
adapter. It preserves the known G2 mechanics so the first validation
question is whether the old fleet member reproduces inside `nb_lib`.

## 1. Thesis

On non-calendar days with a large positive first-half-hour RTH move, MNQ
can continue directionally through the rest of the cash session. A simple
long-only 10:30 entry with a fixed stop and EOD exit captures that
session-level continuation profile.

## 2. Signal Logic

Use 1-second MNQ RTH bars:

1. Let `r1_points = close_at_09:59:59 - open_at_09:30:00`.
2. Require `r1_points > 31.83`.
3. Exclude FOMC, NFP, monthly OPEX, and quad-witch dates.
4. Enter long on the first eligible 1-second bar after 10:30 ET.
5. Short trades are disabled in this canonical bridge.

## 3. Exit Logic

- Initial stop: 25 points below entry.
- No TP1.
- No breakeven.
- No trail.
- EOD flat: 15:58:30 ET.

## 4. Execution Parameters

Empirical Band B:

| Parameter | Value |
|---|---:|
| Entry slippage | 0.50 pt |
| Stop overshoot | 1.16 pt |
| MAE multiplier | 1.20x |
| Commission | $0.35/contract/side |
| Contracts | 15 canonical, 3 deployment scale |

## 5. Current nb_lib Result

Run date: 2026-05-27. Window: 2024-08-01 through 2026-01-31. OOS sealed
at 2026-02-01.

| Metric | Value |
|---|---:|
| Trades | 118 |
| Net P&L, 15c | +$38,766.30 |
| Net P&L, 3c deployment scale | +$7,753.26 |
| Profit factor | 1.53 |
| Win rate | 22.9% |
| Max drawdown, 15c | $8,103.00 |
| Max drawdown, 3c deployment scale | $1,620.60 |
| Exit mix | full_stop 89 / eod 27 / compliance_flat 2 |

The result matches `g2_canonical_v2_pertrade_outputs/g2_canonical_v2_pertrade_report.md`
on headline metrics.

## 6. Management-System Relevance

G2 is a clean substrate for management research because it has simple
single-stop runner geometry. It is useful for asking whether early
underwater state, volatility context, or path shape can improve a
low-win-rate runner without clipping the large winners that carry the
edge.

## 7. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-04 | active-fleet-legacy | Trader-frame v5 records G2 as active fleet member under per-trade empirical canonical. |
| 2026-05-27 | FINAL bridge | Added nb_lib-native bridge implementation and canonical wiki record; rerun matches per-trade empirical canonical exactly. |
