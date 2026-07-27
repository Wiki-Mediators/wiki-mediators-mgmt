# Pantry Picker

Status: local one-page consumables ledger interface.

The Pantry Picker is part of the household ledger family, but it has its own
append-only event vocabulary. Pantry counts are not photo observations.

## Run

Double-click `Open Pantry Picker.cmd`, or run:

```powershell
.\tools\household_inventory\pantry_picker\start_pantry_picker.ps1
```

The launcher checks the API contract before reusing a server already listening
on port 8770. It refuses an outdated Pantry process with a visible instruction
instead of opening a newer page against an incompatible bridge.

The bridge binds only to `127.0.0.1`. The page keeps unfinished edits in
browser storage as a draft. Only an explicit **Save to ledger** appends
operator-confirmed events to:

`<artifact_root>\ledger\pantry_events.jsonl`

The current pantry is always projected from that append-only file.

Catalogue and ledger loading are independent from the optional flyer endpoint.
If an older bridge lacks flyer support, the confirmed pantry remains available
and only the flyer panel asks for a restart.

## One-time desktop shortcut

Double-click `Install Desktop Shortcut.cmd` once. It creates or refreshes
`Pantry Picker.lnk` on the current Windows user's Desktop. The shortcut has a
built-in Windows PowerShell icon and launches the existing connected
`Open Pantry Picker.cmd` workflow; it does not create a second server or copy
the Pantry files.

The installer is idempotent and does not require Administrator privileges.
For scripted installation or removal:

```powershell
.\tools\household_inventory\pantry_picker\install_desktop_shortcut.ps1
.\tools\household_inventory\pantry_picker\install_desktop_shortcut.ps1 -Remove
```

Keep the launcher window open while using Pantry Picker. Closing that window
stops a server instance started by the shortcut.

## Phone access on the trusted home network

First double-click `Install Phone Access.cmd` once and accept the Windows
Administrator prompt. This installs the narrow firewall rule.

Then double-click `Open Pantry Picker on Home Network.cmd`.

The launcher:

- binds the server to the home LAN for that session only;
- generates a new random access token;
- places the token in the URL fragment, which is not sent in ordinary HTTP
  requests or server logs;
- copies the phone link to the clipboard;
- requires the token on ledger reads and writes;
- stops sharing when its launcher window closes.

The firewall rule is restricted to the Python executable, TCP 8770, the
Windows **Private** profile, and `LocalSubnet`. Use this only on a trusted home
network. Do not add router port forwarding or expose the port to the internet.

## Catalogue identity

The catalogue distinguishes:

- generic ingredients;
- blends and mixes;
- branded products.

Brand is a separate field, so a branded ketchup does not replace generic
ketchup. The current seed contains 421 entries: 317 ingredients, 64
blends/mixes, and 40 branded products. Users can add another brand or blend
from the page without changing the source catalogue.

The 2026-07-26 food-family expansion adds distinct everyday and advanced rows
for lettuces, salad/cooking greens and green medleys; pasta shapes and Asian
noodle families; dairy milk varieties and plant-based milk beverages; and
frozen green/vegetable medleys. Generic `Lettuce`, `Spinach`, and `Milk` remain
for backward compatibility with existing selections.

## Location scope

The first site is `HOME`. An optional radius in metres records the intended
on-site boundary without storing coordinates. The page leaves radius blank by
default: blank or zero means the `HOME` site itself. Radius is an advanced
setting, not a requirement for ordinary pantry use. Future named sites use stable
`SITE-<NAME>` identifiers.

## Interface defaults

- the Full catalogue is the default view;
- all catalogue categories start collapsed; search, Expand all, a deliberate
  category click, or a summary-item navigation opens them;
- Expand all and Collapse all control the category list;
- import, export, reset, catalogue filtering, and radius live under
  **Tools & advanced**;
- the right-hand On site panel is reserved for selected items and the explicit
  ledger save.
- stock levels are visible one-tap controls on every selected item:
  **Enough**, **Low**, **One portion left**, and **None**;
