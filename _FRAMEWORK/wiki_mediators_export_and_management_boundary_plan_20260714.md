---
title: "Wiki Mediators Export + Management Boundary Plan"
status: proposed-review
created: 2026-07-14
scope: reusable Wiki Mediators infrastructure, thin management vault, and
  cross-machine correspondence; explicitly excludes exporting NT8lab project
  corpus, data, credentials, or live runtime material.
related:
  - _FRAMEWORK/MANAGEMENT_PIPELINE.md
  - _FRAMEWORK/two_vault_architecture_prebuild_plan.md
  - _FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md
  - tools/management_bridge/management_vault_config.json
  - _HANDOFFS/knowledge_requests/KR-20260714-001_management_vault_completeness.md
---

# Wiki Mediators Export + Management Boundary Plan

## Decision to review

Adopt a three-surface model:

1. **Working vault (`NT8lab`)** remains the private, complete project source
   of truth. It is not a distribution package and is never pushed wholesale.
2. **Management vault (`wiki-mediators-mgmt`)** remains a deliberately thin,
   born-clean, project-specific orchestration view. It receives selected safe
   Markdown and management-scoped derived outputs only. It is not a tool
   runtime or a mirror of the working vault.
3. **Wiki Mediators toolkit** is a future separate reusable repository. It
   carries generic dumb tools as complete, runnable units, plus templates and
   clean-checkout tests. It carries no NT8lab strategy, research, data,
   secrets, account identifiers, or machine-specific configuration.

This plan answers RYRY request `KR-20260714-001` with the **different
boundary** option: management remains thin and honest; reusable tools move to
a dedicated infrastructure distribution surface rather than being copied
partially into management.

## Evidence and current defect

The current management allow-list exports selected files from
`tools/wiki_deriver/`, including `vault_search.py` and its README. It omits
`retrieval_common.py`, `run_derivers.ps1`, `run_derivers.py`, and the runner
config. Therefore a clean management checkout advertises commands it cannot
run. This is a boundary/documentation defect, not evidence that the management
vault should become a copy of the working toolchain.

The existing one-way architecture remains correct:

```text
working vault (private source truth)
        -> deterministic bridge + secret gate
management vault (thin orchestration state)
        -> GitHub main
```

## Boundary rules

### What the management vault may contain

- Safe project orientation and architecture notes needed to direct work.
- Management-scoped derived digests and indexes generated from the staged,
  allow-listed management tree.
- Management-specific documentation that says what the thin vault can and
  cannot do.
- Review-ready plans such as this one, after the bridge secret scan.

### What the management vault must not contain

- Partial runnable tool source or a README that promises unavailable commands.
- Working-vault data, strategy source, historical extracts, session tape,
  live-system files, credentials, account identifiers, or raw reports.
- Raw working-vault derived artifacts that can disclose denied paths by
  reference.
- Machine-local paths, remote URLs, or project-specific allow-lists presented
  as reusable defaults.

### What the reusable toolkit may contain

Each exported dumb tool must be a complete unit:

- entrypoint(s), local Python helpers, configs, and README;
- a minimal fixture or clean-checkout smoke test;
- generic templates/sample configuration in place of project values;
- a clear statement of inputs, outputs, and the rule that tools compute/flag
  and never interpret or repair project truth.

The toolkit must not import from a project vault at runtime. If a tool cannot
run with only its packaged files and documented standard/runtime dependency,
it is not ready to export.

## Staged implementation plan

### Phase 0 — review and freeze the boundary

1. Have Fable 5 review this plan and RYRY's request before changing bridge
   behavior.
2. Record any accepted deviations as edits to this plan, not ad-hoc additions
   to the management allow-list.
3. Do not merge correspondence branches into management `main`.

**Acceptance:** agreement that management is a thin orchestration view and the
toolkit is a separate future distribution surface.

### Phase 1 — make the management vault internally honest

1. Replace the copied working-vault `AGENTS.md` in the management build with a
   management-specific orientation note. It must say: do not run full-vault
   search or session-start derivers here; inspect the supplied management
   corpus and request full-vault work through a local worker.
