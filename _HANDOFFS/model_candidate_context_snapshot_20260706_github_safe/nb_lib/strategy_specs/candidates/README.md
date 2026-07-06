---
status: UNVERIFIED
---

# Strategy Candidates Wiki

This directory is the **strategy ideation pipeline** for nb_lib.
Every strategy idea — whether captured from a paper, a discretionary
trader, a hypothesis, or a one-off observation — gets a file here.
As the idea moves through the lifecycle (recorded → triaged →
specced → implemented → tested), its file is updated, and tested
strategies eventually mirror into `../canonical/`.

For the reasoning layer behind the gates, marginal registry, bypass
discipline, and composition-node split, read
`../_METHODOLOGY_INTUITION.md`. It explains the "why" behind the wiki
pipeline rather than another candidate template.

## Why a wiki

The project pivoted on 2026-05-12 from "build specific strategies"
to "develop a strategy ideation pipeline with nb_lib as the
validation engine." Four strategies have been built end-to-end and
all four failed Apex 50K eval. The bottleneck isn't implementation
capacity (the build cadence is fast); it's **idea quality**. A
wiki front-loads the ideation step so we can capture many ideas
cheaply, triage them, and only spend implementation cycles on
candidates that survive triage.

## Relationship to `../canonical/`

| Directory | Contents |
|---|---|
| `candidates/` (this one) | All strategy ideas — untested ideation, triage-passed, implementation-in-progress, tested |
| `../canonical/` | FINAL specs for tested strategies only |
| `../composition_nodes/` | Non-entry conditioning layers such as regime filters, direction gates, confidence scalers, and routers |

When a candidate's status reaches `tested-rejected` or
`tested-deployed`, the FINAL spec file is also created in
`../canonical/`. The candidate entry in this directory continues
to be updated with results history and cross-references the
canonical FINAL.

Composition nodes are intentionally not candidates: they do not produce
entries, stops, targets, or standalone P&L. They are validated later by
overlay experiments that ask whether the node improves an existing entry
strategy's baseline.

## Strategy lifecycle

```
[untested-ideation]
       |
       v
[untested-triage-passed]  (survives operator review of the candidate file)
       |
       v
[spec-drafted]            (FINAL spec written in ../canonical/)
       |
       v
[implementation-in-progress]
       |
       v
[tested-rejected]  OR  [tested-deployed]
```

Status taxonomy:

| Status | Meaning |
|---|---|
| `untested-ideation` | Idea recorded; not yet evaluated. Anyone can write one. |
| `untested-triage-passed` | Operator reviewed and decided the idea is worth spec-drafting. |
| `spec-drafted` | FINAL spec written in `../canonical/`. Awaiting implementation. |
| `implementation-in-progress` | Spec is being implemented in `nb_lib/scripts/`. |
| `tested-rejected` | Implemented and tested. Doesn't pass Apex 50K eval / doesn't show edge / fails OOS / etc. |
| `tested-positive-bridge` | Legacy/root-level strategy that has been ported onto the `nb_lib` surface and reproduces its prior per-trade empirical canonical; not a fresh candidate-funnel graduation. |
| `tested-deployed` | Implemented, tested, and currently in live use (live-money or paper). |

A strategy can move backward (e.g., `spec-drafted` →
`untested-triage-passed` if operator decides to defer
implementation). Status history at the bottom of each entry tracks
transitions.

## How to use the template

Copy `CANDIDATE_TEMPLATE.md` to a new file `<strategy_name>.md`.
Filename convention: lowercase + underscores, brief but descriptive
(e.g., `mean_reversion_overnight_gap.md`, not `MROG.md`). Edit the
frontmatter and body sections per the template.

Files prefixed with an underscore (e.g.,
`_EXAMPLE_atr_scaled_brackets.md`) are **examples or references**,
not active candidates. They show how the schema looks for a worked
case but won't be confused with real ideation.

## Browsing in Obsidian

To browse via Obsidian:
1. Open Obsidian.
2. Choose "Open folder as vault" and select
   `nb_lib/strategy_specs/` as the vault root.
