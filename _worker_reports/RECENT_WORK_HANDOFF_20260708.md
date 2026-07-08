---
title: "Recent Work Handoff — Wiki Mediators Retrieval + Two-Lane Search"
type: agent handoff
created: 2026-07-08
status: current
---

# Recent Work Handoff — Wiki Mediators Retrieval + Two-Lane Search

This vault is NT8lab, the first working vault running the broader **Wiki
Mediators** architecture: agents write, dumb tools derive, the bridge exposes a
thin management view, and the vault keeps durable memory without asking agents
to remember every convention by hand.

The recent work was on the retrieval / dumb-tool layer, especially making search
useful without turning it into an agent-managed wiki curation task.

## What was built recently

### 1. Vault search v4 became the default topic-search door

Canonical tool:

- `tools/wiki_deriver/vault_search.py`

Default command for normal vault/topic retrieval:

```powershell
python tools\wiki_deriver\vault_search.py "topic or question" --recall-assist --link-neighbor-assist --structural-assist
```

Why it matters:

- plain lexical search missed paraphrases;
- v4 adds corpus-derived recall suggestions, link-neighbor expansion, and
  driverless structural aliases derived from authored structure;
- it beat the committed retrieval benchmark and the larger 60-query challenge.

Current docs:

- `tools/wiki_deriver/README.md`
- `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md`
- `AGENTS.md` canonical-files table

### 2. Two-lane search v5 was built

Canonical command:

```powershell
python tools\wiki_deriver\vault_search.py "topic or question" --two-lane
```

Files:

- `tools/wiki_deriver/two_lane_search.py`
- `tools/wiki_deriver/vault_search_config.json`
- `_DERIVED/two_lane_search_last.json`
- `_DERIVED/two_lane_search_last.md`

What it does:

- searches the organized vault as `VAULT`;
- searches configured outside intake roots as `PERIPHERY`;
- labels each result by lane;
- emits a scope receipt showing roots scanned or skipped;
- never promotes, copies, moves, imports, or rewrites periphery files.

Important principle:

The tool owns periphery roots, deny roots, allowed extensions, lane labels,
size caps, and the scope receipt. Agents should only supply the query and read
the lanes. Promotion/import remains a separate explicit action.

Current default periphery root:

- `C:\Users\meme\Downloads`

Default deny roots include:

- the working vault;
- management vaults;
- sync stages;
- `_HANDOFFS`;
- `codex_tmp`;
- runtime/cache folders;
- conversation archive until archive search has its own mode.

Validation from 2026-07-08:

- happy path scanned 740 vault Markdown docs;
- happy path scanned 343 Downloads `.md/.txt` periphery docs;
- bad periphery root `C:\VMShare\NT8lab` was skipped with a receipt and zero
  periphery docs;
- existing v4 search path still runs;
- compile check passed.

### 3. SQLite FTS5 acceleration is planned, not built

Bundled Python already has SQLite FTS5 available. The roadmap has a v5.1 plan:
if Python scanning becomes too slow for broader periphery, build a disposable
SQLite FTS5 index.

Do not treat the SQLite index as truth. It would be a local cache only, rebuilt
from source files, safe to delete, and not a service dependency.

## How an agent should use this

For normal "where is this in the vault?" questions, use v4:

```powershell
python tools\wiki_deriver\vault_search.py "topic" --recall-assist --link-neighbor-assist --structural-assist
```

For "also check Downloads / loose files / recent downloaded materials" questions,
use v5:

```powershell
python tools\wiki_deriver\vault_search.py "topic" --two-lane
```

Read the VAULT lane as durable memory. Read the PERIPHERY lane as intake context
only. Do not cite periphery as canon unless a separate banking/import action has
been explicitly requested.

## Best current orientation files

Read these if you need the full shape:

- `AGENTS.md`
- `tools/wiki_deriver/README.md`
- `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md`
- `_worker_reports/TASK_rung1_vault_search_findings_20260708.md`
- `_DERIVED/two_lane_search_last.md`

## Current state in one sentence

The vault now has a working search door for durable wiki memory and a separate
config-owned two-lane mode for loose intake/periphery files, preserving the
boundary between "found" and "banked."
