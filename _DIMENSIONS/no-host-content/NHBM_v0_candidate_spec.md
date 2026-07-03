---
title: "NHBM_v0 — No-Host Battle Map — Candidate Spec"
status: candidate-screen-pending
created: 2026-07-03
dimension: no-host-content
register: lighthearted lane, infrastructure-adjacent. This spec is ALSO a
  methodology transfer test — the first candidate spec written outside
  nb_lib, run under the same discipline (pre-committed gates, locked
  verdict vocabulary, trial budget). If the pipeline works on stickmen,
  the domain-agnostic claim in LAYER_ARCHITECTURE holds.
related:
  - entertainment_layer_battle_map_20260703.md
  - decision_graph_battle_edges_seed.md
  - prototypes/battle_edge_demo.svg
---

# NHBM_v0 — No-Host Battle Map — Candidate Spec

## 1. Thesis (the edge claim)

Animated, ground-truth-bound battle edges on a zoomable map reduce
time-to-orientation and keep the operator engaged during mundane review,
versus the static digest/roadmap baseline. Same species of claim as any
strategy candidate: "this structure extracts value the baseline misses."

## 2. The candidate (locked description)

- SMIL-animated SVG per UNDECIDED vault edge; a generated `.canvas` file
  lays out nodes + edge SVGs; Obsidian provides pan/zoom (Tier 1 — zero
  plugins, zero runtime JS).
- Battles bind ONLY to real undecided items (research fork, sweeper
  trigger, range-vs-swing, 6.x benches). Ground-truth card content is
  vault fact, never flavor.
- Aggregation model (§6 of the concept, locked here): per edge, three
  numbers — MASS (evidence + stakes), LEAN (−1..+1, who is winning),
  VOLATILITY (recency/frequency of score movement). Parent lean = mass-
  weighted mean of child leans. Parent volatility = mass-weighted mean of
  child volatilities, where SETTLED CHILDREN CONTRIBUTE ZERO VOLATILITY
  BUT FULL MASS. Render mapping: size←mass, stance←lean, animation
  intensity←volatility. Constant animation density per screen: at any
  zoom, animate only the top-k visible aggregates by volatility.
- Gesture vocabulary: ~6–8 named gestures (idle, jab, recoil, taunt,
  bow, fallen) from the 16-joint rig, baked as SMIL keyframes.

## 3. Pre-committed screen (LOCKED before running — no code required)

- G1 (binary, ~30s): `prototypes/battle_edge_demo.svg` animates in
  Obsidian preview on this machine.
- G2: the same SVG embedded in an Obsidian Canvas still animates and
  remains readable at three zoom levels (far / mid / close).
- G3: ONE hand-written canvas with three battle edges bound to real
  vault decisions is navigable, and each ground-truth card reads
  correctly at close zoom.

All three gates are hand tests. The deriver is NOT built until all three
pass and the operator separately decides the build trigger has fired.

## 4. Believe-it bar for the eventual build (pre-committed failure conditions)

1. G1 fails → verdict `screen-failed-pre-build` for Tier 1. Fallback
   (CSS-animated SVG or standalone HTML map) is a NEW candidate, not a
   rescue. No rescue-by-plugin.
2. ENGAGEMENT RED: over one month of real review sessions after any
   build, if the operator opens the map fewer than N = ____ times when
   the roadmap/digest was the alternative → `candidate-failed-engagement`.
   Shelf without shame. (Operator MUST fill in N before running G1;
   pre-commitment is void if N is set after testing begins.)
3. STRUCTURAL RED: if keeping the map current EVER requires a hand edit,
   that is a compute-don't-keep violation → automatic fail on the
   infrastructure axis regardless of engagement. Two-axis verdicts apply:
   engagement edge and infrastructure deployability are scored
   separately; passing one does not rescue the other.

## 5. Trial budget (Pattern 9 applies)

NHBM_v0 is ONE trial. Render styles, gesture sets, and layout schemes are
overlay dimensions — no trying variants and keeping what "felt engaging."
Engagement is the metric most vulnerable to novelty masquerading as
signal. A materially different mechanism (sound, non-battle metaphor,
non-Obsidian surface) is a new counted candidate.

## 6. Allowed verdict vocabulary

`screen-failed-pre-build` · `screen-passed-build-deferred` ·
`candidate-failed-engagement` · `candidate-failed-structural` ·
`candidate-validated-in-use`

## 7. Status history

| Date | Status | Note |
|---|---|---|
| 2026-07-03 | candidate-screen-pending | Spec locked. G1–G3 defined. N unset — operator to commit N before G1. Demo SVG banked in prototypes/. |
