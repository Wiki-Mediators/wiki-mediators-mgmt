# MNQ Replay Viewer - Build Roadmap

Status: canonical staged build plan.
Created: 2026-05-14.

> **Management-vault boundary:** descriptive only — the runtime, source files,
> commands, APIs, and working paths referenced below live in the full working
> vault and are not runnable from the management checkout.

## Current Build State

Current app stage: Stage 9 V2 batch snapshots built; smoke clean,
40-trade full batch exposes 4h data-window bottleneck.

Next build stage: address 4h snapshot data-window performance if batch
review is the priority, otherwise true rewind or richer Stage 9
lifecycle overlays.

Pause checkpoint 2026-06-11:

- Stage 9 V2 batch snapshots are implemented through a separate
  `/snapshot` page and `batch_snapshot.py`. The script writes fixed
  1600x900 images, per-trade sidecar JSON, and `_run_summary.json`, and
  refuses sealed OOS rows dated 2026-02-01 or later.
- One-trade smoke run passed end-to-end:
  `tools/mnq_replay_viewer/snapshots/v2a_20260611_004927`
  generated 4 images, 1 sidecar, and a clean run summary.
- `multiprocessing.Pool` parallelization is built. `--workers` defaults
  to 4; each worker owns its own Playwright browser and snapshot server
  instance.
- Full v2a 40-trade run with 4 workers completed but was not clean:
  `tools/mnq_replay_viewer/snapshots/v2a_20260611_024234` produced all
  sidecars and all `1m` / `5m` / `30m` images, but only 4 of 40 `4h`
  images before 600000 ms page timeouts. Total elapsed time was about
  10485 seconds.
- Measured bottleneck after parallelization: wide-window 4h snapshots
  repeatedly load and convert large multi-month 1-second DBN files.
  Indicator caching and baseline-library architecture remain deferred;
  the next performance work should target data-window loading or
  pre-aggregated 4h snapshot inputs.

Pause checkpoint 2026-05-17:

- The replay viewer is usable as a local Python-backed manual MNQ replay
  tool with indicators, chart trading, staged orders, limit/stop entry
  orders, ATM brackets, scale-in/scale-out accounting, multi-target ATM,
  journal filtering, and last-trade review.
- Stage 8.5 interaction cleanup is effectively complete for forward-only
  replay. The remaining Stage 8.5 gap is true historical rewind: stepping
  backward or jumping to a journal event currently moves the replay cursor
  visually, but does not reconstruct prior order/account/position state.
- Stage 9 V1 strategy overlays are built as a minimal strategy-trade
  browser. It imports a local strategy trade CSV, lists trades in the
  side panel, jumps previous/next by trade, needle-drops to entry, and
  draws replay-aware entry/exit chart markers.
- Recommended pickup choices:
  - build true rewind/state reconstruction first if manual replay
    correctness during backward navigation matters;
  - extend Stage 9 overlays if the next goal is richer trade-path
    review (URL links, checkpoints, lifecycle events, MFE/MAE traces);
  - do a short browser QA pass before either larger branch if UI behavior
    feels stale after returning to the project.

Stage 8.5 is split into labeled implementation slices in:

```text
tools/mnq_replay_viewer/STAGE_8_5_IMPLEMENTATION_PLAN.md
```

Strategy Overlay Adapter work is Stage 9. The first useful slice is now
built; richer lifecycle rendering remains deferred until the simple
trade browser has been exercised on real strategy CSVs.

Canonical near-term sequence:

| Step | Label | Status |
|---|---|---|
| 8.5.0 | Housekeeping and labels | built |
| 8.5.1 | Manual panel cleanup and live summary | built |
| 8.5.2 | Limit and stop entry orders | built |
| 8.5.3 | Safety locks and hotkeys | mostly built |
| 8.5.4 | Chart context menu and staged ghost orders | mostly built |
| 8.5.5 | Drag-to-modify working lines | built |
| 8.5.6 | Final floating label placement | built |
| 8.5.7 | In-app journal and trade review overlay | built |
| 8.5.8A | Partial position accounting | built |
| 8.5.8B | Manual protective stops and targets | built |
| 8.5.8C | Scale-in toggle | built |
| 8.5.8D | Chart close control | built |
| 8.5.8E | Multi-target ATM | built |
| 9 V1 | Strategy-trade browser | built |
| 9 V2 | Batch snapshot generator | smoke-pass; full-batch 4h bottleneck |

