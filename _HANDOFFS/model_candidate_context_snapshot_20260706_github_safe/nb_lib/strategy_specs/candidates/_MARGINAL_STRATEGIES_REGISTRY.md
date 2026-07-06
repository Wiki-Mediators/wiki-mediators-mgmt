---
name: "Marginal Strategies Registry"
tagline: "Foundational registry for tiny-edge strategies that may later become inputs to a probabilistic composition system."
status: "foundational-draft"
created: 2026-05-17
updated: 2026-05-25
source: "Operator direction 2026-05-17 after tight_opening_window_breakout_long informational multistart produced tiny positive aggregate but failed standalone thresholds."

artifact_type: "methodology_registry"
scope: "marginal-edge preservation and future composition data foundation"
implementation: null
canonical_spec: null

tags:
  - methodology
  - registry
  - marginal-edge
  - ensemble-foundation
  - probabilistic-graph
  - not-a-strategy
---

# Marginal Strategies Registry

**Version:** v1 preliminary  
**Created:** 2026-05-17  
**Status:** foundational draft; long-term composition vision deferred  

This document is not a strategy candidate and not a shortcut around the
normal methodology pipeline. It is a registry for preserving strategies
that show genuine but insufficient standalone edge, so they can later be
studied as components in a multi-signal system.

---

## 1. Why This Registry Exists

The project's stated goal is finding strategies that can survive Apex
50K EOD constraints on MNQ. The empirical pattern from tested candidates
is that finding a single standalone strategy with deployable strength
may be very hard. A true standalone strategy needs more than a positive
backtest: it needs enough trades, realistic friction survival, multistart
robustness, OOS eligibility, Apex drawdown survivability, and a clean
methodology trail.

What may be more achievable is a set of tiny edges.

Tiny edges are strategies that produce weak but positive expectancy,
for example PF 1.05 to 1.50, positive aggregate P&L, or useful regime
specific behavior, while still failing standalone deployment standards.
Individually, these are not deployable systems. They may be too sparse,
too path-dependent, too regime-bound, or too weak after friction to trade
alone.

But tiny edges are not automatically noise. A strategy with PF 1.08 over
dozens of realistic-friction trades may be doing something slightly right.
The edge is simply not large enough, robust enough, or frequent enough
to justify standalone use.

The hypothesis behind this registry:

**Multiple tiny edges, combined intelligently, may produce a deployable
system that no single strategy can.**

The registry exists so these weak-but-informative results are not lost
when a candidate is correctly rejected as a standalone strategy.

---

## 2. Long-Term Composition Vision

The long-term target is a hybrid flowable system. The working idea is
not a single strategy with one entry rule. It is a system that treats
multiple marginal strategies as inputs.

The future system may include:

- Multiple marginal strategies, each contributing signal evidence.
- Conditional weighting based on market regime.
- Weighting based on recent behavior, correlation, time-of-day, and
  signal-family overlap.
- Probability-based position commitment, where confidence comes from
  the network state rather than from any one strategy firing.

The structure is not quite a tree. A tree is too hierarchical: one root,
fixed branches, and one route downward. The desired structure is closer
to a probabilistic graph or node network.

In this framing:

- Nodes are marginal-edge strategies or signal components.
- Edges between nodes represent conditional relationships.
- Edge weights represent the confidence adjustment when two or more
  signals occur together.
- Market regimes may activate or deactivate sub-networks.
- Some nodes may reinforce each other; others may cancel each other.

Useful analogies:

- Bayesian belief networks, where nodes have conditional probability
  relationships.
- Ensemble signal voting, where no individual signal is sufficient but
  agreement among signals matters.
- Regime-conditional routing, where different strategy families are
  emphasized under different market states.

These analogies are conceptual anchors, not implementation commitments.
No composition graph is being implemented in this v1 registry.

---

## 3. What This Registry Currently Is

This registry is the data foundation for future composition work.

It records strategies that may be useful as weak evidence sources:

- Their signal family.
- Their performance signature.
- Their failure mode.
- Their regime / time-of-day context.
- Their possible correlation or complementarity with other strategies.
- Their methodology status and limitations.

This registry is not currently:

- A deployable strategy list.
- A graduation shortcut.
- An ensemble implementation.
- A live trading instruction set.
- A way to consume OOS after a bypass result.

The normal candidate pipeline remains active:

```text
candidate wiki -> Phase 0 -> Phase 1 -> FINAL spec -> implementation -> multistart/test -> reject, deploy, or registry
```

The registry catches strategies that produce something useful but not
enough for standalone deployment.

---

## 4. Current Focus

Current project focus remains individual strategy development through
the wiki methodology pipeline.

This registry is parallel infrastructure. It should be updated after
strategy tests when a candidate is not deployable but leaves behind
some potentially useful marginal signal.

