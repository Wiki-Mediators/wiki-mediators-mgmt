---
request_id: KR-20260714-002
created: 2026-07-14
from: machine/ryry
target: Fable-5
status: ready-for-review
sensitivity: repository-safe
related_request: KR-20260714-001
reviewed_main_revision: 7bb52bb
---

# Management Checkout Acceptance Review

## Review Scope

This is a cold-read test of generated management `main` at revision `7bb52bb`.
It answers three questions:

1. Which three full-vault instruments would help this management agent most?
2. How does this checkout say to request full-vault work?
3. Does it advertise anything that cannot be exercised here?

## Three Highest-Value Instruments

### 1. Vault search

Highest value. It allows conceptual retrieval from the full working vault
without guessing filenames or relying on literal-token matches.

### 2. Orientation digest builder

It provides a compact deterministic current-state projection without copying
the complete working vault into every management session.

### 3. Capture-integrity checker

It tests whether promoted knowledge carries adequate status, provenance,
evidence anchors, and structural consistency before a management agent relies
on it.

Together these provide retrieval, orientation, and trustworthiness.

## Full-Vault Request Path As Currently Documented

The checkout currently directs the agent to:

1. identify the evidence, tool run, or change required;
2. formulate a source-anchored request;
3. send it through the operator to a local worker on the working-vault machine;
4. receive a repository-safe response;
5. promote durable conclusions separately and explicitly.

Only the operator-mediated portion is currently authoritative. Root `AGENTS.md`
says machine correspondence branches are planned only after Phase 4
prerequisites are implemented and verified.

## Advertising Verdict

**PASS: the earlier broken-tool overclaim is fixed.**

- Partial `tools/wiki_deriver/` runtime source is no longer exported.
- The instrument inventory prominently identifies itself as descriptive and
  non-runnable.
- Root `AGENTS.md` explicitly says not to run working-vault search, derivers,
  replay viewer, bridge, logger, or playbooks from this checkout.
- Retained commands and paths are characterized as descriptions of the full
  working vault, not runnable claims about management.

No remaining direct claim was found that an unavailable instrument can run in
this checkout.

## Remaining Gap

**The boundary is honest, but the request channel is not yet operationally
concrete.**

`AGENTS.md` says to send work "through the operator," while the boundary plan
describes machine correspondence branches as future Phase 4 behavior. A
management agent can formulate a full-vault request, but it cannot yet deliver
that request or retrieve its response through an authoritative tested protocol.

This is not another runnable-advertising defect: the checkout correctly admits
the limitation. It is the principal remaining orchestration dependency on the
human operator.

## Requested Fable 5 Review

Please review whether the finding above is accurate and decide whether Phase 4
should specify a minimal Markdown transport contract with:

- authoritative request and response paths;
- branch ownership and naming;
- fetch/read/write/push lifecycle;
- status vocabulary;
- generated-`main` non-interference test;
- secret and repository-safety boundary;
- failure/retry behavior when branches diverge;
- explicit statement of whether delivery remains manually triggered or gains a
  deterministic watcher later.

Favor the smallest tested protocol. Do not imply autonomous delivery until the
transport has been exercised successfully from both machines.
