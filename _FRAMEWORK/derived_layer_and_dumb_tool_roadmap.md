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

**Logger v1.2 candidate -- BOOKED, NOT BUILT:** on `GUARD_TRIPPED`, back off
or quarantine the offending path instead of retrying every debounce cycle.
Trigger: the guard-refused loop on 2026-07-02 12:44-12:56, caused by a large
scratch extract under `codex_tmp/`.

**Bridge v-next candidate -- BOOKED, NOT BUILT:** `--force` must not destroy
the management vault `.git`; remote config persists in a config file.
Trigger: the 2026-07-03 management-history reset.

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
  The 2026-07-09 JSON-summary upgrade is BUILT: it emits
  `_DERIVED/broken_links.json` with role-aware severity counts and the deriver
  runner consumes that JSON instead of scraping Markdown.

### 3.2 Layer 3 deriver — structural index ("the altitude map") — BUILD SOON, STAGED
- **Job:** regenerate, from source, a set of `_DERIVED/` views over the
  vault — both content-parsed (survivor-ledger, dead-scoreboard,
  open-threads, recent-findings-index, artifact-index) and Git-history
  signals (per-note churn, recency, temporal-coupling clusters, backlink
  centrality).
- **Job addition (2026-07-06 drift-reduction trigger):** generate the
  status tables currently hand-maintained in README files. First target:
  the composition-nodes README table, a pure projection of node specs'
  frontmatter plus one-line descriptions. The README keeps its prose; the
  table body becomes generated output, or the README points at the
  derived table. The hand-typed duplicate row dies either way.
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
- **Table-projection trigger — fired, recorded only:** 2026-07-06 produced
  two dual-update events in one session: regime-attribution-panel
  completion required updating both the spec frontmatter and the
  composition-nodes README row; newsroom-candidate booking required both
  the candidate note and a roadmap pointer. This records the measured
  drift seed for a future 3.2 content-view build; it does not build the
  deriver extension.
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
- **Corroboration note (2026-07-09):** independently corroborated by external
  research intake; trigger unchanged.

**3.4a — Title / role collision checker (CANDIDATE).**
- Job: group files by frontmatter `title:` (or a declared role / `home:`);
  flag two files claiming the same identity.
- Why: this session accidentally spawned a second `DUMB_TOOLS_ROADMAP.md`
  claiming to be "the roadmap"; a title/role check catches duplicate-identity
  files instantly, before they diverge. Flags only.
- Trigger: build if duplicate-identity files recur.
- Status: candidate, deferred with 3.4.
- Corroboration note (2026-07-09): independently corroborated by external
  research intake; trigger unchanged.

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
- Possible future extension (2026-07-09): structural contradiction /
  supersession flagging across durable notes is adjacent to this checker, not a
  new peer tool yet. Keep the same trigger shape: book only if a real durable
  contradiction is observed and costs a session.

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

### 3.9 Statistical substrate + legible shutter -- BOOKED CANDIDATE (trigger evidence measured)
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
- **Trigger measurement:** lexical/indexed retrieval failure is now
  machine-checkable via `tools/wiki_deriver/missed_retrieval_detector.py`
  and `_DERIVED/retrieval_detector.md`. The committed paraphrase query set
  lives at `tools/wiki_deriver/retrieval_test_queries.json`; threshold:
  miss rate > 10% on that query set is trigger evidence. The detector
  reports only; it never fires builds.
- **Retrieval improvement ladder (booked, not built):** do not jump straight
  from lexical misses to a model-backed vector store. Treat the committed
  missed-retrieval query set as the benchmark, and climb only while the
  measured miss rate remains above the 10% bar. Rung 1 is corpus-derived term
  co-occurrence: build a deterministic table of meaningful terms and their
  document/paragraph overlap partners (Jaccard-style Venn intersections) from
  committed Markdown, then use it for mechanical query expansion. This is the
  dumbest possible semantic bridge: no model, no judgment, stdlib-compatible,
  regenerated into `_DERIVED/`, and disposable. Rung 2 is LSA over the
  term-document matrix: deterministic linear algebra, no neural model, only if
  co-occurrence under-delivers. Rung 3 is a pinned local embedding model
  (MiniLM-class or similar) used as a fixed function, with vectors stored in a
  gitignored disposable cache and lexical fallback when absent. Rung 3 is
  allowed only after the counting/LSA rungs fail the same detector benchmark,
  because it adds a model binary/runtime dependency even if it remains
  non-generative and deterministic.
