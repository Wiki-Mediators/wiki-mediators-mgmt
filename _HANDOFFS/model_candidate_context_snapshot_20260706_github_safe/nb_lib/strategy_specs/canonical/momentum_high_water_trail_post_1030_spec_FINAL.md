---
status: "tested-informational-rejected"
---

# Momentum High-Water Trail Past 10:30 — Canonical Strategy Specification (FINAL)

**Strategy ID**: `momentum_high_water_trail_post_1030`
**Status**: TESTED-INFORMATIONAL-REJECTED (multistart 2026-05-14; report at `C:/VMShare/NT8lab/nb_lib_mhw_multistart_informational_report.md`). Phase 0 BYPASS test complete; candidate closed.
**Created**: 2026-05-14
**Canonical path**: `nb_lib/strategy_specs/canonical/momentum_high_water_trail_post_1030_spec_FINAL.md`
**Candidate lineage**: `nb_lib/strategy_specs/candidates/momentum_high_water_trail_post_1030.md`
**Phase 0 verdict**: **INADMISSIBLE** (2026-05-14;
`C:/VMShare/NT8lab/nb_lib_phase0_momentum_high_water_trail_post_1030.md`)
**Bypass authorization**: Operator decision 2026-05-14 to bypass the
Phase 0 admissibility gate for informational testing purposes.

---

## METHODOLOGY DISCLOSURE — READ FIRST

**This is a BYPASS spec.** The candidate received an INADMISSIBLE
Phase 0 verdict on 2026-05-14. The operator chose to bypass the gate
and proceed to FINAL spec drafting + canonical implementation +
multistart testing. The methodology contract for the bypass is:

1. **The candidate cannot graduate** from this iteration regardless of
   test results. Edge candidate, weak, or rejected outcomes are all
   INFORMATIONAL.
2. **OOS slot is NOT consumable** for this candidate. The OOS window
   2026-02-01 → 2026-05-04 remains sealed and unavailable to this
   strategy regardless of in-sample outcome.
3. **Wiki body is NOT modified.** The wiki entry's body content
   remains as-authored. One status_history row records the bypass
   decision.
4. **All Section 8 wiki deferrals are RESOLVED in this spec.** No
   "required research" deferrals carry forward.
5. **If informational results are remarkable**, the proper path is a
   wiki revision iteration to address the R2 (Apex survival) + R4
   (signal-frequency) gaps, then a Phase 0 re-run. Only after Phase 0
   admission would OOS become available.

This disclosure exists so future readers (operator + future
Strategic Claude) can correctly weight this iteration's evidence.

---

## 0. Outcome Priors And Scope Acknowledgments

### 0.1 Priors (with Phase 0 evidence)

Pre-test priors for the multistart informational test:

| Outcome | Prior | Meaning |
|---|---:|---|
| No edge / Apex failure | 0.65 | Continuation class has 6 prior failures + Phase 0 R2 cluster-loss gap; account likely fails on most starts |
| Weak in-sample only | 0.20 | PF in [1.00, 1.50] on at least some starts; not OOS-eligible by bypass |
| Edge candidate (informational) | 0.10 | Multistart aggregate PF >= 1.50 with sufficient n; would NOT consume OOS due to bypass; could trigger wiki revision + Phase 0 re-run |
| Implementation blocker | 0.05 | High-water trail mechanics or per-start state reset surfaces issues |

These are methodology priors, not statistical estimates. The 0.65
base rate on "no edge / Apex failure" reflects:

1. **Continuation-class pattern** has 6 prior in-sample failures
   (variant_1, noise_brk, prj3, ema_trend, atr_regime parent +
   tight_target). All failed Apex eval.
2. **Phase 0 R2 cluster-loss gap** explicit in the wiki: $300 × 7 =
   $2,100 > $2,000 floor before commissions/slippage. The wiki self-
   flags this.
3. **10:30 fade is trader-art folklore.** Section 9 of the wiki
   explicitly disclaims peer-reviewed evidence.
4. **Multistart amplifies failure variance.** With 12 starts, even if
   the underlying edge has 0.10 probability of OOS-survival on a
   single start, the probability that ≥ 50% of starts survive is much
   lower.

### 0.2 Scope

This spec defines strategy behavior only. It consumes nb_lib v2.4
library primitives where useful. The candidate has 3 specialists =
**zero** (Section 4 below). The 10:30 transition is the lifecycle
mechanism; no v2.4 specialist set is added.

No new library work required. v2.4 primitives consumed for trail
updates (`apply_bracket_update`) and the at-10:30 transition
(`force_exit_strategy` for exit cases at the transition).

**This is INFORMATIONAL testing, not graduation.** Results do not
consume OOS. Strategy does NOT graduate from this iteration regardless
of result.

### 0.3 Structural difference from prior continuation strategies

| Axis | Prior continuation fleet | This candidate |
|---|---|---|
| Lifecycle | Static brackets (entry → fixed TP/stop → EOD) | Two-phase: pre-10:30 static, post-10:30 high-water trail |
| Risk transition | None | At-10:30 conditional transition (continue with trail OR exit) |
| Trail anchor | Fixed-MFE or no trail | High-water mark from entry → 10:30 |
| Apex survival mechanism | None explicit | Daily loss limit (2 losses → no more entries that day) |

