---
title: Wiki Infrastructure — Layer Architecture
status: living-reference
created: 2026-06-24
purpose: Durable, reproducible reference for the Git-backed, agent-operated wiki infrastructure. Documents the four-layer design AND the concrete files/steps used to build Layer 2, so the mechanism can be recreated against any vault. This note is a view; the source files it points at are the authority.
home: _FRAMEWORK/ (sibling to PATTERNS.md)
related: _FRAMEWORK/PATTERNS.md (pattern "higher-layers-don't-rescue-lower-layers" is the abstract principle this architecture instantiates)
---

# Wiki Infrastructure — Layer Architecture

A domain-agnostic design for a plain-text (Markdown) knowledge base edited by both humans
and AI agents, versioned by Git, and kept coherent over time by **deriving views rather than
hand-maintaining them**. Trading is only the test-bed; the same infrastructure points at any
vault. Only the Layer 1 conventions and the `.gitignore` profile are domain-specific.

> **This note is a view, not the source.** Where it describes a file, the file on disk is the
> authority — if they disagree, the file wins and this note is stale. (That is the system's own
> rule applied to its own documentation.)

---

## 1. The spine (one sentence)

Smart agents **write** (Layer 1) → a dumb tool **records everything** to Git (Layer 2) → a
deterministic tool **derives views** (Layer 3) → a cold agent **distills ideas** (Layer 4) →
all for **the reader**. Under it all: **anything that can drift should rebuild itself — compute
it, don't keep it.**

## 2. Why this shape (the load-bearing principles)

- **Capture is the irreversible act; retrieval is improvable.** You cannot retroactively
  capture history you did not commit. So capture richly and cleanly now; future tools mine a
  clean history well and a noisy one badly.
- **Git tracks bytes, not meaning.** Meaning survives only if an agent *writes it into the
  content* (the what-and-why). No future algorithm retrieves what was never captured.
- **Derive the view, don't maintain it.** Every scoreboard / ledger / signal / summary is
  computed from source on demand — never a hand-kept copy that drifts.
- **Agent commit noise is the single biggest threat.** Commit *settled units of work*, not
  keystrokes. A complete-but-noisy history is analytically useless.
- **Decoupled through the filesystem.** No layer triggers another. Agents write files; the
  logger sees files change; derivers read committed files. This decoupling is what makes the
  logger self-healing.
- **A rule earns its place only if Git or a dumb tool genuinely can't do the job.** Every agent
  rule is a tax on attention; push everything possible down to the dumb layers so the agent's
  capability goes to the task, not the bookkeeping.

This architecture is the concrete instantiation of the `PATTERNS.md` principle
**"higher-layers-don't-rescue-lower-layers"**: each layer must be correct on its own; a clever
upper layer cannot fix a lossy capture beneath it. Capture (Layer 2) is therefore built first
and held to the highest correctness bar.

## 3. The four layers

**Layer 1 — Agents write (warm · faithful capture).** The intelligent layer doing the work.
Reads what it needs, edits content, and writes *meaning* into the files as it goes. Job:
capture faithfully. (Conventions in Section 6 — not yet banked into AGENTS.md as of this note.)

**Layer 2 — The dumb logger (mechanical · BUILT).** An always-running tool that auto-commits
settled states to Git. No understanding; captures bytes, never interprets. This is the
foundation everything else sits on. **Built and tested (TASK_006/007); see Section 5 for the
reproducible recipe.**

**Layer 3 — Mechanical derivation (deterministic · not yet built).** Reads structured fields
(YAML `status:`, history rows) and Git metadata to *compute* views: survivor-ledger /
dead-scoreboard, per-note signals (recency, churn, status, centrality). No model needed. Output
is files, captured by Layer 2 on its next pass.

**Layer 4 — Cold distillation (agent · not yet built).** A *fresh* agent, run on idle time,
reads committed clusters and compresses them into compact "ideas" using hindsight. Lossy, so it
points back to sources and is validated before trusting. Never the same context as the warm
Layer 1 agent.

**The Reader.** The audience everything serves — human or future agent orienting. Not a
rule-bearer; the reason the rules exist. When a rule is ambiguous, resolve it for the reader.

**The two axes that are the real content:** *warm vs. cold* (Layer 1 writes in-the-moment;
Layer 4 reads later with distance — never the same context window) and *smart vs. dumb* (agents
think; the logger and deriver do not).

