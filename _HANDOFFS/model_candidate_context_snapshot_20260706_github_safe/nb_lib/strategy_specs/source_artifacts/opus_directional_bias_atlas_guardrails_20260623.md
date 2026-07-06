# Directional Bias Atlas Guardrails

Source: operator discussion with Opus 4.8, banked 2026-06-23.

Status: source research note. This is not a project verdict and not a
strategy spec.

## Core Idea

After repeated failures from conditional OHLCV entry mechanisms, ask a
different question:

```text
Does MNQ RTH have a persistent directional tilt that survives without a
clever trigger?
```

This is a descriptive atlas, not a strategy. It should map where
directional drift lives, if anywhere, and must not select the best cell
and call it an edge.

## Load-Bearing Instructions

1. Read the whole panel. Do not select the best cell.
2. Prefer structural segments over arbitrary clock times.
3. Decompose overnight/beta drift from intraday drift before reading
   any long bias.
4. Report every drift cell raw and net of the baseline intraday drift.
5. Apply a multiple-comparisons guard: Bonferroni and/or FDR threshold
   based on the number of examined cells.
6. Treat one spectacular cell inside a flat panel as a likely selection
   artifact.
7. Treat a broad same-direction lean across many related cells as more
   interesting than one isolated winner.

## Beta Trap

The likely false positive is simple Nasdaq beta. In a strong 2024-2026
uptrend, "long anything" can look positive without being a tradeable
intraday edge.

Required guard:

- Decompose close-to-close return into overnight and RTH components.
- Report overnight drift separately.
- For each RTH cell, report excess drift relative to the all-day
  intraday baseline.
- Raw positive drift that equals the baseline long lean is not a signal.

## Multiple-Comparisons Trap

An atlas with many cells will naturally produce impressive-looking
cells by chance.

Required guard:

- Report per-cell t-stat.
- Report the total number of cells inspected.
- Report Bonferroni and/or FDR-adjusted thresholds.
- Call a cell "interesting" only if it clears the adjusted bar or if
  the broader panel shape is coherent enough to justify a separate
  pre-committed follow-up.

## Structural Segments

Clock slices are a coarse first pass, but the preferred framing is
structural:

- RTH open / opening drive.
- Initial balance complete.
- Post-IB.
- European close around 11:30 ET.
- Lunch lull.
- Afternoon attention return.
- Close auction.

State-conditioned slices should include:

- Overnight up/down into RTH.
- First 30 minutes up/down into the rest of day.
- Above/below VWAP at 10:30 into the rest of day.
- Open above/below prior close.
- Open above/below PDH/PDL and ONH/ONL.
- ATR tercile.
- Trend-day versus chop proxy.
- Day of week.
- Calendar flags if the frozen catalyst calendar exists.

## Expected Read

The prior is that most apparent long bias is beta, not alpha. A useful
finding would be a state-conditioned excess drift that survives baseline
adjustment and multiple-comparisons discipline.

If the map is flat or pure beta, that is a useful negative result. It
would mean MNQ has no exploitable mechanism-free directional bias in
this in-sample data, and future work should stop assuming that a simple
"lean with the tape" edge is hiding under the failed conditional
entries.
