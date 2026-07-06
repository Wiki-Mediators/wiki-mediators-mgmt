---
status: "tested-apex-failure"
---

# Opening Range Width Switch — Canonical Strategy Specification (FINAL)

**Strategy ID**: `opening_range_width_switch`
**Status**: TESTED-APEX-FAILURE (in-sample 2026-05-17; account FAILED 2024-12-04 via compliance_drawdown; does not graduate to OOS)
**Created**: 2026-05-17
**Canonical path**: `nb_lib/strategy_specs/canonical/opening_range_width_switch_spec_FINAL.md`
**Candidate lineage**: `nb_lib/strategy_specs/candidates/opening_range_width_switch.md`
**Phase 0 v2 verdict**: **ADMISSIBLE FOR PHASE 1** (2026-05-17, post-R1 resolution)
**Phase 1 preflight verdict**: **PASSED** (2026-05-17)
**R4 probe convention**: v1.2

---

## 0. Outcome Priors And Scope Acknowledgments

This is the **second candidate** to reach FINAL spec drafting under the
methodology-clean pipeline, and the **first under the complete v1.2
pipeline** (template v2 + R4 probe v1.2 + Phase 1 preflight + Phase 0
review). Unlike the momentum_high_water_trail informational bypass
test, this candidate is **OOS-ELIGIBLE if the Section 7 pass criteria
are met**. There is no bypass framing.

The candidate also represents the first ADMISSIBLE verdict where R1
is supported by **candidate-specific MNQ empirical data** (79.5%
failed-break reversion rate) rather than literature citation alone.
The Phase 1 preflight confirmed the v1.2 probe extrapolation at full-
window scale (probe predicted 22-89/60d; actual 34.5/60d; attrition
5.6% probe vs 3.96% preflight).

**Honest pre-test priors:**

| Outcome | Probability |
|---|---|
| No edge / Apex failure | ~0.30 |
| Weak in-sample only (PF 1.0-1.5) | ~0.30 |
| OOS-eligible edge | ~0.30 |
| Implementation blocker | ~0.10 |

The 0.30 OOS-edge prior is the highest in the project — higher than
prior_day_value_area_rejection's 0.25 — because:
- The methodology pipeline is now end-to-end validated.
- R1 evidence is direct MNQ measurement, not literature folklore.
- Trade count (~225-240 expected post stop-floor guard) provides
  robust statistical foundation.
- Direction balance is well-centered at preflight (52.4% L).

It is not 0.50: the 10-fleet failure pattern includes prior_day_VA
which had similarly clean methodology and still failed in-sample on
PF (1.17 < 1.50). Methodology cleanliness is necessary, not sufficient.

If this strategy fails in-sample, the issue is **strategy mechanics**.
The methodology pipeline did its job.

### 0.1 Bucket accounting

- In-sample: first canonical alpha test for this strategy.
- OOS reserved: 2026-02-01 → 2026-05-04. **DO NOT load.**
- OOS eligibility: ON; consumable if Section 7 pass criteria met.

### 0.2 Selection-bias acknowledgment

This candidate was selected for FINAL spec drafting after:
1. Phase 0 v2 under v1.2: CONDITIONALLY ADMISSIBLE (R1 partial — mode
   switch design defect).
2. R1 resolution: wiki reframed to rejection-only + MNQ diagnostic
   (79.5% reversion).
3. Phase 0 v2 re-evaluation: ADMISSIBLE.
4. Phase 1 preflight: PASSED (34.5/60d, within probe range).

The reframing from dual-mode to rejection-only was empirically
forced by the v1.2 probe (acceptance threshold unreachable with
5-min ATR). The candidate authored under the original dual-mode
design would have failed admissibility. The reframing is a
methodology-mediated narrowing, not post-result selection.

### 0.3 Structural difference from prior failures

