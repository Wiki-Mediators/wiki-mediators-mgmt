# MNQ Replay Viewer - Strategy Overlay Adapter Spec

Status: pre-implementation design.
Created: 2026-05-14.

> **Management-vault boundary:** descriptive only — the runtime, source files,
> commands, APIs, and working paths referenced below live in the full working
> vault and are not runnable from the management checkout.

## Purpose

This document defines how strategy outputs from `nb_lib`, manual replay
journals, and future external sources should be converted into a
normalized replay-event format for the MNQ Replay Viewer.

The replay viewer should not parse every CSV/log shape directly in the
front end. Source files should be imported by adapters and converted to
a common event schema. The viewer then renders only normalized replay
events.

```text
nb_lib trade CSVs
nb_lib lifecycle logs
management event logs
manual replay journals
future NT8 exports
        |
        v
source-specific import adapters
        |
        v
normalized replay-event JSON
        |
        v
Replay Viewer overlays
```

## Section 1: Source Formats

Initial adapter targets:

1. **Strategy trade CSVs**
   - Example outputs: `*_trades.csv`.
   - Usually contain one row per completed trade.
   - Useful for entry marker, exit marker, final PnL, direction, and
     summary trade labels.
   - Often insufficient for reconstructing in-flight stop/target state
     unless lifecycle details are embedded.

2. **Execution / lifecycle logs**
   - Example outputs: `*_log_YYYYMMDD.csv`, `ExecutionLogger` outputs,
     `TradeLifecycle` event logs.
   - Usually contain order state transitions and bracket events.
   - Useful for reconstructing entries, TP1, runner, stop, BE arm,
     force exits, and EOD exits.

3. **Management event logs**
   - Include adaptive management proposals and applied/rejected bracket
     changes.
   - Important for debugging strategy management behavior.
   - Must preserve rejected proposals, not just accepted changes.

4. **Manual replay journals**
   - Produced by the manual simulator itself.
   - Should already be close to normalized replay-event JSON.
   - Can be loaded back as an overlay for post-session review.

5. **Future NT8 exports**
   - NinjaTrader execution exports, ATM events, or broker/account logs.
   - Not v1 scope, but schema should not prevent future import.

Adapter rule: every adapter must report its source file path, source
type, import timestamp, and any unmapped/ignored columns. The import
process should be explainable; silent field loss is not acceptable.

## Section 2: Normalized Replay-Event Schema

Top-level shape:

```json
{
  "schema_version": "replay_events_v1",
  "instrument": "MNQ",
  "source": {
    "type": "nb_lib_lifecycle_log",
    "path": "C:/VMShare/NT8lab/example_log.csv",
    "imported_at": "2026-05-14T12:00:00-04:00",
    "adapter": "nb_lib_lifecycle_v1"
  },
  "strategies": [
    {
      "strategy_id": "round_number_rejection_microfade",
      "display_name": "Round Number Rejection Microfade",
      "color": "#38bdf8"
    }
  ],
  "events": []
}
```

Every event should include:

```json
{
  "event_id": "evt_000001",
  "ts": "2026-03-16T09:36:01-04:00",
  "strategy_id": "round_number_rejection_microfade",
  "trade_id": "trade_20260316_001",
  "type": "entry_fill",
  "instrument": "MNQ",
  "source_ref": {
    "path": "C:/VMShare/NT8lab/example_log.csv",
    "row": 42
  }
}
```

Required common fields:

- `event_id`
- `ts`
- `type`
- `instrument`
- `strategy_id`
- `trade_id` where applicable
- `source_ref`

Optional common fields:

- `side`: `long`, `short`, `buy`, `sell`
- `qty`
- `price`
- `order_id`
- `order_type`: `market`, `limit`, `stop`
- `role`: `entry`, `stop_loss`, `target`, `runner`, `manual_exit`,
  `force_exit`
- `label`
- `reason`
- `pnl`
- `realized_pnl`
- `unrealized_pnl`
- `account_state`
- `metadata`

### Event Types

Signal and entry:

- `signal`
- `entry_order_submitted`
- `entry_fill`
- `entry_rejected`

Working order lifecycle:

