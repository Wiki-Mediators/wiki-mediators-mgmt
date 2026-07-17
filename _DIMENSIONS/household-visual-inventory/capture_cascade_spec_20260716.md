---
title: "Capture Cascade — Progressive Refinement with Quality-Gated Routing"
status: reviewed-design
created: 2026-07-16
dimension: household-visual-inventory
register: design spec for the intake pattern. Build authorization comes
  from the build-order note's phase gating, not this file.
provenance: operator design (2026-07-15..16) + external validation
  (NoScope VLDB'17 cascade literature; industrial waterfall-filtering
  pipelines) — research-intake caveats in final section.
related:
  - household_inventory_build_order_20260716.md
  - household_visual_inventory_desktop_mvp_plan_20260715.md
---

# Capture Cascade

## Doctrine: over-shoot freely; processing depth is EARNED

Capture is cheap and irreversible; analysis is expensive and patient.
Every image gets the preservation guarantee (hash, immutable original,
manifest, session log). NO image is guaranteed analysis — processing
depth is routed by expected value.

## The cascade (passes in order)

- PASS 0 — deterministic triage (no models, no tokens): blur/exposure
  scoring (existing Laplacian machinery, promoted from record-only to
  rank-and-route), near-duplicate collapse (perceptual hash). Blurred
  frames are MARKED AND PARKED, never deleted (a blurred frame can
  still corroborate presence). VOLUME GATE: batches under ~15 images
  skip triage entirely — everything processes; the filter earns its
  place only when volume does.
- PASS 1 — lightweight model (Florence tiled): quick provisional
  labels on triage's keepers. "Information quickly, not final
  analysis."
- PASS 2 — heavy model (Qwen tiled; chunked, power-capped, temp CSV):
  operator-triggered idle-time batch over the best prospects /
  escalated frames. Never a daemon.
- Each pass APPENDS proposal layers (model/revision/config/timestamp);
  nothing rewrites; memoization makes re-passes free.

## Session scoreboard (mandatory summary line)

Every session reports counts, e.g.:
"38 shot → 6 blurred-parked → 24 unique → 24 pass-1 labeled →
9 heavy-passed → 15 skipped-low-priority". This is the --summary
discipline applied to capture.

## Skip-with-status: the three-state epistemics rule

Never-analyzed must be a RECORDED state, not an absence. Every frame
carries: heavy-pass = completed | queued | skipped-low-priority
(reason). Coverage/reconciliation numbers score ONLY against analyzed
frames. NOT ANALYZED ≠ NOT VISIBLE ≠ ABSENT — three distinct states,
never conflated (extends KR-007's "not visible does not mean absent").
Skips are reversible by construction: originals persist, so any recall
question may promote a skipped frame to the heavy queue (question-
driven promotion is the best trigger there is).

## External validation + adopted refinements (2026-07-16 research)

The cascade is field-standard: NoScope (Stanford, VLDB 2017) built the
same shape — cascades of cheaper models before an expensive reference
model, stopping at the cheapest confident layer — for video analytics;
industrial training pipelines use the same "waterfall filtering"
(physical filters → semantic gates → perceptual-hash dedup). Three
refinements ADOPTED from the literature:

1. AGREEMENT BANDING (buildable now): three-way routing — where
   Florence and Qwen AGREE on a region, it settles cheap (no
   escalation); where they DISAGREE, it escalates. Cross-model
   agreement is the poor-man's confidence band, since both models'
   raw confidence is uncalibrated (they never hedge — known gap;
   nothing may gate on raw confidence until calibrated).
2. PIXEL-DIFF LAYER ZERO (banked with scene-diff, build together):
   for REPEAT coverage of a known location, diff against the prior
   session's frame first — unchanged regions carry the ledger's answer
   forward at zero model cost.
3. THRESHOLD SWEEP AGAINST ANSWER KEYS (banked): triage/routing
   thresholds tuned by deterministic linear sweep against keys #1/#2
   (which settings would have routed known-good frames correctly),
   not hand-picked. Run once per key change; memoized.

## Research-intake caveats

NoScope's orders-of-magnitude claims are paper-reported on fixed-angle
surveillance video; cluttered handheld household shots will see far
less. NoScope's per-video TRAINED specialist models are explicitly NOT
adopted — this cascade stays zero-training, config-only. External
claims remain research-input grade until measured here.
