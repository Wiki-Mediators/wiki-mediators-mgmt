# Pantry Picker

Status: local consumables ledger with read-only flyer and recipe overlays.

The Pantry Picker is part of the household ledger family, but it has its own
append-only event vocabulary. Pantry counts are not photo observations.

## Run

Double-click `Open Pantry Picker.cmd`, or run:

```powershell
.\tools\household_inventory\pantry_picker\start_pantry_picker.ps1
```

The launcher checks the API contract before reusing a server already listening
on port 8770. If an older local-only Pantry Picker owns the port, the launcher
reconfirms the Pantry health identity, resolves the exact TCP-listener PID,
requires a Python process, stops that verified stale server, and starts the
current bridge. It refuses automatic shutdown when the listener is unrelated,
cannot be uniquely identified, changes during verification, or is an active
phone/LAN-sharing server.

The bridge binds only to `127.0.0.1`. Each item, quantity, stock-state, watch,
custom-item, and radius edit immediately refreshes a recoverable browser draft.
On restart, that draft is restored only when its base ledger event count still
matches the confirmed ledger. Draft persistence is not ledger persistence:
there is deliberately no timer that posts changes after 10 seconds or any
other delay. Only an explicit **Save to ledger** appends operator-confirmed
events to:

`<artifact_root>\ledger\pantry_events.jsonl`

The current pantry is always projected from that append-only file.

A future inactivity reminder may highlight the Save button or show an unsaved
countdown, but it must not call the ledger endpoint. This preserves forgotten
work without converting accidental clicks into confirmed append-only history.

## Pantry Cookbook

The top-bar **Cookbook** link opens `/cookbook.html` through the same local
Pantry service. It joins the confirmed `HOME` pantry projection against a
local recipe index and offers:

- food-aware search across recipe titles and indexed food layers. After two
  characters, a local autocomplete offers
  spelling-tolerant food terms (for example, `Califlower` suggests
  `Cauliflower`) and representative recipe titles; no web request or model
  call is made. Choosing a recipe-category suggestion activates the visible
  category chip instead of treating the category name as ordinary title text;
- a searchable category-layers panel: combine categories, remove them as
  chips, return to all categories, or use **Only** for a quick single-category
  view;
- **No listed gaps** through **Missing at most 5** coverage filters;
- a fast **10 meal ideas** lane on first open: it samples only configured
  meal categories, excludes desserts, preserves, drinks, sauces, quick salads,
  and other non-meal classes, then shows zero-missing recipes before using
  one-missing recipes as backfill;
- progressive 60-recipe pages with an explicit **Load more** control instead
  of a hidden 100-result ceiling;
- an **All recipe sources** filter and a visible source label on every card;
- green available, amber Low/One portion left, red missing, and grey
  not-yet-mapped ingredient lines;
- ingredients and step-by-step directions inside each recipe card;
- deterministic ranking with no model call during ordinary browsing.

The first supported source is Kaggle's **Recipes Dataset: 64k Dishes**. Its
listing identifies the dataset as CC0 and documents the CSV/JSON fields for
title, category, subcategory, ingredients, directions, and counts. The local
copy is retained outside the vault under:

`C:\VMShare\household-inventory\recipes\`

The supplied archive is named `kaggle_recipes_64k_dishes_cc0.zip`; its two
files are extracted under `kaggle_recipes_64k_dishes_cc0\`. The deterministic
SQLite index is `recipe_index.sqlite`.

The source CSV contains 62,126 rows. Import collapses exact
title+ingredients+directions duplicates while preserving every distinct
category assignment, producing 25,021 unique recipes across 267 categories in
the 2026-07-28 index.

The second source is Kaggle's **Food.com - Recipes and Reviews**, with only
`recipes.parquet` retained; reviews and duplicate CSV forms were deliberately
not downloaded. Its local files are:

- `foodcom_recipes_522517_cc0_parquet.zip` — 178,227,338 bytes, SHA256
  `4EDBAFDAAA82BB086FC011EC62EDF6C767EF7C1BACA98C2C3639C0AA609C7BC4`;
- `foodcom_recipes_522517_cc0\recipes.parquet` — 178,723,234 bytes.

The combined index contains 545,317 recipes: 25,021 from 64K Dishes and
520,296 usable Food.com rows. Sources remain separate and selectable. Food.com
quantity/name arrays differ in 405,336 imported records; for those rows the
importer retains ingredient names, omits unsafe quantity pairing, and marks the
card **Source list needs review**. No cross-source recipe is silently repaired
or overwritten.

The retained Food.com Parquet file also contains `AggregatedRating` and
`ReviewCount`; the Cookbook imports and displays both without requiring the
separate review-text archive. Ranking uses a ten-review, 4.5-star prior so a
single five-star vote does not outrank a strongly reviewed recipe.

Near-identical Food.com rows are grouped conservatively by normalized source,
title, and ingredient-name set. The config-owned equivalence map currently
treats sea, fine-sea, kosher, and table salt as the `salt` family for this
grouping only. Pantry matching and the original ingredient wording are not
rewritten. The strongest review-supported version is shown, and up to eight
alternatives remain available under **similar versions grouped here**.

All 314 Food.com `Keywords` values are indexed through
`recipe_facet_config.json` into nine filter layers: Cuisine, Dietary,
Difficulty & cost, Household & non-food, Ingredient or dish, Meal or course,
Method, Occasion, and Time. Different layers combine with AND; multiple values
inside one layer combine with OR. The original keyword wording is retained.
The 64K source has no equivalent keyword field, so the importer does not invent
these facets for it.

The 64K source remains selectable pending a measured overlap audit. A future
downgrade should compare its unique recipes, genuine subcategories, ingredient
quality, and instructions against Food.com rather than removing it merely
because Food.com has richer ratings and facets.

Rebuild the combined index with:

```powershell
C:\VMShare\household-inventory\venv\Scripts\python.exe `
  .\tools\household_inventory\pantry_picker\recipe_cookbook.py `
  --profile .\tools\household_inventory\local_profile.json import --summary
