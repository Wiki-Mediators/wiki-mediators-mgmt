---
status: "tested-informational-rejected"
---

# Objective-Level Liquidity Sweep Reversal Family FINAL Spec

**Strategy ID:** `objective_level_liquidity_sweep_reversal_family`  
**Status:** TESTED-INFORMATIONAL-REJECTED  
**Created:** 2026-05-25  
**Canonical path:** `nb_lib/strategy_specs/canonical/objective_level_liquidity_sweep_reversal_family_spec_FINAL.md`  
**Candidate lineage:** `nb_lib/strategy_specs/candidates/objective_level_liquidity_sweep_reversal_family.md`  
**R4 probe:** `nb_lib/scripts/probe_r4_objective_level_liquidity_sweep_family.py`  
**R4 output:** `nb_lib/probe_results/objective_level_liquidity_sweep_reversal_family_r4_probe.json`

---

## Methodology Disclosure

This is a FINAL spec for **informational in-sample implementation and
12-start multistart**. It is not OOS-eligible by itself. The held-out
OOS window beginning 2026-02-01 remains sealed.

This spec exists because the strict PDH/PDL-only liquidity sweep probe
was sparse, while the broader objective-level family passed R4 frequency
without loosening sweep depth or volume confirmation. The implementation
must preserve level-family attribution all the way through trade records
and multistart reporting.

The key question is not only aggregate PF. The key question is:

```text
Does the liquidity-sweep/reclaim/volume mechanism show useful behavior
across objective level families, and which branch carries or drags it?
```

---

## 0. Scope And R4 Priors

The strategy trades MNQ RTH using 1-minute bars derived from the
1-second OHLCV store. It is two-sided and may trade multiple objective
level families, but only one open position at a time.

R4 result:

| Metric | Value |
|---|---:|
| Sample window | 2024-09-09 to 2024-10-04 |
| Trading days | 23 |
| Structural signals | 30 |
| Passing fill guards | 23 |
| Long / short | 15 / 15 |
| Distinct signal days | 14 |
| Sparsity class | moderate |
| Extrapolated passing signals / 60 days | 30-120 |

R4 per-family attribution:

| Level family | Structural signals | Passing fill guards |
|---|---:|---:|
| `PDH_PDL` | 5 | 3 |
| `OPENING_RANGE` | 7 | 4 |
| `ROUND_VWAP` | 18 | 16 |

Interpretation priors:

| Outcome | Prior | Meaning |
|---|---:|---|
| Aggregate no edge | 0.35 | Sweep/reclaim/volume still fails after brackets |
| Round/VWAP dominates and fails | 0.25 | Old round-number failure reappears in cleaner clothes |
| One branch registry-useful | 0.25 | Attribution reveals a marginal component |
| Strong informational edge | 0.10 | Aggregate PF >= 1.50 with account survival |
| Implementation flaw | 0.05 | Overlap or fill semantics make branch accounting unreliable |

---

## 1. Thesis

Obvious objective levels attract breakout orders and protective stops.
This strategy does not trade a first touch of support or resistance. It
waits for a bounded stop sweep, then requires a close back through the
level on expanded volume. The intended edge is trapped-liquidity
reversal: participants who chase the break or are forced out beyond the
level provide liquidity, and the reclaim/rejection shows the break did
not hold.

The family uses three objective level sources:

- `PDH_PDL`: prior completed RTH high and low.
- `OPENING_RANGE`: 09:30-09:45 ET range high and low.
- `ROUND_VWAP`: 25-point round handles close to RTH VWAP.

Counter-hypothesis: MNQ often sweeps and continues, especially around
round numbers. The volume spike may confirm continuation participation
rather than reversal exhaustion. That is why branch tags are mandatory.

---

## 2. Data And Time Semantics

```text
instrument: MNQ
session: RTH
source data: 1-second OHLCV
primary bars: 1-minute OHLCV, label=left, closed=left
tick_size: 0.25
point_value: $2.00 per point
```

A 1-minute bar labeled `10:15:00` covers `[10:15:00, 10:16:00)` and is
only tradable after `10:16:00`.