| Prior failure | Failure mode | This candidate's structural difference |
|---|---|---|
| 6 continuation strategies | Apex blowup | Mean-reversion class; not continuation |
| vwap_stretch_snapback | Apex blowup (mean-reversion) | OR-anchored vs VWAP-band; stops wider [5.75, 107.50] |
| prior_day_VA | Apex-safe but no edge (PF 1.17, n=14) | 17× more signals (267 vs 14); R1 evidence-grounded vs literature-only |
| round_number / mhw | Management-design-dead | Zero specialists; static brackets |
| gap_fill_pressure (Phase 0 inadmissible under v1.1) | Drift attrition 80% | Drift attrition 3.96% at full window |

The structural differences are concrete:
- Same-day OR (no weekend-stale prior data — Monday signals fire).
- Wide OR-anchored stops (mean 37.94pt vs prior_day_VA's 60-75pt
  POC-targeted stops) — absorb drift better.
- Confirmation by **two consecutive 1-min closes back inside**
  (eliminates wick-only false rejections).

---

## 1. Strategy Thesis

When MNQ price breaks outside the 15-minute opening range
(09:30-09:45 ET) early in RTH, a majority of those breaks fail and
price returns inside the OR within 30 minutes. The failure-of-break
identifies trapped initiating breakout positioning; responsive
auction participants fade the trapped flow back toward the OR
midpoint and beyond.

**Empirical evidence** (Section 9): across 161 OR-break events in
127 in-sample days (2024-08 to 2025-01), 79.5% reverted within 30
minutes. Symmetric direction profile (79.7% up-breaks revert, 79.3%
down-breaks revert). Median time-to-reversion: 2 minutes.

**Mechanism** (participant-behavior story):

- Initiating breakouts in the first 15-45 minutes of RTH often draw
  fast-money continuation interest.
- When the breakout fails to extend and price returns inside the OR,
  the initiating positioning becomes trapped.
- Responsive auction liquidity (mean-reversion-disposed actors) fades
  the trapped flow back toward the OR midpoint, then potentially
  toward the opposite OR boundary.

**Counter-hypothesis** (must be acknowledged):

- Trend days can break the OR with conviction and stay outside. The
  79.5% reversion rate means **20.5% of breaks continue** — these are
  full-stop losses on the strategy.
- The 25pt OR-width filter excludes only the narrowest chop days
  (preflight: 1 day skipped in 469).
- BAND_B friction (~1.7pt) can consume a significant fraction of
  stops below ~8pt; the stop-floor guard (Section 3.4) addresses this.

---

## 2. Entry Signal And Timing

### 2.1 Time window

- Opening range: **09:30 - 09:45 ET** (15 minutes).
- Entry evaluation window: **09:45 - 11:00 ET**.
- After 11:00 ET: no new entries.

Half-days excluded (session close < 16:00 ET).

### 2.2 Opening range computation

For each RTH day, build the 15-min OR from 1-min bars:
- `or_high = max(high)` across bars indexed [09:30, 09:45).
- `or_low = min(low)` across bars indexed [09:30, 09:45).
- `or_width = or_high - or_low`.

### 2.3 OR width filter

Reject the day if `or_width < 25.0 pts`. This excludes chop days
where the entire OR range is friction. Preflight observed minimum
OR width 33.5pt, so 25pt provides a sane safety margin.

### 2.4 Break-and-recover trigger sequence

Walk 1-min bars in [09:45, 11:00 ET]:

1. **Find a break**: the first 1-min bar where `close > or_high` (up
   break) or `close < or_low` (down break).
2. **Look ahead 10 bars**: search bars at indices [break_i+1, break_i+10]
   for **two consecutive 1-min closes back inside [or_low, or_high]**.
   Signal fires at the SECOND inside close.
3. If no two-consecutive-inside pair is found within 10 bars, abandon
   this break and continue scanning for the next break.
4. **Track failed_extreme**: while bars after the initial break remain
   outside, update the running extreme (max high for up-break, min low
   for down-break). This is the stop anchor.

### 2.5 Direction

- Break was **above OR** → **short** signal (fade trapped longs).
- Break was **below OR** → **long** signal (fade trapped shorts).

### 2.6 Per-day-per-direction dedup

**Max one trade per RTH day** (any direction). Once a signal is
accepted, no further evaluation occurs that day.

### 2.7 Lookahead discipline

- OR computed from completed 09:30-09:45 bars.
- Break and confirmation use completed 1-min bars at-or-before the
  evaluation timestamp.
