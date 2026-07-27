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

## PASS 0.5 — CLASSICAL MULTI-FRAME STACKING

Operator, 2026-07-18: astronomy-lineage shift-and-add / lucky-imaging SR —
NOT neural upscaling, which remains banned from measurement and answer-key
paths. Mechanism: each keeper frame is re-rendered by registering and stacking
its pass-0-parked near-duplicate neighbors (sub-pixel hand jitter IS the
signal); deterministic registration (ECC/phase correlation), stability-gated
(stack only windows whose inter-frame diff is below threshold —
object-being-moved windows are excluded), full provenance per stacked frame
(source frames, method, weights). Output feeds models AND confirmation display
legitimately — stacked frames are better measurements, not inventions.
Expected yield: modest honest gains (~1.5-2x effective resolution, strong
denoise) on exactly the residual-gap classes (small items, label text).
Trigger amended by operator authority, 2026-07-18: build before the deferred
answer-key #3 sitting because the 322-card confirmation queue is itself the
evidence. Measurability shifts from answer-key delta to before/after queue
metrics: cards shown, grouped distinct-object estimate, label-OCR yield, and
stacked-vs-raw proposal delta. The sitting resumes only at <=120 grouped cards
with duplicates collapsed and label reads present.

## Narration alignment — deictic-lag finding (operator, 2026-07-18)

Speech leads and trails its visual target; line-per-frame or segment-midpoint
assignment is false precision. Tier 1 uses a config-owned asymmetric frame
window (default -6s/+4s) and weights matches by temporal distance; every
corroboration marker carries its measured delta (for example, `Δ+2.3s`). Tier
2 treats Whisper utterances as events that seek their frame: utterance text is
matched against proposal labels and permitted label-OCR reads across the
window under tightened matcher rules, with generic-only tokens excluded. An
utterance attaches where its content matches, not merely where its midpoint
lands. Transcript text and matches remain quarantined proposals; nothing
self-promotes. Tier 3, model-inferred narrative flow, is explicitly refused:
it would invent temporal/identity links beyond the recorded evidence.

### Narration enrichment mechanisms (operator, 2026-07-18)

The config-owned pantry lexicon supplies canonical grocery, spice, condiment,
dairy, and meat vocabulary with explicit aliases and known
mis-transcriptions. Edit-distance plus phonetic matching may emit a
`LEXICON-CORRECTED` proposal, but it always preserves and displays the original
transcript text; only an operator tap ratifies it. Every operator-confirmed
label is eligible for deterministic append to the lexicon's `confirmed`
section, so the household teaches its own vocabulary without model authority.

A deliberately small relation vocabulary (`behind`, `background`, `back-left`,
`next to`, `top`, `hidden`, `cannot see`) preserves matched utterance text as a
location hint. The hint enters observation location context only with operator
confirmation. Scene-graph parsing remains refused under the Tier-3 rule.

If an utterance lexicon-matches an item but no model proposal exists in its
deictic window, it becomes a T2 `narration-only` card. This is operator spoken
testimony, not visual corroboration. Narrator-declared invisibility is the
distinct evidence state `DECLARED-OCCLUDED`, extending the standing separation:
not-analyzed != not-visible != absent != declared-occluded. The verbatim
utterance remains quarantined and nothing self-promotes.
