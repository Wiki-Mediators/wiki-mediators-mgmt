# Wiki Deriver Tools

These tools are dumb Layer 3 helpers for Wiki Mediators. They compute from the
vault, write derived artifacts, and do not make judgment calls.

## Current Vault Search Door

Use `vault_search.py` when an agent needs to find project memory by topic rather
than by exact filename. It is the current default search door for wiki/vault
retrieval questions.

Recommended command shape:

```powershell
.\tools\wiki_deriver\vault_search.ps1 "your topic or question" --recall-assist --link-neighbor-assist --structural-assist
```

Use the `.ps1` doorway from the vault root for agent-facing calls. It resolves
the bundled Codex Python runtime before falling back to PATH, then forwards all
arguments to `vault_search.py`.

What this mode does:

- starts with lexical matching over Markdown notes;
- adds corpus-derived co-occurrence recall suggestions;
- follows Markdown references from surfaced notes;
- adds driverless structural aliases from path words, selected frontmatter,
  and headings.

It does not use hand-written synonym tables, embeddings, LLM summaries, or a
database. If `_DERIVED/term_cooccurrence.json` is stale or missing, the tool
degrades to lexical search and prints the reason.

## Maintenance

Regenerate the co-occurrence artifact after source-note changes when v4 search
matters:

```powershell
python tools\wiki_deriver\build_term_cooccurrence.py
```

Benchmark the retrieval detector:

```powershell
python tools\wiki_deriver\missed_retrieval_detector.py --use-expansion --recall-assist --link-neighbor-assist --structural-assist --json _DERIVED\retrieval_detector_rung1_v4.json --md _DERIVED\retrieval_detector_rung1_v4.md
```

## Current Evidence

As of 2026-07-08, v4 cleared the retrieval trigger benchmark without
hand-maintained synonyms:

- official 28-query benchmark: 26/28 hits, 7.1% miss rate;
- supplemental Markdown-only 60-query challenge: 57/60 hits, 5.0% miss rate;
- `rg` baseline on the same Markdown-only 60-query challenge: 9/60 hits, 85.0%
  miss rate.

The broader `.md/.py/.json` search mode is still scratch-only under
`codex_tmp/`; do not treat it as the default vault search contract.

## v5: Two-Lane Search

Use two-lane mode when the operator asks to search both the organized vault and
loose intake/periphery files, such as Downloads. The command shape is:

```powershell
.\tools\wiki_deriver\vault_search.ps1 "your topic or question" --two-lane
```

This mode is config-owned:

- `VAULT`: organized durable workspace memory;
- `PERIPHERY`: read-only intake context from configured external roots.

The tool, not the agent, owns the infrastructure rules: configured periphery
roots, deny roots, allowed extensions, file-size caps, lane labels, and a scope
receipt. Agents should only supply the query and read the two lanes. Periphery
results are never promoted by search; banking/importing a file is a separate
explicit action.

Current files:

- `tools/wiki_deriver/vault_search_config.json`: roots, labels, deny roots,
  extensions, and file-size cap.
- `tools/wiki_deriver/two_lane_search.py`: lane scanner and scorer.
- `_DERIVED/two_lane_search_last.json` and
  `_DERIVED/two_lane_search_last.md`: latest generated two-lane view.

Initial periphery root: `C:\Users\meme\Downloads`. Default periphery extensions:
`.md`, `.txt`. Default deny roots include the working vault, management vaults,
sync stage, `_HANDOFFS`, `codex_tmp/`, runtime/cache folders, and conversation
archive until archive search has its own mode.

Validation on 2026-07-08:

- happy path: scanned 740 vault Markdown docs and 343 Downloads `.md/.txt`
  periphery docs;
- bad-config path: a periphery root pointed at `C:\VMShare\NT8lab` was skipped
  with a receipt and scanned zero periphery docs;
- existing v4 search mode still compiles and runs.

If Python scanning becomes too slow, v5.1 should add a disposable SQLite FTS5
index using stdlib `sqlite3`. The index is local-only cache, rebuilt from
source files, and never a source of truth.
