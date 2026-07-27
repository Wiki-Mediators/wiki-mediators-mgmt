---
title: Flipp KW Fetch Reconnaissance
status: explored
created: 2026-07-27
purpose: Record the read-only Flipp investigation for a future deterministic
  local-deals collector connected to Pantry Picker needs.
source: Flipp public Canadian web and postal-scoped JSON surfaces, observed
  2026-07-27 for N2M 5E5.
related:
  - local_deals_dimension_seed_20260723.md
  - ../household-visual-inventory/pantry_picker_consumables_ledger_20260726.md
  - ../../tools/household_inventory/pantry_picker/README.md
---

# Flipp KW Fetch Reconnaissance

## Disposition

Investigation complete; no collector was built.

The recommended shape is:

`fixed postal location -> dumb weekly fetch -> append-only raw snapshots -> local matcher -> small ambiguity review queue`

Use postal code `N2M 5E5` as the single location. Prefer Food Basics, Sobeys,
and Real Canadian Superstore in presentation, but retain other local grocery
flyers so the system can discover better prices and grow the Pantry Picker's
advanced catalogue.

Confirmed pantry counts and pantry event history remain local household data.
Flyer candidates are a separate proposal layer and must never mutate the pantry
ledger.

## Fetch finding

Flipp's official help says location is selected by postal code and search
accepts stores, brands, items, and coupons:

- https://help.flipp.com/hc/en-ca/articles/24402324222484-How-to-Use-Flipp-com-to-Find-Savings-and-Deals
- https://help.flipp.com/hc/en-ca/articles/24399868443668-How-to-Use-Search
- https://help.flipp.com/hc/en-ca/articles/24402819409172-How-to-Change-My-Location-on-Flipp-com

Read-only inspection on 2026-07-27 confirmed deterministic JSON responses at:

- `https://backflipp.wishabi.com/flipp/flyers?postal_code=N2M5E5&locale=en-ca`
- `https://backflipp.wishabi.com/flipp/flyers/{flyer_id}?postal_code=N2M5E5&locale=en-ca`
- `https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code=N2M5E5&q={query}`

A full sweep of the 29 grocery flyers visible for this location completed in
about 3.45 seconds during the pass. Browser inspection of the broad term
`milk` took roughly 115 seconds and returned 65 noisy matches. The deterministic
fetch is therefore the correct steady-state mechanism; a browsing agent is a
fallback for ambiguous records, missing sizes, points-only offers, combo ads,
or endpoint/schema failure.

No official consumer API documentation for these JSON surfaces was found.
Treat them as a provisional adapter: low rate, weekly cadence, cached/raw
responses, loud schema-drift checks, no authentication bypass, and a current
terms/permission review before unattended production use.

## Weekly collector specification

1. Fetch active flyers for `N2M5E5`.
2. Retain grocery-category flyers and their raw metadata.
3. Search only for current pantry needs; do not sweep every flyer detail.
4. Deduplicate observations by postal code, flyer-item ID, validity interval,
   and advertised price.
5. Run local deterministic matching against the watch-list configuration.
6. Auto-accept only high-confidence family or specific-product matches.
7. Put incomplete and ambiguous records into a small review queue.
8. Produce a short current-deals summary; do not decide purchases.

The append-only history begins with the first real collector run. Do not
backfill invented prices. Current view selects active observations; History
groups accumulated observations by flyer week; Discovered/Advanced surfaces
frequent unmatched raw products for optional catalogue expansion.

## Watch-list modes

```yaml
location:
  postal_code: N2M5E5
  label: Home

stores:
  preferred:
    - Food Basics
    - Sobeys
    - Real Canadian Superstore
  include_other_local: true

items:
  - id: spaghetti
    mode: product_family
    match_any:
      terms: [spaghetti, spaghettini]
      brands: ["*"]
      preferred_brands: [Catelli]
      exclude: [sauce, squash, prepared meal]
    variants:
      standard_wheat: preferred
      gluten_free: review
      quinoa: review

  - id: kraft_smooth_peanut_butter
    mode: specific_product
    brand: Kraft
    product_name: Smooth Peanut Butter
    accepted_sizes_g: [750, 1000]
    require: [brand, product_name, accepted_size]
```

