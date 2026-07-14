# Wiki Mediators instrument inventory

Status: descriptive management inventory; non-runnable.
As of: 2026-07-14.

This note tells a thin management checkout what exists in the full working
vault. It does not export source, configuration, wrappers, fixtures, or
runtime dependencies. Every instrument below is **descriptive only** and must
be requested through the operator/local worker; no listed command is runnable
from the management checkout. Binaries and source live in the working vault;
toolkit distribution is the future separate `wiki-mediators` repository and
is not authorized by this inventory.

| Instrument | Layer | Job | Inputs | Outputs |
|---|---|---|---|---|
| Vault index builder | Deriver | Enumerates the configured vault and projects file/frontmatter/link metadata. | Vault files, link/index config | `_DERIVED/vault_index.json` and `.md` |
| Link reference checker | Deriver | Resolves note/path references and emits severity-classified broken-link evidence. | Vault corpus, vault index, link and integrity configs | `_DERIVED/broken_links.json` and `.md` |
| Orientation digest builder | Deriver | Projects a compact current-orientation view from indexed, explicitly selected sources. | Vault index, roadmap, strategy-spec metadata | Orientation digest and worker report |
| Derived staleness signal | Deriver | Compares known derived artifacts with their declared/configured source sets. | Derived artifacts, source mtimes, deriver code/config | Staleness JSON and Markdown flags |
| Source census | Deriver | Counts and classifies configured research-source notes and verdict vocabulary. | Source-artifact note roots and frontmatter | Source-census JSON and Markdown |
| Trigger watcher | Deriver | Computes whether documented thresholds or state changes activate follow-up work. | Roadmap, newsroom, source census, retrieval report | Trigger-status JSON and Markdown |
| Deriver runner | Orchestrator | Runs the configured deterministic deriver sequence and summarizes exits/LOUD flags. | Runner config, wrappers, complete enabled-tool closure | Last-run dashboard JSON and Markdown |
| Session-link index | Deriver | Connects durable notes to session/archive references without copying conversation tape. | Vault notes, Git metadata, external conversation archive | Session-index JSON and Markdown |
| Capture-integrity checker | Deriver | Flags capture/frontmatter/status and evidence-integrity problems. | Markdown corpus, Git state, integrity/link configs | Capture-integrity JSON and Markdown |
| Term co-occurrence builder | Retrieval support | Builds a deterministic lexical-neighbor table for recall assistance. | Markdown corpus, retrieval tokenizer/stopwords | Term-cooccurrence JSON and Markdown |
| Missed-retrieval detector | Retrieval QA | Runs configured paraphrase cases and measures retrieval misses. | Test queries, search closure, co-occurrence data | Retrieval-detector JSON and Markdown |
| Two-lane search | Retrieval | Searches the vault and separately configured periphery roots under deny/size rules. | Query, vault-search profile, vault/periphery files | Ranked lane results and last-run artifacts |
| Vault search | Retrieval | Performs lexical, recall, link-neighbor, and structural-assisted vault retrieval. | Query, `retrieval_common`, search configs, index/co-occurrence/query fixtures | Ranked search results; optional two-lane artifacts |
| Wiki logger | Capture | Watches selected changes and records routine Git capture under exclusions/guards. | Logger profile, Git worktree, Windows launch wrappers | Working-vault commits and logger state/logs |
| Management bridge | Boundary | Secret-scans an exact mapping and materializes a one-way thin management tree. | Bridge profile, allow-list/copy mappings, working-vault sources | Staged management tree and scoped derived views |
| Management auto-sync | Boundary automation | Rebuilds a disposable stage, verifies it, and updates generated management `main`. | Auto-sync profile, bridge closure, Git remote/worktree | Validated management commit/push and runtime log |
| Operational playbooks | Procedure | Define repeatable intake, banking, promotion, review, evaluation, and triage workflows. | Operator request, templates, working-vault conventions | Reviewed notes, artifacts, logs, or decisions in the working vault |
| Dependency manifest and catalog renderer | Dependency inventory | Renders the declared tool/data dependency graph into a readable catalog. | Dependency manifest and project profile | Generated dependency catalog |

The Phase 2 dependency and portability classifications live in
`_FRAMEWORK/wiki_mediators_export_and_management_boundary_plan_20260714.md`.
