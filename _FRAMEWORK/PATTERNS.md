# Research-With-Agents Framework Patterns

Status: project-agnostic patterns extracted from the MNQ trading research project (2024-2026)
Purpose: durable patterns for running long-horizon research projects with LLM agents as collaborators
Read order: after AGENTS.md and the methodology reference for the active project; before starting work on a new project

## What this document is

This file holds patterns that emerged from running a multi-year research project with LLM agents as collaborators. The patterns are not MNQ-specific. They are about how to maintain knowledge, run experiments, and preserve discipline when the people doing the work include both humans and AI agents that lack persistent memory across sessions.

Each pattern below is named, briefly described, anchored to a concrete example from the originating project, and tagged with the failure mode it protects against. Patterns are stated with appropriate confidence — some are well-established in the literature, some emerged pragmatically and may not generalize. Where uncertainty exists, it is named.

## How agents should use this document

Read once at the start of working on a project. Apply the patterns to the project at hand. Where a pattern conflicts with the active project's methodology reference, the project's methodology wins — these are general principles, not overrides. When a new pattern is discovered that survives across projects, add it here.

---

## Pattern 1: The LLM Wiki / externalized memory pattern

LLM agents have no durable memory across sessions. The solution is to externalize project knowledge into a structured, human-readable wiki that agents read at the start of each session. The wiki becomes the persistent state the agent lacks internally. This pattern is well-documented; Andrej Karpathy is one of its more visible practitioners, and academic literature treats it as the externalized-memory architecture for LLM agents.

Concrete example from MNQ project: the project root contains `AGENTS.md`, `_PROJECT_ALTITUDE_MAP.md`, `ninja-traitorate-methodology-reference.md`, and a structured wiki of strategy specs and probe results. Every agent reads these in a fixed order before starting work, and writes findings back into the wiki at the end of each session.

Failure mode it protects against: knowledge loss between sessions, agents re-deriving the same conclusions repeatedly, drift in project direction because no one remembers why decisions were made.

## Pattern 2: Human-readable as anti-hallucination layer

