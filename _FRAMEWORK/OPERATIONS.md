# Operational Notes - How This Project Works (cross-agent)

Status: living reference for cross-agent operational truth

Purpose: project-truth that every agent (Claude, Codex, any future model)
needs, kept in the vault because the vault is the shared memory.
Agent-private memory stores are per-agent and invisible across agents;
anything here that matters to all agents lives in the vault, not in one
agent's private notes.

Read order: once per session, after `AGENTS.md` and
`_FRAMEWORK/PATTERNS.md`.

---

## The wiki_logger Runs Outside Your Sandbox

The Git auto-save (`wiki_logger`, see
`_FRAMEWORK/LAYER_ARCHITECTURE.md`) is launched by the human in a
separate interactive terminal. If you run sandboxed, you cannot see that
process, and `tools/wiki_logger/runtime/status.json` is only the last
state the logger wrote. It may still say `STOPPED` from a prior run even
when the logger is currently running.

Do not assert "the logger is not running" from `tasklist`,
`Get-Process`, or `status.json`.

For ordinary task work, keep Git invisible. Write the requested files,
reports, scripts, or wiki notes and report the artifact paths and
findings. Do not add boilerplate such as "no commit by me", "left dirty
for the logger", or "the logger will capture it" to worker reports.
Those lines make the capture layer part of every research conversation,
which is exactly what the logger was built to avoid.

Only if the human explicitly asks "was my work captured?", or if capture
state is itself the task, use Git:

- `git log --oneline -5` - did a commit land that includes the file?
- `git status --porcelain` - is the placed/edited file still dirty?

In that narrow capture-check context, report what Git shows:

- "Committed as of `<hash>` at `<time>`" - when the file appears in the
  commit's `--stat`.
- "Still untracked / dirty; the logger will capture it on its next
  cycle" - when porcelain still flags it.

Leave running-state determination to the human, who can see the actual
window. The same rule applies to any future capture-layer tool whose
process lives outside the sandbox: trust the on-disk artifact (commits,
files), not process/window inspection.

Concrete example: this rule was learned the hard way on 2026-06-24 when
an agent confidently asserted "the logger is not running" based on
`tasklist /v` plus a stale `status.json` immediately after placing
`_FRAMEWORK/LAYER_ARCHITECTURE.md`. The file was committed by the
running logger two minutes later (commit `914f954`), proving the process
was running outside the sandbox the entire time. The assertion was
wrong, but the placement was correct because correctness lives in the
file landing on disk, which Git surfaces only when capture state is the
question.

## Two Kinds Of Memory: Shared Vault Vs Private Agent Memory

- The vault (`C:\VMShare\NT8lab`) is shared, Git-versioned, and read by
  every agent on boot. It holds project-truth: findings, conventions,
  and how the system works.
- Agent-private memory, such as an agent's own `.../memory/` store, is
  per-agent. It is not in the vault, not seen by other agents, and not
  captured by the logger. It is fine for model-specific quirks.
- Rule: when you learn something about how the project works, write it
  into the vault so the next agent inherits it instead of relearning it
  the hard way. Private memory helps one agent next time; the vault
  helps everyone next time.

This note itself is an example: the sandbox/logger rule above was first
learned by one agent and is banked here so all agents get it. Anything
that survives the "is this how I work, or how the project works?" test
belongs in the vault, not in private memory.
