---
title: Pantry Picker Current State and Recipe Overlay
status: built
created: 2026-07-28
updated: 2026-07-29
purpose: Freeze the operator-visible Pantry Picker state before recording the
  first deterministic pantry-to-recipe cookbook overlay.
source_artifact: tools/household_inventory/pantry_picker/
related:
  - pantry_picker_consumables_ledger_20260726.md
  - household_inventory_build_order_20260716.md
  - household_inventory_north_star_20260716.md
  - ../local-deals/pantry_needs_flyer_join_20260727.md
  - ../../tools/household_inventory/pantry_picker/README.md
---

# Pantry Picker current state — 2026-07-28

This note freezes the current product boundary before the cooking overlay
becomes the active development front. The live authority remains the code and
operational contract; this note records the transition.

## Frozen Pantry Picker surface

As of 2026-07-28, Pantry Picker provides:

- a 421-item full catalogue and append-only confirmed `HOME` pantry ledger;
- synchronized stock states `Enough`, `Low`, `One portion left`, and `None`;
- category-local editing, a compact On site summary, flyer-watch eye toggles,
  JSON backup/import, and viewport-preserving rerenders;
- operator-triggered local-flyer discovery with read-only needs derivation,
  explicit shopping-list acceptance, a cache-only all-Low preview, retained
  source provenance, and no pantry-count mutation;
- responsive ambiguous-offer tiles and an in-page flyer viewer that moves from
  original flyer overview to focused clipping;
- item-level clipping navigation with arrows, keyboard keys, active-position
  dots, and the original retained flyer page appended as the final slide;
- localhost and token-protected home-LAN launchers plus the installed desktop
  shortcut flow.

Source anchors: `tools/household_inventory/pantry_picker/README.md` and
`tools/household_inventory/TOOL_CONTRACTS.md`, as of 2026-07-29.

## Draft persistence decision — 2026-07-29

Pantry Picker already saves every working edit to a recoverable browser-local
draft. A recovered draft is not confirmed pantry state and does not append a
`pantry-ledger-v1` event. The operator considered a ten-second automatic ledger
save, but the current decision preserves the explicit confirmation boundary:
only **Save to ledger** may call `POST /api/events`.

No elapsed-time, inactivity, page-close, or background trigger may promote the
draft. If an unsaved-work reminder is added later, it may display a countdown,
badge, or Save-button emphasis only. It must remain non-writing. The draft is
restored only when its recorded base event count still matches the confirmed
ledger, preventing a stale browser draft from silently overriding newer
confirmed history.

## Cooking overlay decision

The first cooking overlay is a deterministic join:

`confirmed pantry projection × local recipe requirements → candidate cookbook`

The operator-supplied source is Kaggle
`prashantsingh001/recipes-dataset-64k-dishes`. Kaggle's dataset page described
the release as CC0 with structured CSV and JSON forms containing title,
category, subcategory, ingredients, directions, and counts when checked on
2026-07-28.

The downloaded `archive.zip` hash was
`C37DB342407C5525275304F5197880386414F3DA892E567B7C32731DEBEC8098`.
It is retained outside the vault as:

`C:\VMShare\household-inventory\recipes\kaggle_recipes_64k_dishes_cc0.zip`

The local data-root check recorded `C:\VMShare\household-inventory\recipes\`
under `C:\VMShare`, outside configured OneDrive/cloud-sync roots. The archive
extract contains:

- `1_Recipe_csv.csv` — 81,142,626 bytes;
- `2_Recipe_json.json` — 85,244,841 bytes.

The CSV has 62,126 rows, not exactly 64,000. Exact
title+ingredients+directions deduplication yields 25,021 unique recipes while
retaining distinct category memberships across 267 categories. The generated
index records 174,520 recognized catalogue requirements and 52,314 ingredient
lines that remain visibly unmapped.

## Food.com addition

The operator downloaded only Food.com's structured recipe Parquet file, not
the reviews or duplicate CSV forms. It is retained outside the vault as:

- `foodcom_recipes_522517_cc0_parquet.zip` — 178,227,338 bytes, SHA256
  `4EDBAFDAAA82BB086FC011EC62EDF6C767EF7C1BACA98C2C3639C0AA609C7BC4`;
- `foodcom_recipes_522517_cc0\recipes.parquet` — 178,723,234 bytes.

The source has 522,517 rows; 520,296 have the title, ingredients, and
instructions required for the local index. The combined index therefore holds
545,317 recipes across two visibly separate sources. Food.com record IDs are
preserved and cross-source records are not silently merged.

Food.com's quantity and ingredient-name arrays differ in 405,336 imported
records. The importer refuses positional guessing: those records retain the
ingredient names without quantities and carry a visible source-review warning.
This addition expands the Cookbook; it does not automatically repair a damaged
64K Dishes record.

The operator also supplied Kaggle notebook
`vedikagupta0/crafting-readable-dish-instructions` (downloaded notebook SHA256
`4645DEE0B33CBF76661F16C8280DB0EA98E1DC9F55D4DD80A28C533B1A6822DD`).
Its numbered-step presentation is useful, but its parser removes JSON syntax
with string replacements and then sentence-splits the flattened directions.
The local importer deliberately keeps its stronger JSON-array parsing so
distinct source steps and exact wording remain intact. Any later cleanup must
be display-only and retain the original text.

## Built cookbook surface

- `recipe_cookbook.py` imports the extracted CSV or original ZIP, validates the
  exact source columns, builds a replaceable SQLite index, deduplicates exact
  recipe content, and matches ingredients against the Pantry catalogue.
- `/api/cookbook/state` projects that index against the confirmed pantry.
- `/cookbook.html` supplies title search, searchable multi-category layers,
  selected-category chips, single-category **Only** shortcuts, progressive
  loading, source filtering and labels, missing-item tolerance, availability
  colours, ingredients, and directions.
- the Pantry Picker top bar links to the Cookbook through the same localhost or
  token-protected LAN service.

## Hard boundaries

- Cookbook reads never write pantry events or shopping-list events.
- Browser-local pantry drafts recover automatically, but never become
  confirmed events on a timer; **Save to ledger** remains the sole pantry
  confirmation action.
- `None` and absent catalogue items count as missing.
- `Low` and `One portion left` remain available but are shown as limited.
- Unmapped ingredient wording is visible and counts against the
  no-listed-gaps measure.
- Quantity sufficiency, substitutions, nutrition claims, and dietary
  classifications are not inferred.
- Matching is deterministic and paid once at import; routine browsing is
  zero-inference.

## Next work

1. Review the first real ready/near-ready results for catalogue-matching
   collisions and move confirmed aliases/exclusions into config.
2. Add quantity normalization only after the ingredient-identity layer is
   operator-checked.
3. Let an operator explicitly turn missing recipe ingredients into shopping
   proposals; preserve the existing acceptance boundary.
4. Add favourites and meal-history events only after the read-only cookbook is
   trustworthy.
