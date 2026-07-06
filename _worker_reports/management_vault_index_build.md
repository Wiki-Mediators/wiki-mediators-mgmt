# Tool 2 Vault Index Build Report

## Verdict

Built the standalone all-file vault index artifacts for Tool 2.

## Artifacts

- `_DERIVED/vault_index.json` — canonical machine-readable index
- `_DERIVED/vault_index.md` — human/agent-readable rendering from JSON
- `tools/wiki_deriver/build_vault_index.py` — deterministic builder

## Counts

- Entries indexed: 166
- Basename collisions: 6

| Extension | Count |
|---|---:|
| `.json` | 1 |
| `.md` | 161 |
| `.py` | 4 |

## Collision List

| Basename | Count | Paths |
|---|---:|---|
| `AGENTS.md` | 2 | `AGENTS.md`<br>`_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/AGENTS.md` |
| `README.md` | 5 | `_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/nb_lib/strategy_specs/README.md`<br>`_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/nb_lib/strategy_specs/candidates/README.md`<br>`_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/nb_lib/strategy_specs/composition_nodes/README.md`<br>`_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/nb_lib/strategy_specs/source_artifacts/README.md`<br>`nb_lib/strategy_specs/composition_nodes/README.md` |
| `_PROJECT_ALTITUDE_MAP.md` | 2 | `_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/_PROJECT_ALTITUDE_MAP.md`<br>`_PROJECT_ALTITUDE_MAP.md` |
| `atr_regime_pullback_continuation.md` | 2 | `_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/nb_lib/strategy_specs/candidates/atr_regime_pullback_continuation.md`<br>`_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/nb_lib/strategy_specs/canonical/atr_regime_pullback_continuation.md` |
| `atr_regime_pullback_tight_target.md` | 2 | `_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/nb_lib/strategy_specs/candidates/atr_regime_pullback_tight_target.md`<br>`_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/nb_lib/strategy_specs/canonical/atr_regime_pullback_tight_target.md` |
| `ninja-traitorate-methodology-reference.md` | 2 | `_HANDOFFS/model_candidate_context_snapshot_20260706_github_safe/ninja-traitorate-methodology-reference.md`<br>`ninja-traitorate-methodology-reference.md` |

## Link Checker Resolver Win Estimate

- Broken rows that would resolve via all-file basename index: 0
- Additional line/symbol suffix rows that would resolve after index: 0
- Broken rows that would become honest ambiguity: 0

## Hand-Off To Tool 3

The validator upgrade should load `_DERIVED/vault_index.json`, use its all-file basename map for resolution, strip `:line`, `:line-range`, and `::symbol` suffixes before resolving, then add config-driven suppression and severity sections.