The 10:30 conditional risk-transition is the structural differentiator.
Prior continuation strategies used static brackets that did not change
shape during the trade. This strategy explicitly defines a transition
point. Whether that transition produces edge is the test.

---

## 1. Strategy Thesis

Plain English, preserved from wiki Section 1 (locked, not revised):

If morning momentum has built enough favorable high-water mark by
10:30 ET, do NOT exit just because the clock says 10:30. Instead,
convert the trade from ordinary momentum management to a high-water-
anchored trail. For longs, the high-water mark is the best price
reached between entry and 10:30; for shorts, the low-water mark. The
post-10:30 stop is anchored to that favorable excursion so the trade
can continue with substantially reduced give-back risk.

Counter-hypothesis (also preserved from wiki): most morning moves
really do fade at or after 10:30, and a trailing mechanism may simply
turn a clean time-exit into a delayed stop-out. The strategy assumes
enough continuation cases exist to justify keeping the runner alive
after the fade window. That assumption is unproven and is what the
informational multistart tests.

Multistart framing: 12 monthly starts over 2024-08-01 to 2025-07-01,
each running to either Apex FAIL or a 2-month cap (whichever sooner).
Aggregation rules in Section 7.5 below.

---

## 2. Entry Signal And Timing

### 2.1 Market and session

- Market: MNQ continuous front-month futures.
- Data source: 1-second OHLCV store.
- Session: RTH only.
- Entry evaluation window: **09:35:00 through 10:20:00 US/Eastern**.
- **Half-days excluded** (entry skipped on half-day sessions). The
  10:30 transition exists on half-days, but the post-10:30 runner
  tail is too short for the trail to do meaningful work.
- Maximum: one long + one short per RTH day (deduplicated; per wiki
  Section 8 lock).

### 2.2 Derived bars

All derived bars are built from 1-second source bars.

- 1-minute bars: opening-range, breakout, volume ratio, high-water.
- 5-minute bars: ATR(20), trail offset.

At decision timestamp T, a derived bar is usable only if
`bar.left_edge + bar_duration <= T`. This right-edge rule is
mandatory for lookahead cleanliness.

### 2.3 Opening range reference

Define the 09:30–09:35 opening range from completed 1-minute bars:

```text
or_high = max(high of 1-min bars with left_edge in [09:30, 09:35))
or_low = min(low of 1-min bars with left_edge in [09:30, 09:35))
```

Both values become available at 09:35:00 (right-edge of the 09:34
bar).

### 2.4 Long momentum predicate

At signal timestamp T = right-edge of a completed 1-min bar B (with
09:35 ≤ T < 10:20):

1. `B.close > or_high` (closes above opening range high)
2. `B.close > session_vwap_at_T` (above session VWAP, anchored 09:30)
3. `B.volume >= 1.5 * mean(volume of prior 20 completed 1-min bars)`
4. ATR sanity guard: `atr_5m_20 in [4.0, 50.0]` points
5. Stop-distance band guard (Section 3.4 below)
6. Daily loss limit not breached (Section 3.4 below)
7. No long entry already taken today

### 2.5 Short momentum predicate

Symmetric:

1. `B.close < or_low`
2. `B.close < session_vwap_at_T`
3. `B.volume >= 1.5 * mean(volume of prior 20 completed 1-min bars)`
4. ATR sanity guard same as long
5. Stop-distance band guard
6. Daily loss limit not breached
7. No short entry already taken today

### 2.6 Direction handling

**Two-sided LOCKED.** Per wiki Section 8 direction symmetry
resolution: long and short morning momentum are treated as
symmetric mechanism candidates. The informed-prior justification:

- Opening-range breaks happen in both directions on MNQ.
- VWAP-side persistence at the time of breakout is a symmetric
  filter.
- Volume participation is direction-neutral.

If informational results show large direction P&L asymmetry, that is
a finding worth recording (per wiki Section 8 "direction symmetry"
deferred). Direction asymmetry is NOT a graduation gate for this
informational test; it is a recorded observation.

### 2.7 Entry fill semantics

```text
signal_ts = right edge of completed 1-minute bar B
entry_ts = first 1-second bar strictly after signal_ts
entry_price = entry bar open + BAND_B entry slippage (direction-signed)
```

Assertions:

```python
assert entry_ts > signal_ts
assert 09:35 <= signal_ts.time() < 10:20
assert entry_ts.date() == signal_ts.date()
```

If no eligible 1-second bar exists after the signal timestamp within
RTH, skip the trade.

---

## 3. Risk And Position Sizing

### 3.1 Fixed-dollar risk

```text
risk_dollars = 300
point_value = 2.00 USD per MNQ point per contract
```

Preserved verbatim from wiki Section 5.

### 3.2 Initial stop placement

The initial stop is the OPPOSITE side of the opening range with a
buffer:

For LONG (entered above `or_high`):

