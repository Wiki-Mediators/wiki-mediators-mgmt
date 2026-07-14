---
title: "Wiki Mediators Export + Management Boundary Plan"
status: proposed-review
created: 2026-07-14
scope: reusable Wiki Mediators infrastructure, thin management vault, and
  cross-machine correspondence; explicitly excludes exporting NT8lab project
  corpus, data, credentials, or live runtime material.
related:
  - _FRAMEWORK/MANAGEMENT_PIPELINE.md
  - _FRAMEWORK/two_vault_architecture_prebuild_plan.md
  - _FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md
  - tools/management_bridge/management_vault_config.json
  - _HANDOFFS/knowledge_requests/KR-20260714-001_management_vault_completeness.md
---

# Wiki Mediators Export + Management Boundary Plan

## Decision to review

Adopt a three-surface model:

1. **Working vault (`NT8lab`)** remains the private, complete project source
   of truth. It is not a distribution package and is never pushed wholesale.
2. **Management vault (`wiki-mediators-mgmt`)** remains a deliberately thin,
   born-clean, project-specific orchestration view. It receives selected safe
   Markdown and management-scoped derived outputs only. It is not a tool
   runtime or a mirror of the working vault.
3. **Wiki Mediators toolkit** is a future separate reusable repository. It
   carries generic dumb tools as complete, runnable units, plus templates and
   clean-checkout tests. It carries no NT8lab strategy, research, data,
   secrets, account identifiers, or machine-specific configuration.

This plan answers RYRY request `KR-20260714-001` with the **different
boundary** option: management remains thin and honest; reusable tools move to
a dedicated infrastructure distribution surface rather than being copied
partially into management.

## Evidence and current defect

The current management allow-list exports selected files from
`tools/wiki_deriver/`, including `vault_search.py` and its README. It omits
`retrieval_common.py`, `run_derivers.ps1`, `run_derivers.py`, and the runner
config. Therefore a clean management checkout advertises commands it cannot
run. This is a boundary/documentation defect, not evidence that the management
vault should become a copy of the working toolchain.

The existing one-way architecture remains correct:

```text
working vault (private source truth)
        -> deterministic bridge + secret gate
management vault (thin orchestration state)
        -> GitHub main
```

## Boundary rules

### What the management vault may contain

- Safe project orientation and architecture notes needed to direct work.
- Management-scoped derived digests and indexes generated from the staged,
  allow-listed management tree.
- Management-specific documentation that says what the thin vault can and
  cannot do.
- Review-ready plans such as this one, after the bridge secret scan.

### What the management vault must not contain

- Partial runnable tool source or a README that promises unavailable commands.
- Working-vault data, strategy source, historical extracts, session tape,
  live-system files, credentials, account identifiers, or raw reports.
- Raw working-vault derived artifacts that can disclose denied paths by
  reference.
- Machine-local paths, remote URLs, or project-specific allow-lists presented
  as reusable defaults.

### What the reusable toolkit may contain

Each exported dumb tool must be a complete unit:

- entrypoint(s), local Python helpers, configs, and README;
- a minimal fixture or clean-checkout smoke test;
- generic templates/sample configuration in place of project values;
- a clear statement of inputs, outputs, and the rule that tools compute/flag
  and never interpret or repair project truth.

The toolkit must not import from a project vault at runtime. If a tool cannot
run with only its packaged files and documented standard/runtime dependency,
it is not ready to export.

## Staged implementation plan

### Phase 0 — review and freeze the boundary

1. Have Fable 5 review this plan and RYRY's request before changing bridge
   behavior.
2. Record any accepted deviations as edits to this plan, not ad-hoc additions
   to the management allow-list.
3. Do not merge correspondence branches into management `main`.

**Acceptance:** agreement that management is a thin orchestration view and the
toolkit is a separate future distribution surface.

### Phase 1 — make the management vault internally honest

1. Replace the copied working-vault `AGENTS.md` in the management build with a
   management-specific orientation note. It must say: do not run full-vault
   search or session-start derivers here; inspect the supplied management
   corpus and request full-vault work through a local worker.
2. Remove the partial `tools/wiki_deriver/` export entries from the management
   allow-list, including its runnable-command README, unless an entry is a
   static, explicitly non-runnable explanatory document.
