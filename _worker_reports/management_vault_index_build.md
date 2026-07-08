# Tool 2 Vault Index Build Report

## Verdict

Built the standalone all-file vault index artifacts for Tool 2.

## Artifacts

- `_DERIVED/vault_index.json` — canonical machine-readable index
- `_DERIVED/vault_index.md` — human/agent-readable rendering from JSON
- `tools/wiki_deriver/build_vault_index.py` — deterministic builder

## Counts

- Entries indexed: 33
- Basename collisions: 1

| Extension | Count |
|---|---:|
| `.json` | 2 |
| `.md` | 25 |
| `.py` | 6 |

## Collision List

| Basename | Count | Paths |
|---|---:|---|
| `README.md` | 2 | `nb_lib/strategy_specs/composition_nodes/README.md`<br>`tools/wiki_deriver/README.md` |

## Link Checker Resolver Win Estimate

- Broken rows that would resolve via all-file basename index: 3
- Additional line/symbol suffix rows that would resolve after index: 0
- Broken rows that would become honest ambiguity: 0

## Hand-Off To Tool 3

The validator upgrade should load `_DERIVED/vault_index.json`, use its all-file basename map for resolution, strip `:line`, `:line-range`, and `::symbol` suffixes before resolving, then add config-driven suppression and severity sections.