## 4. Forensics come after (deliberate deferral)

Repo growth, chronology, biggest-files, cadence — all of it is **derivable from Git history at
any time** by a later read-only forensic tool. The logger therefore keeps **no continuous size
log** (that would be hand-keeping a fact Git already holds — a violation of "compute it, don't
keep it"). The one thing the logger does carry forward is *prevention*, not *recording*: the
size guard (Section 5.3), because a blob committed to history is the one painful-to-undo
mistake and detection-after-the-fact cannot prevent it.

---

## 5. Layer 2 — the reproducible recipe (how to rebuild the logger)

This is the recreate-it section. The authoritative artifacts are the files themselves; this
documents their roles, the build order, and the non-obvious correctness details that a
re-implementation must preserve.

### 5.1 The files (the manifest)

| File | Role |
|---|---|
| `tools/wiki_logger/wiki_logger.py` | The logger. Stdlib-only Python, no file-watch dependency. The whole mechanism. |
| `tools/wiki_logger/wiki_logger.config.json` | Production config (NT profile): vault path, timings, runtime dir, guard thresholds. |
| `tools/wiki_logger/wiki_logger.test.config.json` | Test config: tight timings + tight guard thresholds for the build tests. |
| `.gitignore` (vault root) | **The authoritative exclusion list.** The config does NOT enforce exclusions — the `.gitignore` does. This is the load-bearing safety artifact. |
| `tools/wiki_logger/WikiLogger_v1.0.bat` | Version-stamped launcher; sets the console title before Python loads. |
| `tools/wiki_logger/wiki_logger.bat` | Alias forwarding to the versioned launcher (keeps old references working). |
| `tools/wiki_logger/runtime/` | Runtime dir: `wiki_logger.log`, `status.json`, `trigger_now` (manual trigger), `guard_tripped.txt`. **Gitignored — must never self-commit.** |

### 5.2 The mechanism (design invariants — must not regress)

- **Self-healing / stateless.** Every cycle re-derives "what is uncommitted?" from
  `git status --porcelain`. No stored cursor, no own state file the recovery path depends on.
  Survives shutdown/reboot; catches up on restart with no special logic. (This is the one piece
  of necessary cleverness — it is why a reboot mid-work loses nothing.)
- **Three triggers, one path.** File-change (debounced), a manual `trigger_now` file, and a
  periodic safety net all call the same `commit_now()`. No separate code path for any of them.
- **Debounce defines "a unit of work."** On a detected change, wait for a quiet window
  (default 90s) with no further changes, so a burst of related edits commits as one settled
  unit. More edits during the window reset the timer.
- **Never interprets.** Commit message is mechanical: `date — N files — folder1/, folder2/`.
  The *meaning* lives in the file content (the agent wrote the why), never in the commit message.
- **NON-OBVIOUS CORRECTNESS DETAIL (preserve this):** the staged-file list is derived with
  `git diff --cached --name-only -z` *after* `git add -A` — **not** from `git status --porcelain`.
  Reason: porcelain collapses each untracked directory into a single line, which undercounts
  the committed file set. A re-implementation that counts from porcelain will reintroduce this
  bug. (Discovered and fixed during the TASK_006 self-healing test.)

### 5.3 The size guard (prevention, standing per-commit)

Before each commit, the staged set's total size and largest single file are checked against
configurable thresholds (`guard_total_commit_mb`, default 50; `guard_single_file_mb`, default
10; either set to 0 disables that half). On breach: `git reset` to un-stage, refuse the commit,
raise `CommitGuardTripped`, print a loud banner **once**, write `runtime/guard_tripped.txt`
with the breach dossier (sorted by size + resolution hint), and hold `GUARD_TRIPPED` state.
Cleared automatically on the next clean commit.

> **KNOWN OPERATIONAL BEHAVIOR (not a bug — know it before running unattended):** once tripped,
> the guard wedges *all* capture, not just the offending file. The loop keeps re-detecting the
> same dirty state and re-tripping until a human resolves it (gitignore the file, or remove it).
> Consequence: a single stray oversized file silently halts committing of the *good* work
> alongside it. This is the correct safety tradeoff (better to halt than to commit a data blob),
> but it means `GUARD_TRIPPED` / `guard_tripped.txt` are signals you must actually see — which
> is why the logger is made findable (titled window, `status.json`). Resolution: read
> `guard_tripped.txt`, gitignore or delete the offending file, and the next cycle commits
> normally and clears the flag.

### 5.4 Build order (and the human gate)

1. Write the `.gitignore` FIRST (data exclusion before any commit).
2. **Phase A — preview, then HALT for human authorization.** Compute what *would* be committed
   from Git's own staged list (not a filesystem glob), prove no data files are in the set, prove
   the kept oddballs survive, check total size against the expected baseline, confirm repo root
   == vault root, and check whether history already contains data. Stop. Do not commit.
3. **Phase B — after human authorization:** make the baseline commit, build the running loop,
   run the two must-pass tests (self-healing reboot recovery; echo-loop / no self-commit), then
   the size-guard tests.
4. Identity (TASK_007): version-stamped title + launcher so the operator can confirm it's
   running. Note: Task Manager's image name still reads `python.exe` (Python cannot rename its
   own image); a packaged `.exe` is deferred to a later pass.

