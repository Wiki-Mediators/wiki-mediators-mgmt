---
type: methodology-data-store
version: 1
created: 2026-05-12
updated: 2026-05-12
status: working-draft
source_audit: "../../../nb_lib_database_health_report.md"
---

# nb_lib Data Store Reference (Working Draft v1)

## Purpose

This document records what's actually in the Databento data store
at `C:/VMShare/NT8lab/databento/`, its known limitations, and
loader behavior quirks. Future strategy iterations should consult
this when:

- Picking which instruments to use (verify data exists)
- Designing in-sample windows (account for missing days)
- Choosing a data loader (verify gap-handling semantics)
- Planning library work (identify if new loaders are needed)

Last comprehensive audit: 2026-05-12 (see
`nb_lib_database_health_report.md`).

## Section 1: Instrument inventory

| Path | Files | Size | Range (first → last file) | Notes |
|---|---|---|---|---|
| **`MNQ/ohlcv-1s`** | 9 | 354.8 MB | 2024-08-01 → 2026-05-04 | **Primary store; tested fleet uses this** |
| `MNQ/ohlcv-1m` | 2 | 13.6 MB | 2024-04-01 → 2026-04-05 | |
| `MNQ/ohlcv-1h` | 1 | 343.5 KB | 2024-08-01 → 2026-04-15 | |
| `MNQ/ohlcv-1d` | 1 | 42.5 KB | 2024-04-01 → 2026-04-05 | |
| `MNQ/statistics` | 1 | 18.8 MB | 2024-08-01 → 2026-04-15 | Daily microstructure stats |
| `ES/ohlcv-1m` | 2 | 8.8 MB | 2024-08-01 → 2026-04-15 | Continuous E-mini S&P |
| `ES/ohlcv-1d` | 1 | 48.3 KB | 2024-01-01 → 2026-04-15 | |
| `GC/ohlcv-1d` | 1 | 30.3 KB | 2024-08-01 → 2026-04-15 | Continuous gold |
| `CL/ohlcv-1d` | 1 | 35.6 KB | 2024-08-01 → 2026-04-15 | Continuous crude |
| `UVXY/ohlcv-1d` | 2 | 11.5 KB | 2024-08-01 → 2026-04-15 | Daily volatility ETF |
| `MNQM4/ohlcv-1m` | 1 | 1.8 MB | 2024-03-01 → 2024-06-22 | Raw quarterly (Jun 2024) |
| `MNQU4/ohlcv-1m` | 1 | 1.9 MB | 2024-06-01 → 2024-09-22 | Raw quarterly (Sep 2024) |
| `MNQZ4/ohlcv-1m` | 1 | 1.9 MB | 2024-09-01 → 2024-12-22 | Raw quarterly (Dec 2024) |
| `MNQH5/ohlcv-1m` | 1 | 1.8 MB | 2024-12-01 → 2025-03-22 | Raw quarterly (Mar 2025) |
| `MNQM5/ohlcv-1m` | 1 | 2.0 MB | 2025-03-01 → 2025-06-22 | Raw quarterly (Jun 2025) |
| `MNQU5/ohlcv-1m` | 1 | 1.8 MB | 2025-06-01 → 2025-09-22 | Raw quarterly (Sep 2025) |
| `MNQZ5/ohlcv-1m` | 1 | 1.9 MB | 2025-09-01 → 2025-12-22 | Raw quarterly (Dec 2025) |
| `MNQH6/ohlcv-1m` | 1 | 1.9 MB | 2025-12-01 → 2026-03-22 | Raw quarterly (Mar 2026) |

Total: 18 leaf directories, 28 `.dbn.zst` payload files, ~417 MB.
Manifest `databento/manifest.json` records 33 download attempts
(5 failed, 28 complete; total cost $114.24).

## Section 2: MNQ ohlcv-1s coverage

**Coverage range:** first bar `2024-07-31 20:00:00 ET` (Globex
open for 2024-08-01 RTH); last bar `2026-05-03 19:59:55 ET`.

**Total bars:** 29,081,596.

**RTH-present dates in window:** 443.
**Calendar-expected trading days in window:** 441.
(Two extra RTH dates because the store extends past the
2024-08-01–2026-05-04 audit boundaries by a few hours on each side.)

**Missing days: 9 total.**

| Date | DOW | Pattern |
|---|---|---|
| 2024-09-20 | Fri | Quarterly OPEX (3rd Fri Sep 2024) |
| 2024-12-20 | Fri | Quarterly OPEX (3rd Fri Dec 2024) |
| 2025-01-09 | Thu | Carter National Day of Mourning (markets closed; calendar over-tags) |
| 2025-03-21 | Fri | Quarterly OPEX (3rd Fri Mar 2025) |
| 2025-06-20 | Fri | Quarterly OPEX (3rd Fri Jun 2025) |
| 2025-09-19 | Fri | Quarterly OPEX (3rd Fri Sep 2025); the known-documented gap |
| 2025-12-19 | Fri | Quarterly OPEX (3rd Fri Dec 2025) |
| 2026-03-20 | Fri | Quarterly OPEX (3rd Fri Mar 2026) |
| 2026-05-04 | Mon | Past last download (2026-05-03 was last RTH date covered) |