- **Rung 1 v1 result (2026-07-08):** built and measured, not shipped. The
  pinned paragraph/Jaccard co-occurrence expansion worsened the benchmark from
  9/28 misses (0.321) to 15/28 misses (0.536), recovered no baseline misses,
  and regressed six baseline hits. The tool remains a probe artifact and is
  not routed through `AGENTS.md`; ladder advancement returns to the operator
  before any LSA or embedding work.
- **Rung 1 v3 result (2026-07-08):** lexical-first retrieval plus
  co-occurrence recall suggestions plus link-neighbor suggestions improved the
  benchmark from 9/28 misses (0.321) to 4/28 misses (0.143). It recovered
  five baseline misses and regressed none. Because the link-neighbor assist
  was added after the v1 failure diagnosis rather than in the original pinned
  brief, treat this as a strong ship candidate pending operator approval, not
  an automatic `AGENTS.md` routing change. The 10% ladder bar is still not
  cleared.
- **Rung 1 v4 result (2026-07-08):** adding driverless structural aliases
  derived only from authored structure (path words, selected frontmatter
  fields, headings) improved the benchmark to 26/28 hits, 2/28 misses, miss
  rate 0.071. It cleared the 10% detector bar without hand-authored synonym
  pairs. Remaining misses: machine migration and regime attribution. Because
  v4 was developed after inspecting v1/v3 failures, treat it as successful
  engineering evidence that deserves cold review/research before routing as
  the default search door.
- **Rung 1 v4 adoption note (2026-07-08):** operator approved documenting v4
  for agent use as the current wiki/vault topic-search door. This is not the
  same as building the full 3.9 statistical substrate or shutter. The tool path
  is `tools/wiki_deriver/vault_search.py`; docs live at
  `tools/wiki_deriver/README.md`; recommended flags are
  `--recall-assist --link-neighbor-assist --structural-assist`. Supplemental
  confirmation: on a fresh Markdown-only 60-query challenge, v4 hit 57/60
  (miss rate 0.050), while an `rg` mechanical baseline hit 9/60 (miss rate
  0.850). A broader `.md/.py/.json` search remains scratch-only and is not the
  default contract.
- **Rung 1 v5 build plan (2026-07-08, plan-only):** next build is a
  config-owned two-lane search door, not another agent convention. The agent
  supplies only the query. The tool owns: `vault_root`, `periphery_roots`,
  `deny_roots`, allowed extensions, max file size, lane labels, and a scope
  receipt. Output must always separate `VAULT` (durable workspace memory) from
  `PERIPHERY` (read-only intake context, not banked, not canon, not promoted).
  Promotion/import is a separate explicit tool/action and never a side effect
  of search. Initial periphery root: `C:\Users\meme\Downloads`; default deny
  roots include the working vault, management vaults, sync stage, `_HANDOFFS`,
  `codex_tmp/`, runtime/cache folders, and conversation archive until that
  larger corpus gets its own mode. Feasibility probes:
  `codex_tmp/two_lane_search_probe.py` and
  `codex_tmp/two_lane_search_configured_probe.py`; the configured probe proved
  the tool can skip a bad periphery root (`C:\VMShare\NT8lab`) with a receipt
  instead of relying on an agent to remember the rule.
- **Rung 1 v5 built (2026-07-08):** shipped the config-owned two-lane search
  as `tools/wiki_deriver/two_lane_search.py`, integrated through
  `tools/wiki_deriver/vault_search.py --two-lane`, with config at
  `tools/wiki_deriver/vault_search_config.json` and generated outputs at
  `_DERIVED/two_lane_search_last.json` / `.md`. Step test: happy path scanned
  740 vault Markdown docs and 343 Downloads `.md/.txt` periphery docs; bad
  periphery root `C:\VMShare\NT8lab` was skipped with a scope receipt and zero
  periphery docs. Periphery remains read-only intake; search never promotes,
  copies, moves, or imports.
