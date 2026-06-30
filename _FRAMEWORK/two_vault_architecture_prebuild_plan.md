---
title: Two-Vault Architecture — Pre-Build Plan
status: "pre-build-plan"
created: 2026-06-29
home: _FRAMEWORK/
related:
  - _FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md
  - _FRAMEWORK/LAYER_ARCHITECTURE.md
  - _worker_reports/SECRETS_AUDIT_20260629_findings.md
  - _worker_reports/CONSULT_sync_set_boundary_proposal.md
note: "Design + derivation captured before build. When this and the live vault disagree, the vault wins."
---

# Two-Vault Architecture — Pre-Build Plan

A pre-build plan, not a build. This note captures the **management / working vault** split agreed in this session, and — load-bearing — the **derivation chain that arrived at it**, so a future agent picking this up cold can build it correctly rather than reconstructing the question and getting a different answer. The conclusion is short; the reasoning is not, by design.

## 1. The problem this solves

The single local vault is the source of truth and works well for the project, but it is large (~8,500 tracked files) and **history-contaminated with secrets**: a live databento API key and Apex account IDs (e.g. `APEX-316551-*`) appear in **tracked files AND in git history** (see `_worker_reports/SECRETS_AUDIT_20260629_findings.md`). Two pressures meet here:

1. **We want a chat-side orchestrator agent** — connected to GitHub / project tooling — to have a small, clean knowledge layer it can reason from and direct work against. The current vault is too large to push wholesale, and pushing it would publish secrets.
2. **We want working agents to keep working naturally.** The vault's discipline is "agents write naturally, the substrate captures, the dumb tools maintain coherence." That deliberately keeps the writing agent unburdened. Adding "be careful about what's secret" or "only commit clean things" to every working agent re-burdens them — the very failure mode the dumb tools were built to prevent.

So the design has to satisfy: clean orchestration view + secrets-safe sharable surface + working agents continue to write naturally.

## 2. How we derived the answer (the reasoning chain — preserve in full)

**This section is the one that has to survive context loss.** Skipping the chain and reading only the conclusion will produce someone rebuilding it from scratch, getting a slightly different shape, and re-introducing the failure modes the chain ruled out. Each step replaced the previous one's structural flaw.

**Step 1 — first reach: "push the orchestration subset" via an exporter.** The shape considered first was to keep one vault and add an exporter that walks the local vault, filters out sensitive paths, and pushes a sanitized subset to GitHub. This is the obvious move and matches how filtering is usually done.

**Step 2 — flaw found: derived artifacts are contaminated by *reference*, not by content.** The orientation digest, vault index, and dependency catalog look like safe summaries — but they index/describe the whole vault. The vault index records 3,800+ files including the sensitive paths verbatim. The orientation digest links into source files, some of which carry live credentials. The dependency catalog points at `PRJ_6_NoiseBrk.zip` (which contains the databento key) by full Windows path. **A summary of a contaminated thing is itself contaminated, just by reference.** Filtering at export time would require maintaining a denylist that catches every form the secret takes — full path, basename, account-ID substring, archive-relative inner path, etc. The secrets audit demonstrated that denylists miss things; secrets show up in forms one didn't think to enumerate (a Windows path mid-prose, an archive entry name inside a sidecar, an old config line in `session_history/extracted/`). **Filtering a dirty whole is fragile by construction.**

**Step 3 — refinement: "born clean, grow forward."** Rather than retroactively cleaning a contaminated thing, declare a clean baseline at NOW and accumulate forward only what's known clean. This is the same move that made the original wiki actually work: it wasn't built by importing prior history sorted by modification date and hoping it cohered — it was called as a baseline from a known-clean state and grown. The baseline trick is generalizable: when a substrate has accumulated contamination you cannot reliably reverse, declare a fresh start point and apply discipline going forward. The contaminated history is left alone; the new substrate inherits no contamination because there is none to inherit.

**Step 4 — structural expression: two vaults, not one-vault-plus-filter.** A "born clean, grow forward" baseline implemented as a *filter on top of the existing vault* is still one vault with a filter — i.e. still the Step 1 design wearing a different hat, with the same denylist-miss failure mode. The **structural** way to express "born clean" is to make the clean thing **its own vault from birth**. A management vault that was never indexed against the working vault's contaminated paths cannot reference them — it is clean **by separation**, not by filtering. This is strictly better than an exporter sanitizing in place because correctness comes from the boundary, not from continuously-vigilant filter rules.