The format of the durable memory matters. When agent-written content lives in human-readable prose, hallucinations have a natural verification surface — a human can read the prose and catch errors. When the same content lives in opaque representations (embeddings, structured databases the human doesn't review), hallucinations land silently and become the new ground truth on next read. The human-readable format is therefore not a nice-to-have; it is the load-bearing anti-hallucination mechanism.

This is also doing a second job simultaneously: forcing the agent to produce coherent prose constrains it against hallucinations that wouldn't survive a coherent narrative. The format pressures consistency at write-time, before any human verification.

Concrete example from MNQ project: every probe result is written into prose status histories with named verdict labels and source citations, not into structured logs only. When a suspicious result (G2 showing 100% WR at 300s) appeared, the prose-form investigation note explained the structural cause; the suspicious finding could not silently become a clean victory because the format demanded the caveat.

Failure mode it protects against: agent hallucinations entering durable memory undetected; silent drift of project state away from underlying evidence.

Caveat: the verification mechanism only works at points where humans actually read. As the wiki grows, most of it goes unread on any given session. The protection is real but partial.

## Pattern 3: Gate-not-rescue for compositional overlays

When a research project builds layered systems where higher layers can filter, condition, or modify the behavior of lower layers, there is a constant temptation to use the higher layers to *rescue* lower-layer findings that failed validation. This is overfitting at the architecture level. The discipline rule: higher layers gate the products of validated lower layers; they do not revive failed lower-layer products.

Concrete example from MNQ project: the candidate support stack (daily bias packet, liquidity-zone router, target-invalidation packet, session routers) was explicitly designed as a gate over passing entry candidates, not a rescue mechanism for closed-negative candidates. When the liquidity-zone router showed informative signal for management context, this did not authorize re-opening the closed PDH_PDL entry candidate.

Failure mode it protects against: closed candidates being silently reopened under new framings; project tunneling into graveyard mining instead of forward research.

## Pattern 4: No retroactive rewrite when framings shift

When a research project discovers a better verdict framework, methodology principle, or interpretation lens, the temptation is to re-read prior findings through the new lens and update their labels. Do not. The historical verdicts stand as the record of what was concluded under the framing available at the time. The new framing applies to future work only. One permitted retroactive note: a single observation in the new methodology section that says "under this framing, prior verdicts of type X would map to Y, but the historical record is not being rewritten."

Concrete example from MNQ project: when the two-axis verdict framing (edge vs Apex-deployability) was banked, the existing Step 3 v0.1/v0.2/v0.3 verdict blocks were not rewritten. The new framing applies forward; the old verdicts remain as written.

Failure mode it protects against: retroactive re-labeling that obscures the actual reasoning history; new framings becoming excuses to re-grade old findings favorably.

## Pattern 5: Structured templates over discipline documents

The temptation when project discipline becomes important is to write a rules document that agents read and apply. This is fragile — agents can read rules and partially apply them without anyone noticing. The stronger move is to bake the discipline into the *templates* of the documents themselves. If every empirical claim must appear next to a citation of its source artifact, then "do not write hallucinated numbers" is not a rule the agent must remember; it is impossible to violate without the violation being visibly malformed.

Concrete example from MNQ project: probe-result documents follow a template that includes pre-committed predictions, believe-it bars, partition results, and source-artifact paths. An agent writing into this template cannot easily produce a hallucinated result without the missing fields being visible.

Failure mode it protects against: discipline rules being read but not applied; agents producing plausible-looking content that lacks the structural fields required for verification.

## Pattern 6: Multi-agent disagreement as integrity signal

When two independent agents read the same wiki and produce divergent interpretations, the divergence is the signal — neither agent is necessarily wrong; the wiki is ambiguous at that point and needs sharpening. This requires running at least two agents that share the wiki but operate independently within sessions.

Concrete example from MNQ project: Codex and Opus 4.7 were both used as execution agents, both reading the same wiki, often producing similar "top four next steps" reads. When their reads agreed, the wiki state was confirmed as consistent. When they disagreed on rankings, the disagreement flagged ambiguity worth clarifying in the source document.

Failure mode it protects against: single-agent interpretation locking in subtle errors; the wiki appearing internally consistent when it is actually under-specified.

## Pattern 7: Truth-profile over conditions, not single truth value

Many empirical claims do not have a single truth value across all conditions. They have a truth profile: true under some conditions, false under others, untested elsewhere. The discipline is to track the conditions explicitly rather than collapsing the claim to a single verdict.

This pattern is provisional. It emerged from the MNQ project's experience with results that differed by partition, substrate, or market regime. Whether the truth-profile framing generalizes cleanly to other domains is unverified. Use as a working framework, not as established truth.

Concrete example from MNQ project: the regime-conditioned BE delay rule was true on v2a substrate (both partitions confirmed), partition-asymmetric on V4 substrate (holdout produced the entire effect), and untested on G2. The verdict was not "the rule works" or "the rule fails" but a profile across conditions.

Failure mode it protects against: forcing claims into binary verdicts when the underlying data has conditional structure; losing information by collapsing nuance.

## Pattern 8: Two-axis verdicts when deployment constraints differ from edge

When research findings will eventually be deployed under specific operational constraints (regulatory, financial, prop-firm rules, time/budget limits), the question of "does this finding have edge" is different from the question of "is this finding deployable under our constraints." A finding can have real edge and fail deployability; it is not a failed finding, it is a non-deployable finding whose deployability gap is an engineering problem separate from the underlying edge.

Concrete example from MNQ project: the regime-conditioned BE delay rule showed strong edge (P&L gain on holdout, partition consistency on v2a) but worsened max drawdown enough that Apex's trailing-drawdown rule would not survive it without containment. Single-axis verdicts conflated edge with Apex-deployability; the two-axis split clarified that the edge was real and the deployability was a separate engineering challenge.

Failure mode it protects against: under-crediting findings that work in cash but fail constraint-specific rules; over-crediting findings that happen to fit the constraint by accident rather than by edge.

## Pattern 9: Trial budget multiplication under overlay search

When a project's architecture allows higher-level overlays to modify how lower-level units are evaluated, the search surface multiplies. Testing N candidates with M overlay configurations is not N trials; it is N × M trials. The methodology's trial-budget tracking must multiply accordingly, or the project will accumulate apparent confirmations that are statistically expected by chance.

Concrete example from MNQ project: when the candidate support stack architecture was banked, the trial-budget rule explicitly stated that overlay searches multiply the trial surface. The first liquidity-zone overlay experiment was logged as three trials (G2, v2a, combined), not one.

Failure mode it protects against: false discoveries from multiple comparisons being absorbed into the project as "we found a pattern across substrates."

## Pattern 10: The bootstrap read-order is the integrity backbone

Agents that read a fixed sequence of documents at session start form roughly the same initial mental model, which means subsequent divergences are detectable signals rather than expected noise. The bootstrap read-order is therefore not just convenience; it is the substrate on which multi-agent integrity checking and across-session consistency rest.

Concrete example from MNQ project: `AGENTS.md` declares the bootstrap sequence (methodology reference, altitude map, framework patterns, then active work). Every agent enters the project through the same door, which is what makes cross-checking possible.

Failure mode it protects against: different agents arriving at incompatible interpretations because they entered the project from different starting points.

## Pattern 11: Intake quarantine before promotion

Long-running projects need to capture raw material freely without letting
every captured fragment mutate operating truth. New material from chats,
downloads, screenshots, transcripts, outside-agent notes, or creative seeds
enters as intake by default. It can be explored lightly, but it is not
ground truth until the operator explicitly promotes it.

Useful minimum vocabulary:

- `raw-intake`: captured source material; preserve it, do not reason from it
  as truth.
- `explored`: reviewed or discussed; still not canonical.
- `promoted`: explicitly allowed to influence canonical files, runnable code,
  methodology, or current-state summaries.

Raw or explored material must not update `AGENTS.md`, runnable code,
canonical methodology, strategy specs, altitude-map current-state, or
management allow-lists unless the operator explicitly says to promote it.
This is a promotion boundary, not an anti-capture rule: capture freely,
explore lightly, promote deliberately.

Concrete example from MNQ project: multiple transcript/video intakes were
banked as seeds or context rather than evidence: the trade-plan transcript
was captured as process-discipline material, not a new strategy; the
mean-reversion video was captured as context, not a transferable finding;
and the `bw001_raw.md` comedy fragment in `_DIMENSIONS/no-host-content/`
was captured as lighthearted raw material, not as framework truth.

Failure mode it protects against: agents over-promoting fresh intake into
canonical truth because the surrounding vault feels serious; random
downloads or chat fragments mutating bootstrap files, runnable systems, or
orchestration surfaces without an explicit promotion decision.

---

## What is not in this document

Project-specific methodology (e.g., MNQ's bucket discipline, the specific R1/R2 conventions, prop-firm wrappers, regime calendars) lives in the active project's methodology reference, not here. This document holds patterns about how to run any such project. The specific project's rules go in the specific project's files.

## Status history

| Date | Status | Notes |
|---|---|---|
| 2026-06-02 | seed-v1 | Created during MNQ project Session 21 as project-agnostic extraction of research-with-agents patterns. Ten patterns; some well-established, some provisional. Future projects will confirm, refute, or refine these. |
