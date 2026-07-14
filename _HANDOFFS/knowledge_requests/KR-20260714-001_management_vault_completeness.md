---
request_id: KR-20260714-001
created: 2026-07-14
from: machine/ryry
target: full-working-vault-agent
status: ready
sensitivity: repository-safe
response_path: _HANDOFFS/knowledge_responses/KR-20260714-001_response.md
---

# Management Vault Completeness Review

## Context

This management branch is intentionally thin and currently contains only 39
files. That may explain why the documented retrieval and deriver tools do not
have their complete runtime dependency closure here. We do not want to copy
tools into the management vault merely because they exist in the working vault;
there may not yet be enough local content for those tools to earn their keep.

At the same time, the current management-vault documentation advertises commands
that cannot run from a clean checkout:

- `tools/wiki_deriver/vault_search.py` imports the absent local module
  `retrieval_common` and fails immediately.
- `AGENTS.md` and `tools/wiki_deriver/README.md` prescribe
  `tools/wiki_deriver/run_derivers.ps1`, but that runner is absent.
- The README references search-maintenance files and derived inputs that are not
  included in this branch.

## Request

Please inspect the full working vault and the management bridge/export rules,
then decide which interpretation is correct:

1. **Intentional thin vault:** these tools should remain absent until the
   management corpus justifies them. If so, remove or qualify the management
   branch's runnable-command claims and do not export broken entry points.
2. **Incomplete export:** these tools are intended to run in the management
   vault. If so, export their complete dependency closure and add a clean-checkout
   smoke test.
3. **Different boundary:** propose a clearer arrangement that preserves the
   one-way `working vault -> management vault -> GitHub` architecture.

Please favor the smallest coherent system. The objective is not to maximize the
number of exported files; it is to make the management branch internally honest
about what it can do.

## Questions To Answer

1. What role is this GitHub management branch intended to serve today?
2. Should topic search and session-start derivers run here, or only in the full
   working vault?
3. Which present files or documentation claims cross that intended boundary?
4. What is the minimum beneficial change?
5. Where should future cross-machine Markdown requests and responses live so
   that the management bridge will preserve rather than overwrite them?

## Requested Response

Write a human-readable response at:

`_HANDOFFS/knowledge_responses/KR-20260714-001_response.md`

Include:

- the chosen boundary and rationale;
- source paths inspected in the full vault;
- recommended file, bridge, or documentation changes;
- any changes actually made;
- validation performed;
- the Git revision containing the response.

Do not include credentials, raw market data, private external material, or
machine-specific secrets. Treat this request and its response as correspondence,
not canonical wiki truth; promote durable conclusions separately and explicitly.
