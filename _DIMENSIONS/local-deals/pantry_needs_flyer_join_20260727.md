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

## Low-rate flyer discovery direction

A single read-only postal index request for debug postal code `N2H2E9` on
2026-07-27 returned metadata for all 103 flyer cards visible in Flipp's page
and was 125,399 bytes. Therefore page-source crawling is unnecessary for flyer
discovery: fetch and cache the postal index once, then filter its metadata
locally.

`N2M5E5` remains the HOME production location. `N2H2E9` is only a nearby
Kitchener debug fixture; postal codes must not be rotated to evade source
caching or rate limits.

Normal Pantry joins now make one index request plus only the item-search
requests required by current needs, with a two-second minimum interval. They
do not sweep every grocery flyer detail. Bulk detail fetching is a loud
refusal.

Any later crawler probe requires its own approval and should:

1. reuse a fresh cached postal index when available;
2. select at most two small-cover flyers deterministically from index metadata;
3. wait at least two seconds between requests;
4. cap requests and response bytes before the run;
5. store raw responses and stop loudly on schema drift;
6. never use postal-code rotation as a traffic-avoidance technique.

## Ambiguous package-size review

Retained Flipp search rows may include `clipping_image_url` or
`clean_image_url` even when indexed text omits the package size. The adapter
now carries that URL into normalized offers, and Pantry Picker backfills it
from older retained raw searches when necessary. Parked offers display the
flyer clipping beside the deterministic refusal reason.

The operator remains the authority. A future optional Qwen2.5-VL pass may
propose visible package wording through the existing loopback-only LM Studio
route, but its output must stay in the ambiguity queue and cannot create a
ranked candidate or shopping-list event without explicit confirmation.

## All-Low cache preview

Pantry Picker includes a deliberately non-persistent coverage test that treats
every currently saved item as Low in memory. It uses retained HOME
postal-code searches only, performs zero network requests, writes under the
separate `C:\VMShare\local-deals\previews\` branch, and reports cache hits and
misses. Its candidate rows are `preview-only` and use a filename that the
shopping acceptance command refuses. The pantry hash is sealed before and
after the preview.

## Staples always-watch category

Normal flyer joins include an operator-adjustable **Staples** watch
independently of inventory state. The config supplies initial defaults for
maple syrup, milk, potatoes, spaghetti, and peanut butter. Eye toggles in the
catalogue, inline editor, and On site summary all edit the same recoverable
draft. **Save to ledger** appends a separate `watch-set` event; it does not
recount the product. An explicit false override disables a config default.

A watched product that is already an urgent pantry need is merged by stable
ingredient identity, retains its real urgency, and is searched only once.
Otherwise it enters the lookup as `stock_state: watch` with
`watch_category: Staples`. Watches remain active even when the item is not
currently counted as physically on site.

This category changes search coverage, not inventory truth. Its offers remain
pending proposals under the same matching, ambiguity, and explicit-acceptance
boundaries as ordinary Low/One portion left/None needs.
