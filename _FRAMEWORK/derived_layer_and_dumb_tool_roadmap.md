---
title: Derived-Layer & Dumb-Tool Roadmap (Layers 3–4 + the tooling)
status: living-reference
created: 2026-06-24
purpose: One place that consolidates (a) the retrieval research decisions,
  (b) what each derived/dumb tool is and why it earns its place, and (c) the
  trigger that says when to build each one. This note is a view; the research
  evidence lives in _RESEARCH/two_tier_retrieval_2026.md and the four-layer
  design in _FRAMEWORK/LAYER_ARCHITECTURE.md. If they disagree, those files
  carry their parts and this note is stale.
home: _FRAMEWORK/
related: _FRAMEWORK/LAYER_ARCHITECTURE.md (the four layers),
  _RESEARCH/two_tier_retrieval_2026.md (the evidence)
---

# Derived-Layer & Dumb-Tool Roadmap

This note answers one question: **what background tooling do we build on top
of the running logger, and when?** It consolidates the retrieval research,
the design decisions it produced, and the full list of dumb tools — each with
the *trigger* that says it's time to build it. The governing rule sits over
all of it: **a tool earns its place only if it carries load an agent would
otherwise carry in its head; it flags and computes, it never interprets or
fixes; and it is built only when there is real input data for it to work on.**

## 1. Where this sits (the one-paragraph frame)

The logger (Layer 2) is built and running — it captures everything to Git.
Everything in this note is *derived from* what the logger captures. None of it
is urgent: the substrate grows whether or not these tools exist, and a tool
built before its input data exists runs against near-empty inputs and tells
you nothing. So the discipline is: **let history accumulate, build each tool
when its trigger fires, and keep every tool dumb (flags, never fixes;
regenerates from source, never hand-maintains).**

## 2. The retrieval decisions (what the research settled)

Full evidence: `_RESEARCH/two_tier_retrieval_2026.md`. The decisions that
shape the tooling below:

- **The architecture is validated, not speculative.** Our first-order /
  structural-index / on-demand-summarizer shape independently matches built
  systems (Git-Context-Controller, DiffMem, memsearch). We are more
  disciplined than the field in one way: nothing semantic is ever persisted.
- **The trigger to add a tool is measured failure or accumulated material —
  never a note count.** The "~1000 notes" trigger is dropped; the literature
  gives no defensible document-count threshold.
- **Skip vector search until lexical (grep/BM25) measurably fails.** Ship the
  structural index + lexical search first. Add vectors only when the right
  note exists but lexical search misses it on synonym/paraphrase. We may
  never need them. If ever built: pgvector in our Postgres,
  text-embedding-3-small, hybrid with BM25, a disposable shadow over the
  Markdown truth.
- **Layer 4 needs two-stage citation verification.** Existence-checking a
  citation proves almost nothing about whether the source supports the claim
  (SourceCheckup: 50–90% of LLM responses not fully supported by their own
  citations). So any on-demand summarizer must existence-check AND
  support-check (NLI entailment), with LLM-judge faithfulness as a secondary
  flag only.

## 3. The dumb-tool catalogue (what to build, why, and when)

Each tool below lists its **job** (one line), **why it earns its place**
(the load it removes), its **trigger** (the data/volume it needs to be
worth building), and its **status**. All of them flag/compute and never fix;
fixing-with-judgment is the housekeeping agent's job (last entry).

### 3.1 Link / reference integrity checker — BUILT
- **Job:** scan notes for `[[links]]` and file/commit references that point
  at things that don't exist; list the broken ones.
- **Why it earns its place:** it catches the stale-pointer failure this
  project keeps hitting (the broken-reference cousin of the stale-front-door
  problem). It is pure existence-checking — no judgment — so it is a clean
  dumb tool. An agent never has to verify its own links; the tool catches
  drift after the fact.
- **Trigger:** met now. The vault already has notes with cross-references
  (the architecture note points at PATTERNS.md, OPERATIONS.md, etc.), so it
  has real input today.