No predicate may inspect:

- the next 1-minute bar,
- later 1-second bars after the signal bar close,
- or data on/after the OOS boundary for in-sample runs.

All signal orders become eligible at:

```python
eligible_ts = signal_ts + 1 second
```

where `signal_ts` is the completed signal bar's right edge.

---

## 3. Indicators And Level Definitions

### Volume Context

```python
volume_ma20_prior = SMA(volume_1m, 20).shift(1)
volume_spike_ratio = current_volume / volume_ma20_prior
volume_confirmed = volume_spike_ratio >= 1.50
```

The `.shift(1)` convention is mandatory. The signal bar cannot
contribute to its own volume threshold.

### PDH/PDL

Prior-day levels are computed from the prior completed RTH session:

```python
PDH = max(prior_RTH.high)
PDL = min(prior_RTH.low)
```

The current day never contributes to these values.

### Opening Range

```text
OR window: 09:30:00-09:45:00 ET
ORH = max(high) over OR window
ORL = min(low) over OR window
```

Opening-range signals are allowed only after `09:45:00 ET`.

### RTH VWAP And Round Handles

RTH VWAP starts at `09:30:00 ET` and updates from completed 1-minute
bars:

```python
typical_price = (high + low + close) / 3
rth_vwap = cumulative_sum(typical_price * volume) / cumulative_sum(volume)
```

Round handles:

```text
round_grid = 25.0 points
ROUND_VWAP level qualifies only if abs(round_level - rth_vwap) <= 16.0 pts
```

---

## 4. Common Sweep Signal

Shared parameters:

```text
min_sweep_ticks = 2
max_sweep_ticks = 20
volume_spike_mult = 1.50
entry_timeout = 3 minutes
```

### Long Sweep Reclaim

For a support level `L`:

```python
sweep_depth = L - bar.low
2 ticks <= sweep_depth <= 20 ticks
bar.close > L
bar.close > bar.open OR close_location >= 0.60
volume_spike_ratio >= 1.50

entry_stop_price = bar.high + 1 tick
initial_stop_price = bar.low - 1 tick
```

### Short Sweep Rejection

For a resistance level `L`:

```python
sweep_depth = bar.high - L
2 ticks <= sweep_depth <= 20 ticks
bar.close < L
bar.close < bar.open OR close_location <= 0.40
volume_spike_ratio >= 1.50

entry_stop_price = bar.low - 1 tick
initial_stop_price = bar.high + 1 tick
```

`close_location`:

```python
close_location = (close - low) / (high - low)
```

If `high == low`, no signal may fire.

---

## 5. Branch Windows And Labels

Each generated signal must include:

```text
level_family
level_label
setup
direction
signal_ts
entry_stop_price
initial_stop_price
sweep_depth_ticks
volume_spike_ratio
```

### Branch A: `PDH_PDL`

Scan window:

```text
09:35:00-15:30:00 ET
```

Levels:

- `PDL`: support, long sweep reclaim.
- `PDH`: resistance, short sweep rejection.

Setup tags:

- `pdl_sweep_reclaim_long`
- `pdh_sweep_reject_short`

### Branch B: `OPENING_RANGE`

OR construction:

```text
09:30:00-09:45:00 ET
```

Scan window:

```text
09:45:00-12:00:00 ET
```

Levels:

- `ORL`: support, long sweep reclaim.
- `ORH`: resistance, short sweep rejection.

Setup tags:

- `orl_sweep_reclaim_long`
- `orh_sweep_reject_short`

### Branch C: `ROUND_VWAP`

Scan window:

```text
09:45:00-15:30:00 ET
```

Levels:

- 25-point round handles.
- The handle must be within 16 points of current RTH VWAP.

Setup tags:

- `rn_vwap_sweep_reclaim_long`
- `rn_vwap_sweep_reject_short`

The trade record must also include:

```text
round_level
rth_vwap_at_signal
round_vwap_dist_pts
```

for `ROUND_VWAP` signals.

---

## 6. Conflict And Overlap Rules

The implementation evaluates completed 1-minute bars chronologically.