### Stage 9 First Cut: Strategy-Trade Browser

Restart guidance banked 2026-06-10: if Stage 9 is chosen before true
rewind, begin with the smallest useful strategy overlay rather than the
full normalized lifecycle renderer. Implemented 2026-06-10 as V1.

V1 scope:

- Import one canonical `nb_lib` one-row-per-trade CSV shape first.
- Normalize each row into at least an entry event and an exit event.
- Add a side-panel trade browser with date, entry time, direction, P&L,
  and exit reason.
- Click-to-load should select the session/date, move the replay cursor
  to the entry second, and center the chart near the trade.
- Render entry and exit markers on the chart.

V1 implementation 2026-06-10:

- Added a side-panel Strategy Trades CSV overlay to the local app.
- Imports common `nb_lib` one-row-per-trade CSV columns including
  `entry_ts`/`entry_time`, `exit_ts`/`exit_time`, `direction`, `strategy`
  or `variant`, `pnl`/`net_pnl`, and `exit_reason`.
- Previous/next trade buttons move through the normalized trade list.
- Clicking a trade loads the date, sets the needle-drop to entry time,
  and centers the chart near that entry.
- Chart markers are replay-aware: entry appears only after the cursor
  reaches entry; exit appears only after the cursor reaches exit.

V1 non-scope:

- no MFE/MAE path overlays;
- no 120s/300s checkpoint markers;
- no BE/trail/lifecycle reconstruction;
- no counterfactual-management markers;
- no support for every historical CSV shape.

This first cut is meant to connect numerical strategy reports to visual
path review. URL deep-links from reports, richer lifecycle adapters, and
management-observer overlays come after the basic browser works.

### Stage 9 V2: Batch Strategy Snapshots

Implemented 2026-06-11 as a separate snapshot path, not a mutation of
the live replay UI.

V2 scope:

- Render fixed 1600x900 PNG snapshots for strategy trades.
- Produce four requested timeframes per trade: `1m`, `5m`, `30m`, `4h`.
- Write one sidecar JSON per trade and one `_run_summary.json` per run.
- Preserve OOS discipline by refusing/skipping rows dated 2026-02-01 or
  later.
- Use Playwright for browser rendering.
- Use `multiprocessing.Pool` with configurable `--workers` (default 4).
  Each worker owns its own browser and snapshot server.

Validation:

- Smoke: `v2a_20260611_004927`, 1 trade, 4 images, clean summary.
- Full 40-trade v2a run: `v2a_20260611_024234`, 40 sidecars and 124
  images. All `1m`, `5m`, and `30m` images generated; only 4 of 40
  `4h` images generated before page timeouts.

Finding: after parallelization, the limiting cost is not Playwright
startup or indicator drawing. The hard bottleneck is repeatedly loading
and converting large 1-second DBN windows for `4h` snapshots. Do not
build generic indicator caching first; target data-window loading or
pre-aggregated 4h inputs when this branch resumes.

## Purpose

This roadmap defines the staged implementation order for the MNQ Replay
Viewer. The goal is to build the simulator progressively, with each
stage producing a usable and testable layer before the next layer is
added.

Do not jump ahead to later stages until the earlier stage is working and
verified. In particular, manual trading and ATM brackets depend on the
replay clock, candle building, and indicator overlays being stable.

## Stage 1: Replay Clock And Candles

Status: built 2026-05-14 as a Python-backed local app under
`tools/mnq_replay_viewer/app`.

Scope:

- load MNQ 1-second historical bars;
- select session/date;
- needle-drop to a start timestamp;
- play/pause;
- speed controls: `1x`, `2x`, `3x`;
- aggregate mutable candles from 1-second bars;
- support at least `1s`, `1m`, `2m`, `5m`;
- hide future bars during live-like replay.

Acceptance:

- a 1-minute candle visibly builds from 60 one-second updates;
- changing speed does not skip candle state;
- replay cursor is the single source of truth.

Verification 2026-05-14:

- root page returned HTTP 200;
- `/api/health` returned ok;
- `/api/sessions` selected latest populated session `2026-05-01`;
- `/api/bars?date=2026-05-01` returned 51,503 one-second bars.
- timestamp handling repaired after UI review: API now sends actual UTC
  epoch plus explicit Eastern `display_time` and `session_seconds`, and
  needle-drop uses `session_seconds` instead of browser-local `Date`.