```

The cookbook is read-only. It cannot mutate pantry counts, accept flyer deals,
or add recipe ingredients to the shopping list. Quantity sufficiency is not
yet calculated, and unrecognized ingredient wording remains visibly
unrecognized rather than being guessed. Exact duplicate removal and
catalogue-owned phrase matching happen once during import so browsing remains
a low-cost local operation.

The Cookbook first shows ten quick meal ideas. **Find recipes** switches to the
full filtered catalogue. The **Recipes per page** control offers 20, 40, 60,
100, 150, and 250 for full searches; the browser remembers that display
preference while the recipe and pantry data remain server-owned. Quick-meal
category inclusion, exclusions, minimum recipe substance, and candidate-pool
size are owned by `recipe_facet_config.json`. The Pantry server prepares the
quick-meal candidate pool on a background thread at startup; Cookbook still
reads the current pantry projection when opened, so warming does not stale or
rewrite inventory.

Food.com rows omit measurement units and frequently have quantity/name arrays
of different lengths. A Food.com card therefore offers **Retrieve full
ingredients**. This is an explicit, on-demand server action:

1. the local Pantry server requests that recipe's public Food.com page;
2. it reads the page's Schema.org `recipeIngredient` lines;
3. it requires the title to match and every local ingredient name to appear in
   the recovered sequence, in order;
4. only a verified result is written under
   `C:\VMShare\household-inventory\recipes\foodcom_recovered\<record-id>.json`.

The card updates in place and no Food.com tab opens. Later views use the local
cache and work offline. Failed retrieval or verification leaves the original
ingredient list and warning intact. The cache stores the extracted raw
ingredient lines, source URL, retrieval time, verification counts, and source
page hash; it does not rewrite `recipe_index.sqlite`, append pantry events, or
alter a shopping list. Newly seen ingredient wording is rematched against the
existing Pantry catalogue but does not automatically create inventory. A
future catalogue-enrichment queue should present those unmatched lines for
operator acceptance before adding selectable ingredient definitions.

Food.com cards also provide **View original source beside Cookbook**. It opens
the public source page in a closable split-screen inspector while the Cookbook
remains visible. That browser view does not send pantry or ledger data to
Food.com. **Open in new tab** is an explicit fallback if the source site cannot
render inside the inspector.

### Favourites integration direction

Favourites should be uniform across Cookbook, Pantry Picker, and flyer views,
but they must remain distinct from inventory and accepted shopping needs:

1. store favourite/unfavourite events on the local server using the stable
   recipe source plus source record ID, not browser-only `localStorage`;
2. show the same star state on recipe cards, source inspection, and future
   meal-planning views;
3. favouriting records interest only and never changes pantry counts or adds a
   shopping item;
4. an explicit **Plan this meal** action may derive missing ingredients from a
   favourite recipe and send them to the existing flyer join as proposals;
5. flyer proposals still require operator acceptance, and future receipt or
   shopping-list image recognition remains a separate visual-confirmation
   workflow before any pantry event is appended.

Recovered full ingredient lines and quantities may improve a planned meal's
proposal, but unknown ingredients remain flagged until the catalogue-enrichment
queue is operator-reviewed.

The companion Kaggle notebook **Crafting Readable Dish Instructions** was
reviewed as a display reference. Its useful presentation idea—numbered cooking
steps—is used by the Cookbook, but its string-replacement parsing is not:
Pantry Cookbook decodes the source ingredient and direction arrays as JSON so
adjacent directions cannot be silently joined. Raw wording remains in the
index; readability is a display concern, not a recipe rewrite.

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
from the page without changing the source catalogue. A custom addition appears
immediately as both a selected editor and a reusable **custom** tile inside its
chosen category. Saved custom items are restored as tiles on later launches;
unsaved custom-tile identity remains with the recoverable browser draft. Add,
import, save, and refusal messages also appear briefly as an on-screen
confirmation instead of being visible only below the long On-site list.

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
- the eye control is a separate draftable **Watch flyer prices** setting shown
  on catalogue tiles, inline editors, and On site summary rows; changing it in
  any view updates every other view immediately;
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

The config supplies the initial **Staples** watch category: maple syrup, milk,
potatoes, spaghetti, and peanut butter. The operator can turn the eye on for
any other catalogue item or turn an initial default off. Watch changes are
append-only `watch-set` events, independent from counts, and are confirmed only
by **Save to ledger**. If a watched staple is already Low, One portion left, or
None, the join merges the watch label into that one need instead of searching
it twice. Watching creates price proposals only; it does not change pantry
stock state or automatically add anything to the shopping list.

Every run lands outside the vault under `C:\VMShare\local-deals\runs\`:

- raw postal-scoped Flipp responses;
- the derived `needs.json`;
- normalized `offers.jsonl`;
- pending `candidate_shopping_list.jsonl`;
- `ambiguity_review.jsonl`;
- an immutable run manifest with the pantry-ledger hash before and after.

The optional **Flyer calendar** disclosure projects current retained offers
onto a horizontal 14-day calendar: the prior six local dates, today, and the
next seven dates. It is collapsed by default because a large offer set is more
useful when grouped by pantry item. Candidate and review bars show flyer
validity spans; the calendar does not manufacture dates or reconstruct history
that was never collected.

Each item card carries its useful timing directly. The selected candidate shows
its store, price, and **Ends Mon D** label. Other retained store listings for
that item are grouped underneath for review. If a retained listing begins
after the current local day, the same deterministic formatter shows
**Starts Mon D · ends Mon D**, so preview ads can be represented without a
separate calendar mode. Full ISO timestamps remain in the snapshot artifacts;
the page only formats them for display.

The sticky header carries a compact flyer-status indicator. It is stationary
while Pantry Picker is reading a saved snapshot and shows when that snapshot
was checked plus the next retained offer expiry. It animates only during an
operator-requested live check or cache-only preview; it does not imply a
background crawler. Snapshots older than 24 hours, or snapshots whose retained
offers have all expired, are marked as potentially outdated.

The compact flyer view shows up to three alternate stores beneath a confident
item, up to four offers for a review-only item, and eight rows if the optional
calendar is opened. **Show all offers** expands every candidate and parked
offer already present in that saved snapshot; it performs no network request.
**Compact view** restores the smaller presentation.

An offer is never ranked without a positive cash price and one unambiguous
package size. Points promotions, combo ads, missing/multiple sizes, and
configured identity hazards are parked for review rather than treated as
confident. When Flipp supplies a clipping image, the parked review row shows
that retained source image so the operator can inspect package wording.
Clicking either its thumbnail, **View larger clipping**, or an image-backed
alternate-store line opens an in-page flyer viewer. When retained context is
available, the viewer first loads the original store-flyer overview, projects
the selected clipping at its retained coordinate box, zooms toward that
selection, and then resolves into the clean clipping. **Overview** and
**Focused clipping** let the operator move between both states manually.
When the same pantry item has more than one retained clipping, the viewer
adds previous/next arrows and a bottom row of selectable dots. The darkest
dot marks the current clipping, the counter shows its position, and the left
and right arrow keys provide the same navigation. Moving within that
item-level carousel opens the next clipping directly rather than replaying
the overview animation. When retained flyer-page context is available, the
original full flyer page for the clipping that opened the viewer is appended
as the final carousel image, so two offer clippings appear as three selectable
images rather than losing the source page after the animation.
This on-demand effect loads only the clicked flyer overview; it is not a bulk
flyer-detail fetch, a permanent local clone, or evidence that unsearched flyer
items were collected.

Review-only offers use responsive flyer tiles rather than narrow text rows.
The clipping keeps its natural aspect ratio at a larger size, with store,
price, timing, and the review reason directly beneath it. The layout adapts
its column count to the available width and retains the same compact versus
**Show all offers** boundary.

The viewer does not open a new browser tab or initiate a download; it closes
with its × button, Escape, or a backdrop click. An optional local Qwen2.5-VL
pass may later propose a size from that clipping, but model output remains
untrusted review evidence: it cannot promote, rank, or accept an offer without
explicit operator confirmation.

The **Check current flyers** button only creates pending proposals. A deal
enters the separate append-only shopping-list ledger only after the operator
presses that candidate's **Accept** button and confirms the prompt. Acceptance
does not replenish, decrement, or otherwise change a pantry count. There is no
automatic acceptance path.

**Preview all as Low** is a cache-only coverage test. It treats every saved
pantry row as a hypothetical Low need in memory, reuses only retained HOME
postal-code item searches, reports cache misses explicitly, and makes zero
network requests. Preview candidates cannot be accepted, the preview is stored
separately under `C:\VMShare\local-deals\previews\`, and the pantry-ledger hash
must remain unchanged.

Flipp is an external discovery source, not a pantry authority. Its current
postal JSON surface is provisional rather than an officially documented
consumer API, so the adapter runs at low operator-triggered frequency, retains
raw evidence, and refuses loudly on schema drift.

## Archive

`archive/pantry_picker_v0_20260726.html` is an exact SHA-256-preserved copy of
the downloaded prototype. It is historical input, not the live page.
