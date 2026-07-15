---
title: Household Visual Inventory Desktop MVP Plan — Orchestrator Review
status: reviewed-proceed
created: 2026-07-15
dimension: household-visual-inventory
review_target: Fable-5
sensitivity: repository-safe
related:
  - KR-20260715-007
  - _HANDOFFS/knowledge_requests/KR-20260715-007_household_visual_inventory_proposal.md
  - _HANDOFFS/knowledge_responses/KR-20260715-007_response.md
provenance: operator decisions and local transfer trial, 2026-07-15
---

# Household Visual Inventory Desktop MVP Plan — Orchestrator Review

## Review gate

This is a plan for review, not build authorization. Fable-5 should identify
architecture, privacy, provenance, or scope conflicts before implementation.
No model installation, household capture expansion, ledger promotion, or
automation is authorized by this note.

## Outcome

Build the smallest local desktop path that can take one deliberately selected
phone photograph, preserve the original, produce deterministic intake and
quality evidence, let the operator confirm useful observations, and answer a
small recall question from confirmed records. The product job remains:
**“Where did this thing go?”**

The first fixture is a successfully transferred photograph of the operator's
dog outdoors. It is useful because it exercises a real private image, a living
household entity, associated movable assets such as harness/leash, and a
household location. The binary, filename, hash, and metadata remain local and
do not enter Git or the management bridge.

## Authority and safety boundary

- The operator's existing animal-care schedule remains authoritative. This
  system does **not** decide or prompt feeding, watering, medication, exercise,
  health, safety, or any other care action.
- A photograph may support observations such as `pet seen in yard` or a bowl
  appearing `empty`, `partial`, `full`, or `uncertain`; those observations are
  inventory evidence only and never a care decision.
- No face recognition, person tracking, pet biometrics, surveillance, or
  inference of health/behavior is in scope.
- AI/OCR outputs remain proposals. Only explicit operator confirmation creates
  a durable fact.
- Original photos, derivatives, EXIF, manifests, and the real ledger stay in a
  local artifact root outside the vault, Git, correspondence branches, and all
  cloud-synced folders.
- Git carries this plan, schemas, procedures, synthetic fixtures, and redacted
  findings only. Promotion of real item/location records remains deferred.

## Proposed schema refinement

Keep the KR-007 facet model and add a distinct `living-household-entity` role
for pets. This avoids calling a dog an object while allowing timestamped,
operator-confirmed observations and links to ordinary household assets.

The MVP therefore recognizes three broad record subjects:

1. **Places:** home, yard, room, zone, shelf, drawer, bin, or position.
2. **Things:** fixtures, storage locations, movable assets, and consumable
   lots.
3. **Living household entities:** pets, represented only through minimal
   observations and associations; no care or biometric authority.

The approved durable record boundary remains location, item/entity,
observation, and append-only event. Confidence and confirmation are separate.
`Not visible` never means absent.

## What to build first

### Stage A — explicit one-file intake, no watcher and no model

Create a small command-line intake tool that receives a file path selected by
the operator and:

1. verifies the extension, file signature, and successful image decode;
2. computes SHA-256 and assigns a session/photo ID;
3. copies the original into an immutable local session folder without deleting
   or modifying the source;
4. records byte size, dimensions, capture time when available, and source
   provenance in a local manifest;
5. creates a separate EXIF-stripped working derivative and mechanically proves
   the derivative contains no EXIF;
6. computes deterministic blur and exposure signals, recording thresholds and
   raw measurements rather than silently rejecting the image;
7. writes a human-readable local review report.

LocalSend remains transport only. For the MVP it uses manual acceptance and a
deliberately selected source file. Global Quick Save/auto-accept is not part of
the build. Favorites-only intake and a dedicated LocalSend destination may be
reconsidered after the explicit path proves safe.

### Stage B — manual confirmation and recall

Add the smallest local append-only records needed to:

- confirm a place, living entity, or object observation;
- correct an observation by appending a correction rather than overwriting it;
- record a later confirmed move/location event; and
- answer one or more recall questions using confirmed records only.