When the registry has enough diverse entries, probably 5 to 10 with
adequate data quality, a separate methodology iteration can define the
composition framework.

Until then, this document is a structured memory bank.

---

## 5. Qualification Categories

Registry membership is not the same as passing.

Each entry must be assigned one of these categories.

| Category | Meaning |
|---|---|
| `marginal-positive` | Positive expectancy, adequate trade count, below standalone deployability threshold |
| `regime-positive` | Weak or negative overall, but positive in a specific pre-declared or clearly identifiable regime |
| `component-useful` | Standalone result weak, but a mechanism or signal component appears useful for composition |
| `provisional-seed` | Interesting but below meaningful-count or methodology-quality floor; preserved only as a lead |
| `rejected-not-registered` | No credible useful component; do not preserve beyond normal tested-rejected notes |

An entry should not be added as `marginal-positive` unless it has enough
trade count to make the result meaningful. Thin samples can be logged as
`provisional-seed`, not as evidence.

---

## 6. Preliminary Qualification Rules

These are v1 draft rules. They will be tightened in a later housekeeping
iteration.

To qualify as `marginal-positive`, a strategy should generally have:

- Positive aggregate P&L after BAND_B or equivalent realistic friction.
- PF between 1.05 and 1.50.
- Meaningful trade count, normally `n >= 80`.
- No OOS leak.
- No account-failed continuation.
- Clear signal family and failure mode.
- A reason it might complement other strategies rather than merely
  duplicate the same failure surface.

To qualify as `provisional-seed`, a strategy may have:

- Positive aggregate P&L but trade count below the meaningful floor.
- Weak PF around 1.00 to 1.10.
- A known methodology limitation, such as Phase 0 bypass.
- A useful observed behavior worth preserving for future review.

Provisional seeds should not be used for composition until revisited.

---

## 7. Entry Template

Use this format for each registry row.

```markdown
### Strategy Name

- Registry category:
- Candidate file:
- Canonical spec:
- Implementation:
- Test report:
- Signal family:
- Direction:
- Trade count:
- PF:
- Aggregate P&L:
- Multistart survival:
- Account failure count:
- Failure mode:
- Possible composition value:
- Correlation/complementarity candidates:
- Methodology caveats:
- Current action:
```

---

## 8. Registry Entries

### Tight Opening Window Breakout Long

- Registry category: `provisional-seed`
- Candidate file: [tight_opening_window_breakout_long.md](tight_opening_window_breakout_long.md)
- Canonical spec: [tight_opening_window_breakout_long_spec_FINAL.md](../canonical/tight_opening_window_breakout_long_spec_FINAL.md)
- Implementation: [tight_opening_window_breakout_long_canonical_alpha.py](../../scripts/tight_opening_window_breakout_long_canonical_alpha.py)
- Test report: [nb_lib_tight_opening_window_breakout_long_multistart_informational_report.md](../../../nb_lib_tight_opening_window_breakout_long_multistart_informational_report.md)
- Signal family: tight-state opening-window continuation / breakout
- Direction: long only
- Trade count: 76 aggregate trades across 12 monthly starts
- PF: 1.08 aggregate
- Aggregate P&L: +$799.50
- Multistart survival: 12/12 starts ended active
- Account failure count: 0/12
- Failure mode: below pre-committed `n >= 80` meaningful-count floor; weak PF; Phase 0 bypass; not OOS eligible
- Possible composition value: may act as a weak bullish continuation evidence node in opening-window tight-state contexts
- Correlation/complementarity candidates:
  - Paired short-side tight opening-window candidate, if ever tested
  - Wide-state reversal family, if tested, as opposing regime context
  - VWAP / opening-range state filters, if future composition analyzes overlap
- Methodology caveats:
  - Phase 0 was bypassed.
  - Result is informational only.
  - Candidate was correctly marked `tested-informational-rejected`.
  - This is not a standalone strategy and not eligible for OOS consumption.
- Current action: preserve as provisional seed only; do not promote or combine until registry criteria and composition framework are formally defined.

### Prior Day Value Area Rejection