### 5.5 Running it

Launch `tools/wiki_logger/WikiLogger_v1.0.bat` in a real interactive terminal (not inside an
agent session — agents can only run bounded subprocesses that die with the session). It opens a
console titled `Wiki Logger v1.0` and runs until Ctrl+C / window close. Autostart (Startup
folder / Task Scheduler) is documented, not auto-installed. **A note authored while the logger
is not running is captured by nothing — start the logger before banking durable work.**

### 5.6 Known discrepancy to reconcile (flagged, not silently fixed)

The production config's `expected_gitignore_patterns` lists `tools/wiki_logger/*.log`,
`tools/wiki_logger/state/`, and `wiki_logger.log`, and the actual `.gitignore` also includes
`*.zip / *.gz / *.tar` archives. The config field is a *documented expectation*; the
`.gitignore` is the *authority*. They are close but not identical — the `.gitignore` is the
source of truth. If they ever need to agree exactly, fix the config to match the file (or, per
"compute it, don't keep it," stop duplicating the list in the config and point at the
`.gitignore`). Recorded here so a rebuild does not treat the config list as authoritative.

---

## 6. Layer 1 conventions (the writer contract — NOT yet banked)

These belong in `AGENTS.md` as an operating contract, added deliberately when you want agents
acting on them. Stated here for completeness; this note documents them, it does not enact them.

- **Write down what you changed, with a date** — in the file it happened to (a history row).
- **Always write *why* on meaningful changes** — including meaningful deletions. The one thing
  Git can't reconstruct.
- **Delete and clean up freely** — Git keeps the old version, so nothing is lost. Trivial tidying
  needs no note; a meaningful cut gets a one-line why. (This replaces any "mark-it-superseded"
  rule — preservation is Git's job, not the agent's.)
- **If it's part of a bigger thread, name it** — what you set out to do, where it heads. Optional.

Governing principle: a rule earns its place only if Git or a dumb tool genuinely can't do the
job. Keep the contract light; the tools do the keeping, the agent does the thinking.

---

## 7. Status (as of 2026-06-24)

- **Layer 2 (logger):** built, tested, version-stamped. Ready to run; launch is a manual step.
- **Layer 1 conventions:** designed (Section 6), NOT yet banked into AGENTS.md.
- **Layer 3 (deriver) / Layer 4 (distiller):** designed, NOT built. Deferred until the logger
  has run and accumulated history worth deriving from.
- **Forensic growth/health view:** deferred; derivable from Git history when wanted.
- **Newsroom persona skin** (Reporter/Recorder/Indexer/Editor/Reader): a presentation mnemonic
  only. Build against the layer terminology; use the personas for explaining, never for building.

---

## 8. When to build Layers 3 and 4 (the trigger, not a schedule)

Layers 3 and 4 are deferred on purpose, and the trigger for building them is **accumulated
material to work on**, not elapsed time or "we're on a roll." Building either before there's
something real to derive from produces a tool that runs against near-empty inputs and tells
you nothing.

- **Layer 3 (deriver) earns its keep when** the vault holds enough captured history —
  findings, status-row progressions, notes across multiple sessions — that a freshly computed
  scoreboard / freshness-signal view would surface structure a human would otherwise miss. As
  of 2026-06-24 the history is ~one day of mostly-infrastructure commits; that is not yet
  enough. Let the logger accumulate real cross-session work first.