3. Recommended plugins:
   - **Dataview** — lets you query frontmatter (e.g., "list all
     `status: untested-triage-passed` candidates" or "list all
     `tested-rejected` with `in_sample_pf < 0.5`").
   - **Templates** (core plugin) — set
     `CANDIDATE_TEMPLATE.md` as a template for fast new-candidate
     creation.

Obsidian-specific syntax (wiki-links like `[[other_file]]`) is
**avoided** in this wiki to keep entries readable as plain
markdown in any viewer. Use standard markdown links
(`[label](path)`) instead.

## Tag set (recommended controlled vocabulary)

Use frontmatter `tags:` consistently for filtering. Recommended
controlled vocabulary:

**Session / timing:**
- `rth-only`, `globex`, `eth`, `overnight`
- `intraday`, `swing-1d`, `swing-multi`
- `pre-open`, `morning`, `lunch-window`, `afternoon`, `close-window`

**Signal family:**
- `trend-continuation`, `mean-reversion`, `breakout`, `pullback`,
  `gap-fade`, `gap-continuation`
- `momentum`, `range-bound`, `multi-leg`, `multi-day`

**Execution flavor:**
- `fixed-brackets`, `atr-scaled`, `volatility-adaptive`,
  `vwap-anchored`
- `partial-tp`, `runner`, `be-stop`

**Status (also surfaces in frontmatter `status` field):**
- `tested-rejected`, `tested-deployed`, `untested`, `live-only`

**Methodology markers:**
- `lookahead-audited`, `multistart-validated`, `regime-conditional`,
  `oos-tested`

Multiple tags are encouraged; the goal is queryability.

## How to write a good candidate entry

The candidate file's purpose is to **carry the idea forward**, not
to do the implementation work. A good entry:

1. States the **thesis** in 1-2 paragraphs anyone (including a
   future you who forgot the context) can follow.
2. Lists the **mechanism** as 3-5 bullets — what edge does the
   signal capture? Why might it persist?
3. Names the **entry conditions** in plain English (not pseudocode).
4. Names the **exit logic** (stops, targets, time-based exits).
5. Captures **what's different** about this strategy vs the
   already-tested ones — every new candidate should answer "why
   isn't this just X?"
6. Lists **open research questions** that need answering before
   spec-drafting (e.g., "is ATR computed from RTH or session?",
   "what's the historical regime variance?", "which timeframe?").
7. Cites **source / references** if any.

A good entry can be triaged in 5-10 minutes. A great entry surfaces
the right open questions for the operator to answer before
investing in a FINAL spec.

## Workflow summary

1. **Have an idea** → copy CANDIDATE_TEMPLATE.md to a new file,
   fill in frontmatter + body, save in this directory with status
   `untested-ideation`.
2. **Operator review** → operator updates status to
   `untested-triage-passed` (or leaves it as ideation, or marks it
   `tested-rejected` directly if the idea is structurally similar
   to something already-failed).
3. **Spec drafting** → triaged candidates get a FINAL spec in
   `../canonical/`. Update candidate status to `spec-drafted` and
   add a `canonical_spec` link in the frontmatter.
4. **Implementation** → script lands in `nb_lib/scripts/`. Update
   candidate status to `implementation-in-progress`.
5. **Testing** → run on in-sample window. Update status to
   `tested-rejected` or `tested-deployed`. Fill in
   `test_results.*` frontmatter fields.
6. **Status history** → append a dated entry to the bottom of the
   candidate file at every status transition.

This is the entire flow. Keep it lightweight.

### Vocabulary Conventions (notes from Codex batches)

The frontmatter `tags` field, `signal_type` field, and `markets`
field all accept extensions beyond the values explicitly listed
in this README. Codex 5.5 CLI's batch-1 and batch-2 generations
introduced several extensions that are accepted as legitimate:

**Tag extensions observed:**

- `multi-timeframe` — strategies using more than one bar
  resolution
- `cross-asset` — strategies referencing non-MNQ markets
- `data-acquisition-required` — flags blocked candidates that
  need external data
- `volume-profile` — strategies requiring volume-at-price
  analysis
- `late-day`, `midday`, `macro`, `vwap-based` — time-of-day or
  edge-category descriptors

**signal_type extensions observed:**

- `breakout-failure`, `intraday-reversal`,
  `statistical-arbitrage`, `cross-asset-confirmation`,
  `volatility-expansion`, `gap-fade`, `multi-level-magnetism`
- These describe edge concepts beyond simple "trend" /
  "mean-reversion" labels.

**markets field convention:**

- For multi-instrument strategies (e.g., a strategy that
  references both MNQ and MES for a spread): use a list of
  discrete instrument symbols: `markets: ["MNQ", "MES"]` rather
  than slash notation like `"MNQ/MES"`.

Vocabulary extensions are valid as long as they:
1. Are descriptive (not jargon obscuring the strategy's nature)
2. Are not synonyms of existing tags
3. Can be reasonably queried via Dataview

The wiki is a working document; vocabulary will evolve. Periodic
review by operator to consolidate overlapping tags is reasonable
but not required between batches.

### Methodology Repertoire

A strategy-design methodology reference is at
`_METHODOLOGY_repertoire.md` (working-draft v1). Covers dynamic
adaptation levels, position sizing, stop placement, profit
targets, entry timing, regime classification, risk management,
and indicator catalog (including indicators not yet in nb_lib).
Use when designing new strategy candidates.

The current pre-spec selection gate is documented at
`../_V1_4_EDGE_STABILITY_REGIME_GATE.md`. It extends template-v2 /
R4 v1.2 with edge-stability and regime-conditional checks before a
candidate may move from wiki inventory to FINAL spec drafting.

### Data Store Reference

A data store inventory and limitations reference is at
`_METHODOLOGY_data_store.md` (working-draft v1). Documents
instrument inventory, MNQ ohlcv-1s coverage gaps (9 missing days),
loader behavior differences, and bar quality findings. Use when
designing new strategy candidates to verify data availability
before specifying.






```dataview
TABLE status, test_results.in_sample_pf, test_results.in_sample_n
FROM "candidates"
WHERE status = "tested-rejected"
SORT test_results.in_sample_pf DESC
```