- **Status:** built and upgraded. Initial build landed as TASK_017; the
  vault-index-backed validator upgrade landed as TASK_019. It now consumes
  `_DERIVED/vault_index.json`, strips line/symbol suffixes before resolving,
  separates actionable broken / ambiguous / external-local documented /
  suppressed-by-config rows, and keeps suppression auditable.

### 3.2 Layer 3 deriver — structural index ("the altitude map") — BUILD SOON, STAGED
- **Job:** regenerate, from source, a set of `_DERIVED/` views over the
  vault — both content-parsed (survivor-ledger, dead-scoreboard,
  open-threads, recent-findings-index, artifact-index) and Git-history
  signals (per-note churn, recency, temporal-coupling clusters, backlink
  centrality).
- **Why it earns its place:** it replaces hand-maintained lists (which drift)
  with computed-from-source views (which can't). It surfaces structure a
  human would otherwise miss — what's load-bearing, what's stale, what
  co-evolves. It is the primary navigation layer that lets us defer vector
  search.
- **How (keep it dumb):** parse headings, status/verdict lines, dates, paths,
  explicit "follow-up" sections for the content half; mine `git log` for the
  signals half. Borrow Code Maat's starting thresholds — **min 5 revisions,
  min 5 shared revisions, 30% coupling, max changeset 30, same-day commits
  collapsed** — then tune. No embeddings, no LLM summaries. Flags and
  tabulates; never interprets; regenerates from source; never hand-maintains;
  every view links back to the files behind it. Output is files, captured by
  the logger on its next pass.
- **Trigger — staged:** the *content-parsed* half has enough input now
  (`_worker_reports/` holds real probes and reviews). The *Git-history*
  signals half needs deeper commit history than ~one day to be meaningful
  (coupling needs the 5-shared-revisions minimum). So build the content
  views now if wanted; defer the churn/coupling signals until commit history
  is deep enough.
- **Status:** staged. The first lookup slice is built: the vault index
  (`tools/wiki_deriver/build_vault_index.py`, `_DERIVED/vault_index.json`,
  `_DERIVED/vault_index.md`) landed as TASK_018. The broader content-derived
  views remain to be specced from the live vault; the Git-history/churn
  signals remain deferred until commit history is deep enough.

### 3.3 Orientation digest / ground-truth snapshot -- BUILT
- **Job:** generate a compact, deterministic ground-truth snapshot of the
  vault state an agent should read as given fact before doing work: canonical
  files, live edge status, sealed boundaries, active work, in-flight
  directives, and current bright lines.
- **Reframe:** this is a **ground-truth snapshot**, not a prose summary and
  not model inference. Loading it is the knowing. The model does not
  re-derive which file is canonical, where the OOS seal sits, or what is
  currently live; the dumb tool hands those facts to it in the same shape on
  every run.
- **Why it earns its place:** orientation is expensive and error-prone for
  every agent, especially when the same state facts must be rediscovered from
  `AGENTS.md`, the methodology reference, the altitude map, `_worker_reports/`,
  and the derived artifacts. Stronger models make this more valuable, not
  obsolete: a better model should spend its intelligence on the task, not on
  improvising vault state that can be computed and verified deterministically.
- **Bright line:** generated deterministically from the vault index plus
  canonical frontmatter / explicit status fields. Never hand-written. Never
  LLM-summarized. If a field needs judgment, the judgment belongs in the
  source note first; the digest only surfaces it.
- **Trigger:** build after 3.2's vault index exists and 3.1's validator is
  trustworthy enough that the digest can safely link into indexed files. That
  prerequisite is now mostly met by TASK_018 and TASK_019; the remaining spec
  should bind to the real `vault_index.json` shape rather than inventing a
  parallel roadmap.
- **Status:** built as TASK_020 -- the deterministic orientation digest
  (`tools/wiki_deriver/build_orientation_digest.py`, `_DERIVED/orientation_digest.md`)
  consuming `vault_index.json`.

### 3.4 Orphan / staleness reporter — DEFER
- **Job:** list notes nothing links to (orphans) and notes untouched for a
  long time (stale candidates). This is the "readership" signal, computed —
  what's used vs. abandoned.
- **Why it earns its place:** surfaces dead weight and under-linked notes so
  they can be revisited — without anyone hand-tracking what's used. It
  *flags*; it never decides a note is dead (that's judgment, deferred to the
  housekeeping agent).
- **Trigger:** enough notes that orphans and stale ones actually accumulate.
  Right now everything is recent and linked — nothing to report.
- **Status:** deferred. (Could fold into 3.2 as another derived view when its
  trigger fires.)

**3.4a — Title / role collision checker (CANDIDATE).**
- Job: group files by frontmatter `title:` (or a declared role / `home:`);
  flag two files claiming the same identity.
- Why: this session accidentally spawned a second `DUMB_TOOLS_ROADMAP.md`
  claiming to be "the roadmap"; a title/role check catches duplicate-identity
  files instantly, before they diverge. Flags only.
- Trigger: build if duplicate-identity files recur.
- Status: candidate, deferred with 3.4.

### 3.5 Frontmatter / convention linter — DEFER
- **Job:** check notes carry the fields they should (a date, a status where
  that applies); flag the ones that don't.
- **Why it earns its place:** keeps the conventions that make Layer 3
  derivable from silently rotting, without burdening the writing agent — the
  agent writes naturally, the linter surfaces what drifted. It *flags*; it
  does not fix (fixing edges into judgment).
- **Trigger:** enough notes following conventions that drift from them
  accumulates. Premature now.
- **Status:** deferred.

**3.5a — Controlled-vocabulary status linter (CANDIDATE).**
- Job: hold an approved enum of `status:` values; flag any note whose status
  is outside it.
- Why: this session's status backfill created ~6 new one-off tokens
  (e.g. `spec-drafted-final-bypass-proxy`); a vocabulary check keeps the
  digest's status column from sprawling. Sharper than 3.5's presence-check —
  3.5 checks a status EXISTS; this checks it's VALID.
- Trigger: build when status-vocabulary drift recurs (more than one stray
  token seen). Flags only; never rewrites a status.
- Status: candidate, deferred with 3.5.

**3.5b — Canonical/candidate consistency checker (CANDIDATE).**
- Job: encode the vault's structural rule (canonical/ is authoritative; a
  candidates/ copy must not claim a status contradicting its canonical
  twin) and flag violations.