- **Layer 4 (distiller) earns its keep when** there is a months-long arc of work whose pattern
  no one remembers in full — that is what a cold, hindsight-equipped pass can compress. It is
  the riskiest layer (a model inferring relationships from prose can be confidently wrong), so
  it comes last, after Layer 3, and only with validation.
- **Build order is 3 before 4**, and the capture layer (Layer 2, running now) is precisely
  what makes both possible later. The disciplined move after building capture is to *use* it
  — let history accumulate — not to immediately build the layers that consume history before
  any exists.

This subsection sharpens §7's one-line "deferred until the logger has run and accumulated
history worth deriving from": the trigger is **material**, not calendar — and Layer 3 is
the gate Layer 4 sits behind.

## 9. Retrieval research decisions (2026-06-24) — what changed Layers 3 and 4

Research was run on how to build the derived layers; the full evidence is
banked at `_RESEARCH/two_tier_retrieval_2026.md`. This section records only
the decisions that change the build. Where this disagrees with the research
note, this section carries the decision and the research note carries the
support.

History row: `2026-06-24 | ADDED | retrieval research decisions — sharpened
Layer 3 to compute Git-history structural signals, hardened Layer 4 to
two-stage citation verification, replaced the note-count trigger with a
measured-failure trigger, and deferred vector search until lexical
demonstrably fails.`

**The architecture is validated, not speculative.** Our first-order /
structural-index / on-demand-summarizer shape independently matches built and
benchmarked systems — Git-Context-Controller (pointers-to-Git-truth index),
DiffMem (Git + Markdown + BM25, no vectors), zilliztech/memsearch (Markdown
is truth, vector index is a disposable shadow). The one place we are *more*
disciplined than the field: nothing semantic is ever persisted — GraphRAG,
Zep, Mem0, and Letta all persist LLM-generated semantic content and inherit
its staleness. We regenerate semantics on demand and persist only verifiable
structure.

**The trigger to build is measured failure, not a note count.** The earlier
"~1000 notes" trigger is dropped. The literature gives no defensible
document-count threshold. Build the next layer when there is real captured
material to derive from (Layer 3) and add vector search only when lexical
search (grep/BM25) *measurably* misses notes that exist — synonym/paraphrase
recall failures on a real query. We may never need vectors.

**Layer 3 computes Git-history structural signals, deterministically.** The
sharpened Layer 3 is not only a content-parser (status rows, verdicts,
headings) — its load-bearing, can't-hallucinate, already-have-the-data half
is mining `git log` for: change-frequency (churn) hotspots, temporal
coupling (which notes change together), recency, and backlink centrality.
Prior art: Code Maat / *Your Code as a Crime Scene*. Starting thresholds to
borrow and then tune on our own repo: **min 5 revisions, min 5 shared
revisions, 30% coupling, max changeset 30, same-day commits collapsed to one
logical change.** Keep it dumb: it flags and tabulates, it never interprets,
it regenerates from source, it never hand-maintains. The deriver merges two
halves — content-parsed views (survivor-ledger, open-threads, artifact-index)
AND Git-history signals (churn, coupling, centrality).

**Layer 4 requires TWO-STAGE citation verification — existence is not
enough.** This is the hardest finding and it changes the Layer 4 contract.
A citation that *exists* tells you almost nothing about whether the source
*supports the claim*: SourceCheckup (Nature Communications, 2025) found
50–90% of LLM responses not fully supported by their own cited sources, ~30%
of even GPT-4o-with-search statements unsupported. So Layer 4 must:
(1) existence-check citations mechanically (placeholder-ID substitution kills
fabricated references), AND (2) support-check via an NLI entailment model
(does the cited source entail the claim?). RAGAS-style LLM-judge faithfulness
is a secondary flag only — LLM judges miscalibrate. Default to "draft, then
attach-and-verify citations" (P-Cite); the summary is generated cold,
returned, and not persisted, with its support-check score surfaced alongside.

**Vector search is deferred, and if ever built, is a disposable shadow.**
Ship Layer 3 + lexical (grep/BM25) first. If measured recall failure
warrants vectors: pgvector in our existing Postgres, text-embedding-3-small,
hybrid with BM25 from day one, reranker only if top-3 precision is still
inadequate — and the vector index is always a rebuildable cache over the
Markdown truth, never the source.

**What this research mostly told us: build less.** Skip vectors, defer the
embedder, and note that Layer 3's most valuable signals are derivable from
`git log` we already have. The rigor removed scope rather than adding it.
