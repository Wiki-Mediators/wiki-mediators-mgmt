---
title: "Local Deals & Price Research — Dimension Seed"
status: raw-intake
created: 2026-07-23
dimension: local-deals
register: hobby/household lane, bank-and-log weight. Research-input
  claims cite sources; price data is dated-snapshot evidence, never
  timeless fact. No build authorized by this seed.
provenance: operator + Fable-5 design session 2026-07-23 (conversation
  tape, next archive export).
related:
  - ../household-visual-inventory/household_inventory_north_star_20260716.md
---

# Local Deals & Price Research

## Purpose and the north-star connection

Weekly price intelligence for groceries (first) and secondhand goods
(later) within the operator's pickup range: Kitchener-Waterloo area,
pickup-only, no long travel. THIS DIMENSION FEEDS THE HOUSEHOLD NORTH
STAR: pantry ledger (what we have) x flyer prices (what's cheap this
week) x recipes = the cooking overlay's shopping-list optimizer. Price
data is the input the grocery-suggestion loop was waiting for.

## Sources, honestly classified

- FLIPP (flipp.com — absorbed Reebee; one target, not two): public
  weekly retail flyers, structured, searchable by postal area. BENIGN
  source class — public advertising data, weekly cadence. Primary.
- FACEBOOK MARKETPLACE: DEFERRED, own decision when its day comes —
  login-walled, aggressive anti-automation, ToS friction. Different
  risk class; do not back into it.
- Store sites directly (later, per-store, only if Flipp gaps).

## Architecture: agent-builds-tool, tool-runs-weekly (token doctrine)

NO agent browses on a schedule. The pattern, inherited from the
household lane's token economy:
1. INVESTIGATION (once, agent work): a browsing-capable agent explores
   how Flipp search/flyers work for the KW area and specs the fetch.
2. DUMB FETCHER (the build): deterministic script — grocery watch-list
   in via config, dated price-snapshot out (JSONL/CSV: item, store,
   price, unit, sale dates, source, fetched-at). Compute-and-flag:
   flags price drops vs prior snapshots; never decides purchases.
3. WEEKLY RUN: operator-triggered or session-start, matching flyer
   cycles. Agent reads the <=6-line summary. Zero inference in the
   loop.
4. Snapshots accumulate as an append-only price history — which later
   yields "is this actually a good price" (the real question) from OUR
   OWN data, not vendor claims.

## Data placement (mirrors household pattern)

- Notes/specs/configs: this dimension, in-vault, logger-captured.
- Price snapshots: local data root C:\VMShare\local-deals\ (outside
  vault tree — small text but unbounded weekly growth; same
  outside-vault rule as household artifacts). Watch-list config
  in-vault (it's policy, not machine fact).

## Smallest pilot (pre-committed shape)

One watch-list of ~10 staples the operator actually buys; one manual
agent-assisted Flipp pass for KW; one snapshot banked; one summary
line. Value test: does the snapshot answer "where is item X cheapest
this week within pickup range?" If yes, the fetcher build earns its
trigger. If Flipp resists deterministic fetching, the fallback is
agent-assisted weekly runs — costed honestly against their token bill
before adoption.

## Non-goals (edges)

- No purchase automation, ever a proposal-only system.
- No account-walled sources without their own reviewed decision.
- No per-item online lookups from the household ledger (the household
  privacy rule holds; the JOIN happens locally between local datasets).