- Why: this exact bug — a basename in both `canonical/` and `candidates/`
  with contradictory statuses (the canonical copy read `tested-rejected`) —
  cost a full cleanup pass this session. More specific than the generic
  basename collision the vault index already surfaces; this knows the
  semantic rule. Flags only; the dedupe judgment stays human (3.7).
- Trigger: build if canonical/candidate contradiction recurs.
- Status: candidate, deferred with 3.5.

### 3.6 On-demand summarizer (Layer 4) — DEFER (and gated behind Layer 3)
- **Job:** when called, read a cluster of first-order artifacts (the ones the
  Layer 3 altitude map pointed at), summarize with a cold/fresh model, cite
  each claim to its source, return the result, and do NOT persist it.
- **Why it earns its place:** lets a reader get a body of past work distilled
  on demand without anyone storing a summary that goes stale. The summary is
  a disposable lens, regenerated live, never inherited as truth.
- **How (the hard part):** two-stage verification — existence-check
  (placeholder-ID substitution kills fabricated refs) AND support-check (NLI
  entailment: does the cited source entail the claim?). Default to
  draft-then-attach-citations (P-Cite); surface the support-check score with
  the summary. Cold/fresh context, never the warm writing agent.
- **Trigger:** a months-long arc of work whose pattern no one remembers in
  full — and Layer 3 built first (it is the navigation Layer 4 reads
  through). It is the riskiest layer (a model inferring relationships can be
  confidently wrong), so it comes last, with validation.
- **Status:** deferred, gated behind Layer 3.