- Failed-extreme tracking uses running max/min of completed bars only.
- Entry fill at signal_ts + 1 second using the 1-sec OHLCV bar at
  that timestamp.

---

## 3. Risk And Position Sizing

### 3.1 Risk dollars

**Risk per trade: $300.**

Rationale: matches the project's standard. Cluster/floor math: worst
plausible 6 consecutive losses = $1,800, ratio 0.90 against the $2K
Apex floor. TIGHT but survivable, especially with daily-loss-limit
guard (Section 3.5) and max-one-trade-per-day dedup (Section 2.6).

### 3.2 Sizing formula

```
contracts = floor($300 / (stop_pts × $2)).clamp(1, 12)
```

- Point value: $2 (MNQ).
- Contract cap: **12** (HARD-HALT-CONTRACT-CAP-DRIFT — not 15).

### 3.3 Initial stop placement (structural)

For **long** entries: `stop_price = failed_extreme - 0.50 pt`
For **short** entries: `stop_price = failed_extreme + 0.50 pt`

Where `failed_extreme` is the running extreme of the post-break-outside
bars (Section 2.4 step 4) — the deepest the break went before it
got rejected.

### 3.4 Stop-band guard (PREFLIGHT-DRIVEN)

Reject signals where `stop_distance_pts` (at fill) is outside `[8.0, 120.0]`.

- Lower bound 8 pt: BAND_B friction is ~1.7pt; an 8pt stop leaves
  ~6.3pt structural budget — minimum acceptable margin. Preflight
  observed 10-15% of signals had stops in [5.75, 8.00) range; these
  are rejected.
- Upper bound 120 pt: preflight max observed 107.50pt; 120pt gives
  small safety margin for OOS regime shifts.

**HARD-HALT-STOP-GUARD-DRIFT**: the [8.0, 120.0] band must not be
modified during in-sample or OOS testing.

### 3.5 Daily loss limit

**Max 2 losses per RTH day.** After the second loss, no new entries
for the remainder of that RTH day.

With max-one-trade-per-day (Section 2.6), the DLL only activates if
two signals fire on consecutive RTH days; if both fail, the third
day is blocked. In practice this bounds two-day cluster exposure to
$600.

### 3.6 TP-distance guard

Reject signals where `tp_dist_at_fill` is outside `[5.0, 200.0]`.

- Lower bound 5 pt: ensures meaningful R-multiple potential.
- Upper bound 200 pt: preflight max 161pt; 200pt is the sanity cap.
- `tp_dist_at_fill = |TP1_target - fill_price|`.

**HARD-HALT-TP-GUARD-DRIFT**: the [5.0, 200.0] band must not be
modified.

### 3.7 ATR sanity guard

Reject signals where ATR(20) on 5-min at signal_ts is outside
[4.0, 50.0]. This excludes both completely-still and runaway-fast
regimes that the strategy is not designed for.

### 3.8 Skip-trade conditions (full list)

A signal is skipped (not converted to a trade) if any of:

1. `day` is a half-day (session close < 16:00 ET).
2. `or_width < 25.0 pt` (Section 2.3).
3. `stop_distance_pts` outside `[8.0, 120.0]` (Section 3.4).
4. `tp_dist_at_fill` outside `[5.0, 200.0]` (Section 3.6).
5. ATR(20) on 5-min at signal_ts outside `[4.0, 50.0]` (Section 3.7).
6. ComplianceTracker state != ACTIVE.
7. Daily loss count >= 2 (Section 3.5).
8. Trade already taken on this RTH day (Section 2.6).
9. Fill price has drifted past the structural stop or past the TP2
   target (invalid bracket geometry post-fill).

---

## 4. Adaptive Layers

**Decision: ZERO v2.4 specialists. Static brackets only.**

Rationale (deliberate, not maximalist):

- Mean-reversion-to-OR-midpoint has a defined target (OR midpoint /
  opposite OR boundary). A trail past the target contradicts the
  thesis.
- Round-number microfade and momentum_high_water_trail both had
  management-design-dead patterns (BE arm fires before
  structure_trail can tighten). Zero specialists sidesteps this
  failure mode entirely.