- Registry category: `provisional-seed`
- Candidate file: [prior_day_value_area_rejection.md](prior_day_value_area_rejection.md)
- Canonical spec: [prior_day_value_area_rejection_spec_FINAL.md](../canonical/prior_day_value_area_rejection_spec_FINAL.md)
- Implementation: [prior_day_value_area_rejection_canonical_alpha.py](../../scripts/prior_day_value_area_rejection_canonical_alpha.py)
- Test report: [nb_lib_prior_day_value_area_rejection_implementation_report.md](../../../nb_lib_prior_day_value_area_rejection_implementation_report.md)
- Signal family: prior-day auction-structure mean reversion / value-area rejection
- Direction: two-sided; realized 5 longs / 9 shorts
- Trade count: 14 in-sample trades
- PF: 1.17
- Aggregate P&L: +$70.20
- Multistart survival: 12/12 fixed-end monthly starts ended active
- Account failure count: 0/12 fixed-end monthly starts
- Multistart signature: monthly starts 2024-08 through 2025-07, fixed end 2026-01-31; 6/12 starts positive; aggregate across starts -$411.80; mean PF 0.9192; median PF 0.9027
- Failure mode: single-run weak positive does not survive monthly-start characterization; below pre-committed `n >= 80` meaningful-count floor and PF below `1.50` edge threshold; 89.8% attrition from structural preflight signals to actual tradeable fills
- Possible composition value: may act as a weak auction-structure rejection evidence node, especially as a non-continuation complement to opening breakout and trend-following families
- Correlation/complementarity candidates:
  - VWAP / anchored VWAP mean-reversion nodes, if future tests separate auction-value rejection from intraday VWAP stretch
  - Opening-range rejection nodes, because both express failed acceptance away from a known reference area
  - Tight-state opening-window continuation nodes, as a potentially opposing regime signal
- Methodology caveats:
  - Methodology-clean trail: template v2 Phase 0 passed, Phase 1 preflight passed, FINAL spec drafted before implementation.
  - The single-run result is statistically thin (`n=14`) and cannot be treated as evidence of standalone edge.
  - Monthly-start fixed-end characterization weakens the edge: the starts are Apex-safe but aggregate negative.
  - Preflight over-counted tradeable opportunities because fill-time drift was not sufficiently modeled before implementation.
  - Candidate was correctly marked `tested-rejected`; no OOS consumption.
- Current action: preserve as low-priority provisional seed and as a methodology lesson about fill-time attrition; do not promote or combine until a future composition framework defines how low-count / monthly-negative nodes are handled.

### Opening Range Width Switch

- Registry category: `component-useful`
- Candidate file: [opening_range_width_switch.md](opening_range_width_switch.md)
- Canonical spec: [opening_range_width_switch_spec_FINAL.md](../canonical/opening_range_width_switch_spec_FINAL.md)
- Implementation: [opening_range_width_switch_canonical_alpha.py](../../scripts/opening_range_width_switch_canonical_alpha.py)
- Test report: [nb_lib_opening_range_width_switch_implementation_report.md](../../../nb_lib_opening_range_width_switch_implementation_report.md)
- Multistart report: [nb_lib_marginal_registry_multistart_report.md](../../../nb_lib_marginal_registry_multistart_report.md)
- Signal family: opening-range failed-break rejection / volatility-normalized mean reversion
- Direction: two-sided
- Trade count: 62 in original fixed-end run; 271 aggregate trades across 12 fixed-length monthly starts
- PF: 1.07 original fixed-end run; mean PF 1.2560 and median PF 1.3111 across 42-trading-day monthly starts
- Aggregate P&L: +$603.90 original fixed-end run; +$6,482.80 summed across 12 fixed-length monthly starts
- Multistart survival: 11/12 fixed-length monthly starts ended active
- Account failure count: 1/12 fixed-length monthly starts
- Multistart signature: monthly starts 2024-08 through 2025-07, 42 trading days each; 8/12 starts positive; mean start P&L +$540.23; median start P&L +$923.40; worst start -$2,000.50
- Failure mode: standalone fixed-end run breached Apex trailing drawdown despite positive total P&L; multistart shows path/variance sensitivity rather than uniform no-edge
- Possible composition value: may act as an opening-range rejection evidence node in a future graph, especially if another node can suppress high-variance / unfavorable path regimes
- Correlation/complementarity candidates:
  - Prior-day value-area rejection, as another auction/reference-level rejection node with much lower variance
  - VWAP / anchored VWAP reference-level mean-reversion nodes
  - Tight opening-window continuation nodes, as potentially opposing opening-flow context
- Methodology caveats:
  - The candidate remains rejected as a standalone strategy because it has a documented Apex failure path.
  - It is not `marginal-positive`: the registry's no-account-failed requirement is not met.
  - The current multistart run is in-sample characterization only; no OOS consumption.
  - Regime attribution for the bad windows is not yet known.
- Current action: preserve as component-useful for future composition research; next useful work would be regime/path attribution, not parameter tuning.

### Objective Level Liquidity Sweep Reversal Family - Opening Range Branch

