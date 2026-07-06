---
title: "Newsroom Wiki — Architecture Candidate"
status: architecture-candidate-booked-trigger-not-met
created: 2026-07-06
source: >
  Operator direction 2026-07-06: treat wiki architectures as candidates the
  way we treat strategies. Derived by analogizing real-world information
  roles (journalist sourcing a story; a history professor synthesizing from
  cited reporting — the "she's not saying I know this, cuz she doesn't"
  discipline) onto the existing four-layer architecture.
artifact_type: architecture_candidate
not_a_replacement: true
related:
  - _FRAMEWORK/LAYER_ARCHITECTURE.md
  - _FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md
  - _FRAMEWORK/wiki_architecture_current_future_visual_note_20260628.md
  - _FRAMEWORK/PATTERNS.md
intake_note: >
  Agent: place this file where architecture/framework candidates belong per
  current vault convention (likely under _FRAMEWORK/). If no candidates
  convention exists for architecture, place beside LAYER_ARCHITECTURE.md and
  add a one-line pointer in the derived-layer roadmap's deferred section so
  the trigger is discoverable. Do not build anything from this file.
---

# Newsroom Wiki — Architecture Candidate

## 0. What this is and is not

An **architecture candidate**, held to the same discipline as a strategy
candidate: a thesis, a mechanism, a screen it must pass, named failure
modes, and a trigger before any build. It is NOT a replacement
architecture and NOT a build authorization. The operator's stated path is:
book now; later either alter the current infrastructure or mirror it as a
parallel candidate vault and continue forward.

## 1. Thesis

```text
The current architecture has flat trust: a note is canonical or it is
not, and all judgment about external sources lives in prose inside
intake notes where no tool can compute over it. Real-world information
professionals do not work this way. A working journalist runs a curated
graph of SCOPED, EARNED, DECAYING source trust; a disciplined synthesizer
(the history-professor model) never asserts beyond sources and adds value
only through arrangement. The newsroom candidate makes source trust a
first-class, computed, per-domain property — without adding any layer
that can drift.
```

One-line version: **newsroom = current spine + a derived trust ledger +
provenance made structural in Layer 1.**

## 2. The real-world roles and their mapping