### 3.7 Housekeeping agent — DEFER (needs the dumb tools to have run first)
- **Job:** run cold and occasionally; read the pile of flags the dumb tools
  produced (broken links, orphans, convention drift, contradictions) and make
  the *judgment calls* the dumb tools couldn't — fix the broken link, decide
  an orphan is genuinely dead, refresh a stale front-door pointer.
- **Why it earns its place:** it does the judgment work of maintenance
  *without burdening the working agents* — they just write; this cleans up
  behind them, cold and rarely, in a separate pass. It is essentially Layer 4
  pointed at maintenance instead of distillation.
- **Trigger:** the dumb tools (3.1–3.5) have run and accumulated a real pile
  of flags to resolve, and there is enough vault for there to be mess.
  Building a housekeeper for a clean vault is the over-build trap.
- **Status:** deferred, last.

### 3.8 Derived-staleness "needs regen" signal -- BUILT
- **Job:** flag any `_DERIVED/` artifact whose source files are newer than
  the artifact itself — i.e. "regen me."
- **Why it earns its place:** after the roadmap edit this session, the
  orientation digest's one cited line number went stale because the digest
  wasn't regenerated. A staleness signal surfaces "this derived view no
  longer matches its sources" without a human noticing by eye. It is the
  vault-internal cousin of the 5.4 drift checker (which compares the
  dependency catalog to installed reality); this compares derived artifacts
  to their vault sources. Flags only; it triggers a regen, it does not regen
  or fix.
- **Trigger:** fired. The vault now has several derived artifacts that can
  fall out of sync, and this session repeatedly needed manual "remember to
  regenerate / re-sync" checks after source edits.
- **Status:** built as `tools/wiki_deriver/derived_staleness_signal.py`.
  It writes `_DERIVED/derived_staleness.md` and `.json`, exits non-zero when
  stale artifacts are flagged, and never regenerates or fixes anything.

### 3.9 Statistical substrate + legible shutter -- BOOKED CANDIDATE (trigger not fired)
- **Job:** book, but do not yet build, a future computed-relationship
  substrate plus a visibility lens. The statistical substrate computes
  relationships over vault files (similarity, near-duplicates,
  co-occurrence, staleness, churn/coupling, outliers). The shutter/lens
  then controls which files are visible for a task or dimension, without
  deleting or rewriting anything.
- **Why it earns its place later:** this turns "remember to ignore the
  other domain" into structure. A task scoped to a dimension sees the files
  that dimension admits, while other files are masked. The agent no longer
  carries the whole scoping rule in its head. The statistics prepare Layer
  4's inputs mechanically; the housekeeper later makes only the judgment
  the statistics cannot make.
- **Not a new layer:** the four layers remain write / record / derive /
  distill. The shutter is a cross-cutting visibility mechanism in front of
  what an agent reads; it is a lens/aperture/scope, not "Layer 5."
- **Infra-core aperture design:** the shutter is not simply "show one
  dimension, hide the rest." Its aperture is:
  `visible_set = always_visible_infra_core + current_dimension_content -
  other_dimensions_content`. Infrastructure -- how to manage the wiki -- is
  dimension-agnostic and always visible; domain content is dimension-scoped
  and masked when out of scope. The `always_visible` core must be a positive,
  human-curated config allow-list, never an exclusion rule such as
  "everything outside `_DIMENSIONS/`." This vault has trading content and
  sensitive/local-only material scattered across root files, `nb_lib/`,
  outputs, archives, and `session_history/`, so a negative rule would expose
  too much during another dimension's task. Declaring what is infrastructure
  versus dimension content is a one-time human config judgment; after that
  the tool applies it dumbly: read config, compute the visible set, mask the
  rest, emit a receipt. Every shuttered run must report `always_visible`,
  `current_dimension`, `masked_dimensions`, `deny_always`, counts, config
  path/hash, and the command that produced the aperture. Known-mixed roots
  such as `_worker_reports/`, `_DERIVED/`, `tools/`, `deps/`, and root files
  need per-path classification at build time; broad roots are not a
  substitute for classification. The current directory structure is the
  crude first shutter: for now, a health-lifestyle task can be pointed at the
  shared bootstrap/framework material plus `_DIMENSIONS/health-lifestyle/`.
  The tool automates a config-backed aperture later, when manual pointing
  becomes error-prone.