**Step 5 — the two-vaults shape also makes physical the "two work-modes" principle.** "Agents work naturally, unburdened" governs working agents doing domain work. Orchestration / infra is a different mode — bounded, infrastructure-construction work the agent IS scoped to. Two vaults make the mode boundary **structural**: an agent knows which mode it is in by **which vault it is pointed at**. The discipline that documentation could only request is now enforced by what the agent can see. Pointed at the working vault → natural domain work; pointed at the management vault → scoped management work. The agent doesn't have to remember; the structure remembers.

**Each step replaced a structural failure mode in the previous step.** Step 1 fails because summaries-of-contaminated-things are contaminated. Step 3 (baseline trick) replaces "scrub the past" with "draw a line now." Step 4 (two vaults) replaces "filter at the boundary" with "make the boundary structural." Step 5 (modes) adds the principle that justifies why this is consistent with the existing discipline, not a violation of it. The conclusion only makes sense with this whole path.

## 3. The architecture

Three components:

- **Working vault** — local, private, full, messy. The current `C:\VMShare\NT8lab\` continues as it is. Agents do natural domain work here, undirected toward management. This is the source of truth for the actual project; the management vault never overrides it. Stays local; never pushed.
- **Management vault** — GitHub-/project-connected, human-gated, deliberately **thin**. The orchestration layer: roadmap, distilled current state, coherence pointers — enough that an orchestrator agent can reason about WHERE work is and direct WHAT happens next, but not a copy of the working vault's contents. Born clean (clean baseline at start); grows forward (only what's known clean is ever written into it). Agents work here ONLY when specifically directed with a management-vault spec.
- **The bridge** — a deterministic dumb tool that reads the working vault and **writes** distilled, clean management artifacts INTO the management vault. It does not filter-in-place on the working vault; it regenerates clean artifacts targeted at a clean destination. This is the seam that keeps the two vaults coherent without an agent having to hold the relationship in its head. The bridge is the load-bearing component because the cross-vault coherence problem (pitfall #1) concentrates here.

Asymmetry that matters: **the working vault is authoritative for project facts; the management vault is authoritative for orchestration state.** When the bridge runs, it overwrites management-side artifacts from working-side truth. The bridge never writes back into the working vault.

## 4. The two-modes principle (governing philosophy)

The existing discipline "agents work naturally, unburdened, while dumb tools maintain coherence" governs **working agents doing domain work** — strategy research, data probes, candidate-spec writing. That discipline is NOT violated by handing a working agent a scoped, finite **infrastructure-construction task** (like "build the link-reference checker" or "build the lock tool"), because building a named tool **is the task on hand**. Construction tasks are bounded and end; once the tool is built, the working agent goes back to natural domain work and the tool takes over the maintenance load. The agent is not perpetually thinking about plumbing; they built one piece of plumbing and moved on.

Three guardrails keep this honest:

- **Builds are bounded and END.** No perpetual plumbing. The "build the next dumb tool" cadence is the over-build trap if it never stops; the build cadence has to be driven by accumulated drift (the catalog's "build when trigger fires" rule), not by always having one more tool to build.
- **Infra maintenance never folds into working agents.** Maintenance happens via dumb tools and cold passes (the deferred housekeeping agent), not by asking the warm working agent to remember to do it. The whole point of the dumb-tool catalog is to keep the working agent's attention on the task.
- **First-build hand-holding by the human + orchestrator is legitimate bootstrapping, not a permanent state.** During this session, dense human + orchestrator coordination is doing work that, post-bootstrap, the bridge + the two-vault structure will do automatically. That's the normal arc of a structural change — the structure is built by hand once, then it works without intervention.

Reading: an agent given "build the bridge between vaults" is not violating the "work naturally" rule — it is doing the named construction task. An agent given "while you work, also keep the management vault in sync as you go" WOULD violate the rule. The bridge runs as its own action, not as a hidden tax on every working step.

## 5. The three pitfalls (record all three honestly)

1. **Cross-vault coherence is the same coherence problem, arriving early.** The management vault's picture of the working vault goes stale as the working vault changes. This is the same drift problem the derived-staleness signal (roadmap §3.8) was scoped against, but it appears immediately across the vault boundary instead of within `_DERIVED/`. The **bridge** (deterministic refresh) is the answer; it concentrates the cross-vault coherence risk into one component. Implication: the bridge is the load-bearing build of the next phase. Build it carefully, with the same dumb-tool discipline (regenerates from source; flags drift; never hand-maintains).
2. **"Human-gated" must be a real mechanism, not a hope.** "The human gates what goes to GitHub" is wishful if it relies on everyone remembering to be careful. The structural mechanism is: the management vault is the GitHub-/project-connected one, the working vault has no GitHub remote, and working agents are pointed at the working vault by default. An agent touches the management vault only when handed a management-vault-specific spec. Defaults do the gating; humans don't have to.
3. **Don't let the management vault MIRROR the working vault.** The temptation will be to export "everything that's safe" into the management vault — accumulate notes, accumulate reports, accumulate detail — until it's a sanitized copy. Mirroring rebuilds the contamination problem (the surface area grows, the denylist gets long, the audit pressure returns). The management vault is a **distilled** layer: what an orchestrator needs to reason and direct, not a copy. Keep it thin by design. When in doubt about whether something belongs in the management vault, the answer is probably no.

## 6. Prerequisites + next steps (so the build picks up correctly)

### Prerequisite (before building anything)

- **Rotate the databento key** at the credential provider. This makes the old key in history *inert* — a dead credential leaks nothing if it reaches a public mirror. With a rotated key, the working vault's contaminated history becomes harmless without needing a destructive history scrub. The management vault's clean baseline is then generated from clean inputs and stays clean; the working vault's history can remain as-is. (This is the single highest-leverage cleanup action.)
- Re-read `_worker_reports/SECRETS_AUDIT_20260629_findings.md` to confirm what other sensitive identifiers should be treated similarly (Apex account IDs, etc.); decide for each whether rotation, redaction at bridge time, or simply non-export is the right answer.

### Next build (a future, scoped task — NOT this note)

- Stand up the fresh management vault / repo. Empty, with its own minimal `AGENTS.md` scoped to the management mode.
- Generate the management vault's **clean baseline** from the working vault using known-clean inputs (the dumb-tool roadmap, the framework patterns, the layer architecture — files that have no sensitive content, no archived `databento.key` paths, no APEX-* references). Source-by-source whitelist, not output filtering.
- Build the **bridge** as the seam-defining component:
  - Reads from the working vault.
  - Writes distilled artifacts into the management vault — clean-by-construction, never copies sensitive paths, never includes denylist-prone content.
  - Same dumb-tool discipline as the rest of the catalog (deterministic regen, flags, never fixes, never hand-maintains).
  - Inputs to that build: this note, the secrets-audit findings, and the sync-set boundary proposal (the allow/deny lists at `_worker_reports/CONSULT_sync_set_boundary_proposal.md`).

### Relationship to the template future

This two-vault split is the correct **first** form of the eventual "vault-as-template" idea — justified now by a real need (secrets boundary + orchestration sync), not by speculation about future reuse. **Do not build the general template yet.** This is the concrete seed it would later grow from; build the seed correctly first, then later — if the case for a general template materializes — generalize from the working concrete instance, not from a speculation about what one might want.

## 7. Pointers (reference, do not copy)

- `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md` — the dumb-tools catalog. The bridge will become a roadmap entry when its trigger fires (which is now); not adding it from this note, since this is a pre-build plan and the roadmap edit is a separate, scoped change.
- `_FRAMEWORK/LAYER_ARCHITECTURE.md` — the four-layer model that this two-vault split sits on top of (the layers exist within each vault; the vaults are a structural axis the layers didn't yet need).
- `_worker_reports/SECRETS_AUDIT_20260629_findings.md` — the secrets-contamination evidence that drove Step 2 of the derivation.
- `_worker_reports/CONSULT_sync_set_boundary_proposal.md` — the allow/deny-list boundary proposal that the bridge build will consume.

## Closing note for the picker-upper

If you are reading this cold and tempted to "just push the existing vault with a filter," re-read section 2. The derivation walked away from that shape for a specific structural reason (Step 2): summaries-of-contaminated-things are themselves contaminated by reference, and filtering can only catch what the denylist anticipated. The two-vault shape exists because **separation is correct where filtering is fragile**. The bridge is the only place where the boundary is actively maintained; everywhere else the boundary is structural and free.
