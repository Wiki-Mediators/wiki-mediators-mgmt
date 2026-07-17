---
title: "Household Visual Inventory — North Star: Catalogue + Overlays"
status: living-reference
created: 2026-07-16
dimension: household-visual-inventory
register: product-direction note. Governs WHY builds happen; the build
  order note governs WHEN; the plan governs HOW. No build authorized here.
provenance: operator + Fable-5 design sessions 2026-07-15..16
  (conversation tape, next archive export).
related:
  - household_visual_inventory_desktop_mvp_plan_20260715.md
  - household_inventory_build_order_20260716.md
  - capture_cascade_spec_20260716.md
---

# North Star — a house that knows itself

## The pattern: catalogue + one overlay each

Every application of this system is the SAME shape: the catalogue
(what exists, where, in what state — the expensive durable asset) joined
against one external structure (recipes, organization principles,
calendars). Overlays are cheap; the catalogue is the product. Pipeline
work therefore always outranks any single overlay.

## Ranked overlays

1. COOKING (first, highest query-frequency): pantry inventory x recipe
   requirements = "what can I make tonight." Learning loop: consumption
   events accumulate preference data → grocery suggestions ("add 3
   items, unlock 12 dishes near your favorites"). Note: food is the
   hardest content class (consumable lots, quantity, expiry, opened
   state) — KR-007 gave it its own entity role for this reason.
2. INSURANCE/DISASTER DOCUMENTATION (sleeper, highest per-use value):
   the timestamped photo-evidenced inventory IS a claim file, free as a
   byproduct. Consequence: retention policy keeps originals — they are
   evidence twice over.
3. LOAN TRACKING: `loaned` status exists; "who has my drill" is recall
   with a person attached.
4. CONSUMABLES REPLENISHMENT (beyond food): batteries/filters/supplies
   at reorder thresholds; same overlay as groceries.
5. EXPIRY SWEEPS: derived view flagging date-passed lots (pantry,
   medicine cabinet).
6. SEASONAL SWAP-LISTS, MOVE/RENOVATION PLANNING, DECLUTTERING
   ("unobserved 12 months") — all fall out of event history.
7. TOOL-CHEST / PLACEMENT OPTIMIZATION: booked; KR-007's geometry
   section is its spec. Lower value-per-query; do not lead with it.

## Explicit non-goals (edges of the picture)

- Security/surveillance overlays: OUT (KR-007 rule stands).
- Care decisions of any kind: OUT (the dog rule generalizes).
- Valuation/price tracking: DEFERRED — per-item online lookups are a
  privacy surface and a rabbit hole; wait for a real need.

## Schema pressures the north star creates (only three)

1. Consumable fields (quantity, unit, opened, expiry) exercised EARLY
   because cooking is first.
2. Retention inherits the insurance rationale: originals are kept.
3. Consumption events (`used`, `depleted`) join the event vocabulary at
   the pantry pilot.
