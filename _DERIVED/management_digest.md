# Management Vault — Orientation Digest

Deterministically generated from the staged management tree by `tools/management_bridge/build_management_vault.py`. NOT a research digest; fields are limited to structural facts the orchestrator needs.

- schema: `management_digest_v1`
- generated_from: the staged management vault (NOT the working vault)

## Roadmap entries (from staged `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md`)

| id | name | status |
|---|---|---|
| 3.1 | Link / reference integrity checker | BUILT |
| 3.2 | Layer 3 deriver | structural index ("the altitude map") — BUILD SOON, STAGED |
| 3.3 | Orientation digest / ground-truth snapshot -- BUILT | **Job:** generate a compact, deterministic ground-truth snapshot of the |
| 3.4 | Orphan / staleness reporter | DEFER |
| 3.5 | Frontmatter / convention linter | DEFER |
| 3.6 | On-demand summarizer (Layer 4) | DEFER (and gated behind Layer 3) |
| 3.7 | Housekeeping agent | DEFER (needs the dumb tools to have run first) |
| 3.8 | Derived-staleness "needs regen" signal | DEFER (pairs with all derived artifacts) |
| 5.1 | Dependency manifest + catalog renderer -- NOT BUILT (next) | **Job:** create a machine-readable `dependencies.yaml` as the portable |
| 5.2 | Offline bundle + Python pinning -- NOT BUILT (gated behind 5.1) | **Job:** move the relevant installers out of the Downloads graveyard into a |
| 5.3 | Windows bootstrap installer -- NOT BUILT (gated behind 5.1, 5.2) | **Job:** build a Windows `bootstrap.ps1` where the user picks a working |
| 5.4 | Drift detection + portability stub -- NOT BUILT (gated behind 5.1) | **Job:** add a `check_drift.py` that runs each manifest verify command, |

## Framework notes (titles parsed from staged tree)

| path | title |
|---|---|
| `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md` | Derived-Layer & Dumb-Tool Roadmap (Layers 3–4 + the tooling) |
| `_FRAMEWORK/LAYER_ARCHITECTURE.md` | Wiki Infrastructure — Layer Architecture |
| `_FRAMEWORK/OPERATIONS.md` | Operational Notes - How This Project Works (cross-agent) |
| `_FRAMEWORK/PATTERNS.md` | Research-With-Agents Framework Patterns |
| `_FRAMEWORK/two_vault_architecture_prebuild_plan.md` | Two-Vault Architecture — Pre-Build Plan |
| `_FRAMEWORK/wiki_architecture_current_future_visual_note_20260628.md` | Wiki Architecture Current/Future Visual Note |

## Staged summary

- total_files: **16**

| directory | files |
|---|---:|
| `(root)` | 3 |
| `_DERIVED` | 2 |
| `_FRAMEWORK` | 6 |
| `_worker_reports` | 1 |
| `tools` | 4 |