2. Remove the partial `tools/wiki_deriver/` export entries from the management
   allow-list, including its runnable-command README, unless an entry is a
   static, explicitly non-runnable explanatory document.
3. Retain or regenerate only management-scoped indexes/digests from the staged
   management tree.
4. Add a clean-checkout honesty check: no executable/README command is
   advertised unless all required local files are included and the command
   succeeds in the management checkout.

**Acceptance:** a fresh management clone contains no broken advertised tool
door and its bootstrap accurately describes its limited role.

### Phase 2 — inventory candidate dumb tools

For each candidate from `tools/wiki_deriver/` or `tools/management_bridge/`:

1. State its generic job, inputs/outputs, and trigger that makes it worth
   carrying.
2. Trace its imports, shell wrappers, configs, fixtures, and required runtime.
3. Mark every project-specific assumption: path, vocabulary, status enum,
   source layout, secret scanner rule, or derived-schema dependency.
4. Classify it as **export now**, **needs adapter/template**, or **keep local**.

Initial candidates: vault search (with `retrieval_common`), deriver runner,
index/link/orientation derivers, and the bridge/secret gate. No candidate is
exported merely because source happens to exist.

**Acceptance:** each selected tool has an explicit dependency closure and no
unexamined import from NT8lab.

### Phase 3 — build the separate Wiki Mediators toolkit repository

Create a repository with this broad shape:

```text
wiki-mediators/
  README.md
  templates/
    vault-profile.example.json
    management-bridge.example.json
  tools/
    wiki_deriver/        # complete selected tool closures only
    management_bridge/   # generic bridge + safety gates only
  tests/
    fixtures/minimal-vault/
    clean_checkout_smoke.ps1
```

Use placeholders or profile inputs for vault roots, project vocabulary,
allow-lists, remotes, and secret patterns. Do not copy `NT8lab` configuration
as if it were a generic default.

**Acceptance:** a new empty fixture vault can install/run each exported tool
using only the repository, documented runtime prerequisites, and its example
profile.

### Phase 4 — correspondence that survives management sync

Use GitHub branches outside generated management `main` for correspondence:

- `machine/<machine-name>` branches for requests/responses; or a dedicated
  `correspondence` branch if the collaboration grows beyond two machines.
- `_HANDOFFS/knowledge_requests/` and `_HANDOFFS/knowledge_responses/` are
  valid within those correspondence branches.
- Main remains bridge-owned and is never the manual correspondence surface.

The first response to RYRY should be committed on `machine/nt8lab`, at the
requested response path, and cite this plan. It must be reviewed before push.

**Acceptance:** a bridge sync of `main` cannot overwrite or erase a fetched
machine correspondence branch.

### Phase 5 — controlled adoption

Only after Phases 1–4 pass:

1. Point a non-NT8lab pilot vault at the toolkit templates.
2. Run clean-checkout, no-change, secret-abort, and boundary-honesty tests.
3. Promote any proven generic behavior to the toolkit; leave project-specific
   behavior local.

**Acceptance:** a second vault uses the same tools without copying NT8lab
content or weakening the management separation.

## Explicit non-goals

- No wholesale NT8lab export or history rewrite.
- No change to live strategy/deployment material.
- No new background watcher, database, or agent process.
- No expansion of the management allow-list except review-safe plan and
  orientation material needed to evaluate this proposal.
- No automatic merge/push of cross-machine correspondence.

## Validation required for any implementation phase

- Exact allow-list diff and staged secret-scan result, with no secret values
  printed.
- Fresh-clone/clean-checkout command evidence.
- A test that generated management `main` remains one-way from the working
  vault.
- A test that correspondence branches remain untouched by management sync.
- Reviewer sign-off before a new tool class or project content crosses a
  boundary.

## Source paths inspected for this plan

- `_FRAMEWORK/two_vault_architecture_prebuild_plan.md`
- `_FRAMEWORK/MANAGEMENT_PIPELINE.md`
- `_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md`
- `tools/management_bridge/README.md`
- `tools/management_bridge/management_auto_sync_config.json`
- `tools/management_bridge/management_vault_config.json`
- `tools/wiki_deriver/README.md`
- RYRY request `KR-20260714-001` on branch `machine/ryry`