- **Implementation note:** vector storage such as pgvector is only one
  possible implementation if lexical/indexed retrieval measurably fails.
  The concept is the computed relationship substrate, not a database choice.
- **Safety rule A:** housekeeping does only what statistics cannot. If a
  decision is mechanically derivable, it belongs in the dumb tool. The agent
  only decides irreducible maintenance judgments such as supersede, merge,
  archive, or route.
- **Safety rule B:** the shutter must be legible, never opaque. It must mask
  by transparent, computable criteria the agent can know about (dimension
  tag, directory, recency, explicit allow-list). Every shuttered run must
  emit a scope receipt: included roots/tags, excluded roots/tags, counts,
  and the config/command that produced the aperture. A visible shutter is a
  tool; an invisible one is a trap.
- **Sequencing corollary:** build crisp shutters first (dimension,
  directory, recency, explicit allow-list). Similarity-based shuttering is
  later and riskier because fuzzy relevance is exactly where an agent least
  knows what was excluded.
- **Trigger:** not fired. Build only when all four are true: (1) at least
  two real domains/dimensions exist; (2) the indexed corpus/history is deep
  enough for clusters to mean something; (3) lexical/index tools or human
  navigation show measured failure; and (4) agents demonstrably risk mixing
  domains or tasks without structural scoping.
- **Seed evidence:** `_DIMENSIONS/health-lifestyle/health_lifestyle_dimension_seed_20260630.md`
  is the first concrete second-domain seed. It satisfies trigger condition
  (1) only; the corpus is not yet deep enough, lexical/index failure has not
  been measured, and no cross-domain mixing failure has recurred.
- **Status:** booked candidate, trigger not fired. Do not build yet.

## 4. Build order (the honest sequence)

1. **Link/reference integrity checker (3.1)** — built (TASK_017, upgraded
   by TASK_019).
2. **Vault index slice of the Layer 3 deriver (3.2)** — built (TASK_018).
   This is the lookup substrate consumed by the validator and future digest.
3. **Orientation digest / ground-truth snapshot (3.3)** -- built (TASK_020).
   It binds to the real `vault_index.json` shape and the canonical
   frontmatter/status fields.
4. **Layer 3 deriver, remaining content-views half (3.2)** — soon, specced
   from the live vault. Defer the churn/coupling signals until commit history
   is deep.
5. **Let history accumulate.** The substrate growing is the precondition for
   everything below.
6. **Layer 3 Git-history signals (3.2)** — when commit history crosses the
   coupling thresholds.
7. **Orphan reporter + linter (3.4, 3.5)** — when note volume makes drift
   accumulate.
8. **On-demand summarizer (Layer 4, 3.6)** — when there's a long arc to
   distill, gated behind Layer 3, with two-stage verification.
9. **Housekeeping agent (3.7)** — last, once the dumb tools have produced a
   pile of flags worth resolving.

10. **Dependency manifest + catalog renderer (5.1)** -- next concrete
    environment-reconstitution build.
11. **Offline bundle + Python pinning (5.2)** and **drift detection +
    portability stub (5.4)** -- after the manifest exists.
12. **Windows bootstrap installer (5.3)** -- after the manifest and offline
    bundle exist.

*Candidates 3.4a / 3.5a / 3.5b / 3.8 / 3.9 are deferred with their parents
or explicit triggers and build only when their drift/scope conditions recur.*

## 5. Environment reconstitution -- dependency catalog & bootstrap installer

