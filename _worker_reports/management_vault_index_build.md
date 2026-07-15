# Tool 2 Vault Index Build Report

## Verdict

Built the standalone all-file vault index artifacts for Tool 2.

## Artifacts

- `_DERIVED/vault_index.json` — canonical machine-readable index
- `_DERIVED/vault_index.md` — human/agent-readable rendering from JSON
- `tools/wiki_deriver/build_vault_index.py` — deterministic builder

## Counts

- Entries indexed: 36
- Basename collisions: 0

| Extension | Count |
|---|---:|
| `.md` | 36 |

## Collision List

_None._

## Link Checker Resolver Win Estimate

- Broken rows that would resolve via all-file basename index: 0
- Additional line/symbol suffix rows that would resolve after index: 0
- Broken rows that would become honest ambiguity: 0

## Hand-Off To Tool 3

The validator upgrade should load `_DERIVED/vault_index.json`, use its all-file basename map for resolution, strip `:line`, `:line-range`, and `::symbol` suffixes before resolving, then add config-driven suppression and severity sections.