## Stage 2: SMA/EMA Overlays

Status: built 2026-05-14 as client-side overlays on the price chart.

Scope:

- SMA overlays: 20, 50, 200 presets;
- EMA overlays: 9, 20, 50, 200 presets;
- price-chart line rendering;
- active candle provisional values;
- completed candle locked values;
- visibility toggles.

Acceptance:

- SMA/EMA update on the mutable active candle;
- completed historical indicator values do not change;
- no future bars are used.

Verification 2026-05-14:

- added SMA 20/50/200 and EMA 9/20/50/200 overlay toggles;
- EMA 20 defaults visible;
- overlays recompute from currently visible replay candles only;
- timeframe changes recalculate overlays from the selected chart
  timeframe.

## Stage 3: RTH + ETH/Globex VWAP

Status: built 2026-05-14 as server-side one-second VWAP fields with
client-side line overlays.

Scope:

- RTH VWAP anchored at 09:30 ET;
- ETH / Globex VWAP anchored at 18:00 ET previous calendar day;
- practical active display range may use 18:01-16:59 ET;
- hide ETH / Globex VWAP during the 17:00-18:00 ET maintenance break;
- compute VWAP from 1-second source data.

Acceptance:

- RTH VWAP resets at RTH open;
- ETH / Globex VWAP resets at Globex open;
- VWAP updates once per replay second;
- maintenance gap does not draw a misleading continuous line.

Verification 2026-05-14:

- `/api/bars` now emits `rth_vwap` and `eth_vwap` fields per bar;
- RTH VWAP is blank before 09:30 ET and populated at 09:30 ET;
- ETH / Globex VWAP is populated during the active futures session and
  blank after 17:00 ET maintenance begins;
- front end includes RTH VWAP and ETH VWAP overlay toggles;
- VWAP line values render from visible replay candles only.

## Stage 4: Anchored VWAP

Status: built 2026-05-14 as one active anchored VWAP from the current
replay cursor.

Scope:

- user selects a candle/timestamp as anchor;
- anchored VWAP starts from that point;
- multiple anchored VWAPs can be supported later, but v1 may allow one;
- anchor marker visible on chart;
- anchor can be removed/reset.

Acceptance:

- anchored VWAP uses only bars from anchor through current replay cursor;
- no future bars are used;
- replay start/needle-drop behavior does not corrupt anchor calculations.

Verification 2026-05-14:

- added Anchored VWAP toggle plus Set anchor / Clear controls;
- anchor is set at the current replay cursor timestamp;
- anchored VWAP computes from 1-second bars from anchor through current
  cursor and aggregates to the active chart timeframe;
- anchor resets when a new session is loaded.

## Stage 5: MACD Lower Panel

Status: built 2026-05-14 as a lower chart panel with MACD 12/26/9.

Scope:

- MACD 12/26/9;
- lower indicator panel;
- MACD line, signal line, histogram;
- active candle provisional MACD;
- completed candle locked MACD.

Acceptance:

- active candle MACD recomputes from previous locked EMA values plus the
  active candle's latest close;
- active candle does not recursively compound EMA every second;
- final active candle value locks at candle close.

Verification 2026-05-14:

- added lower MACD chart panel below price chart;
- added MACD 12/26/9 overlay toggle;
- rendered MACD line, signal line, and green/red histogram;
- MACD is computed from the mutable chart-timeframe candle series;
- price and MACD chart time ranges are synchronized with a guard to
  avoid recursive range updates.
- indicator last-value labels moved off the right price scale into
  floating in-chart labels with thin connector lines to avoid hiding
  the latest candles.

## Stage 6: Indicator Menu/Presets

Status: built 2026-05-14 as quick preset buttons plus existing overlay
toggles.

Scope:

- indicator menu in toolbar;
- quick-add presets;
- edit indicator parameters;
- toggle visibility;
- remove indicator;
- reset to default presets.

Initial quick-add defaults:

- `EMA 20`;
- `RTH VWAP`;
- `MACD 12/26/9`.

VWAP quick choices:

- `RTH VWAP`;
- `ETH / Globex VWAP`;
- `Anchored VWAP`;
- `Rolling VWAP` later.

Acceptance:

- user can configure overlays without restarting replay;
- indicator state is separate from replay/order state.