Each observation retains raw evidence and interpretation separately:

```yaml
observed_at:
postal_code:
merchant:
flyer_id:
flyer_item_id:
name_raw:
brand_raw:
price_raw:
size_raw:
valid_from:
valid_to:
source_url:
match_status: matched | ambiguous | unrelated | discovered
watch_item_id:
match_confidence:
packaging_form:
normalized_quantity:
normalized_unit:
unit_price:
review_reason:
```

## Dated five-item sample

Observed 2026-07-27. Most cited flyer periods were 2026-07-23 through
2026-07-29 local time.

| Watch item | Example current flyer evidence | Interpretation |
|---|---|---|
| Maple syrup | Sobeys 100% pure 375 mL, $9.99; Zehrs and Your Independent Grocer PC Organics 375 mL, $12 | High-confidence product matches. No Frills PC 500 mL and Sobeys Compliments Organic were points-only offers without a usable cash flyer price. |
| Milk | Food Basics Natrel lactose-free/organic, apparently 2 L, $4.99; Sobeys organic 2 L, $6.99; No Frills Neilson TruTaste 4 L, $4.99; Longo's Beatrice 4 L, $6.49 | Broad `milk` search also returned formula, dog treats, coconut/condensed milk, ice milk, and non-food products. RCSS had no confidently matching ordinary dairy-milk flyer item in the pass. |
| Potatoes | No Frills white/russet 10 lb bag, $3.99; Sobeys potatoes, $7.49 with size absent; Longo's russet, $3.99; YIG baking potatoes, $2/lb; Walmart Little Potato Co., $2.98 | Do not compare bag, per-pound, count, tray, or unspecified packages without normalization evidence. Food Basics returned fries/chips rather than fresh potatoes. |
| Spaghetti family | Goodness Me Gogo Quinoa spaghetti 227 g, $4.24; Shoppers Catelli gluten-free pasta 340 g, $3.79; FreshCo Garofalo pasta 500 g, $2.99 | No confident standard dry-spaghetti match at the three preferred stores. Catelli/Garofalo are review matches when exact shape is absent; sauce is unrelated. |
| Peanut-butter family | RCSS Kraft 750 g/1 kg, $4.97; Food Basics Selection/Life Smart Naturalia, $4.44; Sobeys Compliments, 2/$7; Zehrs Kraft 750 g/1 kg, $5 | High family confidence; missing size at Food Basics and Sobeys blocks reliable unit-price comparison. |

These prices are dated evidence, not timeless facts.

## Matching hazards

- Potatoes: bag versus pound versus count versus tray; sweet potato/cassava
  versus ordinary potato; chips, fries, wedges, soup, and prepared sides.
- Milk: dairy versus plant-based, condensed, evaporated, chocolate, ice milk,
  formula, and non-food text matches.
- Spaghetti: dry pasta versus pasta sauce, squash, and prepared meals; exact
  shape may be absent even when a matching brand appears.
- Peanut butter: human food versus pet treats and peanut-butter-flavoured
  snacks.
- Combo advertisements: one indexed record may cover multiple products or
  incompatible package sizes.
- Points promotions: reward value is not a cash price.
- Missing package size: retain the offer but do not calculate unit price.
- Duplicate indexing: keep one historical observation per stable dedupe key.

## Token doctrine

The steady-state weekly run should require no model inference. It uses one
cached postal index plus only current-needs searches, with a two-second minimum
request interval. A cheap agent or browser is justified only for the small
ambiguity queue or when the provisional JSON adapter fails.

The earlier 29-grocery-detail sweep demonstrated technical feasibility but is
not the operating design. Bulk detail fetching is now refused. Any later
crawler experiment needs separate approval, a hard request/byte cap, and no
more than two small-cover flyers selected deterministically from the cached
index.
