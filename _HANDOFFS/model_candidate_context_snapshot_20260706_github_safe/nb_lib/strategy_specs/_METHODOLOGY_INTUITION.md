---
name: "Methodology Intuition"
tagline: "The connective tissue behind the gates, registry, composition nodes, and repeated strategy failures."
status: "living-reference"
created: 2026-05-21
updated: 2026-06-21
source: "Session synthesis after repeated MNQ strategy failures, marginal-registry creation, v1.3/v1.4 methodology gates, BVC-proxy rejection, opening-range response-tree rejection, and composition-node category creation."
artifact_type: "methodology_intuition"
scope: "why the project methodology exists; how future agents should interpret artifacts"
tags:
  - methodology
  - intuition
  - composition
  - marginal-registry
  - regime-nodes
  - anti-overfit
  - not-a-strategy
  - process-discipline
  - operator-routine
---

# Methodology Intuition

This document captures the layer above the formal methodology documents.
It is not another gate, not a strategy spec, and not a replacement for
the canonical methodology reference. It records the mental model that
emerged from the project's repeated failures and partial successes: why
the gates exist, what the failures taught, and how future agents should
avoid re-learning the same lessons at high cost.

The short version:

The project is no longer simply searching for "the one profitable MNQ
strategy." It is building a disciplined research system that can:

1. Reject bad standalone strategies quickly.
2. Preserve tiny but genuine signals without pretending they passed.
3. Separate entry strategies from conditioning layers.
4. Eventually compose weak evidence sources into a probabilistic system,
   if the data justifies that architecture.

The durable asset is the methodology. Strategies come and go.

---

## 1. What The Project Is Really Testing

The original practical goal remains: find MNQ/NQ trading systems that
can survive Apex 50K EOD constraints under realistic friction. But the
empirical pattern has changed the research framing.

Standalone deployable edge is hard. Many entry ideas that sound
plausible fail under the same recurring pressures:

- The signal arrives after much of the move has already happened.
- The stop geometry is incompatible with Apex trailing drawdown.
- The strategy clusters losses early in a window.
- The mechanism is sparse after fill-time guards are applied.
- The strategy is directionally asymmetric in a way that was not
  pre-declared.
- The edge is concentrated in a small calendar slice.
- The strategy works in prose but not after 1-second fill mechanics,
  slippage, commission, and compliance state are modeled.

This does not mean every idea is worthless. It means the project needs
to distinguish:

- **Deployable strategy**: robust enough to trade standalone.
- **Marginal signal**: weak but possibly real evidence.
- **Component**: a useful mechanism inside a failed strategy.
- **Conditioning node**: a non-entry layer that may route, gate, or size
  other strategies.
- **Rejected noise**: no credible useful component.

Confusing these categories causes methodology drift. A rejected strategy
should not be rebranded as promising just because one sub-cell was green.
A marginal strategy should not be discarded as if it taught nothing. A
regime filter should not be forced through an entry-strategy pipeline.

---

## 2. The Main Lessons Paid For By Failures

### 2.1 Single-strategy PF 1.50 may be rare here

The project has repeatedly tested plausible intraday MNQ ideas and found
that clean standalone edge is uncommon. This does not mean the PF 1.50
standard is wrong as a deployability threshold. It means many results
should be interpreted as data for composition, not as near-misses that
deserve threshold relaxation.

The correct response to PF 1.05-1.50 is not "lower the pass bar until it
passes." The correct response is:

- preserve it in the marginal registry if methodology-clean enough;
- document the failure mode;
- record what regime, direction, or branch seemed useful;
- avoid consuming OOS or calling it deployable.

### 2.2 Apex survival is not the same as positive expectancy

`opening_range_width_switch` is the clean lesson. It produced positive
P&L and PF above breakeven, yet failed Apex through trailing-drawdown
path geometry. That result forced the project to add the R2 variance
preflight convention.

The intuition: a high-variance strategy can make money and still be
unusable on Apex 50K EOD. The trailing floor follows peaks upward and
does not forgive subsequent drawdowns. A candidate can be edge-positive
but deployability-negative.

Future agents should not collapse these questions. Always ask:

- Is there edge?
- Is there Apex survival?
- Is the edge robust enough to deserve OOS?
- Is the failure a strategy failure, an account-geometry failure, or
  both?

### 2.3 Fill mechanics can destroy a beautiful structural signal

`prior_day_value_area_rejection` is the reference case. Structural
signals looked moderate, but only a small fraction became tradeable
after realistic fill-time geometry. The v1.1 and v1.2 R4 conventions
exist because the project learned that signal-fire geometry is not fill
geometry.

