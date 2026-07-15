# Wiki Mediators management vault — orientation

This checkout is a thin, one-way management view generated from the working
vault. It is useful for reading current project state, plans, architecture
notes, worker digests, and the management-scoped derived index. It is not a
working-vault clone and does not contain the complete tool or project runtime.

Start with `_PROJECT_ALTITUDE_MAP.md`, then inspect
`_DERIVED/management_digest.md` and the relevant `_FRAMEWORK/` notes. Read
`_FRAMEWORK/wiki_mediators_tool_inventory.md` for a descriptive inventory of
the instruments that exist in the working vault but are intentionally absent
here.

Do not run the working-vault session-start derivers, full-vault search, replay
viewer, bridge, logger, or playbooks from this checkout. Their source,
configuration, dependencies, or target corpus are not staged here. Any
commands or working paths retained in descriptive notes refer to the full
working vault and are not runnable claims about this checkout.

When full-vault evidence, a tool run, or a change is needed, send the request
through the operator to a local worker on the working-vault machine. This
generated `main` branch is bridge-owned and one-way. Machine correspondence
branches are planned only after the boundary plan's Phase 4 prerequisites are
implemented and verified; do not use `main` as a correspondence surface.

## Spoken operator commands

### "Check the mail"

For any phrasing of mail, messages, or requests: `git fetch origin`; read new
or still-open files in `_HANDOFFS/knowledge_requests/` on `machine/nt8lab`
addressed to this machine; do what they ask; write responses at the contract's
response path on this machine's own branch; push; report what you did in three
lines.

### "Catch up" / "What's new"

For any phrasing of catch up or what's new: pull `main`; summarize what changed
since the previous pull in five lines or less.