3. Retain or regenerate only management-scoped indexes/digests from the staged
   management tree.
4. Add a clean-checkout honesty check: no executable/README command is
   advertised unless all required local files are included and the command
   succeeds in the management checkout.

**Acceptance:** a fresh management clone contains no broken advertised tool
door and its bootstrap accurately describes its limited role.

### Phase 2 — inventory candidate dumb tools

For each candidate from `tools/wiki_deriver/` or `tools/management_bridge/`:

1. State its generic job, inputs/outputs, and trigger that makes it worth
   carrying.
2. Trace its imports, shell wrappers, configs, fixtures, and required runtime.
3. Mark every project-specific assumption: path, vocabulary, status enum,
   source layout, secret scanner rule, or derived-schema dependency.
4. Classify it as **export now**, **needs adapter/template**, or **keep local**.

Initial candidates: vault search (with `retrieval_common`), deriver runner,
index/link/orientation derivers, and the bridge/secret gate. No candidate is
exported merely because source happens to exist.

**Acceptance:** each selected tool has an explicit dependency closure and no
unexamined import from NT8lab.

### Phase 3 — build the separate Wiki Mediators toolkit repository

Packaging order (adopted 2026-07-14 from KR-20260714-002, RYRY acceptance
review): 1. vault search closure (with retrieval_common), 2. orientation digest
builder, 3. capture-integrity checker — retrieval, orientation,
trustworthiness. Remaining instruments follow demonstrated demand.

Create a repository with this broad shape:

```text
wiki-mediators/
  README.md
  templates/
    vault-profile.example.json
    management-bridge.example.json
  tools/
    wiki_deriver/        # complete selected tool closures only
    management_bridge/   # generic bridge + safety gates only
  tests/
    fixtures/minimal-vault/
    clean_checkout_smoke.ps1
```

Use placeholders or profile inputs for vault roots, project vocabulary,
allow-lists, remotes, and secret patterns. Do not copy `NT8lab` configuration
as if it were a generic default.

**Acceptance:** a new empty fixture vault can install/run each exported tool
using only the repository, documented runtime prerequisites, and its example
profile.

### Phase 4 — correspondence that survives management sync

**Phase 4 prerequisite — SHIPPED 2026-07-14:** bridge v-next preserves `.git`,
local/remote machine refs, history, and the config-owned remote through normal
and `--force` rebuilds; scratch acceptance tests A–E and the auto-sync mismatch
refusal passed.

Use GitHub branches outside generated management `main` for correspondence:

- `machine/<machine-name>` branches for requests/responses; or a dedicated
  `correspondence` branch if the collaboration grows beyond two machines.
- `_HANDOFFS/knowledge_requests/` and `_HANDOFFS/knowledge_responses/` are
  valid within those correspondence branches.
- Main remains bridge-owned and is never the manual correspondence surface.

The first response to RYRY should be committed on `machine/nt8lab`, at the
requested response path, and cite this plan. It must be reviewed before push.

#### Minimal transport contract (v0, for review — smallest tested protocol)

This contract is now the operating protocol. The Phase 4 bridge prerequisite
shipped on 2026-07-14; delivery remains manually triggered,
operator-mediated, and low volume.

- **Paths (authoritative):** requests at
  `_HANDOFFS/knowledge_requests/KR-<date>-<seq>_<slug>.md`; responses at
  `_HANDOFFS/knowledge_responses/KR-<date>-<seq>_response.md`. One file per
  request and one per response; amendments are appended sections, not new
  files.
- **Branch ownership:** `machine/<name>` branches are writer-owned: only
  machine X commits to `machine/X`. Nobody rebases or force-pushes another
  machine's branch. Generated `main` is bridge-owned and never a
  correspondence surface.
- **Lifecycle:** fetch before read; read the other machine's branch read-only;
  write on your own branch; push manually on operator trigger. No watcher, no
  automation, and no autonomous delivery; this stands until a future
  deliberate decision.
- **Status vocabulary (frontmatter `status:`):** `ready-for-review` →
  `under-review` → `answered` → `closed`; `blocked` is permitted with a reason
  line. The writer of the file owns its status field.