- prior_day_VA used zero specialists, and the failure was NOT a
  management issue; this candidate inherits that lesson.
- Max-one-trade-per-day caps daily exposure; no specialist needed
  beyond the simple DLL counter.

If in-sample test reveals R-multiple left on the table (e.g., trades
running through TP2 to extreme reversion), a future iteration may
add `structure_trail` for runners between TP1 and TP2. That is a
FUTURE iteration, not this one.

---

## 5. Bracket Geometry

### 5.1 Initial brackets at entry

For **long** (break below OR, fade up):
- Entry: `entry_price` at signal_ts + 1 second (with BAND_B entry slippage).
- Stop: `stop_price = failed_extreme - 0.50 pt`.
- TP1: `(entry_price + or_high) / 2` — halfway from entry to the
  opposite OR boundary.
- TP2: `or_high` — the opposite OR boundary.
- BE arm: after TP1 fill.

For **short** (break above OR, fade down):
- Entry: `entry_price` at signal_ts + 1 second (with BAND_B entry slippage).
- Stop: `stop_price = failed_extreme + 0.50 pt`.
- TP1: `(entry_price + or_low) / 2`.
- TP2: `or_low`.
- BE arm: after TP1 fill.

### 5.2 TP1 partial close

At TP1 fill, close 50% of position (rounded up to whole contracts;
if 1 contract, no partial close).

### 5.3 BE arm

After TP1 fill, move stop to `entry_price` (BE offset = 0). This is
the only bracket update during the trade.

### 5.4 Strict tighten-only

Any bracket update from compliance or EOD logic must be strict
tighten-only:
- Long stop: `new_stop >= current_stop`.
- Short stop: `new_stop <= current_stop`.

**HARD-HALT-WIDENING**: any widening proposal must be rejected at
the lifecycle layer.

### 5.5 Strategy force-exit conditions

- **EOD-flat**: 15:58:30 ET (90 seconds before 16:00 close).
- **Time exit**: if trade has not resolved (stop, TP, or BE-stop) by
  60 minutes after entry, force-exit at market.
  (Tighter than prior_day_VA's 90 minutes; mean-reversion to OR
  midpoint should resolve faster than to POC.)
- **Apex compliance force-exit**: if ComplianceTracker triggers a
  force-exit (drawdown breach approach, DLL breach), exit immediately.

### 5.6 No runner beyond TP2

Once TP2 (opposite OR boundary) is filled, the trade closes. There
is no runner beyond TP2. The thesis is "revert through OR midpoint
to opposite boundary"; continuing past is no longer the strategy's
edge.

---

## 6. Indicators, Data, And Assumed Library API

### 6.1 Required indicators

- **15-minute opening range**: strategy-local (max/min of 1-min bars
  09:30-09:45). No nb_lib primitive needed.
- **ATR(20) on 5-min**: `nb_lib.indicators.atr.ATR(period=20, smoothing="wilder")`.

### 6.2 Data source

