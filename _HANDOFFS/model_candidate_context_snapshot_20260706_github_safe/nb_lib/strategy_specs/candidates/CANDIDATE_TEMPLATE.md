---
name: "Strategy Name Here"
tagline: "One-sentence summary that captures the edge thesis"
status: "untested-ideation"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration source: literature reference, trader name, novel hypothesis, etc."

# Market and timing
markets: ["MNQ"]                     # list of instrument symbols
session: "RTH"                       # "RTH" | "Globex" | "ETH"
time_of_day: "09:30-12:00 ET"        # active signal window
hold_duration: "intraday"            # "intraday" | "swing-1d" | "swing-multi"

# Signal characteristics
signal_type: "trend-continuation"    # trend-continuation, mean-reversion,
                                     # breakout, gap-fade, momentum,
                                     # range-bound, multi-leg, etc.
indicators: []                       # e.g., ["EMA(20)", "ATR(14)", "VWAP"]
timeframes_used: ["1-second"]        # e.g., ["1-second", "1-minute", "5-minute", "daily"]

# Execution
brackets: "fixed-point"              # "fixed-point" | "atr-scaled" | "volatility-adaptive"
position_sizing: "fixed-contracts"   # "fixed-contracts" | "fixed-risk-dollar" |
                                     # "kelly" | "tiered-by-setup-quality"

# Cross-references (populated when relevant)
canonical_spec: null                 # e.g., "../canonical/this_strategy.md" once FINAL exists
implementation: null                 # e.g., "../../scripts/this_strategy.py" once landed
related_candidates: []               # other candidate files this relates to

# Test status (only populated when status >= tested-*)
test_results:
  in_sample_n: null
  in_sample_pnl_dollars: null
  in_sample_pf: null
  in_sample_win_rate: null
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: null         # e.g., "17/17" or "3/17" once multistart run

# Tags for organization (recommended controlled vocabulary in README)
tags:
  - rth-only
  - intraday
  - trend-continuation
---

# {{Strategy Name Here}}

## 1. Thesis

One or two paragraphs explaining **why this should work**. State
the edge hypothesis in plain English. Don't overclaim — be specific
about which market conditions the strategy expects to encounter and
why it should profit in those conditions.

## 2. Mechanism (what edge it captures)

Three to five bullets:

- **Mechanism 1.** Plain-English description of an exploitable
  market behavior.
- **Mechanism 2.** ...
- **Mechanism 3.** ...

Each mechanism should be **falsifiable** — if mechanism N doesn't
hold in the data, the strategy shouldn't work. Use the mechanisms
as the basis for the open-research questions in section 8.

## 3. Signal logic (entry conditions)

Plain English. No pseudocode at the candidate stage — that's for
the FINAL spec.

- **When does the strategy look for an entry?** (Time of day,
  session phase, after some event)
- **What conditions must hold?** (Price relative to indicator,
  pattern match, threshold)
- **What direction does it take?** (Long, short, or both)

## 4. Exit logic (stops, targets, time-based exits)

- **Stop loss:** how far below/above entry; fixed-point or
  ATR-scaled?
- **Take-profit:** levels and partial-close behavior.
- **Break-even arming:** any?
- **Time-based exits:** EOD flat? Hold-time limit? Other?

## 5. Position sizing

- **Contract count:** fixed at N, or scaled by signal strength /
  ATR / account size?
- **Risk per trade:** dollar amount, percent of account, or
  contract-count-based?

## 6. Required indicators / data

- **Indicators:** list with periods (e.g., `ATR(14)` on daily bars,
  `EMA(20)` on 5-min bars).
- **Bar resolution(s) needed:** 1-second, 1-minute, 5-minute,
  daily, etc.
- **Calendar dependencies:** does it skip half-days, FOMC days,
  etc.?
- **External data:** any non-MNQ data needed?

## 7. Differentiation (vs already-tested strategies)

How does this differ from:
- **Variant 1 / noise_brk Canonical Alpha** (9:36 noise-band
  breakout, fixed brackets): different signal? Different
  filtering?
- **PRJ_3 Canonical Alpha** (9:30-12:00 fractal-pullback, fixed
  brackets): different timing? Different mechanism?
- **ema_trend Canonical Alpha** (11:10 EMA-slope trend continuation,
  fixed brackets): different indicator? Different threshold?

Every new candidate should answer: "what makes this distinct from
what we've already tested and rejected?"

## 8. Required research before spec drafting

Open questions that the operator should answer before this becomes
a FINAL spec:

- **Question 1.** ...
- **Question 2.** ...
- **Question 3.** ...

This section is **the most important triage signal**. Candidates
with clear open questions are easier to evaluate than those that
hand-wave details.

## 9. Source / references

- Literature: papers, books, blog posts.
- Traders: discretionary or systematic operators who use this.
- Code precedents: nb_lib indicators / scripts that already
  provide partial machinery.
- Internal: prior session notes, methodology references, related
  candidate files.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | Initial entry |