- **Rung 1 v5.1 acceleration plan (2026-07-08, plan-only):** if v5's Python
  scan is too slow for broader periphery, build a disposable SQLite FTS5 index.
  The active bundled Python already has SQLite FTS5 available (verified
  2026-07-08; SQLite 3.50.4). The index is a cache, not truth: rebuilt from
  source files, safe to delete, local-only, no service, no installer, stdlib
  `sqlite3` only. Store lane, root, relative path, absolute path for periphery,
  extension, mtime, size, and text. Query output still uses the same two lanes
  and scope receipt. This does not replace v4 structural search; it is the
  speed layer for the same lane contract.
- **Search-routing interceptor candidate (2026-07-08, booked only):** do not
  build a grep wrapper, pre-search hook, tool interceptor, or redirector now.
  Trigger: the reworded AGENTS.md topic-search imperative plus measured-distrust
  line are tested in a fresh no-hints session and the agent still greps a topic
  query blind. Until then, keep routing as wording plus documented tool use.
- **Vault-search doorway fix (2026-07-09):** added
  `tools/wiki_deriver/vault_search.ps1` so the AGENTS.md topic-search command
  resolves the bundled Python runtime itself instead of depending on `python`
  being on PATH. This is a tool-doorway fix, not a prompt workaround.
- **Blind OOS holdout result (2026-07-09):** first true out-of-sample test of
  v4. Query set (15 items) was authored by Claude in chat blind to the tool's
  scorer, co-occurrence table, and favored notes; targets were assigned by
  human judgment AFTER queries were frozen. Recall miss@10 on 13 real-target
  queries: rg 1.000 (13/13), v4 0.308 (4/13), two-lane vault-lane 0.385
  (5/13). Precision on 2 NO_TARGET queries: both v4 and two-lane returned
  confident-looking top-3 answers on both (2/2 FP); rg clean. Periphery lane
  integrity in two-lane: clean, no leaks. Verdict per pre-committed rule:
  **PARTIAL** (0.20 < 0.308 < 0.33) — some of the prior 5% in-sample gain was
  in-sample. The 10% ladder bar is not cleared on this unseen set. Do not add
  features to chase this without a dev/holdout split. Findings and per-query
  outputs: `_worker_reports/TASK_blind_holdout_eval_findings_20260709.md`;
  frozen query set: `codex_tmp/holdout_blind_v1.json`; raw per-query outputs:
  `codex_tmp/holdout_run_20260709/`.
- **If fired -- backend options, decided at build time, deliberation banked
  2026-07-07:** (a) use the existing local pgvector instance already
  installed/operated for the operator's open-brain project -- lower build
  cost and mature at scale, but it adds the vault's first running-service
  dependency and a `needs-machine-setup` migration row; if chosen, isolate
  via a dedicated schema, and keep the DB plus connection strings inside the
  local-only boundary, never bridge-eligible; or (b) use a `sqlite-vec`
  single-file index living gitignored inside the vault -- zero services and
  clone-is-migration portability, adequate at the current ~4K-file corpus
  scale. Either way the index is a disposable cache computed from committed
  source, rebuilt on demand, never a source of truth, and every consumer must
  degrade to lexical rather than fail when the index is absent. Current
  architecture preference: default to `sqlite-vec` unless a later build spec
  proves pgvector is necessary, because clone portability and zero running
  services match the migration doctrine better than adding a machine-local
  service dependency.
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
  is the first concrete second-domain seed, and
  `_DIMENSIONS/no-host-content/no_host_content_j_seed_20260703.md` is an
  early creative/comedy dimension seed. Together they make trigger
  condition (1) more concrete; the corpus is still not deep enough,
  lexical/index failure has not been measured, and no cross-domain mixing
  failure has recurred.
