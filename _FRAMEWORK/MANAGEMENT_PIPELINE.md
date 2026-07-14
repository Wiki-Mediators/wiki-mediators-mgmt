---
title: "Management Pipeline"
status: "orientation-note"
scope: "management vault orchestration"
---

# Management Pipeline

The management vault is regenerated from the working vault. The working vault
remains the full local source of project truth; the management vault is the
thin orchestration surface.

The bridge and auto-sync tools live in the working vault under
`tools/management_bridge/`. They read the working vault, stage a clean
management tree, run the secret scan, and write only to the management vault.

The proposed boundary for reusable dumb tools, the thin management surface,
and cross-machine correspondence is recorded in
`_FRAMEWORK/wiki_mediators_export_and_management_boundary_plan_20260714.md`.

The sync direction is one way:

`working vault -> management vault -> GitHub`

Runtime status is local at:

`C:\VMShare\NT8lab_mgmt_runtime\status.json`

After GitHub is updated, the connected project still needs a manual human
refresh using the project's Sync button. The bridge cannot click that for you.

Orchestration agents should not edit or push from the working vault. The
working vault has no management GitHub remote.