```text
initial_stop = or_low - 0.50  (2 ticks below OR low)
```

For SHORT (entered below `or_low`):

```text
initial_stop = or_high + 0.50  (2 ticks above OR high)
```

The wiki Section 4 mentioned an alternative ("1.25 × ATR(20) from
entry") — this FINAL spec resolves the deferral by picking the
**OR-anchored stop** (cleaner structural anchor; mechanically derived
from the same opening-range that produced the signal).

### 3.3 Position size formula and bounds

```text
stop_pts = abs(entry_price - initial_stop)
raw_contracts = floor(risk_dollars / (stop_pts * point_value))
contracts = clamp(raw_contracts, min=1, max=12)
```

The contract cap is **12**, tighter than the wiki's 15. Rationale:
Phase 0 R2 cluster-loss gap. With 12-contract cap and $300 risk, the
per-trade dollar loss is capped at $300 (assuming stop fills at stop
price; BAND_B stop_overshoot adds modest adverse slippage).

### 3.4 Skip / guard conditions

Skip if any:

- `stop_pts < 5.0` (too tight for BAND_B friction + MNQ opening noise)
- `stop_pts > 35.0` (too wide for Apex 50K survival)
- `contracts < 1`
- `atr_5m_20 <= 0` or NaN or outside `[4.0, 50.0]`
- Compliance state not ACTIVE (post-FAIL guard)
- **Daily loss limit reached** (Section 3.5)

### 3.5 Daily loss limit (cluster-loss mitigation; addresses Phase 0 R2)

**Per-day maximum 2 losses.** After the second losing trade on a
calendar trading day, **no further entries (long or short)** are
opened that day. A "loss" is defined as any closed trade with net
total P&L < 0 after BAND_B friction.

Rationale for the limit:

- Wiki self-flag: 7 × $300 = $2,100 > $2K floor. A 2-loss daily cap
  bounds same-session cluster losses to ~$600 worst case.
- Multi-day cluster losses are still possible (2 losses today + 2
  tomorrow = $1,200 over 2 days; 4 days = $2,400 → could breach
  floor). But the rule constrains intra-day stop sequences which were
  the failure mode for several prior strategies (round-number's 11
  consecutive losers in 5 days, atr_regime tight_target's 6 straight
  in 8 days).
- The rule does NOT eliminate the floor risk; it bounds intra-day
  damage. The informational test will reveal whether the bound is
  sufficient.

### 3.6 Apex compliance

Use `ComplianceTracker` with `apex_50k_eod_eval` (Rithmic variant)
preset per project convention. Strategy must stop opening new trades
after `tracker.state == AccountState.FAILED`.

For multistart: **each start gets a fresh `ComplianceTracker`
instance** (Section 8.5 below).

---

## 4. Adaptive Layers

**This strategy uses ZERO v2.4 specialists.** No
`time_to_resolution_manager`, no `volatility_shock_manager`, no
`structure_trail_manager`, no composer call.

Rationale per wiki Section 4 and methodology Section 9 ("If
management is not used, the candidate must say so plainly. Do not
attach v2.4 management as a decorative layer"):

- The 10:30 high-water transition IS the lifecycle mechanism. It is
  a deterministic, time-anchored, single-event transition rule, not
  an ongoing parallel-composer regime.
- Adding v2.4 specialists would create the round-number BE-arm
  failure mode: a structure_trail proposing swing-based stops
  post-10:30 could conflict with the high-water trail's tightening.
- The high-water trail itself uses `apply_bracket_update` for
  validation and the strict tighten-only invariant. That is library
  consumption, not a specialist.

### 4.1 Layer A: Entry-side filters

Section 2 predicates (OR break, VWAP-side, volume, ATR sanity) act
as the entry regime filter. No further entry-side adaptive layers.

### 4.2 Layer B: 10:30 conditional transition

The single most distinctive lifecycle mechanism. Specified in
Section 5 below. This is **not** a specialist — it fires once per
trade at a deterministic time.

### 4.3 No parallel specialist composer

`compose_proposals` from `nb_lib.scripts.round_number_rejection_microfade_canonical_alpha`
is NOT consumed by this strategy. The high-water trail is computed
deterministically and applied directly via `apply_bracket_update`.

---

## 5. Bracket Geometry

### 5.1 Initial brackets (pre-10:30)

At entry, set:

```text
stop_price = initial_stop  (per Section 3.2)
tp1_price = entry_price + direction * 1.0 * raw_stop_pts  (informational TP1 at +1R)
tp2_price = sentinel far value (not used; high-water trail replaces it)
be_arm_pts = sentinel large value (no BE arm pre-10:30)
```

The lifecycle API expects tp1_pts/tp2_pts/be_arm_pts at construction.
We use:
- `tp1_pts = 1.0 * raw_stop_pts` (real informational TP1 at +1R)
- `tp2_pts = 100.0` (sentinel; never reached before the 10:30
  transition overrides it)
- `be_arm_pts = 100.0` (sentinel; never reached; no BE arm pre-10:30)

### 5.2 TP1 fill mechanics

TP1 closes 50% of contracts at +1R. The remaining 50% becomes the
runner that survives to the 10:30 transition (if pre-10:30) or
continues with the post-10:30 high-water trail.

If `contracts == 1`, no partial; the single contract runs as the
full runner.

### 5.3 Pre-10:30 BE arm

**No BE arm pre-10:30.** The wiki offered two alternatives ("BE not
before +1.0R or TP1" OR "no BE arm before 10:30"). This FINAL spec
locks the no-BE-pre-10:30 choice for two reasons:

1. **Round-number failure mode**: an early BE arm at +1R or at TP1
   would put the stop at entry + small offset. The post-10:30
   high-water trail might propose a stop BELOW that BE-armed level
   (especially on a trade with high-water mark significantly above
   entry, then pullback toward entry near 10:30). Strict tighten-only
   would reject the trail proposal as widening — the same failure
   mode that made round-number's `structure_trail_manager`
   design-dead.
2. **Mechanism clarity**: the 10:30 transition is the decision point.
   Before 10:30, the trade either holds opening-range structure or
   stops out at the OR opposite side. There's no need for a BE arm
   to do work the structural stop already does.

If a future iteration revises this choice, it must address how the
BE timing interacts with the post-10:30 trail.

### 5.4 At-10:30 transition logic

**Transition timestamp**: **10:30:00 ET**, evaluated after the
completed 1-minute bar ending at 10:30 is available (i.e., processed
at the 1-second bar with `bar_ts >= 10:30:00`).

#### 5.4.1 Compute high-water / low-water

For LONG:

```text
high_water = max(high over all 1-min bars from entry_ts through 10:30
                 inclusive, computed lookahead-clean)
```

For SHORT:

```text
low_water = min(low over same window)
```

Implementation: tracked incrementally during the trade. Each completed
1-min bar between entry and 10:30 updates the high/low water.

#### 5.4.2 "Meaningfully favorable" check

For LONG:

```text
favorable_excursion_pts = high_water - entry_price
meaningfully_favorable = (favorable_excursion_pts >= 0.75 * raw_stop_pts)
```

For SHORT:

```text
favorable_excursion_pts = entry_price - low_water
meaningfully_favorable = (favorable_excursion_pts >= 0.75 * raw_stop_pts)
```

The 0.75R threshold is from wiki Section 4 ("at least +0.75R by
10:30"). It is an informed prior.

#### 5.4.3 Transition actions

**If `meaningfully_favorable == False`** (trade hasn't built enough
favorable excursion by 10:30):

- Force-exit at the next 1-second bar's open via
  `lifecycle.force_exit_strategy(ts=10:30:00, exit_reason="rnrm_no_high_water_at_10_30")`.

Wait — that's the round-number reason. Use:
- `exit_reason = "mhw_no_high_water_at_10_30"`

**If `meaningfully_favorable == True`** (trade has built ≥ 0.75R by
10:30):

- Compute trail offset (Section 5.5).
- Propose new stop = `transition_anchor + direction * (-trail_offset)`:
  - Long: `high_water - trail_offset`
  - Short: `low_water + trail_offset`
- If proposed stop ≥ current_price for long (i.e., already crossed):
  exit at next 1-sec bar open via `force_exit_strategy` with reason
  `"mhw_trail_already_crossed"`.
- Otherwise: apply via `lifecycle.apply_bracket_update(...)` with the
  new stop. TP1 fill state and TP2 sentinel preserved.

### 5.5 Post-10:30 trail mechanic (locked: ATR high-water)

**Trail mechanism**: ATR high-water with floor (locked; not
swing-based — that's deferred to a future spec).

```text
trail_offset = max(0.75 * atr_5m_20, 6.0)
```

The 6.0-point floor prevents the trail from collapsing to noise on
low-vol days. ATR-based scaling preserves vol-adaptiveness on
elevated-vol days.

Update cadence: once per completed 1-minute bar after 10:30.

Update rule (long):

```text
if current_high > running_high_water:
    running_high_water = current_high
new_stop = running_high_water - trail_offset
if new_stop > current_stop:
    propose stop update via apply_bracket_update
```

Short: symmetric.

**Strict tighten-only.** The strategy never proposes a wider stop.
HARD-HALT-WIDENING fires if a code path does so.

### 5.6 Strict tighten-only invariant

Per project standard (matching `round_number_rejection_microfade`
and `needle_drop_v2` for stops):

- Long stop: any proposed update must be `> current_stop` AND
  `< current_price`.
- Short stop: `< current_stop` AND `> current_price`.

Library composer's tighten-only check enforces this in
`apply_bracket_update`. Strategy code does not bypass it.

### 5.7 Strategy force-exit conditions

Three force-exit paths via `force_exit_strategy`:

1. **`mhw_no_high_water_at_10_30`** — at 10:30 when meaningfully-
   favorable check fails. Closes full position (or runner if TP1
   fired).
2. **`mhw_trail_already_crossed`** — at 10:30 when the proposed
   trail stop is already below/above current price.
3. **`mhw_eod_buffer`** — at 15:58:30 EOD-flat compliance deadline
   (handled by lifecycle's standard EOD-compliance path, not by
   strategy force-exit explicitly).

No time-based force exits beyond these. The wiki's optional
"after 14:30 if no advance" rule is NOT implemented — that was a
deferred item the wiki itself acknowledged.

---

## 6. Indicators, Data, And Library API

### 6.1 Required indicators

| Field | Source | Rule |
|---|---|---|
| `or_high`, `or_low` | 1-min bars 09:30-09:35 | completed bars only |
| `session_vwap` | 1-min RTH bars | session-anchored 09:30 ET |
| `volume_mean_20` | 1-min bars | trailing 20 completed 1-min bars |
| `atr_5m_20` | 5-min bars | Wilder ATR(20), completed bars |
| `high_water` / `low_water` | 1-min bars | running max/min from entry to 10:30 (lookahead-clean) |

No ATRPercentile, no ATRRatio, no ChoppinessIndex, no swing detector.
Lean predicate stack by design.

### 6.2 Data source

MNQ 1-second OHLCV from project Databento store. Derive 1-min / 5-min
bars via project conventions.

### 6.3 Library API consumed (v2.4)

```python
# At 10:30 transition (Section 5.4):
result = lifecycle.apply_bracket_update(
    ts=transition_ts,
    stop_price=new_stop,
    reason="mhw_10_30_transition",
    metadata={...},
)

# Force-exit paths (Section 5.7):
result = lifecycle.force_exit_strategy(
    ts=ts,
    exit_reason="mhw_no_high_water_at_10_30",
    metadata={...},
)

# Post-10:30 trail (Section 5.5):
result = lifecycle.apply_bracket_update(
    ts=bar_ts,
    stop_price=new_stop_from_trail,
    reason="mhw_high_water_trail",
)
```

No specialist composer. No event-log proposal/accepted/rejected
distinguishing (the strategy has no specialists to attribute).

### 6.4 FILL_ASSUMPTIONS extension

```text
FILL_ASSUMPTIONS["momentum_high_water_trail_post_1030"] = BAND_B
```

This is a 1-line additive change to `nb_lib/trade_record.py`'s
`FILL_ASSUMPTIONS` set, done by the implementation iteration.

---

## 7. Pre-Committed Pass Criteria (INFORMATIONAL — NOT GRADUATION)

### 7.1 Edge thresholds (informational only)

**These thresholds DO NOT trigger graduation. They are informational
labels.**

| Outcome label | Criteria |
|---|---|
| Informational edge candidate | Aggregate PF ≥ 1.50 AND n_aggregate ≥ 150 AND ≥ 50% of starts survive to end-of-window |
| Informational weak | 1.00 ≤ PF < 1.50 OR n < 150 with positive P&L |
| Informational rejected | PF < 1.00 OR < 25% of starts survive |

### 7.2 Trade count minimum

`n_aggregate >= 150` across all 12 starts combined. With ~5-15 trades
per start expected and 12 starts, this is reachable if the strategy
fires meaningfully.

### 7.3 Specialist attribution

**Not applicable.** This strategy has zero specialists. Attribution
requirements in the spec's Phase 0 / round-number lineage do not
apply.

### 7.4 Direction asymmetry tolerance

Recorded but not gated for this informational test. If
`abs(long_pnl - short_pnl) / abs(total_pnl) > 0.65`, the report flags
the asymmetry but does NOT mark the strategy as failed solely on
asymmetry.

### 7.5 OOS trigger conditions

**NOT APPLICABLE — Phase 0 bypass disqualifies OOS consumption
regardless of in-sample result.**

This is the methodology integrity point. Even if the informational
multistart produces remarkable results, the OOS slot for this
candidate remains sealed. The proper path post-informational-test:

- If results are remarkable: operator considers a wiki revision
  iteration addressing R2 (Apex survival) + R4 (signal-frequency)
  gaps, then re-runs Phase 0. If Phase 0 then admits the candidate,
  Phase 1 preflight runs. Only after Phase 1 passes does the operator
  decide on OOS.
- If results are unremarkable: candidate stays closed; no further
  iteration on this design.

### 7.6 Halt and review conditions during implementation

Implementation must halt and consult the operator if:

- Spec constants cannot be pinned exactly in tests.
- Mid-trade update API requires a public signature change outside
  v2.4 (should not happen).
- Per-start state contamination is detected (e.g., balance carry-over
  between starts).
- Multistart aggregation produces self-contradictory metrics.
- Implementation discovers the 10:30 transition fires < 5% of
  intended trades (mechanism would be design-dead at that rate).

### 7.7 Multistart aggregation (Section 7.5 of plan; addresses Phase 0 R4)

**12 monthly starts** spanning 2024-08-01 through 2025-07-01:

| # | Start month | Cap (2 months from start) |
|---:|---|---|
| 1 | 2024-08-01 | 2024-10-01 |
| 2 | 2024-09-01 | 2024-11-01 |
| 3 | 2024-10-01 | 2024-12-01 |
| 4 | 2024-11-01 | 2025-01-01 |
| 5 | 2024-12-01 | 2025-02-01 |
| 6 | 2025-01-01 | 2025-03-01 |
| 7 | 2025-02-01 | 2025-04-01 |
| 8 | 2025-03-01 | 2025-05-01 |
| 9 | 2025-04-01 | 2025-06-01 |
| 10 | 2025-05-01 | 2025-07-01 |
| 11 | 2025-06-01 | 2025-08-01 |
| 12 | 2025-07-01 | 2025-09-01 |

Each start: fresh $50K Apex eval account, fresh `ComplianceTracker`,
run until either FAIL or 2-month cap reached.

**Expected signal-count range per start** (addresses Phase 0 R4):

- ~22 trading days per month × 2 months = ~44 days per start.
- Entry window 09:35-10:20 ET (45 min) with deduplication (1
  long + 1 short max per day).
- After predicate filtering (OR break + VWAP side + 1.5× volume +
  ATR sanity): expect ~10-25% of days fire any signal.
- Per start estimate: **5-15 trades**.
- Aggregate across 12 starts: **60-180 trades total** (before daily-
  loss-limit filtering).

This is the chop-fade-style "what too-sparse looks like" comparison:
chop-fade produced 8/11/19 over 469 days — much sparser than this
strategy's expected per-start rate. And "what too-broad looks like":
round-number produced 1,465 over 469 days — much denser. This
strategy's expected aggregate of 60-180 sits comfortably between
those failure modes.

**Aggregation rules**:

- **Per-start survival**: account NOT in FAILED state at end of
  2-month cap.
- **Aggregate PF**: sum(gross_wins across all starts) /
  sum(gross_losses across all starts).
- **Survival rate**: (count of surviving starts) / 12.
- **≥ 50% survival** (≥ 6 of 12) is the informational threshold for
  "edge candidate (informational)" label.
- **< 25% survival** (< 3 of 12) is the informational threshold for
  "informational rejected" label.

---

## 8. Mechanics

### 8.1 Evaluation cadence

- Entry predicates: once per completed 1-minute bar in 09:35-10:20 ET
  entry window.
- 10:30 transition: at the first 1-second bar with `bar_ts >=
  10:30:00` on each day a trade is open at that moment.
- Post-10:30 trail update: once per completed 1-minute bar after
  10:30 while position is open.

### 8.2 Time exits

| Trigger | Action |
|---|---|
| 10:30 + not meaningfully favorable | force_exit_strategy with reason `mhw_no_high_water_at_10_30` |
| 10:30 + trail stop already crossed | force_exit_strategy with reason `mhw_trail_already_crossed` |
| 15:58:30 EOD-flat compliance | standard lifecycle EOD-compliance exit (`eod_compliance`) |
| Daily loss limit reached | no new entries (Section 3.5); does not exit open trade |

No optional late-afternoon stagnation exit (deferred wiki item; not
implemented in this FINAL spec).

### 8.3 EOD flat

Standard compliance EOD-flat at 15:58:30 ET on regular days
(90-second buffer before close). Half-days excluded per Section 2.1.

### 8.4 Cooldowns and per-day limits

- **Max 1 long + 1 short per day** (deduplication).
- **Max 2 losses per day** (daily loss limit, Section 3.5).
- No 45-minute cooldown like round-number; the entry window is only
  45 minutes wide so the per-direction limit is sufficient.

### 8.5 Multistart-specific

- Each of the 12 starts gets a fresh `ComplianceTracker` instance,
  fresh `ExecutionLogger`, and fresh per-day-state tracking.
- No state carries between starts. Per-start trades are written to
  per-start CSVs; aggregation happens at report-time, not at
  per-start runtime.
- Indicator warmup: each start uses the in-sample data preceding its
  start_date for warmup (matches the established pattern from
  `atr_regime_multistart_runner.py`).

### 8.6 Runtime assertions

At minimum, in production code path:

```python
assert signal_ts.date() == entry_ts.date()
assert 09:35 <= signal_ts.time() < 10:20
assert atr_5m_20 > 0 and 4.0 <= atr_5m_20 <= 50.0
assert 5.0 <= stop_pts <= 35.0
assert 1 <= contracts <= 12
assert direction in (-1, +1)
assert compliance_state.name != "FAILED" at entry time
```

At-10:30 transition:

```python
assert favorable_excursion_pts >= 0  # high_water is post-entry
assert (favorable_excursion_pts >= 0.75 * raw_stop_pts) == meaningfully_favorable
assert new_stop is None or (direction > 0 and new_stop > current_stop) \
                       or (direction < 0 and new_stop < current_stop)
```

Post-10:30 trail update:

```python
assert running_high_water >= current_high_at_update OR new bar set it
assert direction > 0 and proposed_stop > current_stop OR direction < 0 and proposed_stop < current_stop
```

Any assertion failure is HARD-HALT, not silent skip.

---

## 9. HARD-HALT Conditions

Implementation or test must halt on:

1. **HARD-HALT-OOS-LEAK**: any data row with timestamp >= 2026-02-01
   loaded for in-sample multistart.
2. **HARD-HALT-LOOKAHEAD**: any predicate uses a derived bar with
   right-edge > decision_ts.
3. **HARD-HALT-WIDENING**: a code path produces a bracket update
   that widens any field (strict tighten-only).
4. **HARD-HALT-WRONG-START-DATE**: a multistart run uses an
   incorrect start_date (e.g., 2024-08-15 instead of 2024-08-01).
5. **HARD-HALT-MULTISTART-CONTAMINATION**: state (balance, peak,
   per-day counters, indicators) leaks between starts.
6. **HARD-HALT-PHASE-0-BYPASS-FORGOTTEN**: the results report MUST
   state "informational testing, not graduation." If the report is
   silent on the bypass, halt and revise the report.
7. **HARD-HALT-SPEC-DRIFT**: implementation constants differ from
   this FINAL spec without spec revision.
8. **HARD-HALT-REGRESSION**: existing nb_lib tests fail after
   implementation.
9. **HARD-HALT-ACCOUNT-FAILED-CONTINUE**: outer loop opens a new
   trade after `AccountState.FAILED` within a start.
10. **HARD-HALT-WIKI-BODY-MODIFIED**: wiki body content changed
    (only status_history append is permitted per bypass contract).

---

## 10. Open Questions Deferred

All wiki Section 8 deferred items are RESOLVED in this FINAL spec
(per prompt constraint). Specifically:

| Wiki Section 8 item | Resolution |
|---|---|
| 10:30 behavior diagnostic | Not run; informational multistart will reveal in aggregate |
| Apex survival thesis | Daily loss limit (Section 3.5); 2-loss intra-day cap; cluster-loss vulnerability acknowledged |
| Signal-frequency expectation | Section 7.7: 60-180 aggregate (5-15 per start × 12 starts) |
| Direction symmetry | Section 2.6: two-sided locked; asymmetry recorded not gated |
| Management lifecycle | Section 4: zero specialists; 10:30 transition IS the lifecycle |
| Trail choice | Section 5.5: ATR high-water locked |
| Half-day handling | Section 2.1: half-days excluded |
| Initial stop placement | Section 3.2: OR-anchored (not ATR-anchored) |

**No remaining deferrals** in this FINAL spec. Any new spec revision
would require a separate iteration with operator sign-off.

---

## 11. Wiki References And Informed-Prior Status

| Reference | Status | Usage |
|---|---|---|
| `momentum_high_water_trail_post_1030.md` | untested-ideation (Phase 0 inadmissible) | Wiki body NOT modified; this FINAL spec consumes it as ideation source |
| `nb_lib_phase0_momentum_high_water_trail_post_1030.md` | (Phase 0 report) | R2 and R4 gaps directly informed the FINAL spec's Section 3.5 (daily loss limit) and Section 7.7 (signal-frequency expectation) |
| `nb_lib_v2_4_management_infrastructure_report.md` | (v2.4 library) | `apply_bracket_update` + `force_exit_strategy` consumed |
| `vwap_stretch_snapback_spec_FINAL.md` | tested-rejected | 16-section format reference; BAND_B; T+1s entry pattern |
| `round_number_rejection_microfade_spec_FINAL.md` | tested-rejected | 16-section format reference; tighten-only invariant pattern |
| `nb_lib_forward_iteration_plan_post_8fleet.md` | (methodology) | Admissibility rules informed Section 7 pass criteria framing |

**Wiki body NOT modified.** The wiki entry's body content remains
as-authored. Only the status_history table gets one additional row
(noting this bypass FINAL spec was drafted).

---

## 12. FILL_ASSUMPTIONS Extension

Momentum High-Water Trail Past 10:30 inherits BAND_B friction:

- Entry slippage per existing primitive convention (0.5 pt).
- Stop overshoot per BAND_B (1.16 pt).
- TP slippage 0.0 per BAND_B.
- Commission $0.35 per side per contract.

**Bracket update latency** (per v2.4 + project convention):

```text
Bracket update latency: effective at the first 1-second bar strictly
after the management evaluation timestamp.
```

If price crosses the OLD bracket before the update-effective bar, the
old bracket wins. If price crosses the NEW bracket only after the
update is effective, the new bracket applies.

Strategy force exits (`mhw_*`) use TP-class friction (no adverse
overshoot). Commission still applies.

---

## 13. OOS Reservation And Validation Triggers

### 13.1 Reserved window

```text
2026-02-01 through 2026-05-04
```

In-sample script must assert before any results computation:

```python
assert WINDOW_END < pd.Timestamp("2026-02-01", tz="America/New_York")
```

### 13.2 OOS eligibility: NOT ELIGIBLE

**This candidate is NOT eligible for OOS validation due to Phase 0
bypass.** Even if the informational multistart produces remarkable
results (PF >= 1.50, ≥ 50% start survival, etc.), the OOS slot
remains sealed for this candidate.

To become OOS-eligible, this candidate would need:

1. A wiki revision iteration addressing R2 (Apex survival) and R4
   (signal-frequency) gaps from the Phase 0 report.
2. A Phase 0 re-run with the revised wiki, producing an ADMISSIBLE
   verdict.
3. A Phase 1 preflight passing.
4. A non-bypass FINAL spec drafting iteration with the admissible
   wiki as input.
5. Implementation + in-sample test passing per spec Section 7
   criteria.

Only after all of the above would OOS become available.

### 13.3 If informational test produces remarkable results

The operator may consider:

- A wiki revision iteration (Phase 0 R2 + R4 gap closure)
- A second Phase 0 evaluation against the revised wiki
- Documented re-entry into the methodology pipeline

The informational test result alone does NOT bypass any subsequent
gate. The bypass authorization is for THIS iteration only.

---

## 14. Test Plan

### 14.1 Library tests

449/449 nb_lib tests must still pass after the implementation
iteration commits any additive changes. No library modifications
are expected; v2.4 primitives are sufficient.

### 14.2 Strategy constant pinning tests

The implementation iteration must add tests pinning every locked
value in this spec:

- Time gates (09:35, 10:20, 10:30, 15:58:30)
- Entry predicates (OR breakout side, VWAP side, 1.5× volume, ATR
  sanity range [4.0, 50.0])
- Stop placement (OR-anchored with 0.50-pt buffer)
- Risk dollars ($300), contract cap (12), stop-distance band
  ([5.0, 35.0])
- Daily loss limit (2)
- TP1 (+1.0R, 50% close)
- Meaningful favorable threshold (0.75R)
- Trail offset (max of 0.75× ATR(20) and 6.0)
- High-water tracking lookahead-clean
- 12 multistart start dates and 2-month caps

### 14.3 Synthetic strategy behavior tests

- Long entry fires on valid OR breakout + VWAP-above + 1.5× volume
- Short entry symmetric
- Entry skipped outside 09:35-10:20 window
- Entry skipped on half-days
- Entry skipped when stop_pts < 5 or > 35
- Daily loss limit blocks 3rd trade after 2 losses on same day
- TP1 fires at +1R on 50% of contracts
- No BE arm pre-10:30 (BE never arms during pre-10:30 evaluation)
- 10:30 transition + meaningfully_favorable=False → force_exit
- 10:30 transition + meaningfully_favorable=True → apply trail stop
- Post-10:30 trail tightens stop on new high-water
- Post-10:30 trail rejects widening proposals
- 12 multistart starts each get fresh tracker (state isolation
  test)

### 14.4 Multistart configuration

Per Section 7.7 above.

---

## 15. Selection Bias Notes

**EXPLICIT bypass acknowledgment.**

This FINAL spec exists because the operator authorized a Phase 0
bypass on 2026-05-14. The methodology trail records:

1. **Candidate failed Phase 0 admissibility 2026-05-14.** R2 (Apex
   survival) and R4 (signal-frequency) were NOT MET. R1, R3, R5
   were PARTIALLY MET. Report:
   `C:/VMShare/NT8lab/nb_lib_phase0_momentum_high_water_trail_post_1030.md`.

2. **Operator chose to bypass the gate** for informational testing.
   The bypass was a deliberate methodology choice — not an oversight,
   not a procedural error. The bypass authorization is recorded in
   the wiki status_history (one row) and in this spec's Status
   prefix.

3. **Multistart was chosen partly to diversify single-start
   variance.** Prior single-start tests (vwap_stretch_snapback,
   round_number_rejection_microfade) failed in their starting
   window. Multistart over 12 monthly starts provides at least 12
   data points on the strategy's start-date sensitivity. This is a
   defensible methodology choice, but it does not change the
   bypass-status of the iteration.

4. **Results, if positive, do NOT graduate the candidate.** Section
   7.5 + 13.2 explicitly disqualify OOS consumption. If the
   informational results are remarkable, the proper path is the
   wiki-revision + Phase 0 re-run path documented in Section 13.3.

5. **R2 gap addressed via Section 3.5** (daily loss limit). R4 gap
   addressed via Section 7.7 (mechanism-derived expected count).
   These specific Phase 0 gaps were not literally papered over —
   they have spec-level resolutions. But the bypass remains because
   Phase 0 admissibility happens BEFORE FINAL spec drafting in the
   methodology pipeline, not during it. Section 3.5 and 7.7 are
   informed-prior resolutions; they have not been independently
   evaluated against the admissibility rules.

The bypass is a one-time exception, not a precedent. Future
candidates that receive INADMISSIBLE Phase 0 verdicts should follow
the standard wiki-revision + Phase 0 re-run path.

---

## 16. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-14 | spec-drafted-final-bypass | FINAL spec drafted as informational testing of Phase 0-inadmissible candidate. All wiki Section 8 deferred items resolved. Multistart configuration: 12 monthly starts (Aug 2024 - Jul 2025), each capped at 2 months. R2 gap addressed via daily loss limit (Section 3.5); R4 gap addressed via mechanism-derived expected signal-count range (Section 7.7). Results will NOT consume OOS (Section 7.5, 13.2). Strategy does NOT graduate from this iteration regardless of multistart outcome (Section 15). 16-section spec, ~990 lines. |

End of specification.
