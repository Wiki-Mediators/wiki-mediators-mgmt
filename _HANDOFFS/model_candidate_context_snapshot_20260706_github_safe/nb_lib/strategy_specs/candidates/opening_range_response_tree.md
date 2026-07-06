---
name: "Opening Range Response Tree"
tagline: "One opening-range level, three branched responses (reversal / continuation / breakout), each tagged for per-branch attribution."
status: "tested-informational-rejected"
created: 2026-05-20
updated: 2026-05-21
source: "Strategic synthesis 2026-05-20. First candidate built as a composition NODE rather than a standalone strategy: collapses three opening-range variants (sweep-reversal, break-hold continuation, expansion breakout) into one instrumented decision tree. Embodies the marginal-registry composition vision."
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-13:00 ET"
hold_duration: "intraday"
signal_type: "multi-branch-level-response"
indicators: ["opening range high/low", "ATR(14) 2-min", "EMA(8) 2-min"]
timeframes_used: ["1-second source", "2-minute derived"]
brackets: "structure anchored"
position_sizing: "fixed-risk-dollar"
canonical_spec: "../canonical/opening_range_response_tree_spec_FINAL.md"
implementation: "../../scripts/opening_range_response_tree_canonical_alpha.py"
related_candidates:
  - "opening_range_failure_continuation_long"
  - "first_hour_range_expansion_breakout"
  - "opening_range_liquidity_sweep_reversal"
  - "opening_range_width_switch"
test_results:
  in_sample_n: 185
  in_sample_pnl_dollars: -11744.60
  in_sample_pf: 0.62
  in_sample_win_rate: 40.5
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: "0/12"
tags:
  - rth-only
  - intraday
  - multi-branch
  - opening-range
  - objective-level
  - composition-node
  - regime-conditional
  - two-minute
  - per-branch-attribution
---

# Opening Range Response Tree

## 1. Thesis
Three separately-authored opening-range candidates (sweep-reversal,
break-hold continuation, expansion breakout) all read the SAME objective
level — the opening range — and branch on what price does after
interacting with it. Rather than test them as unrelated strategies, this
candidate combines them into one decision tree and instruments each
branch so we learn which response carries edge and which drags.

This is the first candidate built as a composition NODE rather than a
standalone strategy. It directly serves the marginal-registry
composition vision: a single node reading one level, emitting different
signals depending on regime (how the level interaction resolves), with
per-branch attribution so the useful branches can later be routed into
an ensemble and the useless ones dropped.

The decision tree:

```
Opening range formed (09:30-10:00 ET)
  -> break fails and reclaims inside?   -> SWEEP-REVERSAL branch (fade)
  -> break holds on pullback?           -> CONTINUATION branch (with-trend)
  -> post-10:30 break with expansion?   -> BREAKOUT branch (with-trend)
```

Counter-hypothesis: the branches may not be independent edges. One
branch (likely a continuation branch) may carry all the signal while
the reversal branch drags (consistent with the session finding that
fading has lost money repeatedly on MNQ). The per-branch attribution
is designed precisely to surface this rather than hide it in a blended
aggregate.

## 2. Mechanism (what edge it captures)
- One objective level (opening range high/low) watched by many
  participants.
- Three mutually-exclusive responses to the level interaction, each
  with its own thesis:
  - Sweep-reversal: a break that fails and reclaims signals trapped
    breakout traders; fade the failed break.
  - Continuation: a break that pulls back and holds signals acceptance;
    trade with trend.
  - Expansion breakout: a post-10:30 break with range expansion signals
    decisive balance resolution; trade the breakout.
- Each branch fires at its confirmation EVENT (reclaim / hold /
  expansion bar) — the start of the resulting move, reducing the
  fill-time drift that hurt signal-after-move candidates.
- The composition value: per-branch attribution tells us which response
  to the same level is a useful signal node.

## 3. Signal logic (entry conditions)
Opening range = high/low of 09:30-10:00 ET (first fifteen 2-minute
bars). All bars evaluated on completion; all lookbacks use bars strictly
before the current timestamp.

**Branch A - Sweep-Reversal** (fade):
- A completed 2-minute bar trades beyond OR boundary (high above OR-high
  / low below OR-low) but closes back INSIDE the range (reclaim).
- Entry: fade direction (short if OR-high swept, long if OR-low swept),
  stop-market on break of the reclaim bar's far extreme.
- Tag: `branch=sweep_reversal`.

**Branch B - Break-Hold Continuation** (with-trend):
- A completed 2-minute bar closes beyond OR boundary (acceptance).
- Price pulls back toward the boundary (within 0.25 x ATR) without a
  completed bar closing back inside the range.
- A completed bar closes back in the break direction off the level
  (the hold).
- Entry: with-trend, stop-market at hold-bar extreme + 1 tick.
- Tag: `branch=break_hold_continuation`.

**Branch C - Expansion Breakout** (with-trend):
- After 10:30 ET, a completed 2-minute bar closes beyond OR boundary
  AND that bar's range >= 1.5 x ATR(14) measured before the bar.
- Entry: with-trend, stop-market at breakout-bar extreme + 1 tick.
- Tag: `branch=expansion_breakout`.

**Precedence and conflict rules** (pre-committed):
- The branches are largely time-sequential: a break either holds
  (Branch B) or fails-and-reclaims (Branch A), not both; Branch C is a
  distinct post-10:30 event.
- Maximum ONE structural entry per day across all branches. The first
  valid branch to fire takes the day; later branch signals are logged
  as skipped with the firing branch noted.
- If a Branch A reclaim and a Branch B hold somehow both qualify on the
  same path, Branch A (the earlier event) takes precedence.
