---
title: Wiki Architecture Current/Future Visual Note
status: catalogued-finding
created: 2026-06-28
source: operator discussion + visual screenshot
related:
  - _FRAMEWORK/LAYER_ARCHITECTURE.md
  - _FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md
  - _RESEARCH/two_tier_retrieval_2026.md
asset: _FRAMEWORK/assets/wiki_architecture_current_future_20260628.png
---

# Wiki Architecture Current/Future Visual Note

![Current and future state of the wiki architecture](assets/wiki_architecture_current_future_20260628.png)

## Finding

Cataloguing the wiki is not overfitting in the prediction sense: it is
organizing existing knowledge, not fitting a model to generalize to unseen
data. The real failure mode is the knowledge-organization analog of
overfitting: imposing a taxonomy finer than the substrate supports. That
looks like premature schema, over-naming, or categories that reflect the
organizer's bias rather than the vault's actual shape.

The guardrail is to derive structure from what is already present. Dumb
tools should surface real clusters, broken links, stale references, churn,
coupling, and centrality. The system should resist hand-drawing the taxonomy
before those signals exist.

## Current State

The current architecture state is:

- Layer 1: agents write; conventions still being tightened.
- Layer 2: logger records; built and running.
- Layer 3: first dumb deriver tool is being specced/built.
- Layer 4: distillation is designed and banked, but not built.
- Git substrate: the source of truth under all layers.

The important read is that the shape is already stable. The future system
does not require a different architecture; it deepens the same spine.

## Future State

The intended future state keeps the same flow:

```text
write -> record -> derive -> distill
```

The derive layer fills out into a toolkit:

- link/reference checker
- churn and coupling
- centrality
- survivor ledger
- orphan reporter
- convention linter

The smart passes remain occasional and cold:

- on-demand summarizer
- two-stage citation verification
- housekeeping agent that resolves flags raised by dumb tools

## Visualization Lesson

Venn diagrams are the wrong tool once there are many overlapping topics.
They break down after a few sets and encourage hand-imposed categories.

The right future view is a coupling matrix: a proportional table showing
which notes or topics co-occur and how strongly. That should be derived
from commit history and references, not drawn by hand. In other words, the
"overlap of topics" visual is itself a deferred deriver output.

## Operational Note

Do not name or taxonomize the system too early. Let the name and category
structure emerge from what the Layer 3 tools surface.
