---
title: "Household Visual Inventory — Build Order"
status: living-reference
created: 2026-07-16
dimension: household-visual-inventory
register: sequencing authority. Rule: measurement integrity first,
  cheapest-per-token second, product-visible third, overlays last.
  Later items are SCORED by earlier ones — order is load-bearing.
provenance: operator-reviewed sequence, 2026-07-16 session.
related:
  - household_inventory_north_star_20260716.md
  - capture_cascade_spec_20260716.md
---

# Build Order

## Phase 1 — make numbers and sessions cheap
1. Token-economy pass: tools/household_inventory/TOOL_CONTRACTS.md
   (uniform columns: invocation, inputs, outputs, exit codes — format
   generalizable to other tool families later); --summary modes
   (<=6-line stdout + artifact path) on pipeline/merge/reconciliation
   reporters; exit-code discipline (0/1/2 meaningful everywhere).
2. Semantic-matcher tightening: kill generic-token inflation; re-score
   existing runs (honest numbers before anything else is graded).
3. Inference memoization: cache by (photo content-hash, model revision,
   prompt config); re-scores become free lookups.

## Phase 2 — close the open experiments (operator-involving)
4. PANTRY CONVERGENCE RUN (resequenced from old step 10 — all-new
   items, no answer key exists): operator over-shoots pantry with
   flash + close-ups → capture cascade (see cascade spec) → assisted
   confirmation builds ANSWER KEY #3 (skim-and-veto's live audition) →
   honest prefill number vs the standing 70% bar. Old shelf keys #1/#2
   remain the regression benchmark (memoized re-scores are free).
5. Transcript redaction glance: the never-exercised privacy step gets
   its first rep (two quarantined transcripts pending).

## Phase 3 — complete the product loop
6. Ledger-carryover proposer formalized (from implicit-in-
   reconciliation to a named tool).
7. Scene-diff cataloguing (photograph-and-walk-away engine; builds on
   6; includes pixel-level difference detection as layer zero — see
   cascade spec steal #2).
8. Derived views as Layer-3-style derivers: current-location
   projection, unresolved-item queue, stale-location signal.
9. Exception-review session UX (the flash-me-images burn-down).

## Phase 4 — first overlay
10. Pantry catalogue matures: quantity/expiry/opened-state fields live;
    consumption events join the vocabulary.
11. Cooking overlay: pantry x recipes join; grocery-suggestion learning
    loop begins.

## Booked, not sequenced
Tool-chest placement; expiry sweeps (falls out of 8+10); loan tracking
(vocabulary exists); retention lister; insurance rationale (a policy
line, not a build).

## Standing rules (all phases)
180W GPU cap + chunked batches + temp CSV; append-after-completion;
nothing self-promotes; every bar pre-drawn before its result exists;
audio local-only; quarantines stand.