The 1-second delay matters. The price at `signal_ts` and the price at
`signal_ts + 1s` can differ enough to invalidate stops, targets, or
guard predicates. This is especially dangerous for signal-after-move
strategies where the trigger fires during fast displacement.

Future probes must model fill-time guards. If a candidate's thesis
depends on a narrow target, anchor, or stop band, check it at the fill,
not at the signal bar close.

### 2.4 Bypass tests usually confirm why the gate existed

Several tests skipped normal gates by operator choice. That is allowed
as an explicit informational bypass, but the results have repeatedly
validated the gate discipline rather than disproving it.

Examples:

- `momentum_high_water_trail_post_1030`: core mechanism did not invoke
  meaningfully.
- `wide_opening_window_reversal_family`: severe failure.
- `wide_state_bvc_proxy_divergence_reversal`: severe failure even after
  proxy divergence confirmation.
- `opening_range_failure_continuation_long`: direct test produced
  negative P&L and low PF.
- `opening_range_response_tree`: branch instrumentation was useful, but
  all full branches were negative.

The intuition: bypassing a gate may be useful to answer a burning
question quickly, but it creates methodology debt. The result must be
marked informational, cannot graduate directly, and should usually teach
why the skipped gate mattered.

### 2.5 Proxy evidence has bounded interpretation

The BVC-proxy experiment was valuable because it was honest about what
it was. BVC estimated buy/sell pressure from OHLCV; it did not measure
aggressor-side delta. The proxy result was negative, but that does not
prove real footprint delta is useless. It proves that this OHLCV-derived
proxy did not rescue the wide-state reversal mechanism.

The general rule:

- Positive proxy result: may justify acquiring better data or testing
  the true mechanism.
- Negative proxy result: ambiguous about the true mechanism, but useful
  evidence against the proxy implementation and any strategy depending
  on it as-is.

Never let a proxy result masquerade as real data.

### 2.6 Branch attribution is a methodology tool, not a rescue trick

The opening-range response tree was the first serious composition-node
style test of an entry cluster: one objective level, multiple responses,
per-branch attribution.

The result was negative:

- `sweep_reversal`: negative.
- `break_hold_continuation`: negative.
- `expansion_breakout`: negative.

One small sub-cell (`expansion_breakout` short) was positive, but with
only 11 trades. That is a lead, not evidence.

The intuition: branch attribution is valuable because it prevents a bad
aggregate from hiding a good branch, and prevents a tiny green sub-cell
from being mistaken for a strategy. It sharpens interpretation. It does
not rescue a failed family by itself.

### 2.7 Process discipline is part of the trading system

Transcript intake (2026-06-02): a "routine / mechanical trade plan"
lesson was reviewed for project relevance. The durable takeaway is not
the discretionary entry model. It is the operating-system layer around a
trading plan: pre-session preparation, execution guardrails, journaling,
and review.

This matters because the project has repeatedly learned that edge is not
only an entry predicate. Results depend on the full lifecycle:

- what is checked before a session starts;
- which calendar windows are blocked before trades are allowed;
- whether the active trade plan, entry criteria, management rules, and
  exit criteria are reviewed before execution;
- whether the operator is calm, clear, and following the plan;
- whether trades are journaled with decision context, emotions,
  violations, screenshots or notes, and outcome metrics;
- whether post-session review turns mistakes and strengths into
  measurable feedback instead of memory.

For this project, the useful translation is:

- Add process gates around research runs and live decisions, not just
  around trade entries.
- Before important runs, verify the active spec, data partition, OOS
  boundary, calendar/regime assumptions, execution model, output paths,
  and trial-budget status.
- Before any live or replayed management policy is trusted, confirm the
  management rule, allowed actions, invalidation rule, and logging
  contract.
- After a run, record whether the plan was followed, which guardrails
  fired, what was learned, and what should not be re-tested without a new
  pre-commitment.

The transcript's chart concepts (premium/discount, supply and demand
zones, liquidity sweep, market shift, point of interest) are not evidence
by themselves. They may become useful only if translated into objective
observable predicates and tested against cheap baselines under the same
partition discipline as every other candidate.

The strongest wiki addition is therefore:

```text
Process is not admin. It is part of the system boundary.
If preparation, execution state, guardrails, and review are not logged,
the project cannot tell whether a result came from edge, management
geometry, operator discretion, or methodological drift.
```

