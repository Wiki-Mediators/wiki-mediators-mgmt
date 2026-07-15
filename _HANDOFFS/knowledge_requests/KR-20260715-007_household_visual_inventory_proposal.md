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

## Amendment 1 — Operator-led product and technical decisions

The operator has delegated routine design decisions to the notebook worker so
iterations remain quick. Fable-5 is an escalation/review surface when the work
is genuinely stuck or when a proposed decision conflicts with broader vault
architecture; it is not intended to become an approval bottleneck for every
field or implementation detail. No build begins until this amended concept has
received one orchestrator review for insight and conflicts.

### Product job

The primary user question is:

> Where did this thing go?

The product must reduce search and memory burden without turning household
organization into a labeling or data-entry job. The core user loop is:

1. photograph or narrate one bounded area;
2. receive candidate items and virtual labels;
3. correct only meaningful mistakes;
4. clean, store, or move objects normally;
5. photograph destination areas;
6. record confirmed move events and evidence;
7. retrieve an item by name, description, previous location, or destination.

The pilot is successful when the operator can later locate five moved items
quickly and trace each answer to a confirmed destination record. If capture and
confirmation are more burdensome than ordinary searching, the workflow must be
redesigned before expansion.

### Classification decision — facets, not one taxonomy

The catalog will not force every entity into a single category tree. It will
use a small set of entity roles plus independent facets.

Entity roles:

- structure: room, wall, floor, ceiling, window;
- fixture: electrical outlet, built-in light, cabinet, fixed shelf;
- storage location: drawer, shelf volume, bin, closet zone;
- movable asset: bicycle, helmet, toaster, blender, phone, cable, clothing;
- consumable lot: spices, food, cleaning supplies;
- observation: timestamped evidence that an entity was visible somewhere;
- event: move, store, consume, discard, loan, correct, or mark missing.

Independent facets may include mobility, function, category, condition,
organization state, dimensions, weight, usable volume, access frequency,
operating constraints, sensitivity, and confirmation state.

Examples:

- A slow cooker is a movable asset, small appliance, kitchen item, occasional-
  use object, and electricity/clearance-constrained object. Its current and
  preferred storage locations are separate fields.
- Clothing on the floor remains a clothing asset. Its current location is a
  floor zone and its organization state is `out-of-place`; putting it away
  creates a move event.
- Spices are consumable lots with quantity, unit, opened state, expiry, storage
  requirements, and later recipe-compatibility metadata.
- `electrical-outlet` is the canonical term for building power receptacles so
  they cannot be confused with storage containers.

### State and uncertainty decision

An untouched house area has a high probability of remaining unchanged, but
probability is not observation. Each entity may carry:

- `last_seen_at`;
- `last_confirmed_at`;
- `current_location_id`;
- `preferred_location_id`;
- `location_confidence`;
- `mobility_class`;
- `change_risk`;
- evidence and confirmation status.

Fixtures can have low change risk; phones, cables, clothing, food, and tools
have high change risk. The system may rank likely locations but must not
silently restate “probably unchanged” as “confirmed present.”

### Virtual identity decision

Physical labels are optional and should not be required for ordinary objects.
The system mints a stable virtual item ID on first observation even when label
or location is unresolved:

```text
item_id: ITEM-000184
suggested_label: unknown-small-electronic
location_id: UNRESOLVED/session-001/frame-region-07
confirmation: unreviewed
```

Later evidence may refine the label and attach the item to a stable location
without changing its ID. Physical QR labels may be considered later for opaque
bins or high-value storage containers only.

Model labels do not establish personal identity. Cross-session identity
suggestions may use crop similarity, narration, prior location, time proximity,
and distinguishing features, but uncertain merges require operator review.

### Geometry and simulation decision

The useful representation is a logistics model before it is a photorealistic
digital twin:

1. 2D rooms, zones, furniture footprints, and storage containers;
2. 2.5D room heights, shelf volumes, and object bounding boxes;
3. simple 3D boxes and labels;
4. storage-fit and placement suggestions based on dimensions, weight, access
   frequency, proximity, clearance, and environmental constraints;
5. detailed reconstructed geometry only where it demonstrates additional
   value.

Approximate room and shelf measurements should initially come from a tape or
known scale reference. Uncalibrated photographs do not provide trustworthy
dimensions. A complete house scan or floor model is not a pilot prerequisite.

### Narrated-video intake decision

A short narrated video may be the lowest-friction intake mode. Proposed flow:

```text
video + audio
  -> regularly sampled candidate frames
  -> blur/exposure rejection
  -> scene-change and redundancy filtering
  -> timestamped narration transcript
  -> candidate objects, boxes, OCR, and descriptions
  -> human confirmation queue
  -> item/location/observation/move records
  -> Wiki projections and recall indexes
```