- **Status:** booked candidate for the full substrate/shutter; v4 Markdown
  vault search is documented for agent use, but broader text search, recency
  reranking, LSA, embeddings, and shutters remain unbuilt.

### 3.10 Newsroom wiki architecture candidate -- BOOKED CANDIDATE (trigger not fired)
- **Pointer:** `_FRAMEWORK/newsroom_wiki_architecture_candidate_20260706.md`
  books a candidate architecture pattern: current spine plus structural
  provenance in Layer 1 and a future derived, scoped, decaying trust ledger
  over external sources. It is not a replacement architecture and not a
  build authorization; run only the candidate's own source-volume /
  trust-event screen when its trigger fires.

### 3.11 Source census -- BUILT
- **Job:** count external source/intake notes and their trust-relevant
  events, emitting `_DERIVED/source_census.md` and `.json` with n beside
  every count and `UNSTATED` where frontmatter lacks scope/source fields.
- **Why it earns its place:** this is the newsroom architecture
  candidate's §6 screen as a dumb tool. It measures the source-volume /
  event-count trigger without building the trust ledger.
- **Status:** built as `tools/wiki_deriver/source_census.py` on
  2026-07-06. v2 run: 5 distinct external origins, median 0 explicit
  trust-relevant events/source, screen verdict `DO-NOT-BUILD-YET`.

### 3.12 Trigger watcher -- BUILT
- **Job:** parse the roadmap and newsroom candidate for booked triggers,
  classify each as `FIRED`, `NOT-FIRED`, or `NOT-MACHINE-CHECKABLE`, and
  emit `_DERIVED/trigger_status.md` and `.json`. The watcher reports only;
  it never fires builds.
- **Why it earns its place:** a fired trigger in 3.2 was previously noticed
  only by a cold external review. This removes the "remember to reread the
  roadmap" tax while preserving operator control over build decisions.
- **Status:** built as `tools/wiki_deriver/trigger_watcher.py` on
  2026-07-06. v2 run: 1 fired entry, 2 not-fired entries, and 22
  not-machine-checkable entries.
- **Booked refinement (do not build):** split `FIRED` into
  `TRIGGER-EVIDENCE-RECORDED` (measured/banked/not actionable; must not hold
  runner exit 1), `FIRED-ACTIONABLE`, and `FIRED-DEFERRED`; current examples:
  3.9 = evidence-recorded, 3.2 = actionable. Trigger to build: the ambiguity
  causes an actual session misread, or the runner exit code is wrongly held by
  an evidence-only trigger and it matters.

### 3.13 Deriver runner / flags aggregator -- BUILT
- **Job:** run the existing Layer 3 dumb derivers in config-owned order,
  collect exit classes and flag counts, and emit one session-start dashboard
  at `_DERIVED/derivers_last_run.md` / `.json`.
- **Why it earns its place:** the vault now has enough separate flag emitters
  that "remember which deriver to run" is itself head-load. The runner
  sequences them without merging their logic: each tool stays dumb and
  independent; the runner only invokes, times out, records, and points at the
  source report. It never fixes anything and is not a daemon.
- **Trigger:** fired. More than three flag-emitting tools exist
  (link checker, trigger watcher, staleness, capture integrity, retrieval
  detector, session index), and the session-start ritual needed one dashboard
  instead of many commands.
- **Status:** built as `tools/wiki_deriver/run_derivers.py` with config at
  `tools/wiki_deriver/run_derivers.config.json` and doorway
  `tools/wiki_deriver/run_derivers.ps1` on 2026-07-09. Retrieval detector is
  config-present but disabled by default; staleness runs last; timeouts are
  killed and recorded as tool failures; `_DERIVED/derivers_last_run.md/.json`
  are excluded from staleness self-reference pressure.

### 3.14 External URL-rot checker -- BOOKED, NOT BUILT
- **Job:** check external URLs referenced by vault notes and flag dead or
  unstable links without fixing them.
