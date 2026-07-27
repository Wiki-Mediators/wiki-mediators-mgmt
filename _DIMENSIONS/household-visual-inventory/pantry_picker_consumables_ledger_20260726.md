---
title: Pantry Picker Consumables Ledger
status: built
created: 2026-07-26
purpose: Record the separate pantry-count branch added to the local household
  ledger and its explicit on-site containment boundary.
source_artifact: tools/household_inventory/pantry_picker/
related:
  - household_inventory_build_order_20260716.md
  - household_inventory_north_star_20260716.md
  - ../../tools/household_inventory/pantry_picker/README.md
  - ../local-deals/flipp_kw_fetch_recon_20260727.md
---

# Pantry Picker Consumables Ledger

## Decision

Pantry belongs to the household ledger family, but pantry counts are not photo
observations. They use a separate append-only event stream and projection.

The first containment scope is `HOME`. An optional radius in metres describes
the intended on-site boundary without storing coordinates. The model can later
support named `SITE-<NAME>` boundaries.

## Built surface

- one local HTML page;
- localhost-only Python bridge;
- explicit Save confirmation boundary;
- browser storage for recoverable drafts only;
- append-only `pantry_events.jsonl` under the profile-owned artifact root;
- count, clear, and scope events;
- retry deduplication by client event ID;
- stable ingredient IDs rather than display-name deduplication;
- quantity, unit, and stock-state projection;
- Basic and Full catalogue filters;
- custom entries and JSON import/export;
- 421-item seed catalogue: 317 ingredients, 64 blends/mixes, and 40 branded
  products;
- optional brand and item-kind fields preserve generic, blended, and branded
  identities separately;
- food-family expansion for lettuces and cooking greens, greens medleys,
  pasta/noodle shapes, dairy and plant-based milk varieties, and frozen
  vegetable medleys;
- token-protected trusted-home-LAN launcher for phone access.
- idempotent one-time desktop-shortcut installer for the connected local
  launcher; it uses a built-in Windows icon and requires no Administrator
  privilege.
- launcher API-contract check prevents a newer page from silently reusing an
  outdated Pantry bridge; catalogue/ledger startup is isolated from optional
  flyer-endpoint failure.
- Full catalogue as the default view, with Expand all and Collapse all;
- compact `Tools & advanced` menu for Basic-only filtering, optional radius,
  import, export, and draft reset.
- restored visible stock-level controls and summary counts using operator
  wording `Enough`, `Low`, `One portion left`, and `None`, projected to the
  existing stable values `on-hand`, `low`, `last-meal`, and `out`.
- restored category-local editing for selected rows (amount, unit, stock level,
  remove) plus quick generic additions; the sticky On site panel is now a
  summary/navigation surface whose explicit item click opens and scrolls to the
  matching inline editor;
- stock urgency sorts `None`, `One portion left`, `Low`, then `Enough` in both
  inline and summary lists, and promotes categories containing urgent items.
- categories start collapsed, while item/state rerenders preserve their
  viewport anchor instead of returning the operator to the top;
- Data tools carry plain-language, action-specific descriptions;
- a horizontally scrollable 14-day flyer calendar shows retained candidate
  and review validity spans around the current date.
- one-time legacy-import adapter for the archived prototype's
  `pantry-selection` JSON exports; conversion lands in the unsaved draft rather
  than bypassing the explicit Save boundary; legacy rows default to Ingredient,
  and an optional Windows UTF-8 BOM is removed before JSON parsing.

The expanded seed catalogue is a foundation, not the requested eventual thousands-scale
catalogue.

## Archive

The downloaded prototype is retained byte-for-byte at:

`tools/household_inventory/pantry_picker/archive/pantry_picker_v0_20260726.html`

Its SHA-256 is
`4014EC4D3C8CD378B37A8CA566FE2C29DC849446B8B52C4CC15F4A0CE11D954A`.

## Validation

As of 2026-07-26:

- eight focused pantry-ledger tests pass;
- Python and page JavaScript syntax pass;
- all 421 catalogue IDs are unique;
- a synthetic local HTTP save projected two events, one item, and a 25-metre
  `HOME` radius;
- the real household profile passed a read-only server/page/state smoke with
  zero existing pantry events and no pantry ledger file created;
- tokenless LAN state access returns `403`, while an authorized branded-product
  event preserves brand and item-kind identity;
- the page is reachable through the machine's private `192.168.1.x` address;
- Windows Firewall rule `Pantry Picker (Private Home LAN)` is enabled only for
  the household Python executable, TCP 8770, the Private profile, and
  `LocalSubnet`.
- the newest legacy export `pantry_2026-07-26 (1).json` contains 90 items: 89
  match a current catalogue name/category or a unique current name, while the
  unmatched custom `Lemon juice` row remains custom.

## Open work

- substantial catalogue expansion and taxonomy review;
- opened and expiry fields;
- acquire, consume, discard, and transfer event vocabulary;
- a separate flyer-deal candidate layer: derive needs from Low/Last meal/Out,
  search local Flipp/reebee content by operator-supplied postal-code area,
  normalize price and package size, preserve source links and validity dates,
  then require operator acceptance into a shopping list;
- use only an authorized/documented external feed for automated flyer
  ingestion; do not let flyer candidates mutate confirmed pantry counts;
- operator visual review of the new page.

External-source anchor, checked 2026-07-26: Flipp's official Canadian surface
supports postal-code-localized flyers and item/brand/store search
(`https://flipp.com/?locale=en-ca`); its current corporate FAQ describes
reebee as a Canadian shopper-facing channel within Flipp
(`https://corp.flipp.com/faq/`).

## Local-deals reconnaissance update

The 2026-07-27 read-only investigation fixed the first location at postal code
`N2M 5E5`, with Food Basics, Sobeys, and Real Canadian Superstore preferred
while retaining other local grocery flyers. It found that a deterministic
weekly collector is technically feasible through Flipp's postal-scoped JSON
surfaces and is substantially cheaper than browser-by-item collection.

That interface is not an officially documented consumer API. The fetch design
therefore remains an explored specification, not an authorized production
integration: low-rate weekly snapshots, raw-response retention, schema-drift
checks, and browser review only for ambiguous or incomplete records. Historical
prices begin with the first collected snapshot and accumulate forward; no
earlier history is invented.

The full fetch boundary, family-versus-specific matching schema, current
five-item sample, and packaging hazards are recorded in
`../local-deals/flipp_kw_fetch_recon_20260727.md`.
