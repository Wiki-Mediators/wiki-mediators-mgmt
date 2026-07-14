# Management Vault — Orientation Digest

Deterministically generated from the staged management tree by `tools/management_bridge/build_management_vault.py`. NOT a research digest; fields are limited to structural facts the orchestrator needs.

- schema: `management_digest_v1`
- generated_from: the staged management vault (NOT the working vault)

## Bootstrap / orientation files

| path | title | exists |
|---|---|---:|
| `AGENTS.md` | NT8lab — Bootstrap for new sessions | true |
| `ninja-traitorate-methodology-reference.md` | Ninja Traitorate — Methodology Reference | true |
| `_PROJECT_ALTITUDE_MAP.md` | Project Altitude Map | true |

## Roadmap entries (from staged `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md`)

| id | name | status |
|---|---|---|
| 3.1 | Link / reference integrity checker | BUILT |
| 3.2 | Layer 3 deriver — structural index ("the altitude map") | BUILD SOON, STAGED |
| 3.3 | Orientation digest / ground-truth snapshot | BUILT |
| 3.4 | Orphan / staleness reporter | DEFER |
| 3.5 | Frontmatter / convention linter | DEFER |
| 3.6 | On-demand summarizer (Layer 4) | DEFER (and gated behind Layer 3) |
| 3.7 | Housekeeping agent | DEFER (needs the dumb tools to have run first) |
| 3.8 | Derived-staleness "needs regen" signal | BUILT |
| 3.9 | Statistical substrate + legible shutter | BOOKED CANDIDATE (trigger evidence measured) |
| 3.10 | Newsroom wiki architecture candidate | BOOKED CANDIDATE (trigger not fired) |
| 3.11 | Source census | BUILT |
| 3.12 | Trigger watcher | BUILT |
| 3.13 | Deriver runner / flags aggregator | BUILT |
| 3.14 | External URL-rot checker | BOOKED, NOT BUILT |
| 5.1 | Dependency manifest + catalog renderer | BUILT |
| 5.2 | Offline bundle + Python pinning | NOT BUILT (gated behind 5.1) |
| 5.3 | Windows bootstrap installer | NOT BUILT (gated behind 5.1, 5.2) |
| 5.4 | Drift detection + portability stub | NOT BUILT (gated behind 5.1) |
| 6.1 | Watch registry + sweeper | BOOKED, NOT BUILT |
| 6.2 | Second logger instance | BOOKED, NOT BUILT |
| 6.3 | Session-index deriver | BUILT |
| 6.4 | Unified cross-vault timeline | BOOKED, NOT BUILT |
| 6.5 | Session-to-commit crosswalk | BOOKED, NOT BUILT |
| 6.6 | Cross-vault search wrapper | BOOKED, NOT BUILT |
| 6.7 | Vault spawner + profiles | BOOKED, NOT BUILT |
| 6.8 | Archive-to-wiki distiller | BOOKED, NOT BUILT |
| 6.9 | SQLite ingestion | BOOKED, NOT BUILT |
| 6.10 | Commit-noise auditor | BOOKED, NOT BUILT |

## Current state snapshot

Derived from roadmap statuses and tool-file presence.

### Tool presence

| id | state | source root | path |
|---|---|---|---|
| bridge | BUILT | working | `tools/management_bridge/build_management_vault.py` |
| auto_sync | BUILT | working | `tools/management_bridge/management_auto_sync.py` |
| vault_index | BUILT | management | `tools/wiki_deriver/build_vault_index.py` |
| link_checker | BUILT | management | `tools/wiki_deriver/link_reference_checker.py` |
| derived_staleness | BUILT | management | `tools/wiki_deriver/derived_staleness_signal.py` |

### Roadmap counts

| group | count |
|---|---:|
| built | 8 |
| staged | 1 |
| not_built | 13 |
| deferred | 4 |
| unstated | 2 |

## Framework notes (titles parsed from staged tree)

| path | title |
|---|---|
| `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md` | Derived-Layer & Dumb-Tool Roadmap (Layers 3–4 + the tooling) |
| `_FRAMEWORK/drift_reduction_program_20260706.md` | Drift Reduction Program — Observed Species and the Computed-Copy Rule |
| `_FRAMEWORK/LAYER_ARCHITECTURE.md` | Wiki Infrastructure — Layer Architecture |
| `_FRAMEWORK/MANAGEMENT_PIPELINE.md` | Management Pipeline |
| `_FRAMEWORK/newsroom_wiki_architecture_candidate_20260706.md` | Newsroom Wiki — Architecture Candidate |
| `_FRAMEWORK/OPERATIONS.md` | Operational Notes - How This Project Works (cross-agent) |
| `_FRAMEWORK/PATTERNS.md` | Research-With-Agents Framework Patterns |
| `_FRAMEWORK/two_vault_architecture_prebuild_plan.md` | Two-Vault Architecture — Pre-Build Plan |
| `_FRAMEWORK/wiki_architecture_current_future_visual_note_20260628.md` | Wiki Architecture Current/Future Visual Note |
| `_FRAMEWORK/wiki_architecture_flow.md` | Wiki Architecture Flow Map |
| `_FRAMEWORK/wiki_mediators_export_and_management_boundary_plan_20260714.md` | Wiki Mediators Export + Management Boundary Plan |

## Staged summary

- total_files: **40**

| directory | files |
|---|---:|
| `(root)` | 3 |
| `_DERIVED` | 2 |
| `_DIMENSIONS` | 3 |
| `_FRAMEWORK` | 12 |
| `_worker_reports` | 5 |
| `nb_lib` | 3 |
| `tools` | 12 |

