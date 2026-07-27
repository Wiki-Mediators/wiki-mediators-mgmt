---
title: Pantry Needs to Local Flyer Join
status: built
created: 2026-07-27
purpose: Record the deterministic Pantry Picker needs-to-flyer candidate join,
  its operator-acceptance gate, and the first live N2M5E5 result.
source_artifact: tools/household_inventory/pantry_picker/pantry_flyer_join.py
session_ref: 019f8ca7-857b-77a3-bf42-3217bff193b2
related:
  - flipp_kw_fetch_recon_20260727.md
  - ../household-visual-inventory/pantry_picker_consumables_ledger_20260726.md
  - ../../tools/household_inventory/TOOL_CONTRACTS.md
  - ../../tools/household_inventory/pantry_picker/README.md
---

# Pantry Needs to Local Flyer Join

## Built flow

`pantry projection -> Low / One portion left / None needs -> postal Flipp snapshot -> deterministic matching -> pending candidate or review queue -> explicit operator acceptance -> separate shopping-list ledger`

The join reads the append-only pantry ledger and writes only beneath
`C:\VMShare\local-deals`. Rows in the `on-hand` state are excluded. Generic
ingredients use family matching; branded products use brand-locked
specific-product matching. Thresholds, preferred stores, terms, and exclusions
are config-owned in `tools/local_deals/local_deals.config.json`.

The Flipp adapter retains the raw flyer list, grocery-flyer detail responses,
per-need search responses, normalized offers, pending candidates, ambiguity
queue, unmatched needs, and a run manifest. Ranking requires a positive cash
price and exactly one parseable package size. Points promotions, combo
advertisements, missing or multiple sizes, and configured identity exclusions
cannot become confident candidates.

## Acceptance boundary

Flyer candidates never mutate pantry counts. The page exposes a separate
operator action on a pending confident candidate. Only that explicit action
appends a provenance-rich `candidate-accepted` event to:

`C:\VMShare\local-deals\ledger\shopping_list_events.jsonl`

There is no automatic acceptance path, and accepting a shopping proposal is
not a pantry replenishment event.

The boundary has three loud stop conditions:

1. any pantry-ledger hash change during the join or acceptance;
2. any ambiguous offer presented as confident;
3. any offer with missing price or ambiguous/missing size ranked as
   comparable.

## First live snapshot

As of 2026-07-27, run
`LD-20260727T210437Z-aae5e2cd` derived one need: Maple syrup in `low` state.
It produced one pending candidate:

- Your Independent Grocer;
- PC Organics maple syrup, 375 mL;
- $12.00;
- valid 2026-07-23T04:00:00Z through 2026-07-30T03:59:59Z;
- unit price $0.032/mL.

The source is
`C:\VMShare\local-deals\runs\2026-07-27\LD-20260727T210437Z-aae5e2cd\run_manifest.json`.
The pantry ledger SHA-256 before and after was
`e66bd49b292f51928ebf8f32af5dd5ea04ed18f00a4057e3bb62356bc6f1cad9`.
Nothing was accepted.

Three alternatives were parked for review even though a confident candidate
existed: Sobeys Panache at $9.99 with package size missing, a No Frills
points-only offer, and a Sobeys Scene+ points-only offer. The cheaper-looking
Sobeys cash price was not ranked because its missing size makes unit-price
comparison unsafe.

## Verification

- 64 household tests passed, including focused contract, pantry-ledger, and
  flyer-join coverage.
- The four-way state seal proved `on-hand` excluded and `low`,
  `last-meal`, and `out` included in urgency order.
- Missing sizes, combo ads, points promotions, and sweet-potato exclusions
  were parked or excluded.
- The served page returned HTTP 200 and contained the Local Flyers panel. The
  state endpoint loaded the initial live run successfully; the final live
  rerun retained one candidate and three review rows.
- The live command emitted a six-line summary and preserved the pantry hash.

## Operating doctrine

This remains a low-frequency, operator-triggered dumb tool. Flipp's postal JSON
surface is provisional and not an officially documented consumer API; raw
evidence and schema-drift refusals are therefore part of the contract. An
agent is reserved for the ambiguity queue, not the weekly deterministic fetch.

## Calendar and history direction

Pantry Picker now projects retained candidate and review offers onto a
horizontal 14-day window: six local dates before today, today, and seven dates
after today. Bars use the source offer's `valid_from` and `valid_to`; missing
dates are not inferred.

The later history view should extend this same timeline backward across dated
run manifests and raw snapshots, with horizontal period navigation and a
current/history switch. History begins at the first retained collection and
must never backfill prices or flyer periods that were not observed.
