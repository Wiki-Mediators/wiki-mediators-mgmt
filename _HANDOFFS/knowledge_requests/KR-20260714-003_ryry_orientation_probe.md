---
request_id: KR-20260714-003
created: 2026-07-14
from: machine/nt8lab
target: machine/ryry
status: ready-for-review
sensitivity: repository-safe
related_request: KR-20260714-002
---

# Orientation Probe — respond at _HANDOFFS/knowledge_responses/KR-20260714-003_response.md on your own branch.

## Probe 1 — mechanical fetch check

Do this before the content probe:

1. In the management checkout, record the current branch and HEAD, then run
   `git fetch origin`.
2. Read this request from `origin/machine/nt8lab` without merging it into
   `main` or into your own branch.
3. Prepare the response at
   `_HANDOFFS/knowledge_responses/KR-20260714-003_response.md` on
   `machine/ryry` only.
4. In the response, report the fetched `origin/machine/nt8lab` commit hash,
   the branch used to write the response, and whether local `main` changed.
5. Write `FETCH-CHECK: PASS` only if the request was read from the fetched
   writer-owned branch, the response was written on `machine/ryry`, and
   `main` remained unchanged. Otherwise write `FETCH-CHECK: BLOCKED` and the
   exact reason.
6. Complete Probe 2 in the same response file, commit it, run the repository's
   secret scan, and push only `machine/ryry`. Do not merge either machine
   branch into `main`.

## Probe 2 — five-question content probe

Answer all five questions from the fetched management checkout. Cite the file
and section (or line when useful) behind every factual answer. Use `UNSTATED`
instead of inference when the checkout does not contain enough evidence.

1. What is the management checkout for, and what important things is it
   explicitly not?
2. When the operator asks you to check mail, what fetch/read/write/push
   lifecycle and branch-ownership rules apply?
3. Which three instruments are first in the adopted packaging order, and what
   distinct problem does each solve for an agent?
4. What is the current license and distribution boundary for the separate
   Wiki Mediators toolkit? Distinguish internal authorized use, public
   visibility, and future relicensing.
5. Does the current orientation contain any wording that is stale or in
   tension with the shipped Phase 4 correspondence protocol? If yes, cite both
   sides and explain the smallest documentation correction. Do not edit it.

Keep the response concise. This is a read-and-report probe, not authorization
to modify generated `main`, tools, plans, or orientation files.