- `working_order_created`
- `working_order_modified`
- `working_order_cancelled`
- `working_order_filled`

Targets and stops:

- `target_created`
- `target_modified`
- `target_fill`
- `stop_created`
- `stop_modified`
- `stop_fill`
- `breakeven_move`
- `trail_update`

Management proposals:

- `working_order_proposal`
- `working_order_proposal_applied`
- `working_order_proposal_rejected`

Rejected management proposals are first-class events. They should not be
discarded. Example: round-number-rejection produced rejected
structure-trail proposals because the proposed stop would have widened
relative to the BE-armed stop. Visualizing those rejected proposals is
useful for understanding why management was design-dead.

Exits:

- `partial_exit`
- `force_exit`
- `eod_exit`
- `position_closed`

Compliance/account:

- `compliance_block`
- `daily_loss_limit_hit`
- `account_failed`
- `apex_state_change`

Replay/manual:

- `manual_order_submitted`
- `manual_order_filled`
- `manual_order_cancelled`
- `manual_note`

### Example Events

Entry fill:

```json
{
  "event_id": "evt_1001",
  "ts": "2026-03-16T09:36:01-04:00",
  "type": "entry_fill",
  "strategy_id": "vwap_stretch_snapback",
  "trade_id": "vwap_20260316_001",
  "instrument": "MNQ",
  "side": "long",
  "qty": 3,
  "price": 29766.5,
  "label": "Entry"
}
```

Stop modification:

```json
{
  "event_id": "evt_1010",
  "ts": "2026-03-16T09:42:00-04:00",
  "type": "stop_modified",
  "strategy_id": "example_strategy",
  "trade_id": "trade_001",
  "order_id": "stop_001",
  "old_price": 29761.25,
  "new_price": 29766.75,
  "reason": "breakeven_move"
}
```

Rejected proposal:

```json
{
  "event_id": "evt_1020",
  "ts": "2026-03-16T09:45:00-04:00",
  "type": "working_order_proposal_rejected",
  "strategy_id": "round_number_rejection_microfade",
  "trade_id": "rnrm_20260316_001",
  "order_id": "stop_001",
  "proposed_price": 29764.25,
  "current_price": 29766.5,
  "reason": "rejected_would_widen_stop",
  "metadata": {
    "specialist": "structure_trail",
    "proposal_side": "stop_loss"
  }
}
```

Compliance block:

```json
{
  "event_id": "evt_2001",
  "ts": "2026-03-16T11:04:00-04:00",
  "type": "compliance_block",
  "strategy_id": "example_strategy",
  "instrument": "MNQ",
  "reason": "account_failed_no_new_entries",
  "account_state": "FAILED"
}
```

## Section 3: Visual Rendering Rules

### General Principles

- Render only events at or before the current replay cursor.
- Future strategy events remain hidden during replay.
- Events should be visually tied to the chart timestamp nearest their
  event timestamp.
- If an event timestamp falls between 1-second bars, snap to the next
  available 1-second bar unless the source explicitly says otherwise.
- Strategy overlays must be visually optional: each strategy can be
  toggled on/off.

### Markers

- `signal`: small hollow marker above/below bar.
- `entry_fill`: solid arrow marker at fill price.
- `target_fill`: green/check marker at fill price.
- `stop_fill`: red/x marker at fill price.
- `partial_exit`: smaller exit marker with quantity label.
- `force_exit`: orange exit marker.
- `eod_exit`: gray exit marker.
- `compliance_block`: warning marker at top of chart or event lane.

### Lines

Working order lines:

- `target_created` / `working_order_created` with role target: horizontal
  limit line.
- `stop_created` / role stop_loss: horizontal stop line.
- `stop_modified`: update stop line from old to new price.
- `target_modified`: update target line from old to new price.
- `working_order_cancelled` or fill: end the line at event timestamp.

Stop evolution granularity:

- Render stop evolution only when the stop level changes.
- Do not render one visual event per management evaluation if the stop
  price is unchanged.
- Rejected proposals may appear in an event lane or tooltip stream, but
  they should not draw new stop lines because no working order changed.

### Rejected Proposals

`working_order_proposal_rejected` should be visible but low-noise.

Recommended rendering:

- small amber tick/icon on a management-event lane;
- tooltip includes specialist, proposed price, current price, and reason;
- optional filter: show/hide rejected proposals.

This is important for diagnosing "management did nothing" cases. A
strategy can be alive internally but have every proposal rejected by
tighten-only rules, compliance checks, or bracket ordering invariants.

### Compliance Blocks

`compliance_block`, `daily_loss_limit_hit`, `account_failed`, and
`apex_state_change` should render in a distinct account-state lane or as
chart banners.

These are not trade fills. They are simulation/account state events and
should not be confused with market executions.

### Multi-Strategy Overlay

The schema must allow multiple strategies on the same chart, even if v1
only renders one at a time.

Rules:

- Every event has `strategy_id`.
- Top-level `strategies` list defines display metadata.
- Colors should be assigned per strategy.
- Trade ids only need to be unique within a strategy; viewer can use
  `(strategy_id, trade_id)` as the composite identity.
- UI should eventually allow toggling each strategy independently.

v1 implementation may load one strategy overlay at a time. The schema
must not forbid multi-strategy layering.

## Section 4: State Reconstruction

The viewer must reconstruct trade/order state from events rather than
assuming final trade CSV rows are enough.

At replay cursor `T`:

1. Load all normalized events.
2. Sort by `(ts, event_sequence)`.
3. Apply only events with `ts <= T`.
4. Rebuild per-strategy state:
   - open positions;
   - working orders;
   - active stops/targets;
   - realized PnL;
   - account/compliance state.
5. Render state as of `T`.

### Event Ordering

If multiple events share the same timestamp, adapters should assign
`event_sequence`.

Recommended order:

1. signal
2. order submitted
3. fill
4. attached orders created
5. management proposal
6. management proposal applied/rejected
7. order modified/cancelled
8. exit fill
9. position closed
10. compliance/account state

This prevents ambiguous state when an entry fill and attached bracket
creation occur at the same timestamp.

### Working Order State

Working orders are reconstructed by `order_id`.

- `working_order_created`: add order.
- `working_order_modified`: update price/qty/status.
- `working_order_cancelled`: mark inactive.
- `working_order_filled`: mark filled and update position.
- `stop_fill` / `target_fill`: may either be specialized fill events or
  aliases for `working_order_filled` with role metadata.

Adapters should preserve source ids when possible. If source logs do not
have order ids, adapter must synthesize stable ids from trade id, role,
and event sequence.

### Position State

Position state is reconstructed by `(strategy_id, trade_id)`.

Rules:

- `entry_fill` opens or adds to position.
- `partial_exit` reduces position.
- `target_fill` reduces or closes position.
- `stop_fill`, `force_exit`, and `eod_exit` reduce or close position.
- `position_closed` finalizes trade state.

If event stream and final trade CSV disagree, adapter should mark the
import with a warning. Do not silently force consistency.

### Management Proposal State

Management proposals do not change working order state unless an
`applied` event follows.

- `working_order_proposal`: record proposal.
- `working_order_proposal_applied`: record proposal and apply resulting
  order modification.
- `working_order_proposal_rejected`: record proposal but do not modify
  working order state.

Rejected proposals should still be available for tooltips, counts, and
diagnostic overlays.

### Missing Data Handling

If a source trade CSV contains only final entry/exit rows:

- Create minimal `entry_fill` and exit event.
- Do not invent stop/target evolution.
- Mark `reconstruction_quality = "summary_only"`.

If lifecycle logs contain bracket details:

- Mark `reconstruction_quality = "lifecycle"`.

If management event logs include proposals:

- Mark `reconstruction_quality = "management_full"` or similar.

The UI should expose reconstruction quality so the user knows whether
they are seeing full state or summary markers.

## Adapter Build Recommendation

Build adapters in this order:

1. Manual replay journal JSON -> normalized replay events.
2. Simple `nb_lib` trade CSV -> summary overlay.
3. `nb_lib` lifecycle log -> full order/position reconstruction.
4. Management event log -> proposals, applied updates, rejected updates.
5. NT8 execution export -> future adapter.

Do not start with the most complicated log shape. A summary trade
overlay is useful quickly, but the schema must be ready for full
lifecycle reconstruction.