- **Safety:** every correspondence file is repository-safe by construction:
  no secrets, credentials, machine-local absolute paths beyond illustrative
  ones, or non-exportable project data. Sensitivity is mandatory, and the
  committing worker runs the same secret scan the bridge uses before any
  push.
- **Non-interference test (acceptance):** after any bridge rebuild and push of
  `main`, all `machine/*` refs on the remote are unchanged and a fetched local
  copy survives. This test passed against a disposable local bare remote on
  2026-07-14 and remains a regression gate for bridge changes.
- **Divergence rule:** correspondence branches are append-only. If a branch
  diverges, the writer machine resolves it by appending a reconciliation
  section, never by rewriting history.

**Acceptance:** a bridge sync of `main` cannot overwrite or erase a fetched
machine correspondence branch.

### Phase 5 — controlled adoption

Only after Phases 1–4 pass:

1. Point a non-NT8lab pilot vault at the toolkit templates.
2. Run clean-checkout, no-change, secret-abort, and boundary-honesty tests.
3. Promote any proven generic behavior to the toolkit; leave project-specific
   behavior local.

**Acceptance:** a second vault uses the same tools without copying NT8lab
content or weakening the management separation.

## Explicit non-goals

- No wholesale NT8lab export or history rewrite.
- No change to live strategy/deployment material.
- No new background watcher, database, or agent process.
- No expansion of the management allow-list except review-safe plan and
  orientation material needed to evaluate this proposal.
- No automatic merge/push of cross-machine correspondence.

## Phase 0 accepted deviations — 2026-07-14

The operator approved Phases 0–2 with these boundary clarifications:

1. Bridge v-next `--force` must preserve the management repository's `.git`
   directory and configured remote instead of deleting and recreating them.
   This is a Phase 4 prerequisite, not part of the present Phase 1 staging
   edit. The requirement follows the 2026-07-03 `MGMT_HISTORY_RESET` recovery
   evidence: generated content may be replaced, repository identity may not.
2. "Thin" means **thin but informed**. Management keeps one explicitly
   non-runnable inventory of all built Wiki Mediators instruments, with their
   layer, job, inputs, and outputs. Source/config/runtime closures remain out.
3. Operational playbooks are Phase 2 portability candidates. Their generic
   procedures are reusable, but worked examples, project paths, statuses, and
   source citations must become profile placeholders or neutral fixtures
   before export.
4. Phase 3 remains blocked until the operator makes an explicit license
   decision for the public/reusable toolkit repository. No license is inferred
   from the current private vault or management repository.

Phase 1 also uses a config-driven `copy_as` rule to stage
`_FRAMEWORK/management_vault_AGENTS.md` as root `AGENTS.md`. The source is not
also allow-listed: the orientation file must appear exactly once in a fresh
management tree.

## Phase 2 portability and dependency inventory — 2026-07-14

No instrument is approved for as-is export in this pass. `NEEDS-ADAPTER`
means the generic job is worth carrying, but its complete closure must first
be packaged with profile inputs, neutral fixtures, and clean-checkout tests.