- **Why it earns its place later:** external source links are weaker than
  vault paths and can rot outside the Git substrate, but this should wait
  for enough external URL volume or an observed dead-link failure.
- **Trigger:** external-URL count grows materially or a dead link causes an
  observed failure.
- **Status:** booked, not built.
- **Corroboration note (2026-07-09):** independently corroborated by external
  research intake; trigger unchanged.

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

10. **Dependency manifest + catalog renderer (5.1)** -- built (TASK_021).
11. **Offline bundle + Python pinning (5.2)** and **drift detection +
    portability stub (5.4)** -- after the manifest exists.
12. **Windows bootstrap installer (5.3)** -- after the manifest and offline
    bundle exist.
13. **Deriver runner / flags aggregator (3.13)** -- built. One session-start
    doorway runs the existing derivers and writes `_DERIVED/derivers_last_run.*`.
14. **External URL-rot checker (3.14)** -- when external URL volume grows
    materially or a dead external link causes an observed failure.

*Candidates 3.4a / 3.5a / 3.5b / 3.9 / 3.14 are deferred with
their parents or explicit triggers and build only when their drift/scope
conditions recur.*

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

### 5.1 Dependency manifest + catalog renderer -- BUILT
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
- **Status:** built as TASK_021. Artifacts: `deps/dependencies.yaml`,
  `deps/tools/render_catalog.py`, `deps/catalog.md`, and
  `_worker_reports/TASK_021_dependency_manifest_build_findings.md`.

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
- **Status:** not built; manifest prerequisite met, no build authorization in
  this rehearsal.

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
- **Measured trigger evidence:** the 2026-07-07 migration rehearsal needed
  `git -c core.longpaths=true clone` to check out the working vault on
  Windows and needed explicit clone-root/config overrides so dumb tools and
  bridge staging did not silently use machine-local absolute paths. This is
  evidence for the bootstrap-installer need, not a build authorization.
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
- **Measured trigger evidence:** the 2026-07-07 migration rehearsal found
  clone portability depends on separate machine state and path configuration:
  the conversation archive lives outside the repo, the management bridge and
  auto-sync configs carry absolute paths, `databento/` and installer artifacts
  are correctly absent/heavy, and derived-staleness reported 3 stale artifacts
  in the scratch clone. This records the drift/portability need; it does not
  build 5.4.
- **Status:** not built; manifest prerequisite met, trigger evidence recorded,
  no build authorization in this rehearsal.

## 6. The one rule under all of it

Every tool here is dumb in the same disciplined way: it **flags or computes,
never interprets or fixes; it regenerates from the Git substrate, never
hand-maintains a copy that drifts; and it is built only when real input data
exists for it.** The smart, judgment-bearing work (distillation, fixing) is
done cold, occasionally, by a separate pass — never by the warm working
agent, whose attention stays on the actual work. The tools do the keeping;
the agent does the thinking. That is the whole system, applied to its own
tooling.

## 6. Conversation archive track -- rescue built, ongoing infrastructure booked

Decision record:
`_FRAMEWORK/conversation_archive_decision_record.md`

This is a separate local-only vault track for raw conversation/session tape.
It is intentionally outside the working vault so raw transcripts do not
contaminate the working wiki substrate.

### 6.1 Watch registry + sweeper -- BOOKED, NOT BUILT
- **Job:** scheduled dumb copy of new sessions from registered roots into the
  conversation archive.
- **Why it earns its place:** capture is irreversible and retrieval is
  improvable; once usage evidence exists, a sweeper protects new tape without
  asking warm agents to remember it.
- **Trigger:** operator actually opens the archive to answer a question, or
  about a month of un-rescued sessions worth keeping accumulates.
- **Status:** booked, not built. One-shot rescue completed 2026-07-02.
- **Status note:** current `rescue_sweep.py` is a rescue seed,
  non-conforming to `_FRAMEWORK/capture_tool_spec.md` (machine facts
  hardcoded, registry written but not read); refactor to conformance happens
  when the forward-capture trigger fires, per the spec's grandfather clause.