Follow-up transcript intake (2026-06-02): a "daily bias" lesson adds one
durable process rule:

```text
bias = plan + invalidation
```

For this project, that is more important than the discretionary chart
examples. A bias, diagnostic, or management recommendation is not
complete unless it states what would falsify it. "Bullish because the
market looks bullish" is not a research object. "Bullish while price
holds above X; invalidated by acceptance below X" can be logged, scored,
and replayed.

Useful translation for observer/replay work:

- Bias should be expressed as a market-state hypothesis with an
  invalidation boundary.
- Invalidation should require acceptance, not a wick-only breach, unless
  wick-only invalidation is explicitly pre-committed.
- Mid-range / equilibrium states should default to reduced risk or no
  action until a state boundary is reached.
- Bias changes only when the pre-defined invalidation condition fires,
  not after every bar.

This reinforces the observer design: every diagnosis should carry a
prediction and an invalidation condition. Without that, the label is
narrative, not evidence.

---

## 3. Why The Marginal Registry Exists

The marginal registry exists because "tested-rejected" is too blunt for
some results.

Some candidates are simply rejected-not-registered: they failed badly,
showed no useful component, or violated methodology assumptions. Others
leave behind weak evidence:

- a small positive PF but low trade count;
- a component that worked while the full strategy failed;
- a branch that may be useful if separated cleanly in a future test;
- a regime-specific behavior worth preserving.

The registry preserves these without promoting them.

This distinction matters. Without a registry, future agents either lose
weak evidence or keep trying to resurrect failed strategies. With a
registry, the project can say:

> This is not deployable, but it may be a component later.

The registry is a data foundation for possible future composition. It is
not a shadow deployment list, not a way around OOS discipline, and not a
place to launder bypass results into "almost passed" status.

The current categories should be treated seriously:

- `marginal-positive`: meaningful positive edge below standalone bar.
- `regime-positive`: weak overall, positive in a real identifiable
  regime.
- `component-useful`: standalone failed, but a mechanism may be useful.
- `provisional-seed`: interesting but too thin or methodologically
  limited.
- `rejected-not-registered`: no useful component.

When in doubt, classify conservatively.

---

## 4. Why Composition Nodes Exist

The `composition_nodes/` category is a major inflection. It names a
different kind of artifact:

- not an entry strategy;
- no stop or target;
- no standalone trade list;
- validated by overlay experiment, not by standalone P&L.

The first node, `markov_daily_regime_router`, is a daily regime filter
that emits bull/bear/sideways probabilities and long/short permissions.
Its purpose is not to trade MNQ by itself. Its purpose is to answer:

> Does higher-timeframe context improve existing intraday strategies?

This category exists because the project was trying to force every idea
into the candidate pipeline. That works for entries. It fails for
filters, routers, confidence scalers, volatility labels, and session
classifiers.

Future agents should ask of any new idea:

- Does it produce entries? Put it in `candidates/`.
- Does it condition other strategies? Put it in `composition_nodes/`.
- Does it define a reusable measurement or diagnostic convention? Put it
  in methodology docs.

The Markov node also introduces a new discipline: walk-forward
calculation. A transition matrix built from full-history labels is
lookahead-contaminated. Every decision day must use only prior data. That
rule is not optional.

---

## 5. What The Current Gates Are Really Doing

The gates are not bureaucracy. Each one corresponds to a failure mode the
project has already paid for.

### R4 signal-frequency probe

Prevents spending implementation time on predicates that barely fire or
fire too densely. v1.2 extended the sample window because 5-day probes
missed tail attrition.

Intuition: count before building. Count with fill-time geometry.

### R2 variance preflight

Prevents net-positive but Apex-incompatible candidates from reaching
full implementation unchanged.

Intuition: a strategy can make money and still fail the account path.

### v1.4 edge-stability and regime gate

Prevents promoting a candidate because one sample window had enough
signals. Requires monthly distribution and a pre-declared regime thesis.

Intuition: an edge that only appears in one slice, or has no regime where
it should work, is not ready for expensive testing.

### Multistart

Characterizes start-date dependence and Apex path sensitivity. It is not
a way to prove a failed strategy secretly passed. It is most useful when
the initial result is ambiguous or when registry characterization needs
comparable signatures.

Intuition: path matters under trailing drawdown.

---

## 6. Recurring Strategy-Class Lessons

### Continuation class

Continuation ideas often sound clean: identify the move, enter with it,
target the next leg. In practice they have repeatedly struggled with:

- late entries;
- stop clusters after failed breaks;
- loss streaks during chop;
- Apex drawdown pressure;
- sensitivity to whether the move has already exhausted.

Continuation is not closed forever, but future continuation candidates
need a sharper reason they avoid the same surface.

### Mean-reversion / fade class

Fades have been dangerous on MNQ when they fight a larger directional
move. VWAP stretch, wide-state reversal, BVC-proxy divergence, and sweep
logic all touched versions of this problem.

The lesson is not "never fade." The lesson is:

- fading without context is expensive;
- a reference level alone is not enough;
- higher-timeframe or session-state permission may be necessary;
- signal-after-move fill drift is a major hazard.

This is one reason the Markov regime node matters.

### Objective-level strategies

Opening range, prior-day value, VWAP, round numbers, and previous
high/low levels are attractive because they are mechanically definable.
But objective levels do not automatically imply edge. Many traders see
the same level; the edge is in how price responds to it, and whether the
response is early enough to trade after friction.

Per-branch attribution is useful here because one level can host multiple
response types.

### Order-flow / footprint concepts

Footprint concepts may be useful, but the current OHLCV store does not
contain real aggressor-side delta. Any order-flow proxy must be labeled
as proxy. Real footprint strategies require real data.

---

## 7. How Future Agents Should Use This Document

Before drafting or implementing another strategy, ask:

1. Is this an entry strategy, a composition node, a registry update, or a
   methodology convention?
2. Which previous failure mode does it claim to avoid?
3. Is that avoidance mechanically testable before full implementation?
4. Does it require data the project actually has?
5. Are we about to bypass a gate? If yes, is the result clearly marked
   informational and non-graduating?
6. If it fails, what would we learn beyond "another strategy failed"?

When interpreting results:

- A failed aggregate with all branches negative is a real rejection.
- A tiny positive sub-cell is a lead, not evidence.
- Positive P&L with Apex failure belongs in deployability analysis, not
  automatic rejection or automatic promotion.
- A proxy result has proxy-limited conclusions.
- A marginal result belongs in the registry only if it meets the
  registry category honestly.
- A node is validated by overlay improvement, not standalone P&L.

The project should stay creative, but creativity needs containers. The
containers are what let the project learn instead of merely iterate.

---

## 8. Current Parked Threads

### Markov daily regime router

Status: note-only composition node.

Next useful work: inspect existing classifier/router infrastructure
before building anything new. Candidate reusable files include:

- `prj_realsim_classifier.py`
- `prj_realsim_classifier_v2.py`
- `prj_realsim_classifier_battery.py`
- `prj_realsim_router_evaluator.py`
- existing `day_tags_v*.csv` outputs in `prj_realsim/`

Build only a walk-forward daily output series first. Overlay testing
comes after correctness is proven.

### Opening range response tree

Status: tested-informational-rejected.

Lesson: composition-style branch attribution was useful, but the tested
branches did not carry edge. The positive `expansion_breakout` short
sub-cell is too small to promote.

### Wide-state / BVC proxy path

Status: informational rejected.

Lesson: proxy divergence did not rescue wide-state reversal. This does
not invalidate real footprint data, but it is strong evidence against
this OHLCV proxy as a rescue path.

### Marginal registry

Status: foundational draft with provisional/component entries.

Next useful work: keep it honest. Do not inflate categories. Add entries
only when results leave behind real component value.

---

## 9. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-06-21 | living-reference | Added cross-reference to `_EXTERNAL_METHOD_REFERENCES.md`, a citation-hygiene index for Carr-Lopez de Prado optimal trading rules, Lipton-Lopez de Prado OU corridors, Kaminski-Lo stop-loss evidence, volatility-management evidence, and overfit/PBO/Deflated-Sharpe references. External citations are hypothesis context only; local `nb_lib` results and OOS discipline remain authoritative. |
| 2026-06-02 | living-reference | Added daily-bias transcript intake. Banked the useful rule as "bias = plan + invalidation"; bias labels must include falsification boundaries and acceptance criteria before they can be logged or scored. |
| 2026-06-02 | living-reference | Added transcript intake on trading routine / mechanical trade plan. Banked the useful lesson as process discipline: pre-session gates, execution-state checks, guardrails, journaling, and review are part of the system boundary; discretionary chart concepts require objective predicates before research use. |
| 2026-05-21 | living-reference | Initial intuition document authored after creation of composition nodes, Markov regime router note, BVC-proxy rejection, opening-range response-tree rejection, R2 variance convention, v1.4 gate, and marginal-registry expansion. |