MNQ 1-second OHLCV from Databento, store at
`C:\VMShare\NT8lab\databento\MNQ\ohlcv-1s\`. Loaded via the parent-
script helper `load_seconds`.

### 6.3 Library API consumed (v2.4)

- `nb_lib.lifecycle.TradeLifecycle` — bracket lifecycle, TP1 partial
  fill, BE arm, EOD-flat, strict tighten-only `apply_bracket_update`.
- `nb_lib.compliance.reporting.ComplianceTracker` — Apex 50K EOD eval
  preset.
- `nb_lib.compliance.reporting.make_combined_compliance_check` —
  composed DLL + drawdown + EOD compliance check.
- `nb_lib.logging.ExecutionLogger` — entry / partial / exit /
  strategy_force_exit event logging.
- `nb_lib.trade_record.write_trades_csv` — canonical trade CSV writer.
- `nb_lib.calendar.TradingCalendar` — session close lookup, half-day
  detection.
- `nb_lib.empirical.BAND_B_PARAMS` — friction defaults.
- `nb_lib.reporting.compute_full_summary` / `format_full_summary` —
  in-sample summary printout.

### 6.4 FILL_ASSUMPTIONS extension

`nb_lib.trade_record.FILL_ASSUMPTIONS.add("opening_range_width_switch")`
— required for the canonical trade CSV writer.

---

## 7. Pre-Committed Pass Criteria

This strategy is OOS-eligible if ALL Section 7 criteria are met on
the in-sample window.

### 7.1 Edge: PF >= 1.50

Total in-sample profit factor >= 1.50.

Rationale: the project's canonical PF threshold.

### 7.2 Trade count: n >= 150

Total in-sample trades >= 150.

Rationale: preflight produced 267 signals passing fill guards. The
8pt stop-floor guard (Section 3.4) will reject ~10-15% of those at
canonical-alpha runtime, leaving ~225-240 expected. The Section 3.5
DLL and 3.8 skip conditions may filter further. 150 is a
conservative floor providing clear pass/fail discrimination.

### 7.3 Account state: != FAILED

ComplianceTracker state must not enter FAILED during the in-sample
window.

### 7.4 Direction asymmetry: <= 65% imbalance

`max(long_share, short_share) <= 0.65`.

Preflight showed 52.4% long; well within 65% bound. If in-sample
exceeds 65%, the strategy is one-sided in practice regardless of
two-sided design; the asymmetry is regime-artifact, not strategy edge.

### 7.5 Cluster behavior

No cluster sequence of 6+ consecutive losses. The DLL limits clusters
to 2/day, so 6 consecutive losses requires 3+ consecutive days of
double-loss-quota. If observed, OOS-eligibility is suspended.

### 7.6 OOS trigger conditions

If 7.1, 7.2, 7.3, 7.4, 7.5 all pass: OOS-eligible. Operator decides
whether to consume the OOS slot immediately or save.

If 7.1 fails (PF < 1.50): no OOS. Strategy joins the failure pattern
as `tested-rejected`.

If 7.3 fails (account FAILED): no OOS. Strategy joins as
`tested-apex-failure`.

### 7.7 Empirical signal-frequency context

| Source | Trade count over 18 months |
|---|---|
| v1.2 probe (23 days) extrapolated | 22-89 / 60 trading days |
| Phase 1 preflight (full window, no stop-floor) | 267 |
| Expected canonical alpha (with 8pt stop-floor) | ~225-240 |
| **Pass criterion 7.2** | **n >= 150** |

The pass criterion is conservatively below the preflight count to
provide margin against unexpected drift in OOS or regime shifts.

---

## 8. Mechanics

### 8.1 Evaluation cadence

Entry predicate evaluation: every completed 1-min RTH bar within the
09:45-11:00 ET window. Break-and-recover scan uses completed 1-min
bars only.

Bracket evaluation: every 1-second bar after entry, via TradeLifecycle.

### 8.2 Time exits

Two time-decay exits:

- **Per-trade time exit**: 60 minutes after entry. If still open,
  force-exit at next 1-sec bar's close.
- **EOD-flat**: 15:58:30 ET. All open trades close at this timestamp.

### 8.3 EOD-flat semantics

EOD-flat fires via the lifecycle's session-close machinery. Half-days
are skipped at session-entry (Section 2.1). EOD-flat closes at
`session_close - 90 seconds` to avoid the final seconds' liquidity
issues.

### 8.4 Cooldowns and per-day limits

- Per-day: max one trade (Section 2.6).
- Per-RTH-day loss limit: 2 losses (Section 3.5).
- No per-direction cooldown (max-one-per-day makes this redundant).

### 8.5 Weekday handling

All weekdays (Mon-Fri) are eligible. The preflight confirmed no
Monday stale-prior issue (Mondays produce signals on the
same-day OR; no prior-day data dependency).

### 8.6 Runtime assertions

- `assert OOS_START not in loaded_data_range` (OOS-leak guard).
- `assert stop_price != entry_price` (sizing-degeneracy guard).
- `assert long: stop < entry < tp1 < tp2; short: stop > entry > tp1 > tp2`.
- `assert direction in {-1, +1}`.
- `assert 25.0 <= or_width`.

---

## 9. HARD-HALT Conditions

| Sentinel | Trigger |
|---|---|
| HARD-HALT-OOS-LEAK | Data loaded with date >= 2026-02-01 |
| HARD-HALT-LOOKAHEAD | Predicate uses incomplete bar or future bar |
| HARD-HALT-WIDENING | Any bracket update widens stop |
| HARD-HALT-STOP-GUARD-DRIFT | `STOP_BAND_PTS` modified from `(8.0, 120.0)` |
| HARD-HALT-TP-GUARD-DRIFT | `TP_DIST_BAND_PTS` modified from `(5.0, 200.0)` |
| HARD-HALT-CONTRACT-CAP-DRIFT | `CONTRACT_MAX` modified from 12 |
| HARD-HALT-OR-WIDTH-FLOOR-DRIFT | `OR_WIDTH_MIN_PTS` modified from 25.0 |
| HARD-HALT-DAILY-LOSS-LIMIT-MISSING | DLL constant missing or != 2 |
| HARD-HALT-MAX-ONE-PER-DAY-DRIFT | per-day dedup removed |
| HARD-HALT-LOOKAHEAD-BARS-DRIFT | `POST_BREAK_LOOKAHEAD_BARS` modified from 10 |
| HARD-HALT-TIME-EXIT-DRIFT | time-exit modified from 60 minutes |
| HARD-HALT-OR-MINUTES-DRIFT | OR window != 15 minutes (09:30-09:45) |

Each HARD-HALT corresponds to a constant-pinning test in the
synthetic test suite (Section 14.2).

---

## 10. Open Questions Deferred

Minimal by design. Items deferred to FUTURE iterations:

1. **OR-width filter calibration**: 25pt floor is based on preflight
   observation. If OOS reveals systematically wider chop days,
   filter may need to tighten.
2. **2-min vs 1-bar trigger comparison**: spec uses two consecutive
   1-min closes; an alternative is a single 2-min bar close. Not
   tested in this iteration.
3. **Volume confirmation**: spec does not require a volume confirmation
   on the break or recovery bars. A future iteration may test
   adding a `volume > rolling_mean × 1.5` filter.

No R2 or R4 deferrals. Stop-band, TP-distance, OR-width-filter, and
all sizing parameters are preflight-derived, not "future research."

---

## 11. Wiki References And Informed-Prior Status

This candidate has the cleanest methodology trail in the project,
exceeding prior_day_value_area_rejection on the R1 evidence layer
(MNQ diagnostic vs literature citation).

| Stage | Artifact |
|---|---|
| Wiki entry (template v2, reframed) | `nb_lib/strategy_specs/candidates/opening_range_width_switch.md` |
| Phase 0 v2 (initial, CONDITIONAL) | `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_2_opening_range_width_switch.md` |
| R1 resolution diagnostic | `nb_lib/scripts/diagnostic_orws_failed_break_reversion.py` |
| R1 diagnostic output | `nb_lib/probe_results/opening_range_width_switch_r1_diagnostic.json` |
| Phase 0 v2 (re-eval, ADMISSIBLE) | `C:/VMShare/NT8lab/nb_lib_phase0_v2_v1_2_opening_range_width_switch_re-eval.md` |
| R4 probe convention | `nb_lib/strategy_specs/_R4_PROBE_CONVENTION.md` (v1.2) |
| R4 probe script | `nb_lib/scripts/probe_r4_opening_range_width_switch.py` |
| R4 probe output | `nb_lib/probe_results/opening_range_width_switch_r4_probe.json` |
| Phase 1 entry preflight script | `nb_lib/scripts/opening_range_width_switch_entry_preflight.py` |
| Phase 1 preflight signals CSV | `C:/VMShare/NT8lab/opening_range_width_switch_preflight_signals.csv` |
| Phase 1 preflight summary JSON | `C:/VMShare/NT8lab/opening_range_width_switch_preflight_summary.json` |
| Phase 1 preflight report | `C:/VMShare/NT8lab/nb_lib_phase1_preflight_opening_range_width_switch_report.md` |

Informed priors at spec time:

- R1 supported by 79.5% MNQ failed-break reversion rate (direct
  measurement, not literature).
- R4 probe (v1.2) predicted [22, 89] tradeable per 60d.
- Preflight validated probe at 34.5 tradeable per 60d (within range).
- Preflight attrition (3.96%) closely matched probe attrition (5.6%).
- Direction balance settled at 52.4% L at full-window scale (well
  within 65% asymmetry bound).
- 267 tradeable signals over 464 eligible days; ~225-240 expected
  after 8pt stop-floor guard.

---

## 12. FILL_ASSUMPTIONS Extension

Strategy fill assumption: **BAND_B** (the project default).

```
nb_lib.trade_record.FILL_ASSUMPTIONS.add("opening_range_width_switch")
```

BAND_B friction parameters (from `nb_lib.empirical.BAND_B_PARAMS`):
- Entry slippage: 0.5 pt
- Stop slippage / overshoot: 1.16 pt
- TP slippage: 0.0 pt
- Commission: $0.35 / contract / side

Bracket update latency: 1 second between predicate fire and bracket
modification (lifecycle default).

---

## 13. OOS Reservation And Validation Triggers

### 13.1 Reserved OOS window

**2026-02-01 → 2026-05-04** (sealed; no data load permitted).

### 13.2 OOS ELIGIBLE

This spec is **OOS-eligible if Section 7 pass criteria are met**.
There is no bypass framing. A successful in-sample test consumes the
candidate's right to the OOS slot, and the operator decides whether
to consume immediately or save for parallel-cohort testing.

### 13.3 OOS validation procedure

If in-sample passes Section 7:

1. Operator decision: consume OOS now or save.
2. If consume: run strategy unchanged against 2026-02-01 → 2026-05-04
   data with same Section 7 pass criteria, scaled proportionally.
3. OOS pass: real candidate.
4. OOS fail: tested-oos-rejected.

### 13.4 OOS guard at runtime

The strategy `main()` must include:

```python
assert (loaded_seconds_df.index.date.max() < date(2026, 2, 1)), \
    "HARD-HALT-OOS-LEAK"
