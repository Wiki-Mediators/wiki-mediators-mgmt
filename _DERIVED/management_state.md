# Management Vault - Current State

Deterministically generated from roadmap statuses and tool-file presence. No hand-written narrative; unavailable facts are `UNSTATED`.

- schema: `management_state_v1`
- generated_from: roadmap statuses plus tool-file presence; UNSTATED over guessing

## Tool Presence

| id | name | state | source root | path |
|---|---|---|---|---|
| bridge | management bridge | BUILT | working | `tools/management_bridge/build_management_vault.py` |
| auto_sync | management auto-sync | BUILT | working | `tools/management_bridge/management_auto_sync.py` |
| vault_index | vault index builder | BUILT | management | `tools/wiki_deriver/build_vault_index.py` |
| link_checker | link reference checker | BUILT | management | `tools/wiki_deriver/link_reference_checker.py` |
| derived_staleness | derived staleness signal | BUILT | management | `tools/wiki_deriver/derived_staleness_signal.py` |

## Roadmap Status Groups

### built

| id | name | status |
|---|---|---|
| 3.1 | Link / reference integrity checker | BUILT |
| 3.3 | Orientation digest / ground-truth snapshot | BUILT |
| 3.8 | Derived-staleness "needs regen" signal | BUILT |
| 3.11 | Source census | BUILT |
| 3.12 | Trigger watcher | BUILT |
| 5.1 | Dependency manifest + catalog renderer | BUILT |
| 6.3 | Session-index deriver | BUILT |

### staged

| id | name | status |
|---|---|---|
| 3.2 | Layer 3 deriver — structural index ("the altitude map") | BUILD SOON, STAGED |

### not_built

| id | name | status |
|---|---|---|
| 3.13 | Flags aggregator | BOOKED, NOT BUILT |
| 3.14 | External URL-rot checker | BOOKED, NOT BUILT |
| 5.2 | Offline bundle + Python pinning | NOT BUILT (gated behind 5.1) |
| 5.3 | Windows bootstrap installer | NOT BUILT (gated behind 5.1, 5.2) |
| 5.4 | Drift detection + portability stub | NOT BUILT (gated behind 5.1) |
| 6.1 | Watch registry + sweeper | BOOKED, NOT BUILT |
| 6.2 | Second logger instance | BOOKED, NOT BUILT |
| 6.4 | Unified cross-vault timeline | BOOKED, NOT BUILT |
| 6.5 | Session-to-commit crosswalk | BOOKED, NOT BUILT |
| 6.6 | Cross-vault search wrapper | BOOKED, NOT BUILT |
| 6.7 | Vault spawner + profiles | BOOKED, NOT BUILT |
| 6.8 | Archive-to-wiki distiller | BOOKED, NOT BUILT |
| 6.9 | SQLite ingestion | BOOKED, NOT BUILT |
| 6.10 | Commit-noise auditor | BOOKED, NOT BUILT |

### deferred

| id | name | status |
|---|---|---|
| 3.4 | Orphan / staleness reporter | DEFER |
| 3.5 | Frontmatter / convention linter | DEFER |
| 3.6 | On-demand summarizer (Layer 4) | DEFER (and gated behind Layer 3) |
| 3.7 | Housekeeping agent | DEFER (needs the dumb tools to have run first) |

### unstated

| id | name | status |
|---|---|---|
| 3.9 | Statistical substrate + legible shutter | BOOKED CANDIDATE (trigger evidence measured) |
| 3.10 | Newsroom wiki architecture candidate | BOOKED CANDIDATE (trigger not fired) |