Verification 2026-05-14:

- added quick presets: Default, Clean, Trend, VWAP, MACD;
- presets update overlay checkbox state and visible chart series;
- anchored VWAP is not auto-enabled by presets unless an anchor exists;
- indicator state remains client-side and independent from replay state.

## Stage 7: Slice A - Manual Market Orders

Status: built 2026-05-14 as manual market-order simulation with delayed
fills, position state, PnL, and downloadable JSON journal.

Scope:

- simulated account state;
- position state;
- `Buy Mkt`;
- `Sell Mkt`;
- `Close`;
- 1-second default order delay;
- optional 2-second and 3-second delay presets;
- BAND_B default friction profile;
- tunable friction fields;
- realized/unrealized PnL;
- event journal JSON.

Acceptance:

- market orders fill no earlier than the next eligible 1-second bar;
- position/PnL updates deterministically;
- close exits the position and writes journal events;
- replay journal can be reloaded as an overlay later.

Verification 2026-05-14:

- added Buy Mkt, Sell Mkt, and Close controls;
- added qty, delay, slippage, and commission inputs;
- market orders remain pending until the configured next eligible
  1-second bar, then fill at that bar's open plus/minus slippage;
- position state, realized PnL, unrealized PnL, working order count,
  and journal event count update from replay state;
- journal can be downloaded as normalized JSON;
- duplicate entry clicks are rejected while an entry order is pending.

## Stage 8: Slice B - ATM Brackets

Status: built 2026-05-14 as a simple one-stop / one-target ATM bracket
with optional auto-breakeven.

Scope:

- ATM template JSON storage;
- selected ATM template on order panel;
- attached stop and target after entry fill;
- working stop/target lines on chart;
- target fill;
- stop fill;
- cancel/modify working orders;
- basic auto-breakeven stop strategy;
- `Rev` behavior.

Acceptance:

- one entry creates one stop and one target;
- same-bar ambiguity uses adverse-first, including the first eligible
  stop/target bar;
- attached orders cancel correctly when position closes;
- BE updates stop only when level changes.

Verification 2026-05-14:

- added editable ATM controls: template, stop ticks, target ticks,
  auto-BE, BE trigger ticks, and BE plus ticks;
- when a market entry fills, the selected ATM creates one target limit
  and one stop order with the same delayed eligibility model;
- working stop/target orders render as chart price lines;
- stop/target fills are checked against 1-second OHLC after eligibility;
- if stop and target touch in the same 1-second bar, stop fills first;
- manual Close cancels attached bracket orders before submitting the
  exit market order;
- auto-breakeven moves the stop only when the new stop tightens risk.

## Stage 9: Strategy Overlay Adapter

Status: V1 strategy-trade browser built 2026-06-10; richer lifecycle
overlay adapter deferred.

Scope:

- import normalized replay-event JSON;
- adapter for manual replay journals;
- adapter for simple `nb_lib` trade CSV summary overlays;
- later adapter for lifecycle logs;
- later adapter for management event logs;
- render entries, exits, stops, targets, proposal rejections,
  compliance blocks, and account-state events.

Acceptance:

- overlay renders only events at or before replay cursor;
- future strategy events remain hidden;
- stop evolution renders only when stop level changes;
- rejected management proposals are visible but low-noise;
- schema supports future multi-strategy overlays.

## Stage 8.5.8: Real Position And Order Accounting

Status: built 2026-05-16. Partial position accounting, manual
protective stops/targets, scale-in toggle, chart close control, and
multi-target ATM are built.

Research note:

```text
tools/mnq_replay_viewer/CHART_TRADING_RESEARCH_NOTES.md
```

Why this stage exists:

- the current replay app approximates chart trading, but the position
  model still behaves like one entry plus one full exit;
- manual stops/targets while already in a position need explicit
  protective-stop and profit-target roles;
- scale-out needs fills to reduce by order quantity;
- scale-in needs weighted average-entry recalculation;
- multi-target ATM cannot be reliable until partial fills are correct.

Build sequence:

| Slice | Label | Purpose |
|---|---|---|
| 8.5.8A | Partial position accounting | Reduce/close positions by order quantity instead of assuming full exits. |
| 8.5.8B | Manual protective stops and targets | Allow in-position stop-loss and take-profit orders, including no-ATM trades. |
| 8.5.8C | Scale-in toggle | Permit deliberate same-direction adds with weighted average entry. |
| 8.5.8D | Chart close control | Add an on-chart flatten/close button near the AVG position label. |
| 8.5.8E | Multi-target ATM | Add multi-target bracket rows after partial accounting is proven. |