```

---

## 14. Test Plan

### 14.1 Library tests

All 574 existing nb_lib tests must continue to pass. No library
modifications are required.

### 14.2 Strategy constant-pinning tests

New test module at
`nb_lib/tests/test_opening_range_width_switch_constants.py`:

- Time window: 09:30-09:45 OR, 09:45-11:00 entry gate.
- OR width minimum: 25.0 pt.
- Post-break lookahead: 10 bars.
- Stop buffer: 0.50 pt.
- Stop band: [8.0, 120.0].
- TP-distance band: [5.0, 200.0].
- ATR-sanity band: [4.0, 50.0].
- Risk dollars: 300.
- Contract max: 12 (NOT 15 — anti-drift assertion).
- DLL: 2.
- Max-per-day: 1.
- Time exit: 60 min.
- EOD-flat seconds before close: 90.
- FILL_ASSUMPTION key registered.

### 14.3 Synthetic behavior tests

New test module at
`nb_lib/tests/test_opening_range_width_switch_behavior.py`:

- OR computation: 1-min bars produce expected high/low.
- OR-width filter: width < 25pt → empty signals.
- Break detection: 1-min close > OR_high triggers up-break tracking.
- Two-consecutive-inside trigger: signal fires at second inside close.
- Failed-extreme tracking: running max/min across consecutive outside bars.
- Direction: above-break → short, below-break → long.
- Max-one-per-day: second signal on same day is rejected.
- Stop-band guard: stop=7.5 rejected, stop=8.0 accepted, stop=120 accepted, stop=120.5 rejected.
- TP-distance guard: tp=4.9 rejected, tp=5.0 accepted, tp=200 accepted, tp=200.5 rejected.
- DLL: third trade on day with 2 prior losses is rejected.
- Sizing: stop=50pt → 3 contracts; stop=10pt → 12 contracts (cap); stop=200pt → 1 contract (clamp).
- Long bracket order: stop < entry < tp1 < tp2.
- Short bracket order: stop > entry > tp1 > tp2.
- BE arm: after TP1 fill, stop moves to entry; strict tighten-only.

Target ~25-35 tests across the two modules.

### 14.4 In-sample run plan

- Window: 2024-08-01 → 2026-01-31 (full in-sample).
- Strategy main: `nb_lib/scripts/opening_range_width_switch_canonical_alpha.py`.
- Output: `opening_range_width_switch_trades.csv` + log CSV.
- Compliance: Apex 50K EOD eval preset.
- Friction: BAND_B.
- Expected trade count: 200-250 (per Section 7.7).
- Run time estimate: 5-15 minutes wall-clock.

Pass criteria evaluated against Section 7 in the in-sample run report.

---

## 15. Selection Bias Notes

Honest acknowledgment of the selection-bias chain:

1. **Project-level**: 10 prior canonical alphas tested; only
   prior_day_VA achieved Phase 0 ADMISSIBLE; that one failed
   in-sample. Methodology infrastructure (template v2, probe v1 →
   v1.1 → v1.2, R1 diagnostic pattern) was developed in response.
2. **Phase 0 selection**: this candidate was selected from the
   untested-ideation pool for v1.2 validation specifically because
   it had measurable predicates (OR-based) and was structurally
   different from prior failures (early-firing rejection, not
   late-firing mean-reversion-to-POC).
3. **Mid-iteration reframe**: the original dual-mode wiki design was
   empirically forced to rejection-only by the v1.2 probe. This is
   methodology-mediated narrowing, not post-result selection — the
   probe revealed the design defect BEFORE in-sample test.
4. **R1 diagnostic specifically run**: the failed-break reversion-
   rate diagnostic was authored to ground R1 evidence. It returned
   a favorable result (79.5%). A different result (e.g., 30%
   reversion) would have failed R1 and closed the candidate.

What this DOES mean:
- The candidate has the cleanest methodology trail in the project.
- Multiple gates were cleared; each could have failed and didn't.

What this DOES NOT mean:
- The candidate is guaranteed to succeed in-sample.
- Methodology cleanliness has been demonstrated to be predictive of
  in-sample success (prior_day_VA disproved this).

Section 7 pass criteria are the same as for any other candidate.
Methodology cleanliness gets the candidate to in-sample testing; it
does not lower the in-sample bar.

---

## 16. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | Wiki entry created in Codex batch 2 (dynamic adaptive intraday focus). |
| 2026-05-17 | `untested-ideation` (retrofit v2) | Retrofitted to template v2 + R4 probe v1.2. Probe found 18 signals, 17 passing fill guards (5.6% attrition), sparsity moderate. Acceptance mode (ratio ≤ 0.35) found structurally unreachable with 5-min ATR. |
| 2026-05-17 | `phase-0-conditionally-admissible` | Phase 0 v2 under v1.2: CONDITIONALLY ADMISSIBLE. R1 PARTIAL (mode-switch defect + folklore evidence). |
| 2026-05-17 | `untested-ideation` (R1 resolution) | Wiki reframed to rejection-only; MNQ failed-break reversion diagnostic (79.5%) added to R1 evidence base. |
| 2026-05-17 | `phase-0-admissible` | Phase 0 v2 re-evaluation: ADMISSIBLE FOR PHASE 1. All 5 requirements met. First fully ADMISSIBLE candidate under v1.2 pipeline. |
| 2026-05-17 | `phase-1-preflight-passed` | Phase 1 preflight passed. 278 signals fired, 267 passing fill guards (3.96% attrition — lowest in project). Actual 34.5/60d WITHIN probe range [22, 89]. Direction 52.4% L. Methodology fully validated. |
| 2026-05-17 | `spec-drafted-final` | FINAL spec drafted at `nb_lib/strategy_specs/canonical/opening_range_width_switch_spec_FINAL.md` (16 sections). **Second candidate to reach FINAL spec under methodology-clean pipeline; first under complete v1.2 pipeline.** Stop-floor guard at 8pt incorporated from preflight findings. R2 frontmatter range tightened to [8, 108]. Section 7.2 pass criterion n >= 150. Time exit 60 min (tighter than prior_day_VA's 90). Zero v2.4 specialists (deliberate). **OOS-ELIGIBLE** if Section 7 pass criteria met (NOT bypass). |