- Registry category: `provisional-seed`
- Candidate file: [objective_level_liquidity_sweep_reversal_family.md](objective_level_liquidity_sweep_reversal_family.md)
- Canonical spec: [objective_level_liquidity_sweep_reversal_family_spec_FINAL.md](../canonical/objective_level_liquidity_sweep_reversal_family_spec_FINAL.md)
- Implementation: [objective_level_liquidity_sweep_reversal_family_canonical_alpha.py](../../scripts/objective_level_liquidity_sweep_reversal_family_canonical_alpha.py)
- Test report: [nb_lib_objective_level_liquidity_sweep_reversal_family_multistart_informational_report.md](../../../nb_lib_objective_level_liquidity_sweep_reversal_family_multistart_informational_report.md)
- Signal family: opening-range liquidity sweep / reclaim reversal, isolated from a broader objective-level sweep family
- Direction: branch aggregate two-sided, but signal concentrated in the long side; opening-range long produced the meaningful positive observation
- Trade count: 32 opening-range branch trades across 12 monthly starts; positive long-side observation is only 14 trades
- PF: 1.40 for the opening-range branch; 2.19 for opening-range long; 0.99 for opening-range short
- Aggregate P&L: +$2,069.30 for the opening-range branch; +$2,108.10 opening-range long; -$38.80 opening-range short
- Multistart survival: parent family 3/12 starts ended active; branch-only Apex survival was not separately tested
- Account failure count: parent family failed 9/12 starts; branch-only failure count not established
- Failure mode: parent family is tested-informational-rejected with aggregate -$11,555.20, PF 0.75, and 9/12 failed starts; the `ROUND_VWAP` branch drove losses and is closed, while `PDH_PDL` was negative and is closed as a fade
- Possible composition value: faint evidence that opening-range sweep/reclaim behavior, especially long-side reclaim, may be a weak opening-session reversal node if separated from dead level families and tested with enough count
- Correlation/complementarity candidates:
  - `opening_range_width_switch`, as an existing opening-range rejection component-useful entry
  - Tight opening-window continuation nodes, as a potentially opposing opening-flow signal
  - Future opening-range response-tree / branch-attribution candidates, if they isolate opening-range branch behavior without bundling dead level families
- Methodology caveats:
  - This is a branch observation from a rejected parent family, not a standalone strategy pass.
  - The apparent edge is too thin and too sub-divided: only 32 branch trades, with the useful signal effectively 14 long trades.
  - Branch-only Apex survivability is unknown because the parent family carried `ROUND_VWAP` and `PDH_PDL` losses.
  - Do not promote to `component-useful` or `marginal-positive` without a clean branch-specific test and higher trade count.
  - OOS remains sealed.
- Current action: preserve as a faint provisional seed only; closed-book negative findings are `ROUND_VWAP` sweep-reversal and `PDH_PDL` sweep-reversal.

---

## 9. Future Housekeeping Needed

This v1 registry is intentionally preliminary. Later cleanup should:

1. Define hard thresholds for `marginal-positive`, `regime-positive`,
   and `component-useful`.
2. Decide whether bypass results can ever enter above `provisional-seed`.
3. Add correlation fields once multiple marginal candidates exist.
4. Define required regime descriptors.
5. Define whether registry entries need per-month or per-time-window
   performance signatures.
6. Decide how to represent graph/node relationships in markdown before
   any code implementation.
7. Decide whether registry data should eventually be mirrored to JSON
   for machine-readable composition analysis.

---

## 10. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-17 | `foundational-draft` | Registry created from operator direction after 12-start informational multistart on `tight_opening_window_breakout_long`. Long-term vision documented as probabilistic graph / ensemble foundation. First entry logged as provisional seed, not a passing strategy. |
| 2026-05-17 | `backfilled-project-history` | Project history backfill completed. Added `prior_day_value_area_rejection` as a second provisional seed. Rejected-not-registered candidates documented separately in `nb_lib_marginal_registry_backfill_report.md`; no marginal-positive, regime-positive, or component-useful entries were added. |
| 2026-05-18 | `multistart-signatures-added` | Monthly-start characterization completed for `prior_day_value_area_rejection` and `opening_range_width_switch` without touching OOS. `prior_day_value_area_rejection` remains provisional-seed but lower priority after fixed-end monthly starts aggregate negative. `opening_range_width_switch` added as `component-useful`: 8/12 positive 42-trading-day starts, aggregate +$6,482.80, mean PF 1.2560, but 1/12 starts failed Apex, so it is not marginal-positive. |
| 2026-05-25 | `opening-range-sweep-branch-seed-added` | Added the `OPENING_RANGE` branch observation from `objective_level_liquidity_sweep_reversal_family` as a faint `provisional-seed` only. Parent family remains tested-informational-rejected; `ROUND_VWAP` and `PDH_PDL` sweep-reversal findings are treated as closed negative evidence. |
| 2026-05-25 | `orws-v2-base-hit-retraction` | Pre-OOS verification found the earlier `opening_range_width_switch_v2_base_hit` pass was contaminated by left-label early-fill lookahead. After timing fix, corrected multistart failed: 329 trades, -$1,307.70, PF 0.95, 5/12 profitable starts, 0/12 failed starts. The candidate was removed from registry membership and marked tested-rejected; OOS remains sealed. |