| Candidate | Generic job and carry trigger | Inputs → outputs | Dependency closure | NT8lab/project assumptions requiring adaptation | Classification |
|---|---|---|---|---|---|
| Vault index builder | Enumerate a vault when agents need a deterministic file/frontmatter/link map. | Markdown/files + profile → index JSON/Markdown and report | `build_vault_index.py`, `link_reference_checker.py`, link config, integrity config/module, Python stdlib | NT8lab ignore roots, frontmatter/status vocabulary, output/report paths and link policy | **NEEDS-ADAPTER** |
| Link reference checker | Resolve references when structural integrity needs a LOUD, non-repairing check. | Notes + index/config → broken-link JSON/Markdown | Checker, link config, capture-integrity severity config/module, optional index | Baselines, ignored patterns, external prefixes, source-role/status severity policy and report paths | **NEEDS-ADAPTER** |
| Orientation digest builder | Project a compact orientation surface when a large vault needs a deterministic first read. | Index + selected authoritative notes → digest/report | Builder, dynamic vault-index import, expected index schema | Hard-coded `nb_lib/strategy_specs` lanes, roadmap path, strategy status fields and collision rules | **NEEDS-ADAPTER** |
| Derived staleness signal | Flag stale derived outputs when source/tool/config mtimes advance. | Known artifact/source sets → staleness JSON/Markdown | Signal, index/link/orientation builders and config; test fixture | Explicit NT8lab artifact registry, generated markers, output names and source policies | **NEEDS-ADAPTER** |
| Source census | Count/classify research inputs when source coverage or verdict mix matters. | Configured source notes/frontmatter → census JSON/Markdown | `source_census.py`, stdlib, corpus conventions | `nb_lib/strategy_specs/source_artifacts`, excluded roots, source naming and verdict vocabulary | **NEEDS-ADAPTER** |
| Trigger watcher | Compute documented work triggers when roadmap thresholds need a dumb signal. | Roadmap, newsroom, census and retrieval data → trigger JSON/Markdown | `trigger_watcher.py`, Git CLI, upstream derived schemas | NT8lab roadmap/newsroom paths, trigger wording, schema keys and thresholds | **NEEDS-ADAPTER** |
| Deriver runner | Execute independent derivers in order when one dashboard/exit contract is needed. | Runner profile + full enabled closures → per-tool outputs and last-run dashboard | Python runner, PowerShell wrapper, runner config, every enabled tool/config and output parser | Absolute vault root, enabled set, LOUD/exit policy, timeouts, report schemas and self-reference exclusions | **NEEDS-ADAPTER** |
| Session-link index | Link notes to archived sessions when durable provenance must stay separate from conversation tape. | Notes/frontmatter + Git + archive → session index JSON/Markdown | `session_link_index.py`, Git CLI, readable external archive | Hard-coded `C:/VMShare/conversation_archive`, session-ref conventions and repository layout | **NEEDS-ADAPTER** |
| Capture-integrity checker | Flag capture/frontmatter/evidence problems when writer conventions need enforcement. | Corpus + Git + integrity/link profiles → integrity JSON/Markdown | Checker, `retrieval_common`, link checker, both configs, Git CLI | LOUD statuses, scratch roots, evidence markers, grandfathered vocabularies and path roles | **NEEDS-ADAPTER** |
| Term co-occurrence builder | Build lexical-neighbor data when recall assist needs a deterministic corpus signal. | Markdown corpus + tokenizer settings → co-occurrence JSON/Markdown | Builder + `retrieval_common`; Python stdlib | Corpus skip rules, stopwords, output paths and tuned thresholds | **NEEDS-ADAPTER** |
| Missed-retrieval detector | Benchmark paraphrase retrieval when search changes need regression evidence. | Query fixture + search/co-occurrence closure → detector report | Detector, `retrieval_common`, query JSON, co-occurrence data, vault-search closure | NT8lab query set, expected notes, scoring thresholds and derived output schema | **NEEDS-ADAPTER** |
| Two-lane search | Keep vault truth separate from periphery/intake when wider search is explicitly requested. | Query + search profile + two corpora → ranked lanes and last-run artifacts | `two_lane_search.py`, search config, stdlib | Absolute vault/periphery/deny roots, lane contract, size/extensions and skip lists | **NEEDS-ADAPTER** |
| Vault search | Retrieve concepts and neighbors when literal grep is insufficient. | Query + corpus/index/co-occurrence/profile → ranked results; optional two-lane files | `vault_search.py`, wrapper, **`retrieval_common.py`**, `two_lane_search.py`, search config, query fixture, co-occurrence artifact/builder | Vault paths, derived schemas, tuned weights/stopwords, benchmark corpus and periphery policy. `retrieval_common` travels with vault search or neither exports. | **NEEDS-ADAPTER** |
| Wiki logger | Capture routine durable changes when Git should remain background infrastructure. | Git worktree + logger profile/wrappers → commits and logger state/logs | Logger Python, production/test configs, both Windows launchers, Git CLI and ignore/guard contract | NT8lab absolute root, exclusions, debounce/identity policy, Windows daemon assumptions and capture vocabulary | **NEEDS-ADAPTER** |
| Management bridge | Materialize a safe thin view when selected state must cross a repository boundary. | Bridge profile + exact mappings + working sources → secret-scanned staged tree and scoped derived views | Bridge script/config, Git CLI, working-vault index builder/link closure, secret signatures | NT8lab roots/allow-list/key path, digest fields, selected architecture paths, commit/bootstrap expectations | **NEEDS-ADAPTER** |
| Management auto-sync | Rebuild/compare/push generated management `main` when one-way publication is desired. | Auto-sync profile + bridge closure + Git repositories → validated commit/push and runtime log | Auto-sync script/config, bridge/config, Git CLI, disposable stage/runtime directories | Windows paths, repository/remote/branch identity, debounce and generated-main ownership rules | **NEEDS-ADAPTER** |
| Operational playbooks | Standardize intake, banking, promotion, evaluation, review and triage when a repeatable human/agent procedure exists. | Request + template + vault conventions → reviewed notes/artifacts/logs/decisions | `_FRAMEWORK/playbooks/*.md` as a reviewed set; any named local helper must be separately packaged | Worked examples, source citations, paths, statuses, Pattern references and NT8lab authority hierarchy | **NEEDS-ADAPTER** |
| Dependency manifest/catalog renderer | Render tool/data dependencies when the system needs an inspectable closure catalog. | Dependency manifest/profile → catalog Markdown | `deps/dependencies.yaml`, `deps/tools/render_catalog.py`, schema assumptions | NT8lab component names, repository paths, roles and catalog destination | **NEEDS-ADAPTER** |