Maximums:

```text
max_structural_signals_per_day = 6
max_realized_losses_per_day = 2
max_open_positions = 1
```

Per-day duplicate prevention:

```text
one accepted structural signal per level_family + level_label + direction
```

If multiple signals qualify on the same completed bar, choose one using
this precedence:

1. `PDH_PDL`
2. `OPENING_RANGE`
3. `ROUND_VWAP`

Within the same family and bar:

1. prefer the level with the larger sweep depth,
2. if tied, prefer the larger volume spike ratio,
3. if still tied, prefer the first deterministic sort key by
   `level_label`.

If a position is open, later signals are logged as skipped with
`skip_reason = position_open`; they are not traded.

No branch may be removed or direction-filtered inside this FINAL spec
after seeing results.

---

## 7. Entry Fill Model

Entry order:

```text
type: stop-market
side: signal direction
eligible: signal_ts + 1 second
expires: signal_ts + 3 minutes
```

Long fills when a 1-second bar has:

```python
second.high >= entry_stop_price
```

Short fills when:

```python
second.low <= entry_stop_price
```

The backtest fill price uses the existing nb_lib stop-entry execution
resolver with BAND_B friction. If the strategy implementation uses a
local resolver first, it must preserve the same semantics and document
the fill assumption in `trade_record.py`.

If the entry stop is not triggered within 3 minutes:

```text
exit_reason / skip_reason: entry_not_triggered
```

No trade record with P&L is created for non-filled structural signals,
but the multistart report must count them in structural attribution.

---

## 8. Risk, Sizing, And Guards

```text
risk_dollars = 300
point_value = 2.0
max_contracts = 12
stop_pts_min = 5.0
stop_pts_max = 35.0
daily_realized_loss_limit = 2
```

The stop band is chosen from R4 geometry: passing stop distances ranged
from 8.75 to 34.0 points, median 13.5. A wider stop band is not
pre-committed here because wide stops were a known Apex damage source in
earlier strategies.

Contracts:

```python
stop_pts = abs(entry_fill_price - initial_stop_price)
contracts = floor(risk_dollars / (stop_pts * point_value))
contracts = min(contracts, max_contracts)
skip if contracts < 1
```

Skip reasons:

- `stop_too_tight`
- `stop_too_wide`
- `contracts_lt_one`
- `daily_loss_limit_reached`
- `position_open`
- `entry_not_triggered`

---

## 9. Brackets And Management

No adaptive specialists are used in the first implementation.

Bracket:

```text
target = 2.0R
stop = initial_stop_price
max_hold = 30 minutes
EOD flat = 15:58:30 ET
```

No TP1/runner split in the baseline. The first test should answer
whether the sweep entry has any basic fixed-R behavior before adding
management complexity.

Exit priority inside a 1-second bar:

1. EOD / max-hold if timestamp condition is already true.
2. Stop / target same-second ambiguity uses adverse-first.
3. Otherwise first touched level fills.

Exit reasons:

- `fixed_2r_target`
- `initial_stop`
- `same_bar_adverse_stop`
- `max_hold_30m`
- `eod_flat`
- `compliance_flatten`

---

## 10. Compliance And Multistart Configuration

Compliance:

```text
account preset: Apex 50K EOD eval
friction: BAND_B
fresh account per multistart
```

In-sample multistart:

```text
starts: monthly 2024-08-01 through 2025-07-01
window length: 42 trading days per start
OOS boundary: 2026-02-01
```

Implementation must assert:

```python
max_loaded_timestamp < 2026-02-01 00:00:00 America/New_York
```

No OOS validation is authorized by this spec.

---

## 11. Required Trade Record Fields

In addition to standard nb_lib trade columns, every filled trade must
preserve:

```text
strategy_id
variant
signal_ts
level_family
level_label
setup
direction
entry_stop_price
initial_stop_price
sweep_depth_ticks
volume_spike_ratio
trigger_bar_high
trigger_bar_low
trigger_bar_close
close_location
rth_vwap_at_signal
round_vwap_dist_pts
structural_signal_rank_for_day
skip_reason
```