Pattern: 7 of 9 missing days are quarterly OPEX Fridays
(3rd Fri of Mar/Jun/Sep/Dec); 1 is a federal mourning closure
the `TradingCalendar` does not encode; 1 is the boundary day past
the last download.

- **In-sample window (2024-08-01 → 2026-01-31) missing: 7 days.**
- **OOS window (2026-02-01 → 2026-05-04) missing: 2 days.**

This is NOT a Databento delivery defect. It is a known
characteristic of the continuous-front-month `MNQ.c.0` contract
feed: on quarterly OPEX days, the front-month contract changes
hands at the close and the continuous synthesis omits the
single-session RTH window. The raw quarterly contracts
(`MNQU5`, `MNQZ5`, etc., listed in Section 1) DO have data for
those days but only at 1-minute resolution, not 1-second.

## Section 3: Other instruments coverage

| Instrument | Resolution | Coverage | Loader status | Notes |
|---|---|---|---|---|
| MNQ | 1s | 2024-07-31 → 2026-05-03 | `load_mnq_1s` | Primary store; 9 missing days per Section 2 |
| MNQ | 1m | 2024-03-31 → 2026-04-14 | none in nb_lib | Could replace inline `to_minutes` resampling |
| MNQ | 1h | 2024-07-31 → 2026-04-14 | none | Used by no current strategy |
| MNQ | 1d | 2024-03-31 → 2026-04-02 | none | Used by no current strategy |
| MNQ | statistics | 2024-08-01 → 2026-04-15 | none | Daily statistics; unused |
| ES | 1m | 2024-07-31 → 2026-04-14 | none in nb_lib | UNBLOCKS `es_leads_nq_divergence_reversion` at data layer |
| ES | 1d | 2024-01-01 → 2026-04-15 | none | Daily ES |
| GC | 1d | 2024-07-31 → 2026-04-13 | none in nb_lib | PARTIALLY unblocks `gold_vs_nq_risk_off_rotation`; intraday GC still needed |
| CL | 1d | 2024-07-31 → 2026-04-13 | none | No current strategy uses crude |
| UVXY | 1d | 2024-07-31 → 2026-04-13 | none | Daily volatility proxy |
| MNQM4–H6 | 1m | varies per quarter | none | Raw quarterly contracts; have data on OPEX days that `.c.0` omits |

**Raw quarterly contracts.** Eight contract files (`MNQM4`,
`MNQU4`, `MNQZ4`, `MNQH5`, `MNQM5`, `MNQU5`, `MNQZ5`, `MNQH6`)
contain MNQ 1-minute data on quarterly OPEX Fridays that the
continuous `.c.0` feed omits. If a strategy needs MNQ data on
those days, the raw-symbol files are the source — but only at
1-minute resolution.

**Note on micro vs E-mini.** The ES store is the full-size
E-mini (`ES.c.0`), not the micro (`MES`). Strategies that
specifically need MES data require additional download. For most
spread / divergence purposes, ES and MES are interchangeable
(tick size differs; price level moves are proportional).
Similarly, the gold store is full-size `GC.c.0`, not `MGC`.

## Section 4: Loader behavior

### `nb_lib.data.load_mnq_1s` (canonical library loader)

- Raises `FileNotFoundError` if any calendar-expected RTH date in
  the requested window has zero bars (`data.py:99-102`).
