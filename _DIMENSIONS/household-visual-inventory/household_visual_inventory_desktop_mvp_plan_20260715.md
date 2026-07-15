---
title: Household Visual Inventory Desktop MVP Plan — Orchestrator Review
status: proposed-review
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