Keyframe selection should combine time sampling, sharpness/exposure, perceptual
similarity, scene changes, coverage quotas, and narration timestamps. A phrase
such as “this is the east shelf” should promote nearby frames for review.

Audio, transcripts, and vision outputs remain evidence layers. Original audio
is retained locally so transcription errors can be checked. Transcribed words
are proposals until confirmed when they affect durable item or location facts.

### Software decision — smallest stack first

Initial implementation stack:

1. **FFmpeg + OpenCV** for video/audio handling, candidate-frame extraction,
   existing Laplacian sharpness checks, exposure checks, scene changes, and
   duplicate reduction.
2. **faster-whisper** for local timestamped narration transcription, including
   word timestamps and voice-activity filtering where useful.
3. **Microsoft Florence-2** on the GPU desktop for initial scene descriptions,
   object boxes, dense-region captions, OCR, and phrase grounding.
4. **Human confirmation** before any candidate becomes a durable item,
   location, observation, or move fact.

Deferred until measured need:

- **Grounding DINO** for open-vocabulary detection of operator-requested
  concepts that Florence-2 misses;
- **SAM 2** for segmentation and propagation of confirmed objects through
  video;
- visual embeddings for cross-session identity suggestions;
- an online vision agent for selected, operator-approved difficult cases.

Official implementation references:

- Florence-2: `https://huggingface.co/microsoft/Florence-2-large`
- Grounding DINO: `https://github.com/IDEA-Research/groundingdino`
- SAM 2: `https://github.com/facebookresearch/sam2`
- faster-whisper: `https://github.com/SYSTRAN/faster-whisper`
- OpenCV Laplacian: `https://docs.opencv.org/trunk/d5/db5/tutorial_laplace_operator.html`

The initial build remains `OpenCV -> Florence-2 -> human confirmation` after
video/keyframe/transcript preparation. Grounding DINO and SAM 2 do not enter
the dependency surface merely because they are capable.

### Machine split

Notebook responsibilities:

- capture video/audio and stills;
- write session metadata before inference;
- select and hash keyframes;
- perform inexpensive deterministic quality and redundancy checks;
- optionally transcribe on CPU if measured runtime is acceptable;
- package binaries and sidecars for out-of-band transfer.

Desktop responsibilities:

- validate the exact Pascal-compatible model runtime before model download;
- run Florence-2 and any later GPU inference;
- create candidate item/box/OCR/description sidecars;
- support local-agent review and identity reconciliation;
- bank confirmed results and produce repository-safe Wiki projections.

Online analysis is optional and privacy-gated. Default processing remains
local. Any online pass requires operator selection, prefers crops to whole-room
images, redacts faces/documents/screens/addresses/security details where
needed, records the service/model and exact derivative sent, and never promotes
the result automatically.

### Layering into Wiki Mediators

- Layer 1 / local evidence: original video, audio, photographs, keyframes,
  transcripts, boxes/masks, model outputs, and review receipts.
- Structured working records: stable item IDs, location hierarchy,
  observations, move events, uncertainty, and source anchors.
- Derived indexes: current-location projection, unresolved-item queue,
  stale-location signal, room/container inventories, and cross-session recall.
- Durable prose: procedures, schemas, accepted decisions, pilot findings, and
  source-anchored summaries. Prose does not become the authoritative item
  ledger.

Raw household media remains local-only and outside Git. Model outputs carry
model/version, prompt/configuration, source frame, timestamp, candidate label,
box/mask, confidence, and confirmation status. Derived current location is a
projection over confirmed append-only events.

### Revised smallest pilot

Use one narrated 30–60 second video of one basement shelf, wall segment,
drawer, or similarly bounded area:

1. one wide establishing view plus slow detail passes;
2. narration of location and meaningful objects;
3. approximately 10–20 retained nonredundant keyframes;
4. timestamped transcript linked to frames;
5. Florence-2 candidate descriptions and boxes on the desktop;
6. manual confirmation of meaningful candidates only;
7. unresolved location IDs permitted;
8. one before/after/destination movement test;
9. three recall questions plus a friction/privacy review.

The first deliverable is a review sheet showing retained frames, retention
reasons, nearby narration, candidate objects, confirmed records, and unresolved
location or identity questions. No database UI, SAM 2 integration, whole-house
capture, or 3D renderer is required for the pilot.

### Requested orchestrator review

Treat the above as the operator/notebook working decision set. Please identify:

1. conflicts with existing Wiki Mediators layer or authority rules;
2. privacy or provenance failure modes not addressed here;
3. a smaller end-to-end pilot if any step is still premature;
4. an existing working-vault tool or schema that should be reused instead of
   rebuilt;
5. Pascal/runtime constraints that materially change the Florence-2-first
   choice;
6. the correct durable promotion destination for this dimension.

If no blocking conflict exists, respond with a concise proceed/revise verdict
and the smallest corrections. Implementation remains paused until that review.
