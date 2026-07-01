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
| 3.8 | Derived-staleness "needs regen" signal | DEFER (pairs with all derived artifacts) |
| 3.9 | Statistical substrate + legible shutter | BOOKED CANDIDATE (trigger not fired) |
| 5.1 | Dependency manifest + catalog renderer | NOT BUILT (next) |
| 5.2 | Offline bundle + Python pinning | NOT BUILT (gated behind 5.1) |
| 5.3 | Windows bootstrap installer | NOT BUILT (gated behind 5.1, 5.2) |
| 5.4 | Drift detection + portability stub | NOT BUILT (gated behind 5.1) |

## Current state snapshot

Derived from roadmap statuses and tool-file presence.

### Tool presence

| id | state | source root | path |
|---|---|---|---|
| bridge | BUILT | working | `tools/management_bridge/build_management_vault.py` |
| auto_sync | BUILT | working | `tools/management_bridge/management_auto_sync.py` |
| vault_index | BUILT | management | `tools/wiki_deriver/build_vault_index.py` |
| link_checker | BUILT | management | `tools/wiki_deriver/link_reference_checker.py` |

### Roadmap counts

| group | count |
|---|---:|
| built | 2 |
| staged | 1 |
| not_built | 4 |
| deferred | 5 |
| unstated | 1 |

## Framework notes (titles parsed from staged tree)

| path | title |
|---|---|
| `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md` | Derived-Layer & Dumb-Tool Roadmap (Layers 3–4 + the tooling) |
| `_FRAMEWORK/LAYER_ARCHITECTURE.md` | Wiki Infrastructure — Layer Architecture |
| `_FRAMEWORK/MANAGEMENT_PIPELINE.md` | Management Pipeline |
| `_FRAMEWORK/OPERATIONS.md` | Operational Notes - How This Project Works (cross-agent) |
| `_FRAMEWORK/PATTERNS.md` | Research-With-Agents Framework Patterns |
| `_FRAMEWORK/two_vault_architecture_prebuild_plan.md` | Two-Vault Architecture — Pre-Build Plan |
| `_FRAMEWORK/wiki_architecture_current_future_visual_note_20260628.md` | Wiki Architecture Current/Future Visual Note |

## Staged summary

- total_files: **17**

| directory | files |
|---|---:|
| `(root)` | 3 |
| `_DERIVED` | 2 |
| `_FRAMEWORK` | 7 |
| `_worker_reports` | 1 |
| `tools` | 4 |

