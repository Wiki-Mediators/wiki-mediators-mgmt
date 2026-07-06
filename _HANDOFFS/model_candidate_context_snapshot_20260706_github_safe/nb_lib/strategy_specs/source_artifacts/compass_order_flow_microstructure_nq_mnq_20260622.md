# Order-Flow And Microstructure Intraday Signals For NQ/MNQ

Source status: operator-provided Compass artifact, banked 2026-06-22.
This is external research context and direction-setting material, not a
local `nb_lib` result. No order-flow data was downloaded and no OOS was
touched by banking this note.

## Main Read

A pivot to order-flow research is reasonable, but the realistic target
is not sub-second queue imbalance or one-second OFI. Those signals are
real but decay too quickly and belong mostly to co-located / queue-priority
market making. For this project, the only plausible cost-survivable
direction is **sustained multi-minute order-flow imbalance** computed on
the deeper full-size NQ book and traded via MNQ.

Current local data check on 2026-06-22:

- Available locally: MNQ 1-second OHLCV, MNQ 1-minute/hour/day OHLCV,
  MNQ statistics, some ES/CL/GC/UVXY OHLCV.
- Not found locally: Databento MBP-10, MBO, or trades schema with CME
  aggressor side for NQ/MNQ/ES.

Therefore this is **not build-ready from current data**. The next step
would be a Databento cost/availability preflight for a small in-sample
slice before any download or strategy build.

## Evidence Hierarchy From The Source Artifact

- OFI explains contemporaneous short-horizon price moves strongly, but
  this is mostly mechanical impact and not directly tradable once
  observed.
- Predictive OFI at one-minute-plus horizons is much weaker and decays
  quickly.
- Queue imbalance predicts the next mid-price move, but monetizing that
  requires passive queue priority; a taker strategy paying the spread is
  structurally disadvantaged.
- Trade signing / CVD can be exact with CME aggressor-side data, but
  expected edge is weak and should be treated as a confirming feature,
  not a standalone alpha until proven locally.
- VPIN belongs, at most, as a volatility/toxicity regime filter, not as
  a directional signal.
- NQ likely leads MNQ because NQ is deeper and faster, but the lead is
  likely milliseconds. Practical use: compute cleaner signals on NQ,
  trade MNQ only if the minutes-horizon drift survives costs.

## Candidate To Screen First If Data Is Acquired

**Sustained multi-minute NQ OFI / CVD traded on MNQ.**

Proxy hypothesis:

```text
Compute signal on NQ MBP-10 + trades.
Aggregate OFI / integrated OFI / CVD over 5-15 minute windows.
Only act on extreme persistent imbalance, e.g. top/bottom decile.
Hold for minutes, not seconds.
Trade MNQ.
Require net edge after an explicit 2-point MNQ round-turn cost.
```

This should be screened with `nb_lib/screening.py` before any full build.
The mechanism-class screen should pay special attention to:

- cost-distance: expected gross drift must clear the 2-point round-turn
  floor by a meaningful margin;
- frequency-power: extreme imbalance filters may become sparse;
- regime-concentration: order-flow edges may live only around news,
  open/close, or high-volatility periods;
- cross-correlation: likely overlaps with momentum/breakout sleeves
  unless it produces genuinely different trade days.

## Recommended Preflight Before Spending Data Budget

1. Use the Databento cost-estimate flow first; do not download MBP/trades
   blindly.
2. Estimate a short slice only, preferably NQ + MNQ + ES:
   - `trades` schema for aggressor-side signed volume / CVD;
   - `mbp-10` schema for top-10 book OFI / integrated OFI;
   - avoid MBO unless passive queue-position modeling becomes the
     explicit research question.
3. If cost is acceptable, download a small historical slice and build a
   feature-pipeline validation report, not a strategy first:
   - confirm timestamps;
   - confirm symbol/contract mapping;
   - compute basic OFI, CVD, queue imbalance;
   - verify no lookahead in feature aggregation;
   - run a minutes-horizon predictability diagnostic net of a 2-point
     MNQ cost floor.

## Discipline Note

Do not be seduced by high contemporaneous OFI R-squared claims. The only
project-relevant question is whether a causally observed order-flow
feature predicts a future move large enough to survive MNQ friction.

This order-flow branch should remain a **data-preflight and feature
pipeline project** until a small, pre-committed slice shows minutes-scale
net predictability. If the signal cannot clear a 2-point cost floor in
the preflight, abandon the microstructure direction rather than trying
to compete with co-located market makers.