### 6.2 Second logger instance -- BOOKED, NOT BUILT
- **Job:** run existing logger v1.1 with a second `--config` against the
  conversation archive repo.
- **Why it earns its place:** the archive should get the same Git substrate as
  the working vault once ongoing sweeping exists.
- **Trigger:** same trigger as the sweeper; they ship together.
- **Status:** booked, not built.

### 6.3 Session-index deriver -- BUILT
- **Job:** derive a metadata-only table joining archived session transcripts,
  worker-report frontmatter `session_ref` values, and git/file timestamps
  into `_DERIVED/session_index.md` and `_DERIVED/session_index.json`.
- **Why it earns its place:** browsing raw folders stops scaling once enough
  tape exists, and task notes need a stated/inferred session bridge without
  quoting transcript content.
- **Trigger:** fired by the conversation-archive rescue and follow-on
  session-link convention work.
- **Status:** built as `tools/wiki_deriver/session_link_index.py` on
  2026-07-07 from `_worker_reports/TASK_session_link_index_20260707.md`.
  First run: 7 archived sessions, 0 stated links before the findings report,
  131 inferred links, 5 orphan sessions, and 1 copied task brief missing
  `session_ref` after the convention date.

### 6.4 Unified cross-vault timeline -- BOOKED, NOT BUILT
- **Job:** merge-sort git logs from all vaults into one chronological
  add/modify/delete ledger.
- **Why it earns its place:** some questions are temporal across vaults, not
  local to one substrate.
- **Trigger:** first real question of when X happened relative to Y across
  vaults is answered manually.
- **Status:** booked, not built.

### 6.5 Session-to-commit crosswalk -- BOOKED, NOT BUILT
- **Job:** join transcript tool-call records and timestamps to working-vault
  commits.
- **Why it earns its place:** it answers which conversation produced a given
  change.
- **Trigger:** first real "which conversation produced this change" question.
- **Status:** booked, not built.

### 6.6 Cross-vault search wrapper -- BOOKED, NOT BUILT
- **Job:** grep multiple vault roots and label hits by vault.
- **Why it earns its place:** one search surface beats repeated manual greps
  once cross-vault retrieval is actually asked for.
- **Trigger:** first time "search everything" is asked and two greps annoy.
- **Status:** booked, not built.

### 6.7 Vault spawner + profiles -- BOOKED, NOT BUILT
- **Job:** script and profile config for git init, skeleton, logger config,
  and deriver selection.
- **Why it earns its place:** doing vault creation by hand twice provides the
  template data for the third time.
- **Trigger:** creation of vault number three.
- **Status:** booked, not built.

### 6.8 Archive-to-wiki distiller -- BOOKED, NOT BUILT
- **Job:** cold Layer-4 pass that reads tape and writes settled notes into the
  working wiki.
- **Why it earns its place:** raw transcript tape is evidence, not orientation;
  distilled notes are what belong in the working wiki.
- **Trigger:** a months-long arc whose reasoning nobody remembers, after Layer
  3 navigation exists.
- **Status:** booked, not built.

### 6.9 SQLite ingestion -- BOOKED, NOT BUILT
- **Job:** ingest Codex SQLite stores as a second Codex source format.
- **Why it earns its place:** JSONL is the Phase-1 source; SQLite only matters
  if it holds conversations the JSONL sweep misses.
- **Trigger:** evidence that the JSONL sweep misses conversations present in
  `C:\Users\meme\.codex\*.sqlite`.
- **Status:** booked, not built.

### 6.10 Commit-noise auditor -- BOOKED, NOT BUILT
- **Job:** compute git-log hygiene stats and flags over the working vault.
- **Why it earns its place:** commit noise can degrade future derivers, but
  should be measured before it becomes another hand-maintained concern.
- **Trigger:** build when commit noise is next suspected of degrading a
  deriver.
- **Status:** booked, not built.

### Inbox pressure signal -- DEAD
- **Job:** none.
- **Why it does not earn its place:** it depended on the dropped inbox-capture
  design.
- **Trigger:** dead unless inbox capture is ever revived.
- **Status:** dead.
