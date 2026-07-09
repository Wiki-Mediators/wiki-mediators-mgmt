---
title: "Wiki Architecture Flow Map"
status: living-reference
created: 2026-07-02
purpose: Obsidian-friendly map of how the working wiki layers connect, which tools move information between them, and which files are the concrete anchors.
related:
  - _FRAMEWORK/LAYER_ARCHITECTURE.md
  - _FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md
  - _FRAMEWORK/OPERATIONS.md
  - AGENTS.md
canvas: _FRAMEWORK/wiki_architecture_flow.canvas
---

# Wiki Architecture Flow Map

Open `_FRAMEWORK/wiki_architecture_flow.canvas` for the zoomable/clickable
version. This Markdown note is the readable companion.

## Mental Model

This is not a TensorFlow model, but it is a graph architecture. The nodes are
files, tools, vaults, and derived views. The edges are disciplined flows:
write, record, derive, distill, bridge, and cold-search.

The load-bearing rule:

```text
Capture is irreversible. Retrieval is improvable.
```

## High-Level Flow

```mermaid
flowchart TD
    L1["Layer 1: write / work<br/>operator + agents<br/>strategy notes, reports, specs"] --> WV["Working vault<br/>C:/VMShare/NT8lab"]
    WV --> L2["Layer 2: record<br/>tools/wiki_logger/wiki_logger.py<br/>config: tools/wiki_logger/wiki_logger.config.json"]
    L2 --> GIT["Git substrate<br/>complete byte history"]
    GIT --> L3["Layer 3: derive<br/>tools/wiki_deriver/*.py<br/>11 built dumb-tool capabilities<br/>flags, search, indexes, receipts"]
    L3 --> DER["_DERIVED/<br/>vault_index, broken_links, orientation_digest,<br/>search views, trigger/status views, capture integrity"]
    DER --> L4["Layer 4: distill<br/>cold occasional agent pass<br/>writes settled notes back"]
    L4 --> WV

    WV --> BR["Management bridge<br/>tools/management_bridge/build_management_vault.py"]
    BR --> MV["Management vault<br/>C:/VMShare/NT8lab_mgmt"]
    MV --> GH["Private GitHub / Claude project<br/>clean orchestrator subset"]

    CA["Conversation archive<br/>C:/VMShare/conversation_archive<br/>raw session tape, local-only"] -. "cold search when asked" .-> L4
    CA -. "not part of working vault substrate" .-> WV
```

## Concrete File Spine

```mermaid
flowchart LR
    AG["AGENTS.md<br/>bootstrap door and routing"] --> METH["ninja-traitorate-methodology-reference.md<br/>method authority"]
    AG --> ALT["_PROJECT_ALTITUDE_MAP.md<br/>current state and fronts"]
    AG --> OPS["_FRAMEWORK/OPERATIONS.md<br/>runtime conventions"]
    AG --> ARCH["_FRAMEWORK/LAYER_ARCHITECTURE.md<br/>four-layer model"]
    AG --> ROAD["_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md<br/>tool backlog and triggers"]
    AG --> CAP["_FRAMEWORK/capture_tool_spec.md<br/>capture tool conformance"]

    ARCH --> LOG["tools/wiki_logger/wiki_logger.py"]
    LOGCFG["tools/wiki_logger/wiki_logger.config.json<br/>vault_path, runtime_dir, timing, guard"] --> LOG
    LOG --> GIT[".git history"]

    GIT --> IDX["tools/wiki_deriver/build_vault_index.py"]
    GIT --> LINK["tools/wiki_deriver/link_reference_checker.py"]
    GIT --> DIG["tools/wiki_deriver/build_orientation_digest.py"]
    GIT --> STALE["tools/wiki_deriver/derived_staleness_signal.py"]
    GIT --> RET["tools/wiki_deriver/vault_search.py<br/>build_term_cooccurrence.py<br/>missed_retrieval_detector.py<br/>two_lane_search.py"]
    GIT --> GOV["tools/wiki_deriver/source_census.py<br/>trigger_watcher.py<br/>session_link_index.py<br/>capture_integrity_checker.py"]

    IDX --> VI["_DERIVED/vault_index.json/md"]
    LINK --> BL["_DERIVED/broken_links.md"]
    DIG --> OD["_DERIVED/orientation_digest.md"]
    STALE --> DS["_DERIVED/derived_staleness.json/md"]
    RET --> RS["_DERIVED/term_cooccurrence<br/>retrieval_detector<br/>two_lane_search_last"]
    GOV --> GS["_DERIVED/source_census<br/>trigger_status<br/>session_index<br/>capture_integrity"]

    VI --> LINK
    VI --> DIG
    VI --> STALE
    VI --> RET
    VI --> GOV
```

## Layer Inventory

### Layer 1 - Write

Main routing files:

- `AGENTS.md` - bootstrap order, working directories, archive routing, Git/logger abstraction.
- `ninja-traitorate-methodology-reference.md` - methodology authority.
- `_PROJECT_ALTITUDE_MAP.md` - broad current-state map.
- `_FRAMEWORK/PATTERNS.md` - project-agnostic research-with-agents patterns.
- `_FRAMEWORK/OPERATIONS.md` - operational conventions.

Snippet-level summary:

```text
AGENTS.md routes agents to the durable authorities and tells them not to
foreground Git/logger mechanics in ordinary work.
```

### Layer 2 - Record

Tool:

- `tools/wiki_logger/wiki_logger.py`

Config:

- `tools/wiki_logger/wiki_logger.config.json`

Key fields:

```text
vault_path, runtime_dir, poll_interval_sec, debounce_window_sec,
periodic_safety_sec, guard_total_commit_mb, guard_single_file_mb
```

Role:

```text
The logger captures settled file states into Git. It does not understand
meaning. It commits bytes.
```

### Layer 3 - Derive

Built dumb-tool capabilities:

1. `tools/wiki_deriver/build_vault_index.py` - all-file index and basename collision surface.
2. `tools/wiki_deriver/link_reference_checker.py` - broken/ambiguous reference checker.
3. `tools/wiki_deriver/build_orientation_digest.py` - deterministic ground-truth orientation snapshot.
4. `tools/wiki_deriver/derived_staleness_signal.py` - flags stale `_DERIVED/` views.
5. `tools/wiki_deriver/source_census.py` - external-source/event census.
6. `tools/wiki_deriver/trigger_watcher.py` - booked-trigger status dashboard.
7. `tools/wiki_deriver/session_link_index.py` - session/report/archive link index.
8. `tools/wiki_deriver/build_term_cooccurrence.py` - corpus-derived term overlap table.
9. `tools/wiki_deriver/missed_retrieval_detector.py` - retrieval benchmark / miss detector.
10. `tools/wiki_deriver/vault_search.py` with `two_lane_search.py` and `vault_search.ps1` - agent search door over vault and periphery lanes.
11. `tools/wiki_deriver/capture_integrity_checker.py` - provenance/capture-gap flagger.

Support files not counted as separate capabilities:

- `tools/wiki_deriver/retrieval_common.py` - shared corpus/scoring helper.
- `tools/wiki_deriver/*.config.json` - config-owned roots, thresholds, and deny-lists.

Adjacent environment dumb tool:

- `deps/tools/render_catalog.py` - dependency manifest/catalog renderer for roadmap 5.1. It follows the same dumb-tool rules but lives in the environment-reconstitution track rather than the wiki-deriver track.

Outputs:

- `_DERIVED/vault_index.json`
- `_DERIVED/vault_index.md`
- `_DERIVED/broken_links.md`
- `_DERIVED/orientation_digest.md`
- `_DERIVED/derived_staleness.json`
- `_DERIVED/derived_staleness.md`
- `_DERIVED/source_census.json/md`
- `_DERIVED/trigger_status.json/md`
- `_DERIVED/session_index.json/md`
- `_DERIVED/retrieval_detector*.json/md`
- `_DERIVED/term_cooccurrence.json/md`
- `_DERIVED/two_lane_search_last.json/md`
- `_DERIVED/capture_integrity.json/md`

Role:

```text
Dumb tools compute views from the vault. They flag and tabulate; they never
fix or interpret.
```

### Layer 4 - Distill

Status:

```text
Booked concept, not a constantly running tool.
```

Role:

```text
A cold agent reads committed material and derived views, then writes settled
notes back into the working wiki with source links. It is occasional, cited,
and separate from warm working context.
```

## Adjacent Vaults

### Management Vault

Path:

```text
C:/VMShare/NT8lab_mgmt
```

Bridge tools:

- `tools/management_bridge/build_management_vault.py`
- `tools/management_bridge/management_auto_sync.py`
- `tools/management_bridge/management_vault_config.json`
- `tools/management_bridge/management_auto_sync_config.json`

Role:

```text
The management bridge exports an allow-listed clean subset to the management
vault and private GitHub/Claude project. It is one-way. It must not push or
mirror raw working-vault material broadly.
```

### Conversation Archive

Path:

```text
C:/VMShare/conversation_archive
```

Decision record:

- `_FRAMEWORK/conversation_archive_decision_record.md`

Capture spec:

- `_FRAMEWORK/capture_tool_spec.md`

Role:

```text
Raw conversation/session tape lives outside the working vault. Search it cold
when asked about prior discussions. Extracts and scratch go in codex_tmp/,
which is untracked.
```

## Read This With The Canvas

Use the Canvas when you want to zoom around the system visually:

- `_FRAMEWORK/wiki_architecture_flow.canvas`

Use this Markdown note when you want the concise text explanation and Mermaid
views.