The dog fixture may establish `living household entity observed`, an outdoor
location, and associated visible assets. A later bounded-area pilot supplies
ordinary objects and a before/after/destination move test.

### Stage C — assisted vision only after A and B pass

Validate the Pascal-compatible runtime before downloading Florence-2. If
introduced, run it at fp32 and record model/runtime versions and source photo
IDs. Descriptions, boxes, OCR, and bowl-state suggestions enter a confirmation
queue only. Non-label OCR remains quarantined. Grounding DINO, SAM 2, online
vision, narrated video, and cross-session identity remain deferred to their
existing triggers.

#### Rung-1 scorecard (2026-07-15, STAGEC-20260715T182353Z-801365f3)

Engineering **PASS** (Pascal fp32 GPU inference, torch `2.6.0+cu118`,
transformers `4.49.0` pinned after `5.8.1` incompatibility, model revision and
safetensors hash recorded). Model performance **FAIL** versus the skim-and-veto
bar: 12.5% confirmed coverage, approximately 9% thing recall, less than 6%
ledger-conditioned precision, and all three known uncertainties unseen (no
waffle, no guess - not detected). Failure class: dense cluttered scenes, small
objects, and whole-frame detection; confidence band `0.117-0.482` throughout.
Caveats: the ledger is not exhaustive, so the precision floor is understated;
the conservative matcher may undercount vocabulary variants.

#### Progressive-enrichment model ladder

1. **Rung 1:** Florence-2 fast pass.
2. **Rung 2:** Qwen2.5-VL-7B-class quantized VLM; sequential batch passes only,
   never co-resident with another model in 12 GB VRAM.
3. **Rung 3:** online inference only under the KR-007 privacy gates.

Pattern 6 for vision: cross-model disagreement routes to the confirmation queue
at priority. Qwen is the Rung-2 comparison default. MiniCPM-V 2.6 is banked
separately against the deferred cross-session-identity trigger. VLM OCR of
serials and barcodes remains quarantine-by-default regardless of capability.

Rung-2 install decision waits on the tile-crop and matcher-audit experiments.
If tiled recall remains below approximately 30-40%, the Rung-2 trigger fires
with the named failure class and Qwen installs in the next authorized session.

#### Rung-1 follow-up experiments (2026-07-15)

**Tile-crop pass — `STAGEC-TILED-20260715T183746Z-547c9d74`.** Florence-2
ran over overlapping 2x2 and 3x3 crops with 20% overlap. Region boxes were
mapped back into full-frame coordinates; 48 overlap duplicates were removed.
The meaningful deduplicated set held 181 non-empty region proposals. Against
the same 48-observation ledger, mechanical recall rose from 12.5% to 22.9%
(`+10.4` percentage points) and thing recall reached 25.0%, while
ledger-conditioned precision fell from 8.7% to 6.1% (`-2.6` points). Tiling
helped, but did not reach the approximately 30-40% skim-and-veto gate and
increased proposal volume substantially.

**Original matcher audit — 69 whole-frame region proposals.** A one-time
semantic reconciliation removed three generic/ambiguous automatic matches and
added three clear vocabulary or matcher misses (`footwear` to `shoes` in two
photos; `shelf` to the confirmed lower-shelf place). The conservative corrected
floor is therefore still 6 confirmed hits: 6/69 = 8.7% ledger-conditioned
precision, 6/48 = 12.5% observation recall, and 5/44 = 11.4% thing recall.
Generic `box` and `storage box` proposals were not credited to more specific
confirmed box or basket records without identity evidence.

**Rung-2 trigger: FIRED.** Named failure class: dense clutter plus small-object
loss persists after tiling; the recall gain comes with proposal explosion and
remains below the gate. Qwen2.5-VL-7B-class is next-session work under a
separate install/run authorization; it is not installed by this experiment.

### Staged roadmap - scene-diff cataloguing