- Per-date session-close filtering for half-days (closes at
  13:00 ET on observed half-days; Finding #4 fix).
- TradingCalendar-derived expected-days set (Finding #3 fix).
- Behavior on the 9 missing days: any call whose range overlaps
  any of them will raise.

### `nb_lib.scripts.prj3_canonical_alpha.load_seconds` (strategy-local)

- Silently includes whatever `.dbn.zst` files exist
  (`prj3_canonical_alpha.py:142-161`).
- NO missing-day validation.
- Used by all four nb_lib-native tested strategies (variant_1,
  noise_brk Canonical Alpha, PRJ_3 Canonical Alpha, ema_trend
  Canonical Alpha).
- Result: tested strategies have silently dropped ~7 OPEX days
  from their in-sample windows without warning. The omission
  affects <2% of days; past results are not invalidated but
  future iterations should be explicit about included dates.

### Strategy-level data-completeness floors

- `prj3_canonical_alpha.py` lines 131-135 define
  `MIN_RTH_SECOND_BARS=1000`, `MIN_RTH_MINUTE_BARS=30`,
  `MIN_TREND_WINDOW_SECONDS=100`, `MIN_FRACTAL_WINDOW_MINUTES=11`,
  `MIN_BARS_AFTER_SIGNAL=22`.
- Days falling below the per-day floors are silently skipped (no
  signal evaluation, no contribution to results).
- All 27 low-bar days in the audit (including Juneteenth at
  5,980 bars) pass the current 1000-bar floor. Tighter floors
  would silently drop more days.

### `nb_lib.execution.resolve_entry_fill`

- Returns `None` when `len(post_signal) < ENTRY_DELAY +
  MIN_BARS_AFTER` (`execution.py:77-78`).
- Per-trade, not per-day. Correctly drops signals near
  session-end where there isn't time for the trade lifecycle.

## Section 5: Bar quality

From a random 1,000,000-bar sample (seed=42):

- **Zero data corruption.** Zero negative or zero prices. Zero
  zero-volume bars in either RTH or ETH samples.
- **~3.88% of RTH bars are flat** (`high == low` AND
  `open == close`) — consistent with quiet-second behavior at
  midday and on slow sessions; not synthetic fills or
  interpolation.
- **953 large bar-to-bar jumps (>50 pt)** in the sample;
  concentrated at session boundaries (ETH-bar followed by
  RTH-open bar with a multi-hundred-point gap).
- **Max bar-to-bar absolute close diff: 716.75 pt** — almost
  certainly a session-boundary gap rather than an intra-session
  microstructure event.

The check is sample-based, not exhaustive. A strategy that
specifically depends on intra-session bar continuity should
run a targeted scan over the relevant window before relying on
clean continuity.

## Section 6: Implications for strategy design

**If your strategy reacts to events on OPEX days:** use the raw
quarterly contracts (`MNQU5`, `MNQZ5`, etc.) at 1-minute
resolution, not the continuous `.c.0` feed at 1-second. OR
acquire missing 1-second data as a Stage 0 prerequisite.

**If your strategy uses ES data:** ES 1m is present but no
nb_lib loader exists. Either author a strategy-local loader or
wait for a separate iteration to add `load_es_1m()` to the
library. The ES store's gap pattern mirrors MNQ's exactly (same
9 missing days), so cross-asset signals should account for the
same OPEX-Friday and 2025-01-09 omissions.

**If your strategy uses GC (gold) data:** daily resolution only.
If your edge requires intraday gold, that's a Stage 0
data-acquisition prerequisite. The `gold_vs_nq_risk_off_rotation`
candidate specifies MGC (micro gold); the store has full-size GC
only — usable as a proxy, but tick-size differences matter for
execution-precision modeling.

**If your strategy uses other instruments (CL, UVXY, MNQ-1h,
etc.):** data exists at the resolutions documented in Section 3,
but no nb_lib loaders. Strategy-local loader required.

**If your strategy uses a date range starting before 2024-08-01:**
the 1-second MNQ store starts there. Earlier dates have only
1-minute MNQ (back to 2024-03-31) or daily MNQ (back to
2024-03-31).

**If your strategy depends on accurate calendar-day filtering:**
the 2025-01-09 Carter mourning day is NOT in the calendar's
holiday list. Future fix: change `is_trading_day` for that date
from True to False (one-row update in `calendar_data.csv`).
Deferred per audit Section J; documented for awareness.

## Section 7: Library extensions deferred

- `load_es_1m()` — needed if `es_leads_nq_divergence_reversion`
  proceeds; analogous structure to `load_mnq_1s` but at 1-minute
  resolution.
- `load_mnq_1m()` — would simplify the inline `to_minutes`
  resampling currently in the consumer scripts. Not blocking
  anything.
- `load_gc_1d()`, `load_uvxy_1d()`, `load_cl_1d()` — if
  candidates emerge using those instruments.
- `load_seconds(strict=True)` flag — explicit raise-on-missing-day
  variant for new strategies that want loud failure on data
  gaps (preserves existing default silent-skip semantics).

Each is a small iteration when needed. None is blocking current
work.

## Section 8: Cross-references

- Full audit findings:
  [`nb_lib_database_health_report.md`](../../../nb_lib_database_health_report.md)
  (Section C inventory, Section D coverage, Section H loader
  behavior).
- Related methodology doc:
  [`_METHODOLOGY_repertoire.md`](_METHODOLOGY_repertoire.md). Its
  Section 8 indicator catalog complements this Section 3
  instrument catalog — "what can we measure" alongside "what can
  we measure it on".
- Calendar limitations: `nb_lib/HANDOFF.md` "Calendar Limitations"
  subsection (CPI/GDP over-tagging documented; 2025-01-09 fix
  flagged for future iteration).
- This doc: `nb_lib/HANDOFF.md` "Data Store Limitations"
  subsection (added 2026-05-12 alongside this file).

End of document.