Stage 8.5.8 is the bridge between the visual approximation and a real
manual replay state machine. Do not build multi-target ATM first; it
depends on 8.5.8A.

## Stage 8.5: Replay UI / Control Cleanup

Status: in progress 2026-05-15. Slices 8.5.0 through 8.5.2 are built;
chart trading, floating labels, and drag-to-modify are partially built;
real partial-position accounting is next.

Detailed backlog:

```text
tools/mnq_replay_viewer/REPLAY_UI_CONTROL_CLEANUP_BACKLOG.md
```

Labeled implementation plan:

```text
tools/mnq_replay_viewer/STAGE_8_5_IMPLEMENTATION_PLAN.md
```

Why this sits before Stage 9:

- manual chart trading needs direct chart interactions, not just
  side-panel buttons;
- order/indicator labels need final placement to avoid covering candles
  or price-scale numbers;
- the manual trading panel needs a clearer ORDER / COSTS / ATM /
  POSITION / SUMMARY / ACTIONS structure;
- journal and trade-review overlays should be improved before imported
  strategy overlays are layered into the same visual surface.

Scope summary:

- Chart Trading ON/OFF and Trading Enabled lock;
- crosshair price readout rounded to `0.25`;
- right-click chart menu for limit/stop orders and alerts;
- staged ghost orders with confirm/cancel;
- draggable working LMT/STP/TP/AVG lines and labels;
- direct limit/stop entry activation with ATM after entry fill;
- BE Now button;
- Cancel All Working and Close / Flatten safety controls;
- hotkeys while chart is focused;
- risk/reward preview;
- floating non-price labels to the right of the price scale over the
  existing tools panel, without adding a label column or shrinking the
  chart;
- in-app clickable/filterable journal;
- post-trade review overlay.

Verification 2026-05-14 for Stage 8.5.1:

- added labeled Stage 8.5 implementation plan;
- reorganized manual trading panel into clear sections;
- added order type, price source, order price, Use Last, BE Now, Cancel
  All Working, and live risk/reward summary;
- limit/stop entry buttons are visible but disabled until Stage 8.5.2;
- server compile, JavaScript syntax check, and local HTTP smoke test
  passed.

Verification 2026-05-14 for Stage 8.5.2:

- added side-panel limit entries (`Buy Bid`, `Sell Ask`) and stop
  entries (`Buy Stop`, `Sell Stop`);
- entry orders use delayed eligibility, render as working price lines,
  and activate ATM brackets only after fill;
- invalid stop placement is rejected and journaled;
- applied screenshot-driven visual cleanup: stronger section/card
  styling, green/red buy/sell actions, highlighted BE Now, live
  effective Order price display, estimated summary styling, and
  floating label placement to the right of the price scale over the
  tools panel;
- server compile, JavaScript syntax check, and local HTTP smoke test
  passed.

Verification 2026-05-14 for chart-trading click/menu slice:

- added Trading Enabled lock and Chart Trading toggle;
- added transparent chart hit layer so browser context menu is
  suppressed while chart trading is enabled;
- left-click/right-click maps chart Y coordinate to tick-rounded MNQ
  price;
- click/right-click stages a dashed ghost order line and opens custom
  Buy/Sell Limit/Stop menu;
- submitted staged orders reuse the Stage 8.5.2 limit/stop entry
  engine;
- staged ghost order lines and floating `STAGED` labels can be dragged
  before submit;
- drag working orders and hotkeys are partially built; alert creation
  and one-click trading remain deferred.

Verification 2026-05-14 for drag-to-modify slice:

- working order lines and floating order labels can be selected;
- selected orders get visual feedback;
- dragging a working order line/label creates a pending modification;
- modification applies after the configured replay delay, not instantly;
- journal records submitted and applied order modification events;
- chart menu can add reduce-only exit limit/stop orders while already in
  position, so manual protective stops/targets are possible outside the
  initial ATM bracket.

## Rule

Each stage should leave the viewer in a coherent working state. If a
stage exposes a design flaw in an earlier layer, fix the earlier layer
before proceeding.