This section is a different category from the logger-derived dumb tools
above. The 3.x tools derive vault coherence and retrieval views from what the
logger captures; this effort reconstitutes the machine environment from
installed-software reality. Two of its stages still follow the same dumb-tool
discipline: the catalog renderer (5.1) and drift checker (5.4) compute from a
source of truth, regenerate their outputs, never hand-maintain, and never fix.
Full detail lives in
`nb_lib/strategy_specs/source_artifacts/RESEARCH_dependency_catalog_and_bootstrap_installer_20260629.md`
and `_worker_reports/DEPENDENCY_INVENTORY_20260629_findings.md`.

### 5.1 Dependency manifest + catalog renderer -- NOT BUILT (next)
- **Job:** create a machine-readable `dependencies.yaml` as the portable
  truth for dependency name, kind, purpose, version, source, and verify
  command, plus a stdlib `render_catalog.py` that generates human/agent-readable
  `catalog.md` from it.
- **Why it earns its place:** it replaces scattered, in-someone's-head
  machine knowledge with one computed catalog. This is the same dumb-deriver
  discipline as 3.2/3.3: manifest to rendered Markdown, regenerated from
  source, never hand-maintained.
- **Trigger:** met now. The 2026-06-29 inventory provides real input: Git
  2.53.0, Python 3.12.10, NinjaTrader 8.1.6.3, Bookmap 7.5.0, the logger and
  dumb tools as internal dependencies, and archived installers in Downloads.
- **Status:** not built; this is the next build in this section.

### 5.2 Offline bundle + Python pinning -- NOT BUILT (gated behind 5.1)
- **Job:** move the relevant installers out of the Downloads graveyard into a
  `bundle/installers/` folder with SHA256 sidecars; add an embeddable/pinned
  Python; add `pyproject.toml` plus a lockfile for the tools, even while they
  remain stdlib-only.
- **Why it earns its place:** it makes restore work offline and pins the
  proprietary tools, especially NinjaTrader and Bookmap, that are not reliable
  package-manager artifacts. The inventory also found `winget` absent from the
  agent shell, so the design cannot assume a package manager is present; the
  offline bundle is the primary path, not a fallback.
- **Trigger:** after 5.1's manifest exists to drive what belongs in the bundle.
- **Status:** not built; gated behind 5.1.

### 5.3 Windows bootstrap installer -- NOT BUILT (gated behind 5.1, 5.2)
- **Job:** build a Windows `bootstrap.ps1` where the user picks a working
  folder, the script places/inits the git repo there, verifies dependencies
  against the manifest, installs anything missing from the offline bundle, and
  starts the logger committing. It must be idempotent and safe to re-run.
- **Why it earns its place:** it turns "reconstitute the whole environment on
  a new machine" from tribal knowledge into one re-runnable script -- the
  operational payoff of the whole effort.
- **Trigger:** after 5.1 (manifest) and 5.2 (bundle) exist for it to read from
  and install from.
- **Status:** not built; gated behind 5.1 and 5.2.

### 5.4 Drift detection + portability stub -- NOT BUILT (gated behind 5.1)
- **Job:** add a `check_drift.py` that runs each manifest verify command,
  diffs against the manifest, and flags mismatches without fixing them; also
  add a stub `recipes/ubuntu.yaml` to keep the portable-principle /
  platform-recipe split honest.
- **Why it earns its place:** it keeps the catalog from rotting with the same
  flags-never-fixes discipline as 3.4/3.5. The portability stub keeps the
  "principle is portable, recipe is platform-specific" split real: Windows
  now, Ubuntu later in principle.
- **Trigger:** after 5.1's manifest exists to diff against.
- **Status:** not built; gated behind 5.1.

## 6. The one rule under all of it

Every tool here is dumb in the same disciplined way: it **flags or computes,
never interprets or fixes; it regenerates from the Git substrate, never
hand-maintains a copy that drifts; and it is built only when real input data
exists for it.** The smart, judgment-bearing work (distillation, fixing) is
done cold, occasionally, by a separate pass — never by the warm working
agent, whose attention stays on the actual work. The tools do the keeping;
the agent does the thinking. That is the whole system, applied to its own
tooling.