- the On site panel summarizes the current count in all four stock levels.
- category panels contain the full editor for each selected item: amount, unit,
  stock level, and remove;
- item toggles, removals, and stock-level rerenders preserve the current
  viewport anchor instead of bouncing the operator to the top of the page;
- the On site summary exposes the same four stock levels as a compact selector;
  changes synchronize with the category editor and remain draft-only until
  Save to ledger;
- the On site list is a compact summary; selecting a summary row opens its
  category and moves to that item's inline editor;
- urgent items sort first everywhere: **None**, then **One portion left**, then
  **Low**, followed by **Enough**; categories containing urgent items also rise
  above all-Enough categories;
- every category includes a quick generic-ingredient entry field, while the
  top product form remains available for brands and blends.
- Data tools explain their effects in place: Export downloads a JSON backup,
  Import loads current or legacy JSON into the reviewable draft, and Discard
  unsaved edits returns to the last confirmed ledger save.

Pantry JSON exports carry both the durable `stock_state` value
(`on-hand`, `low`, `last-meal`, or `out`) and a human-readable
`stock_state_label`. Imports use the durable value and safely ignore the
display label.

The visible wording is independent from the stable ledger vocabulary:
`Enough → on-hand`, `Low → low`, `One portion left → last-meal`, and
`None → out`.

## One-time legacy import

The Import action recognizes the archived prototype's
`type: "pantry-selection"` JSON format. It maps old names and categories to
stable current catalogue IDs, translates `ok` to `on-hand`, `last` to
`last-meal`, and `to taste` to `to-taste`, while retaining unmatched rows as
custom ingredients. Legacy rows default to the `Ingredient` item kind because
the old format did not record blend or branded-product identity. The reader
also removes an optional Windows UTF-8 BOM before parsing older exports.

Legacy imports merge into the recoverable browser draft. They do not append
ledger events until the operator reviews the result and presses
**Save to ledger**.

Legacy conversion requires the connected page opened by
`Open Pantry Picker.cmd`; the direct `file:///.../pantry_picker.html` copy does
not have the catalogue or ledger service. The page reports this distinction
explicitly instead of attempting a partial import.

## Local-flyer candidate join

The page can now derive shopping needs from pantry rows marked **Low**,
**One portion left**, or **None**, then run an operator-triggered,
postal-scoped Flipp lookup. **Enough** rows are sealed out of needs derivation.

The deterministic adapter uses `N2M 5E5`, presents Food Basics, Sobeys, and
Real Canadian Superstore as preferred stores, and retains other local grocery
flyers when they produce a cheaper confident match. Matching rules and
exclusions live in `tools/local_deals/local_deals.config.json`; branded
products use brand-locked matching, while generic ingredients use
product-family matching.

Every run lands outside the vault under `C:\VMShare\local-deals\runs\`:

- raw postal-scoped Flipp responses;
- the derived `needs.json`;
- normalized `offers.jsonl`;
- pending `candidate_shopping_list.jsonl`;
- `ambiguity_review.jsonl`;
- an immutable run manifest with the pantry-ledger hash before and after.

The page projects current retained offers onto a horizontal 14-day calendar:
the prior six local dates, today, and the next seven dates. Candidate and
review bars show flyer validity spans; the calendar does not manufacture dates
or reconstruct history that was never collected.

An offer is never ranked without a positive cash price and one unambiguous
package size. Points promotions, combo ads, missing/multiple sizes, and
configured identity hazards are parked for review rather than treated as
confident.

The **Check current flyers** button only creates pending proposals. A deal
enters the separate append-only shopping-list ledger only after the operator
presses that candidate's **Accept** button and confirms the prompt. Acceptance
does not replenish, decrement, or otherwise change a pantry count. There is no
automatic acceptance path.

Flipp is an external discovery source, not a pantry authority. Its current
postal JSON surface is provisional rather than an officially documented
consumer API, so the adapter runs at low operator-triggered frequency, retains
raw evidence, and refuses loudly on schema drift.

## Archive

`archive/pantry_picker_v0_20260726.html` is an exact SHA-256-preserved copy of
the downloaded prototype. It is historical input, not the live page.
