---
title: "TASK — AGENTS.md Search-Routing Edit"
type: worker report
created: 2026-07-08
status: complete
---

# TASK — AGENTS.md Search-Routing Edit

Applied the agreed small edit set from
`C:\Users\meme\Downloads\TASK_agents_search_routing_edit.md`.

## What changed

- Added a new top-level `## Topic search` section near the top of `AGENTS.md`.
- Wording used: for TOPIC or CONCEPT note retrieval, first action is
  `python tools\wiki_deriver\vault_search.py "<question>" --recall-assist --link-neighbor-assist --structural-assist`.
- Added the measured-distrust line in `AGENTS.md`: ripgrep measured 9/60 vs
  vault_search 57/60 on the paraphrase benchmark.
- Preserved the grep boundary explicitly: grep/ripgrep remain correct for
  exact strings, filenames, error text, literal-token searches, and code
  identifiers.
- Removed the now-redundant `Wiki/vault search door` row from the canonical
  files table to pay for the top-section imperative and keep bootstrap weight
  small.
- Booked the deferred search-routing interceptor candidate in
  `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md`.

## Deferred

No grep wrapper, pre-search hook, tool interceptor, redirector, or runtime
machinery was built. Trigger remains: test the reworded imperative plus
measured-distrust line in a fresh no-hints session; only if the agent still
greps a topic query blind does the structural candidate fire.

## Boundary confirmation

The final wording cannot reasonably be read as a blanket grep ban: it forbids
grep/ripgrep only for topic/concept note retrieval and immediately states the
allowed exact-string/code/file/error cases.

## Follow-up doorway fix

2026-07-09: added `tools/wiki_deriver/vault_search.ps1` and changed the
AGENTS.md command to call the launcher. The launcher resolves the bundled Codex
Python runtime before falling back to PATH, so topic-search routing no longer
depends on every agent having `python` on PATH or remembering a hardcoded
runtime path. Testing also surfaced and fixed a small two-lane hygiene issue:
`_DERIVED/two_lane_search_last.md` is now skipped so the generated "last search"
artifact cannot rank itself as a vault result.