For non-`ROUND_VWAP` trades, `rth_vwap_at_signal` may still be populated
for diagnostics; `round_vwap_dist_pts` may be null.

The multistart report must include at minimum:

- aggregate PF/P&L/n,
- per-start table,
- Apex failure count,
- direction attribution,
- level-family attribution,
- level-family-by-direction attribution,
- setup attribution,
- exit-reason table,
- skip/non-fill structural signal counts,
- comparison against strict PDH/PDL R4 frequency,
- explicit comparison against prior `round_number_rejection_microfade`
  failure mode.

---

## 12. Pre-Committed Informational Criteria

This in-sample informational test cannot graduate directly to OOS.

| Verdict | Conditions |
|---|---|
| Frequency failure | Filled n < 80 across 12 starts |
| Informational rejected | PF < 1.05 and no branch PF >= 1.05 with positive P&L |
| Branch registry-useful | Any level family has PF [1.05, 1.50), positive P&L, adequate n, and no severe Apex-failure concentration |
| Aggregate marginal-positive | Aggregate PF [1.05, 1.50), positive P&L, n >= 80, failed starts <= 3 |
| Strong informational | Aggregate PF >= 1.50, n >= 80, failed starts <= 1 |

Branch evidence must not be used to silently delete losing branches
inside the same run. If a branch looks useful, it becomes a separate
future candidate or registry component.

---

## 13. Differentiation From Prior Failures

Compared with strict `pdh_pdl_liquidity_sweep_reversal`:

- This spec broadens objective levels because PDH/PDL alone was sparse.
- It does not loosen sweep depth or volume thresholds.

Compared with `round_number_rejection_microfade`:

- This is not a generic touch/rejection microfade.
- It requires a bounded sweep, reclaim/rejection close, 1.5x volume
  confirmation, VWAP proximity, and a stop-entry confirmation.
- The prior round-number loss-cluster risk remains a major warning and
  must be addressed in the report.

Compared with `opening_range_response_tree`:

- This uses a single sweep/reclaim/volume mechanism across level
  families, not three different opening-range response branches.
- It may take multiple level-family signals per day, but only one open
  position at a time.

---

## 14. HARD-HALT Conditions

- HARD-HALT-OOS-LEAK: any data loaded at or after 2026-02-01.
- HARD-HALT-ATTRIBUTION-LOSS: missing `level_family`, `level_label`, or
  `setup` in filled trade records.
- HARD-HALT-BRANCH-DELETION: removing a branch after seeing in-sample
  results.
- HARD-HALT-THRESHOLD-DRIFT: changing `volume_spike_mult`,
  `min_sweep_ticks`, `max_sweep_ticks`, round grid, VWAP distance, or
  stop band during implementation.
- HARD-HALT-ROUND-NUMBER-DRIFT: allowing round-number signals without
  VWAP confluence.
- HARD-HALT-GRADUATION: positive informational result cannot skip OOS
  methodology.

---

## 15. Implementation Checklist

1. Implement canonical alpha:
   `nb_lib/scripts/objective_level_liquidity_sweep_reversal_family_canonical_alpha.py`
2. Add any required fill assumption key to `trade_record.py`.
3. Preserve all branch tags in CSV output.
4. Add or update focused tests for:
   - volume SMA uses `shift(1)`,
   - same-bar branch precedence,
   - round/VWAP proximity gate,
   - stop-band skip,
   - trade record branch fields.
5. Run existing tests.
6. Run 12-start multistart:
   `nb_lib/scripts/objective_level_liquidity_sweep_reversal_family_multistart.py`
7. Generate informational report with required attribution tables.

---

## 16. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-25 | spec-drafted-final | FINAL informational spec drafted after R4 family probe passed frequency. Branch tags and per-level attribution are mandatory through implementation and multistart reporting. |
| 2026-05-25 | tested-informational-rejected | Implementation + 12-start multistart completed. Aggregate rejected: 233 trades, -$11,555.20, PF 0.75, 9/12 failed starts. Opening-range branch positive as registry-review lead; round/VWAP drove aggregate loss. |
