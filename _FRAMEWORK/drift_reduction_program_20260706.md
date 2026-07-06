---
title: "Drift Reduction Program — Observed Species and the Computed-Copy Rule"
status: banked-program-note
created: 2026-07-06
source: >
  Operator + management-session review 2026-07-06, grounded in drift
  instances observed in this vault (dual-update events on 2026-07-06,
  the PROBE_006 stale-number correction, cross-vault mirror staleness).
artifact_type: framework_program_note
related:
  - _FRAMEWORK/LAYER_ARCHITECTURE.md
  - _FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md
  - _FRAMEWORK/PATTERNS.md
  - AGENTS.md
intake_note: >
  Agent: this note carries THREE actions. (1) Place this file in
  _FRAMEWORK/. (2) Bank the two writer-contract rules in §3 into AGENTS.md
  (or wherever Layer 1 writer conventions are being banked), phrased
  tersely per bootstrap style — this note is the rationale, AGENTS.md
  carries only the rule. (3) Amend roadmap entry 3.2 (content-views half)
  per §4: the README-table projection is added to its job description and
  its trigger is recorded as FIRED with the two 2026-07-06 events cited.
  Do NOT build the deriver extension in this same session unless the
  operator separately says so — recording the fired trigger and building
  are different acts. No other files change.
---

# Drift Reduction Program

## 1. Organizing principle

```text
Drift cannot be prevented, only made computable. Any rule that says
"remember to also update X" is a tax on agent attention and will
eventually be missed. The move is always the same: find every place a
fact lives twice, decide which copy is the source, and make the other
copy either generated or flagged-when-stale.
```

This is the existing architecture's own logic (compute it, don't keep
it), applied systematically to the drift instances this vault has now
actually produced. Per house rules, everything here is tied to an
observed failure or observed near-miss; nothing is speculative.

## 2. Observed drift species (the evidence base)

1. **Duplicated state needing hand-sync.** 2026-07-06, twice in one
   session: the regime-attribution-panel completion required updating
   both the spec frontmatter AND the composition-nodes README table row;
   the newsroom candidate required both its own status AND a roadmap
   pointer. Both were done correctly — by luck-plus-discipline, which is
   not a mechanism. Every duplicated fact is a drift seed.
2. **Quoted numbers outliving their correction.** The PROBE_006 case:
   original report claimed p≈0.003; the TASK_014 correction established
   N=48, p≈0.048, in-sample-strict. Any note that quoted the old number
   is now silently wrong. The current mitigation ("read §3a before
   citing") is a human-attention patch — exactly the kind of rule the
   architecture says should not exist where a tool could do the job.
3. **Stale derived views.** Digest/index/management-mirror are only as
   fresh as their last run. Already named on the roadmap as built
   (`_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md` §3.8, as of
   2026-07-06) and as the cross-vault bridge-run gap.
4. **Prose restating structure.** Narrative files (altitude map, READMEs)
   repeat statuses and numbers that also live in spec frontmatter. The
   narration is valuable; the bare copy is the drift seed.

## 3. Writer-contract rules — BANK NOW (zero tooling)

These two rules go into the Layer 1 writer conventions (AGENTS.md or its
designated conventions home). They cost a few words per note and make
species 2 and 4 detectable-in-principle by future dumb tools; without
them, stale copies are undetectable even in principle.

### Rule A — Quote with anchor

```text
Any quantitative claim copied from a source artifact carries its anchor:
the source path (section if applicable) and the as-of date.

  Good:  N=48, p≈0.048 (prior_session_level_fade_aged.md §3a, as of
         2026-06-26)
  Bad:   N=48, p≈0.048
```

Rationale: an anchored quote can be mechanically found and checked
against its source's modification history; a bare number cannot. This
does not prevent staleness — it makes staleness computable.

### Rule B — Point, don't restate

```text
Where prose must mention a status, verdict, or number for readability,
phrase it as a pointer ("status per the spec frontmatter", "verdict per
the screen report") or anchor it per Rule A. Never a bare copy.
The structured field (frontmatter, report header) is the source; prose
is a projection.
```

Rationale: species 4. Narration keeps its reader value; the copy stops
being a second place the truth must be maintained.

Both rules are writer discipline, not tooling. They are deliberately the
enabling half: detection tools (a quote-checker) stay UNBOOKED until a
stale anchored quote is actually observed causing a failure — the same
measured-failure bar as everything else.

## 4. Roadmap amendment — table projection into 3.2, trigger FIRED

Species 1 gets a tool, because its trigger has demonstrably fired.

**Amendment to roadmap entry 3.2 (Layer 3 deriver, content-views half):**

- **Job addition:** among its `_DERIVED/` views, generate the status
  tables currently hand-maintained in README files — first target: the
  composition-nodes README table, which is a pure projection of the
  node specs' frontmatter (name, status, one-line description). The
  README keeps its prose; the table body becomes generated output (or
  the README points at the derived table — implementer's choice, but
  the hand-typed table row dies either way).
- **Trigger status: FIRED, 2026-07-06.** Two dual-update events in one
  session (regime panel completion; newsroom candidate booking) are the
  observed failure mode this view exists to remove. Recorded here so the
  build, whenever the operator schedules it, is justified by measurement
  rather than tidiness.
- **Discipline unchanged:** standard dumb tool. Parses frontmatter,
  tabulates, links back to sources, regenerates on every run, never
  interprets, never hand-maintained. Output captured by the logger.

Note the distinction: this note records the fired trigger; it does not
build. Building is a separate scheduled act (house rule: booked-vs-built
is a real boundary).

## 5. Explicitly NOT actioned (and why)

- **3.8 staleness signal:** already built as
  `tools/wiki_deriver/derived_staleness_signal.py`
  (`_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md` §3.8, as of
  2026-07-06). It flags stale `_DERIVED/` artifacts and never regenerates
  or fixes them.
- **3.5 convention linter:** stays deferred. Frontmatter-vs-body
  divergence has produced no observed failure yet.
- **A quote-staleness checker:** deliberately unbooked (see §3). Rule A
  is the prerequisite that makes it possible; the tool waits for its
  failure.
- **Any new persistent housekeeping layer:** the fix for drift is never
  a standing agent that "keeps things tidy" — that is hand-maintained
  judgment wearing a tool costume (same drift analysis as the newsroom
  candidate's §4 editor rule). Housekeeping remains occasional, cold,
  and flag-resolving per the existing roadmap.

## 6. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-07-06 | banked-program-note | Created from operator direction to keep working drift down. Banks Rules A/B into the writer contract; amends roadmap 3.2 with the README-table projection and records its trigger as FIRED citing the two 2026-07-06 dual-update events; explicitly declines to promote 3.8/3.5 or book a quote-checker absent observed failures. |
| 2026-07-06 | correction | Corrected the 3.8 status copy: derived-staleness is built per `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md` §3.8 (as of 2026-07-06), and `tools/wiki_deriver/derived_staleness_signal.py` exists and runs. |
