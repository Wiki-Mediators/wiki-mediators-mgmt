---
request_id: KR-20260715-007
created: 2026-07-15
from: machine/ryry
target: machine/nt8lab
status: ready-for-review
sensitivity: repository-safe
related_request: KR-20260714-005
proposed_dimension: household-visual-inventory
response_path: _HANDOFFS/knowledge_responses/KR-20260715-007_response.md
---

# Proposal — Household Visual Inventory and Destination Map

The operator wants to pause 3D reconstruction while retaining the useful
capture discipline. The new goal is an evolving, photo-supported map of what
exists in the house, where each item was observed, where it moved during
cleaning or reorganization, and its final known destination.

This is not a surveillance system and not merely an image collection. It is a
human-confirmed inventory with photographic evidence and an append-only move
history.

## Core lifecycle

1. **Before capture:** photograph a bounded area before cleaning or moving
   anything. Take one wide context image plus detail images where necessary.
2. **Itemize:** identify visible items and assign stable item IDs. AI may
   suggest labels, but the operator confirms, corrects, merges, or rejects
   every durable item record.
3. **Move:** record an event linking the item, its previous location, its new
   location, time, reason, and evidence image where useful.
4. **After capture:** photograph the cleaned/reorganized source area so the
   record shows what left and what remained.
5. **Destination capture:** photograph the final shelf, drawer, box, room, or
   other destination and link the visible item IDs to that location.
6. **Recall:** answer questions such as “Where are the scissors?”, “What moved
   out of this cabinet?”, and “What is stored in this box?” from confirmed
   records rather than model inference alone.

## Location model

Use stable hierarchical IDs rather than prose-only locations:

```text
HOME / room / zone / container / position
```

Examples:

```text
HOME/kitchen/pantry/shelf-02/front-left
HOME/garage/west-wall/bin-07
HOME/office/desk/right-drawer
```

Rooms, zones, containers, and positions may be added gradually. A location can
exist before a complete floor map. The eventual house map is a projection of
these confirmed location records, not a prerequisite for starting.

## Minimum durable records

### Capture session

- session ID and purpose;
- bounded source area/location ID;
- before, after, and destination photo IDs;
- operator-confirmed start/end times;
- lighting/camera notes and completeness status.

### Item

- stable item ID;
- operator-confirmed name;
- optional category, description, quantity, and distinguishing features;
- current confirmed location ID;
- status: present, moved, stored, loaned, disposed, missing, or uncertain;
- sensitivity tag controlling what may be promoted into repository-safe text.

### Observation

- photo ID, item ID, location ID, and capture time;
- bounding box or coarse region when useful;
- label source: operator, OCR, model suggestion, or imported record;
- confirmation state and confidence separated explicitly.

### Move event

- event ID and item ID;
- from/to location IDs;
- operator-confirmed time and reason;
- source/destination evidence photo IDs;
- append-only correction linkage if a prior event was wrong.

## Evidence and authority rules

- Photographs are evidence, not self-interpreting truth. Occlusion, duplicates,
  reflections, and items inside containers remain possible.
- AI/OCR outputs are proposals until confirmed. Model confidence never becomes
  operator confirmation by rounding or threshold alone.
- The latest confirmed move event determines current location. Corrections
  append; they do not silently rewrite history.
- “Not visible” does not mean absent. Absence requires an explicit operator
  conclusion or a completed bounded-area audit.
- Quantities remain uncertain unless manually counted or supported by a clear
  counting procedure.

## Privacy and storage boundary

- Full-resolution household photographs, EXIF, faces, addresses, serial
  numbers, labels, documents, keys, screens, and security details stay in a
  local artifact store outside Git and outside machine correspondence.
- Git may carry repository-safe schemas, procedures, synthetic fixtures,
  redacted summaries, item/location IDs, and confirmed non-sensitive records
  only when deliberately promoted.
- Default sensitivity is local-only. Promotion to repository-safe must be an
  explicit operator action, not an automatic export.
- Face recognition is out of scope. Incidental people should be avoided or
  locally redacted before any derivative leaves the artifact store.

## Relationship to the notebook capture kit

Reuse the parts that already work:

- session-first logging;
- preparation tones and timed snapshots;
- hashes, EXIF handling, manifests, and non-destructive rejection;
- Explorer thumbnail review;
- out-of-band binary transfer.

Do not inherit assumptions that belong only to photogrammetry: 60-angle
orbits, reconstruction-specific blur thresholds, and watertight-mesh goals are
not required for inventory captures. Inventory needs wide context, readable
detail, stable locations, and human confirmation.

## Smallest useful pilot

Choose one bounded area with approximately 10–20 ordinary items, such as one
desk, shelf, or drawer:

1. Assign one source location ID and two or three possible destination IDs.
2. Take one before image and any necessary detail images.
3. Manually confirm item IDs and names; no automated detection is required.
4. Move or clean the items.
5. Take one after image plus destination images.
6. Record move events and test three recall questions.
7. Review friction, missing evidence, privacy exposure, and whether stable IDs
   remain understandable before expanding to another area.

The pilot succeeds if the operator can reliably answer where the pilot items
went and can trace each answer to confirmed evidence. It does not require a
complete house map or automatic computer vision.

## Later capabilities, gated by pilot evidence

- assisted object detection and bounding boxes;
- OCR for user-created bin/shelf labels;
- printable QR labels linking physical containers to location IDs;
- before/after visual comparison;
- room and floor-map projections;
- duplicate/uncertain-item review queues;
- query interface over the confirmed item and move ledger;
- phone-camera intake and multi-machine artifact synchronization.

## Orchestrator decisions requested

1. Approve this as a distinct `household-visual-inventory` dimension or route
   it under an existing broader dimension.
2. Select the local-only artifact root and retention policy for household
   photographs.
3. Approve or revise the item, observation, location, and move-event record
   boundary.
4. Select the first bounded pilot area; do not authorize whole-house capture
   before the pilot review.
5. Decide whether repository-safe confirmed item/location records are ever
   allowed, or whether all real household inventory remains local-only and Git
   contains schemas/procedures only.
6. Identify the smallest promotion path from this request into the working
   vault’s durable dimension notes.

No detection model, database, floor map, bulk photography, or household-data
promotion is authorized by this proposal. Please respond at
`_HANDOFFS/knowledge_responses/KR-20260715-007_response.md` on
`machine/nt8lab`.