- Direction for each branch is set by the mechanism, not post-hoc
  selection.

## 4. Exit logic (stops, targets, time-based exits)
Per-branch bracket geometry (each branch anchors to its own structure):
- Branch A (reversal): stop on far side of OR boundary; TP1 1.0R, TP2
  2.0R (reversal targets resolve faster); BE arm 1.25R.
- Branch B (continuation): stop below OR boundary (for long) - buffer;
  TP1 1.0R, TP2 2.25R; BE arm 1.5R.
- Branch C (breakout): stop at OR-range midpoint or ATR multiple; TP1
  1.0R, TP2 2.25R; BE arm 1.5R.
- Shared: stop-band guard reject if stop < 5 pts or > 40 pts; max hold
  30-40 minutes per branch; EOD flat 15:58:30 ET.

## 5. Position sizing
Fixed dollar risk, $300 per trade: contracts = floor(300 / (stop_points
x $2)), capped at 12 MNQ contracts. Skip if contracts < 1. Daily loss
limit: 2 realized losing trades per RTH date (across all branches).

## 6. Required indicators / data
Opening-range high/low (09:30-10:00 ET), ATR(14) on 2-minute bars,
EMA(8) on 2-minute bars (optional trend context for continuation
branch). 2-minute bars derived from MNQ 1-second OHLCV. No footprint,
delta, or order-flow dependency — fully OHLCV-testable.

## 7. Differentiation (vs already-tested strategies)
This is structurally novel for the project: it is the first candidate
built as a composition node with per-branch attribution rather than a
single-mechanism standalone. Unlike opening_range_width_switch (which
switched modes by OR width and Apex-failed on variance), this branches
by level-interaction RESPONSE and tags each branch for attribution.
Unlike the three separately-authored OR candidates, it tests them as one
instrumented tree so per-branch edge is visible rather than scattered
across three independent tests.

The key deliverable is NOT a single PF number. It is the per-branch
attribution table: which of {sweep-reversal, break-hold continuation,
expansion breakout} actually carries edge on MNQ. Given the session
finding that fading has lost repeatedly, the prior is that the
continuation branch outperforms the reversal branch — but the
instrumentation tests this rather than assuming it.

## 8. Required research before spec drafting
- R4 probe MUST report PER-BRANCH signal frequency, not just aggregate.
  Key question: do all three branches fire enough to matter, or does one
  branch dominate the count while another barely fires? A lopsided tree
  (e.g., 50 reversal signals, 2 expansion signals) is really a
  single-branch strategy with vestigial branches.
- Pre-commit all branch thresholds (pullback proximity 0.25 x ATR,
  expansion multiple 1.5x ATR, reclaim/hold bar logic) before testing.
- Pre-commit precedence rules for the rare simultaneous-qualification
  edge cases.
- Verify the one-trade-per-day cap leaves enough trades per branch for
  meaningful per-branch n across 12-start multistart.
- Decide per-branch stop references at spec stage.
- Honest concern: the reversal branch is mean-reversion class, which has
  failed repeatedly. The attribution will likely show it dragging. The
  value of including it is to CONFIRM that with data and to define the
  node's useful sub-signals, not to assume the reversal works.

## 9. Source / references
Strategic synthesis from 2026-05-20 session. The decision-tree structure
was identified by cross-analysis of six independently-authored
objective-level candidates (three by Strategic Claude, three by Codex
GPT-5.5), which converged on opening-range level-plus-confirmation
mechanics. The composition-node framing (one level, branched output,
per-branch attribution) embodies the marginal-registry composition
vision documented in _MARGINAL_STRATEGIES_REGISTRY.md.

## 10. Informational multistart result
The operator explicitly bypassed the R4/v1.4 gate and requested direct
FINAL-spec implementation plus multistart on 2026-05-21. The result was
informational only and does not consume OOS.

Across 12 monthly starts (2024-08-01 through 2025-07-01, 42 trading-day
cap per start), the response tree produced 185 trades, aggregate P&L
-$11,744.60, aggregate PF 0.62, 40.5% win rate, 5/12 failed account
states, and 2/12 profitable starts. The strategy does not graduate.

Per-branch attribution:

| Branch | Trades | P&L | PF |
|---|---:|---:|---:|
| `sweep_reversal` | 122 | -$6,809.10 | 0.67 |
| `break_hold_continuation` | 46 | -$3,960.50 | 0.48 |
| `expansion_breakout` | 17 | -$975.00 | 0.65 |

The attribution table shows that no full branch carried edge. A tiny
sub-cell (`expansion_breakout` short, n=11, P&L +$679.90, PF 1.59)
was positive, but it is too small and too post-hoc to promote. At most,
it is a weak lead for future ideation, not registry evidence.

Report:
`C:\VMShare\NT8lab\nb_lib_opening_range_response_tree_multistart_informational_report.md`

## 11. Status history
| Date | Status | Notes |
|------|--------|-------|
| 2026-05-20 | untested-ideation | Authored as the first composition-node candidate: one opening-range level with three tagged branches (sweep-reversal / break-hold continuation / expansion breakout). Per-branch attribution is the key deliverable. Pending R4 probe with PER-BRANCH frequency reporting before any FINAL spec. Embodies the marginal-registry composition vision. |
| 2026-05-21 | tested-informational-rejected | Operator bypassed R4/v1.4 gate and requested direct FINAL spec, implementation, and 12-start multistart. Informational result: n=185, P&L -$11,744.60, PF 0.62, win rate 40.5%, 5/12 failed starts, 0/12 pass rate. All three main branches were negative. OOS not consumed. |