Scene-diff cataloguing (operator vision, 2026-07-15): the post-Stage-C
loop inverts from operator-narrates-facts to photograph-and-walk-away -
new photo of a known location diffs (deterministic set arithmetic, dumb-
tool shape) model proposals against the ledger's last confirmed state
for that location ID, emitting candidate move/arrival/departure events
into the confirmation queue. Accuracy asymptote acknowledged <100%;
the residual queue is the product's human session, by design. Ordering:
Stage C detection first, scene-diff second (its own go), cross-session
identity stays deferred on its existing trigger. Confirmation gate and
append-only ledger are invariant across all automation depth.

## Local storage contract proposed for review

The operator still selects the artifact root. Under a placeholder
`<local-artifact-root>` outside the vault and cloud-sync roots:

```text
incoming/                 manually accepted transfer files
sessions/<session-id>/
  originals/              immutable local copies
  working/                EXIF-stripped derivatives
  checks/                 deterministic reports
  manifest.csv
  capture_session.md
ledger/
  observations.jsonl
  events.jsonl
  corrections.jsonl
```

No background daemon is required. The initial command processes one explicit
file and exits.

## Acceptance tests before any bounded household pilot

1. The transferred fixture decodes and its local original hash is unchanged
   before and after processing.
2. The tool never deletes or edits the transfer source or immutable original.
3. The derivative opens successfully and the EXIF-removal check passes.
4. Blur/exposure measurements and thresholds appear in the report; an
   uncertain result remains visible instead of disappearing.
5. One operator-confirmed observation can be appended, corrected, and recalled
   without rewriting earlier evidence.
6. A repository scan proves no photo, EXIF, real ledger, local absolute path,
   or household detail entered the vault or management tree.
7. Re-running the same source is detected by content hash and does not create
   an ambiguous duplicate record.

## Operator gates after review

1. Select and verify a local artifact root outside the vault and every
   cloud-synced path.
2. Select one bounded pilot area after Trial 0 passes. The outdoor dog fixture
   validates intake but does not replace the before/after/destination pilot.
3. Approve any dependency installation separately after the implementation
   plan names the exact packages and versions.

## Questions for Fable-5

1. Does adding `living-household-entity` conflict with the accepted KR-007
   facet/record boundary, or is it the cleanest schema extension?
2. Is explicit one-file intake the correct first build, ahead of a watcher,
   narrated video, or Florence-2?
3. Are any privacy/provenance failure modes missing from the immutable-original
   plus stripped-derivative design?
4. Should the executable and real ledger live entirely beside the artifact
   root, while the vault keeps only procedures/schemas, or should generic code
   have a separate repository-safe source location?
5. Is any existing capture-kit component mature enough to reuse without
   importing photogrammetry assumptions?
6. Verdict requested: `PROCEED`, `REVISE`, or `BLOCK`, with only the smallest
   required corrections.

## Fable-5 review (2026-07-15) — PROCEED with four corrections

1. living-household-entity approved as schema extension; observation-only
   authority and care-decision disavowal are binding.
2. Stage A (explicit one-file intake) confirmed as first build; Stage B/C
   ordering and existing deferral triggers stand.
3. Corrections: (a) LocalSend destination pinned to `<root>/incoming/` — never
   Downloads; setup step with check. (b) Metadata strip covers ALL blocks:
   EXIF, XMP, IPTC, and embedded thumbnail; the mechanical check proves absence
   of every metadata segment. (c) Windows thumbnail-cache/recent-files residue
   documented as accepted known local residue. (d) Code lives in the vault
   (generic, no machine facts); artifact-root path and machine facts live in a
   local gitignored profile config per the adapter pattern; ledger and media
   stay beside the artifact root.
4. Capture-kit reuse: mechanics yes (hash/manifest/EXIF/non-destructive
   reject), photogrammetry thresholds no; record-don't-reject stands.
5. Build authorization: Stage A may proceed under Amendment 1 delegation once
   the operator supplies the artifact root; dependency installs still require
   the named-packages gate from the plan's operator gates.