| Newsroom role | Real-world behavior | Maps to | New? |
|---|---|---|---|
| Journalist | Curates dependable sources per domain (Ukraine → O'Brien, economy → Krugman); trust inherited from what other trusted nodes rely on; trust decays ("I don't trust MSM as much as I used to"); reads curated layer before institutional layer | Layer 1 writer, with provenance structural | Tightened, not new |
| Archive | Keeps everything filed, verbatim, retrievable | Layer 2 dumb logger | Unchanged |
| Source desk | Tracks who has earned what trust, in which domain, as of when | **New Layer 3 deriver + trust ledger** | **The only new machinery** |
| Professor (synthesizer) | "Here's what the WSJ reported, here's what the Times reported" — never asserts own knowledge of events; value = selection, arrangement, context | Layer 4 cold distiller (two-stage citation verification) | Near-verbatim match; validation, not addition |
| Editor / fact-checker | Adversarial challenge of claims before publication | **Decomposed** (see §4) — dumb existence checks + stateless cold review | Already exists disassembled; candidate names it so nobody builds the drifting version |

Key observation: three of five roles already exist under other names. The
professor-model is external validation that Layer 4's contract matches how
a disciplined real-world synthesizer actually operates. The candidate's
entire novel content is the source desk.

## 3. The trust ledger (the one new piece)

### 3.1 Design contract

- **Derived, never hand-maintained.** The ledger is a `_DERIVED/` view,
  regenerated from Git-committed source on every run, exactly like the
  vault index. If it breaks, delete and rebuild. Nothing kept = nothing
  to drift.
- **Computed from countable events already in the vault/Git history:**
  - citation frequency: how often a source is cited by banked notes;
  - confirmation events: a source's claim later verified by project
    measurement (e.g., a transcript concept that survived its screen);
  - contradiction/retraction events: a source's claim later refuted or
    retracted (e.g., a claimed edge that failed the mechanism screen);
  - recency: when the source last earned anything.
- **Scoped per domain.** Trust is never global. A source can be
  `earned` on execution-discipline content and `unknown` on
  MNQ-specific claims. Scope tags come from the intake note's existing
  frontmatter, not from new hand-labeling.
- **Decaying.** Scores decay toward `unknown` with staleness. Decay is a
  pure function of dates already in Git; no judgment call.
- **Flags, never gates (v1).** The ledger informs agents and readers; it
  does not automatically block or admit content. Any future gating use is
  a separate, pre-committed decision.

### 3.2 What it explicitly is not

- Not an opinion store. No agent ever writes "I now trust X less" into
  the ledger; agents write ordinary source notes (intakes, screen
  verdicts), and the deriver counts them.
- Not a reputation system for internal notes. Internal canon keeps the
  existing flat model (canonical or not). The ledger covers EXTERNAL
  sources only: transcripts, videos, research notes, papers, people.
- Not an LLM judgment pass. v1 scoring is arithmetic over counted
  events. If arithmetic proves too crude, that finding is banked before
  anything smarter is proposed.

## 4. The editor question (drift analysis — the operator's concern)

The operator's instinct is correct and is adopted as a design rule:

```text
An editor implemented as a persistent, opinion-holding layer is
hand-maintained judgment — the exact drift disease this architecture
exists to prevent. Do not build one.
```

The newsroom candidate therefore contains NO new editor layer. The
editorial function is decomposed into the two drift-proof forms the
current system already uses:

1. **Mechanical verification → dumb tools.** Link/reference existence
   checks, citation existence + support checks (the Layer 4 two-stage
   contract). These cannot drift; they recompute from source.
2. **Judgment → stateless cold review.** A fresh agent with no history is
   pointed at material, renders a verdict, and is discarded. The verdict
   is banked as an ordinary source note that everything else (including
   the trust ledger) can count. Nothing persists except the artifact.

The candidate's contribution on this point is purely nominal: naming the
decomposition so a future session never "helpfully" builds the persistent
editor by accident.

## 5. Layer 1 change: provenance made structural

Current state: source-trust judgment lives in prose ("treat as process
material, not evidence") inside intake notes. Human-readable, tool-opaque.

Candidate change: intake notes carry a small structured block —
source identifier, domain scope tags, claim type (evidence / process /
seed) — so the trust deriver can count without parsing prose. This is a
writer-contract tightening of the same kind as the existing what/why/date
conventions, not a new layer. Cost: a few frontmatter lines per intake.

## 6. The screen (must pass before any build)

Same discipline as a strategy candidate. The screen question:

```text
Does the structure pay for its maintenance cost on the substrate that
actually exists — or is it taxonomy finer than the substrate supports?
```

Concrete screen, runnable cheaply when triggered:

1. Count distinct external sources currently in the vault with at least
   one banked intake note. (As of 2026-07-06 the estimate is ~6: two
   transcripts, the compass research notes, one video, assorted papers.)
2. Count trust-relevant events per source (citations, confirmations,
   contradictions) derivable from existing notes WITHOUT new labeling.
3. Verdict rule, pre-committed:
   - fewer than ~15 sources OR median <3 events/source → **DO-NOT-BUILD
     YET** (ledger would be a table of unknowns; re-screen at next
     trigger check);
   - thresholds met → build the v1 deriver as a standard Layer 3 dumb
     tool (flags/computes, never interprets, regenerates from source).

## 7. Failure modes (named up front)

- **Premature taxonomy.** Building the ledger over ~6 sources — the
  knowledge-organization analog of overfitting the vault already banked
  a warning about. Mitigated by the screen threshold.
- **Score theater.** Numbers that look authoritative but encode ~no
  events. Mitigated by printing n (event count) beside every score,
  same rule as the regime panel.
- **Scope creep into internal canon.** The ledger quietly becoming a
  reputation system for the project's own notes. Forbidden in §3.2;
  internal trust stays flat.
- **Gate creep.** Flags silently becoming admission gates without a
  pre-committed decision. Forbidden in §3.1 v1 contract.
- **The persistent editor.** Rebuilt by a helpful future session.
  Forbidden in §4; this file is the record of why.

## 8. Trigger

Booked, not built. Re-run the §6 screen when ANY of:

1. External-source intake volume roughly triples from today (≈15+
   distinct sources with banked notes); or
2. A concrete retrieval failure occurs that scoped trust would have
   prevented (e.g., an agent treats a previously-refuted external claim
   as live evidence because the refutation lived in prose it did not
   read); or
3. A second project/vault adopts this infrastructure and imports
   external sources at volume (the reusable-system goal), where flat
   trust demonstrably does not scale.

Trigger type 2 is the strongest justification: it is a measured failure,
which is this project's standard for building anything.

## 9. Relationship to current infrastructure

The candidate deepens the same spine (write → record → derive →
distill); it does not fork it. If built:

- Layers 1/2/4 and the Git substrate are unchanged except the §5
  frontmatter tightening.
- The trust deriver is one more standard Layer 3 dumb tool beside the
  vault index and link checker, listed on the derived-layer roadmap.
- The operator's "alter or mirror" decision (change this vault vs. stand
  up a parallel candidate vault) is deferred to build time and belongs
  to the operator.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-07-06 | architecture-candidate-booked-trigger-not-met | Created from operator direction: analogize real-world information roles (journalist / professor / editor) to wiki architecture and book as a candidate. Novel content = derived scoped-decaying trust ledger over external sources + structural provenance in Layer 1. Editor explicitly NOT added as a layer (drift analysis §4). Screen and triggers pre-committed; current source volume (~6) is below the build threshold. |