The management inventory is descriptive and does not override these
classifications. Packaging, templating, licensing, and toolkit-repository work
remain Phase 3.

## Adapter pattern — profile/policy split (accepted 2026-07-14)

Every Phase 2 `NEEDS-ADAPTER` verdict resolves through one uniform mechanism,
not per-tool improvisation:

1. **Every tool config splits into two kinds of content:**
   - **PROFILE (machine facts):** vault root, periphery/deny roots,
     interpreter locations, remote URLs, and machine-local paths of any kind.
     These move into one per-installation file (`vault-profile.json` or
     equivalent), referenced by tools and never embedded in tool configs.
   - **POLICY (learned judgment):** stopword lists, severity-by-role rules,
     skip conventions, debounce/timeout values, status vocabularies, and
     suppression classes. These ship portable as-is: they contain facts about
     the method, not about any machine.
2. **The exportable unit is:** tool closure (entrypoints, local helpers, and
   wrappers) plus its policy configs, an `example-profile.json` with
   placeholder paths, and a README stating inputs/outputs and the
   compute-and-flag rule.
3. **The proof of export-readiness is mechanical:** the closure must pass the
   Phase 3 fixture-vault smoke test using only the example profile. If a tool
   cannot run against a profile that is not NT8lab's, it is not ready.
4. **Doctrine note:** this is the existing no-machine-facts-in-code rule
   applied one level up: no machine facts in policy either; machine facts live
   in exactly one file per installation. The same split makes local machine
   migration a one-file edit, unifying the export problem with the 5.4
   portability track.
5. **Sequencing:** the split executes inside Phase 3, after the license gate,
   tool by tool, using the Phase 2 dependency-closure table as the refactor
   map. No dual-mode "export flags" are added to any tool: export is a
   packaging property, never runtime behavior.

Banked 2026-07-14: design policy only; no refactor, tool change, packaging, or
Phase 3 execution was performed.

## Validation required for any implementation phase

- Exact allow-list diff and staged secret-scan result, with no secret values
  printed.
- Fresh-clone/clean-checkout command evidence.
- A test that generated management `main` remains one-way from the working
  vault.
- A test that correspondence branches remain untouched by management sync.
- Reviewer sign-off before a new tool class or project content crosses a
  boundary.

## Source paths inspected for this plan

- `_FRAMEWORK/two_vault_architecture_prebuild_plan.md`
- `_FRAMEWORK/MANAGEMENT_PIPELINE.md`
- `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md`
- `tools/management_bridge/README.md`
- `tools/management_bridge/management_auto_sync_config.json`
- `tools/management_bridge/management_vault_config.json`
- `tools/wiki_deriver/README.md`
- RYRY request `KR-20260714-001` on branch `machine/ryry`
