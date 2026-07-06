---
status: "tested-rejected"
---

# Prior Day Value Area Rejection — Canonical Strategy Specification (FINAL)

**Strategy ID**: `prior_day_value_area_rejection`
**Status**: TESTED-REJECTED (in-sample 2026-05-15; PF 1.17, n=14; does not graduate to OOS)
**Created**: 2026-05-14
**Canonical path**: `nb_lib/strategy_specs/canonical/prior_day_value_area_rejection_spec_FINAL.md`
**Candidate lineage**: `nb_lib/strategy_specs/candidates/prior_day_value_area_rejection.md`
**Phase 0 v2 verdict**: **ADMISSIBLE FOR PHASE 1** (2026-05-14)
**Phase 1 preflight verdict**: **PASSED** (2026-05-14)

---

## 0. Outcome Priors And Scope Acknowledgments

This is the FIRST candidate to clear the project's methodology-clean
pipeline (template v2 Phase 0 admissibility + R4 probe convention v1
+ Phase 1 entry preflight). Unlike the momentum_high_water_trail
informational bypass test, this candidate is **OOS-ELIGIBLE if the
Section 7 pass criteria are met**. There is no bypass framing.

The methodology pipeline produced 137 in-sample entry signals over
374 eligible trading days; the R4 probe extrapolation predicted
reality (probe range [12, 48] per 60 trading days; actual 22.0).
Stop-distance, TP-distance, and weekday-distribution findings from
the preflight drive the risk-geometry guards in Section 3.

**Honest pre-test priors:**

| Outcome | Probability |
|---|---|
| No edge / Apex failure | ~0.40 |
| Weak in-sample only (PF 1.0-1.5) | ~0.25 |
| OOS-eligible edge (real possibility given methodology cleanliness) | ~0.25 |
| Implementation blocker (data, lookahead, etc.) | ~0.10 |

The 0.25 OOS-edge prior is higher than for prior candidates because
the methodology trail is cleaner. It is not 0.50: the 9-fleet failure
pattern includes vwap_stretch_snapback (mean-reversion class, account
FAILED in-sample), which is the closest tested relative. The candidate
differs structurally — see Section 0.3 — but mean-reversion class
historically has not produced a project win.

If this strategy fails in-sample, the issue is **strategy mechanics**,
not methodology. The methodology pipeline did its job.

### 0.1 Bucket accounting

- In-sample: first canonical alpha test for this strategy. No prior
  in-sample slot consumed.
- OOS reserved: 2026-02-01 → 2026-05-04. **DO NOT load.**
- OOS eligibility: ON; consumable if Section 7 pass criteria met.

### 0.2 Selection-bias acknowledgment

This candidate was selected for FINAL spec drafting after passing
both Phase 0 v2 (under template v2 created after four Phase 0 v1
INADMISSIBLE verdicts) and Phase 1 preflight. The methodology
infrastructure was developed in response to prior failures. Strategy-
selection bias is acknowledged: this is "the candidate the new
methodology pipeline produced first," not "a candidate randomly
selected from the candidate pool."

### 0.3 Structural difference from prior failures

The 9-fleet failure pattern includes six continuation strategies, one
level-rejection (round_number microfade), one regime-conditional
(atr_regime tight_target), and one mean-reversion (vwap_stretch_snapback).
Plus one Phase 0 informational rejection (momentum_high_water_trail).

This candidate differs structurally from each:

- **vs vwap_stretch_snapback** (mean-reversion, closest tested
  relative): prior-day volume profile is a different level type than
  intraday VWAP. PD-VA is a structural snapshot of where volume
  actually transacted yesterday; VWAP is a real-time volume-weighted
  average. PD-VA persists; VWAP recomputes each second. Stop placement
  also differs: PD-VA-rejection stops are wider (preflight mean 70.7pt
  vs vwap_stretch_snapback's ~10-15pt band-anchored), reducing
  single-tick-puncture risk in fast regimes.
- **vs round_number microfade**: level-rejection structure (failed
  acceptance + rejection) is similar, but round-number levels are
  fixed at 50/100 multiples; PD-VA boundaries adapt to actual volume.
  Round-number's max-trades-per-day was 4; this strategy is max-one-
  trade-per-day, structurally bounded cluster exposure.
- **vs mhw informational rejection**: mhw's R4 estimate was ~5×
  optimistic (60-180 expected vs 14 actual). This candidate's R4
  probe predicted reality within bracket. The methodology shift is
  the operational difference.
- **vs continuation cluster**: signal-class entirely different.
  Mean-reversion to POC vs continuation past an OR break.

The structural differences are real, not labels. They do not
guarantee success.

---

## 1. Strategy Thesis

When MNQ trades outside the prior day's value area (VAH or VAL) but
fails to accept there — i.e., produces two consecutive 5-min closes
back inside value — the failure-of-acceptance identifies trapped
positioning. The trapped longs above VAH (or shorts below VAL) face
unwind pressure when responsive auction participants reject the
extension. Price reverts toward POC, the volume-weighted center of
yesterday's auction.

**Mechanism** (participant-behavior story):

- Yesterday's value area is where 70% of volume transacted — a real
  consensus zone among initiating and responsive actors.
- When today's price ventures outside that zone, the consensus is
  challenged. If the venture is rejected (price returns inside), the
  challenge failed, and the actors who positioned for the breakout
  are trapped.
- Responsive auction theory (Steidlmayer, Dalton) predicts trapped
  positioning unwinds toward POC, the gravitational center.

**Counter-hypothesis** (must be acknowledged):

- The PD value area is stale by next-day RTH. Many tests succeed
  (accept) rather than reject; the 137 signals over 374 days
  represent only 37% of eligible days.
- "Failed acceptance" defined as two consecutive 5-min closes back
  inside value is a 10-25 minute pattern; in fast regimes, real
  trapped positioning may unwind in seconds, before the predicate
  fires.
- POC may be far from entry in trend regimes, making the TP target
  unreachable within RTH.

The preflight surfaced both of these counter-mechanisms (variable VA
width, TP-to-POC tail to 1348pt). Section 3 guards address them.

---

## 2. Entry Signal And Timing

### 2.1 Time window

Entry evaluation window: **09:30 ET (RTH open) to 15:00 ET**.
- Reason: preflight showed all 137 signals fired before 15:00 ET; no
  late-afternoon firings observed.
- After 15:00, the strategy is in time-decay zone (less than 1 hour
  to EOD-flat); no new entries.

Half-days excluded.

### 2.2 Prior value area computation (preserved verbatim from preflight)

Build prior-day RTH volume profile from 1-min OHLCV bars (09:30 ET
to 16:00 ET prior session):

- **Price binning**: 1-point bins. Each 1-min bar's volume is
  attributed to the bar's midpoint price `(high + low) / 2`, rounded
  to the nearest 1-pt bucket.
- **Value-area percentage**: 70%.
- **Value-area calculation**: smallest contiguous price range
  containing 70% of total volume, expanded outward from POC (the
  max-volume bucket), with ties broken by attaching the higher-volume
  adjacent bucket first.
- **VAH**: highest price in the value-area range.
- **VAL**: lowest price in the value-area range.
- **POC**: midpoint price of the max-volume bucket.

### 2.3 Outside-value detection

For the current RTH day, evaluate from 09:30 ET to 15:00 ET on 1-min
bars: did any bar's high exceed VAH (sets `last_outside_seen = "above"`,
records the failed_extreme as the max 5-min high in the last 3-bar
window) OR any bar's low fall below VAL (`last_outside_seen = "below"`,
failed_extreme = min 5-min low). If neither, skip the day.

### 2.4 Two-consecutive-5-min-closes-back-inside trigger

After `last_outside_seen` is set, iterate 5-min bars. When two adjacent
5-min bars BOTH close in `[VAL, VAH]` AND the prior outside direction
is set, declare a setup at the second bar's timestamp `setup_ts`.

Direction:
- If `last_outside_seen == "below"`: **long** setup.
- If `last_outside_seen == "above"`: **short** setup.

### 2.5 First-pullback entry trigger

After `setup_ts`, scan the next 20 1-min bars. The first 1-min bar
where:
- close is in `[VAL, VAH]` (still inside value), AND
- for long: low is within 2.0pt of VAL (pullback toward the failed
  extreme), OR
- for short: high is within 2.0pt of VAH

Triggers entry at `signal_ts` (the 1-min bar's close timestamp).
Entry fill at `signal_ts + 1 second` per project convention.

### 2.6 Per-day-per-direction dedup

**Max one trade per RTH day** (any direction). Once a signal is
accepted on a day, no further signals are recorded for that day.

### 2.7 Monday handling

The Phase 1 preflight surfaced **zero Monday signals** across 18
in-sample months. Cause: Monday's "prior RTH session" is Friday's,
which is stale after the weekend gap.

**Decision**: skip Mondays explicitly. The strategy issues no signals
on Mondays. This is consistent with empirical behavior, prevents
strategy from firing on the rare Monday-with-Friday-VA-coincidentally-
intact case (which would be a degenerate sample), and simplifies the
spec.

Implementation: at evaluation time, `if day.weekday() == 0: return []`
before VA lookup.

### 2.8 Lookahead discipline

All predicates are evaluated on completed bars only. VA computation
uses prior-day RTH bars (definitionally completed). Outside-value
detection uses bars at-or-before the current evaluation timestamp.
Two-consecutive-close detection uses two completed 5-min bars.
Pullback detection scans forward in time within the next 20
1-minute bars; entry fills at signal close + 1 second using the
1-sec OHLCV bar at that timestamp.

---

## 3. Risk And Position Sizing

### 3.1 Risk dollars

**Risk per trade: $300.**

Rationale: matches the project's standard risk dollars across prior
canonical specs (round_number, mhw, atr_regime). Cluster/floor math:
worst plausible cluster of 5 consecutive losses = $1,500, ratio 0.75
against the $2K Apex floor. Acceptable margin with the daily-loss-
limit guard (Section 3.5) and max-one-trade-per-day dedup (Section 2.6).

### 3.2 Sizing formula

```
contracts = floor($300 / (stop_pts × $2)).clamp(1, 12)
```

- Point value: $2 (MNQ).
- Contract cap: **12** (not 15). Per mhw learning, 15 produced
  excessive exposure in fast regimes; 12 is the project's pinned
  ceiling for new candidates.

### 3.3 Initial stop placement (structural)

For **long** entries: `stop_price = failed_extreme - 0.50pt`
For **short** entries: `stop_price = failed_extreme + 0.50pt`

Where `failed_extreme` is the recorded min/max from Section 2.3 (the
extreme of the failed-acceptance excursion outside value, plus a
2-tick buffer beyond).

### 3.4 Stop-band guard (PREFLIGHT-DRIVEN)

The Phase 1 preflight measured stop-distance distribution:

| Stat | Value (pts) |
|---|---|
| mean | 70.71 |
| p50 | 60.25 |
| min | 8.75 |
| max | 251.25 |

**Stop-band guard**: reject signals where `stop_distance_pts` is
outside `[8.0, 100.0]`.

- Lower bound 8pt: rejects micro-stop signals where price already
  recovered close to the failed extreme (entry-to-stop too tight for
  reliable fills under BAND_B friction; min preflight observed 8.75
  is at this boundary).
- Upper bound 100pt: rejects fast-regime / wide-VA outliers. The 251pt
  observed maximum would size to 1 contract under standard sizing
  formula (floor(300 / (251 × 2)) = 0); the guard makes the skip
  explicit and documents the band.

Based on preflight distribution, ~50% of signals have stops above
60pt; the [8, 100] band keeps approximately 65-75% of signals (an
empirical guess pending in-sample test).

**HARD-HALT-STOP-GUARD-DRIFT**: the [8.0, 100.0] band must not be
modified during in-sample or OOS testing. Drift in either bound
breaks the pre-commitment.

### 3.5 Daily loss limit

**Max 2 losses per RTH day.** After the second loss, no new entries
for the remainder of that RTH day.

Rationale: with max-one-trade-per-day in Section 2.6, the daily loss
limit only matters if two signals occur on consecutive RTH days; if
both fail, the third day is blocked. In practice this bounds two-day
cluster exposure to $600, two-week worst-case to $3,000 ($300 × 2 ×
5 days) — but the trailing-drawdown floor regenerates with each
new peak, so this is upper-bound math.

The strategy's `max-one-per-day` already limits cluster exposure
materially. The DLL is belt-and-suspenders.

### 3.6 TP-distance guard (PREFLIGHT-DRIVEN)

The Phase 1 preflight measured TP-to-POC distance:

| Stat | Value (pts) |
|---|---|
| mean | 82.22 |
| p50 | 48.00 |
| min | **-26.50** (negative — POC behind entry) |
| max | **1348.75** (unreachable) |

**TP-distance guard**: reject signals where `tp_distance_to_poc_pts`
is outside `[5.0, 150.0]`.

- Lower bound 5pt: rejects signals where POC is too close to entry
  for meaningful R-multiple (TP1 at midpoint to POC would be <2.5pt,
  below BAND_B slippage noise).
- Upper bound 150pt: rejects unreachable-POC signals. With TP2 at
  POC and a 90-min time exit (Section 8.2), 150pt distance is at
  the boundary of plausible mean-reversion within the trade window.

**HARD-HALT-TP-GUARD-DRIFT**: the [5.0, 150.0] band must not be
modified.

### 3.7 Skip-trade conditions (full list)

A signal is skipped (not converted to a trade) if any of:

1. `day.weekday() == 0` (Monday — Section 2.7).
2. `stop_distance_pts < 8.0` or `> 100.0` (Section 3.4).
3. `tp_distance_to_poc_pts < 5.0` or `> 150.0` (Section 3.6).
4. ATR(20) on 5-min at signal_ts is outside `[4.0, 50.0]` (sanity).
5. ComplianceTracker state != ACTIVE.
6. Daily loss count >= 2 (Section 3.5).
7. Trade already taken on this RTH day (Section 2.6).

---

## 4. Adaptive Layers

**Decision: ZERO v2.4 specialists. Static brackets only.**

Rationale, deliberate not maximalist:

- Preflight signal density is ~22/60 trading days = ~1 signal per 3
  days. Per-trade duration estimate from mean-reversion class is
  30-90 min typical hold. Trade duration does NOT structurally
  require management to add value.
- Round-number microfade and momentum_high_water_trail both had
  management-design-dead patterns (BE arm fires before
  structure_trail can tighten). Zero specialists sidesteps this
  failure mode entirely.
- Mean-reversion-to-POC has a defined target (POC). A trail past the
  target contradicts the thesis. Static TP1 + TP2 + BE-after-TP1 is
  thesis-coherent.
- max-one-trade-per-day naturally caps daily exposure. No
  daily-loss-protector specialist needed beyond the simple DLL counter.

If in-sample test reveals R-multiple left on the table, a future
iteration may add `structure_trail` for runners between TP1 and TP2.
That is a FUTURE iteration, not this one.

---

## 5. Bracket Geometry

### 5.1 Initial brackets at entry

For **long**:
- Entry: `entry_price` (Section 2.5 + 1-sec fill).
- Stop: `stop_price = failed_extreme - 0.50pt`.
- TP1: midpoint between `entry_price` and POC =
  `entry_price + (POC - entry_price) / 2`.
- TP2: POC.
- BE arm: after TP1 fill.

For **short**: symmetric.

### 5.2 TP1 partial close

At TP1 fill, close 50% of position (rounded up to a whole contract
count; if 1 contract, no partial close).

### 5.3 BE arm

After TP1 fill, move stop to `entry_price` (no offset / BE = entry).
This is the only bracket update during the trade.

### 5.4 Strict tighten-only

Any subsequent bracket update from compliance or EOD logic must be
strict tighten-only:
- Long stop: new_stop >= current_stop.
- Short stop: new_stop <= current_stop.

**HARD-HALT-WIDENING**: any widening proposal must be rejected at
the lifecycle layer.

### 5.5 Strategy force-exit conditions

- **EOD-flat**: 15:58:30 ET (90 seconds before 16:00 close).
- **Time exit**: if trade has not resolved (stop, TP, or BE-stop) by
  90 minutes after entry, force-exit at market.
- **Apex compliance force-exit**: if ComplianceTracker triggers a
  force-exit reason (drawdown breach approach, DLL breach), exit
  immediately.

### 5.6 No runner beyond POC

Once TP2 (POC) is filled, the trade is closed. There is no runner
position past POC. The thesis is "revert to POC"; continuing past
POC is no longer the strategy's edge.

---

## 6. Indicators, Data, And Assumed Library API

### 6.1 Required indicators

- **PD value area computation**: strategy-local (no nb_lib primitive
  required at this iteration). Implemented per Section 2.2; the
  `compute_value_area` function in the preflight script is the
  reference implementation.
- **ATR(20) on 5-min**: `nb_lib.indicators.atr.ATR(period=20,
  smoothing="wilder")`.
- **(Optional) VWAP for log/context**: not used for decisions.

A future iteration may extract `compute_value_area` into a `nb_lib.
indicators.value_profile` primitive if a second strategy needs it.

### 6.2 Data source

MNQ 1-second OHLCV from Databento, store at
`C:\VMShare\NT8lab\databento\MNQ\ohlcv-1s\`. Loaded via
`nb_lib.scripts.atr_regime_pullback_continuation_canonical_alpha.load_seconds`
(parent-script helper reuse).

### 6.3 Library API consumed (v2.4)

- `nb_lib.lifecycle.TradeLifecycle` — bracket lifecycle, partial
  fills, EOD-flat, strict tighten-only `apply_bracket_update`.
- `nb_lib.compliance.reporting.ComplianceTracker` — Apex 50K EOD eval
  preset, balance/peak/floor tracking.
- `nb_lib.compliance.reporting.make_combined_compliance_check` —
  composed DLL + drawdown + EOD compliance check.
- `nb_lib.logging.ExecutionLogger` — entry / partial / exit /
  strategy_force_exit event logging.
- `nb_lib.trade_record.write_trades_csv` — canonical trade CSV
  writer.
- `nb_lib.calendar.TradingCalendar` — session close lookup,
  half-day detection, is_trading_day.
- `nb_lib.empirical.BAND_B_PARAMS` — friction defaults.
- `nb_lib.reporting.compute_full_summary` / `format_full_summary` —
  in-sample summary printout.

### 6.4 FILL_ASSUMPTIONS extension

`nb_lib.trade_record.FILL_ASSUMPTIONS.add("prior_day_value_area_rejection")`
— required for the canonical trade CSV writer.

---

## 7. Pre-Committed Pass Criteria

This strategy is OOS-eligible if ALL Section 7 criteria are met on
the in-sample window.

### 7.1 Edge: PF >= 1.50

Total in-sample profit factor >= 1.50.

Rationale: the project's canonical PF threshold. 1.50 is the
PF-distinguishing-strategies-from-noise cut.

### 7.2 Trade count: n >= 80

Total in-sample trades >= 80.

Rationale: preflight produced 137 raw entry signals. Section 3 guards
(stop-band, TP-distance, ATR-sanity, weekday) are expected to skip
30-50%, leaving 70-95 trades. 80 is a slightly conservative floor;
below 80 the dataset is too thin for stable PF inference.

### 7.3 Account state: != FAILED

ComplianceTracker state must not enter FAILED during the in-sample
window. Apex floor must not be breached.

### 7.4 Direction asymmetry: <= 65% imbalance

`max(long_share, short_share) <= 0.65`.

Rationale: preflight showed 41.6% long / 58.4% short (well within
65%). If the in-sample test exceeds 65%, the strategy is one-sided in
practice regardless of two-sided design; the asymmetry is regime-
artifact, not strategy-edge.

### 7.5 Cluster behavior

No cluster sequence of 6+ consecutive losses. The DLL limits clusters
to 2 per day, so 6 consecutive losses requires 3+ consecutive days
of full-loss-quota days. If observed, this signals a regime where
the strategy systematically fails; OOS-eligibility is suspended.

### 7.6 OOS trigger conditions

If 7.1, 7.2, 7.3, 7.4, 7.5 all pass: OOS-eligible. Operator decides
whether to consume the OOS slot immediately or save.

If 7.1 fails (PF < 1.50): no OOS. Strategy joins the 9-fleet failure
pattern as `tested-rejected`.

If 7.3 fails (account FAILED): no OOS. Strategy joins the failure
pattern as `tested-apex-failure`.

### 7.7 Empirical signal frequency context

The Phase 1 preflight produced 137 entry signals over 374 eligible
trading days. Pass-criteria 7.2 (n >= 80) accounts for Section 3
guards skipping 30-50% of signals. If in-sample produces fewer than
80 trades, R4 retroactively fails (the guards are too restrictive
in practice) — see Section 10 for spec-revision pathway.

---

## 8. Mechanics

### 8.1 Evaluation cadence

Entry predicate evaluation: every completed 1-min RTH bar within the
09:30-15:00 ET window. Two-consecutive-5-min-closes check is on
completed 5-min boundaries.

Bracket evaluation: every 1-second bar after entry, via TradeLifecycle.

### 8.2 Time exits

Two time-decay exits:

- **Per-trade time exit**: 90 minutes after entry. If still open,
  force-exit at next 1-sec bar's close.
- **EOD-flat**: 15:58:30 ET (90 seconds before 16:00 close). All
  open trades close at this timestamp.

### 8.3 EOD-flat semantics

EOD-flat fires via the lifecycle's session-close machinery. The
session close from `TradingCalendar.get_session_close(day)` is the
truth; on half-days the strategy is already skipped (Section 2.1).
EOD-flat closes at `session_close - 90 seconds` to avoid the final
seconds' liquidity issues.

### 8.4 Cooldowns and per-day limits

- Per-day: max one trade (Section 2.6).
- Per-RTH-day loss limit: 2 losses (Section 3.5).
- No per-direction cooldown (max-one-per-day makes this redundant).

### 8.5 Monday handling

Skip all Mondays. `if day.weekday() == 0: return []` at the top of
`evaluate_signals_for_day`.

### 8.6 Runtime assertions

- `assert OOS_START not in loaded_data_range` (OOS-leak guard).
- `assert stop_price != entry_price` (sizing-degeneracy guard).
- `assert tp1_price strictly between entry and tp2` (bracket order).
- `assert long: stop < entry < tp1 < tp2; short: stop > entry > tp1 > tp2`.
- `assert direction in {-1, +1}`.

---

## 9. HARD-HALT Conditions

| Sentinel | Trigger |
|---|---|
| HARD-HALT-OOS-LEAK | Data loaded with date >= 2026-02-01 |
| HARD-HALT-LOOKAHEAD | Predicate uses incomplete bar or future bar |
| HARD-HALT-WIDENING | Any bracket update widens stop (long: new < current; short: new > current) |
| HARD-HALT-STOP-GUARD-DRIFT | `STOP_BAND_PTS` modified from `(8.0, 100.0)` |
| HARD-HALT-TP-GUARD-DRIFT | `TP_DIST_BAND_PTS` modified from `(5.0, 150.0)` |
| HARD-HALT-CONTRACT-CAP-DRIFT | `CONTRACT_MAX` modified from 12 |
| HARD-HALT-DAILY-LOSS-LIMIT-MISSING | DLL constant missing or != 2 |
| HARD-HALT-MAX-ONE-PER-DAY-DRIFT | per-day dedup removed |
| HARD-HALT-MONDAY-SKIP-MISSING | Monday filter not in place |
| HARD-HALT-VA-BIN-DRIFT | `PRICE_BIN_PTS` modified from 1.0 |
| HARD-HALT-VA-PCT-DRIFT | `VA_PCT` modified from 0.70 |

Each HARD-HALT corresponds to a constant-pinning test in the
synthetic test suite (Section 14.2).

---

## 10. Open Questions Deferred

Minimal by design — the methodology-clean pipeline resolved most
questions before spec drafting. Items deferred to FUTURE iterations:

1. **POC bin resolution**: 1-pt bins are coarse for MNQ tick (0.25pt).
   A future iteration may test 0.25-pt bins to see if POC precision
   affects TP-distance.
2. **VA calculation method variants**: smallest-contiguous-range vs
   developing-VA vs other Market Profile variants. Pinned to
   smallest-contiguous-range; alternatives untested.
3. **Monday handling generalization**: explicit Monday skip is the
   simple choice. A future iteration may test "Monday with Friday+
   Thursday VA combined" as an alternative.
4. **Volume profile primitive extraction**: if a second strategy
   adopts this VA computation, extract to
   `nb_lib.indicators.value_profile`.

No R2 or R4 deferrals. Stop-band and TP-distance guards are
preflight-derived, not "future research."

---

## 11. Wiki References And Informed-Prior Status

This candidate has the cleanest methodology trail in the project:

| Stage | Artifact |
|---|---|
| Wiki entry (v2 template) | `nb_lib/strategy_specs/candidates/prior_day_value_area_rejection.md` |
| Phase 0 v2 admissibility report | `C:/VMShare/NT8lab/nb_lib_phase0_v2_prior_day_value_area_rejection.md` |
| Phase 0 v2 batch results | `C:/VMShare/NT8lab/nb_lib_phase0_v2_batch1_results.md` |
| R4 probe convention | `nb_lib/strategy_specs/_R4_PROBE_CONVENTION.md` (v1) |
| R4 probe script | `nb_lib/scripts/probe_r4_prior_day_value_area_rejection.py` |
| R4 probe output | `nb_lib/probe_results/prior_day_value_area_rejection_r4_probe.json` |
| Phase 1 entry preflight script | `nb_lib/scripts/prior_day_value_area_rejection_entry_preflight.py` |
| Phase 1 preflight signals CSV | `C:/VMShare/NT8lab/prior_day_value_area_rejection_preflight_signals.csv` |
| Phase 1 preflight summary JSON | `C:/VMShare/NT8lab/prior_day_value_area_rejection_preflight_summary.json` |
| Phase 1 preflight report | `C:/VMShare/NT8lab/nb_lib_phase1_preflight_prior_day_value_area_rejection_report.md` |

Informed priors at spec time:

- Probe extrapolation validated by preflight (probe predicted 12-48
  per 60 days; actual 22 per 60 days, within range).
- Direction balance settled at 41.6% / 58.4% (within pre-committed
  65% asymmetry bound).
- 137 entry signals over 374 eligible days; Section 3 guards expected
  to skip 30-50% leaving 70-95 trades; Section 7.2 pass criterion
  n >= 80 is slightly conservative.

---

## 12. FILL_ASSUMPTIONS Extension

Strategy fill assumption: **BAND_B** (the project default).

```
nb_lib.trade_record.FILL_ASSUMPTIONS.add("prior_day_value_area_rejection")
```

BAND_B friction parameters (from `nb_lib.empirical.BAND_B_PARAMS`):
- Entry slippage: 0.5pt
- Stop slippage / overshoot: 1.16pt
- TP slippage: 0.0pt
- Commission: $0.35/contract/side

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
to consume immediately or save.

### 13.3 OOS validation procedure

If in-sample passes Section 7:

1. Operator decision: consume OOS now or save for parallel-cohort
   testing.
2. If consume: run strategy unchanged against 2026-02-01 → 2026-05-04
   data with same Section 7 pass criteria, scaled proportionally.
3. OOS pass: real candidate.
4. OOS fail: tested-oos-rejected (in-sample edge did not generalize).

### 13.4 OOS guard at runtime

The strategy `main()` must include:

```python
assert (loaded_seconds_df.index.date.max() < date(2026, 2, 1)), \
    "HARD-HALT-OOS-LEAK"
```

---

## 14. Test Plan

### 14.1 Library tests

All 517 existing nb_lib tests must continue to pass. No library
modifications are required by this spec; the strategy consumes v2.4
primitives only.

### 14.2 Strategy constant-pinning tests

New test module at
`nb_lib/tests/test_prior_day_value_area_rejection_constants.py`:

- Time window: 09:30-15:00 ET.
- VA parameters: VA_PCT=0.70, PRICE_BIN_PTS=1.0.
- Lookahead bars for pullback: 20.
- Pullback wick tolerance: 2.0pt.
- Stop buffer: 0.50pt.
- Stop band: [8.0, 100.0].
- TP-distance band: [5.0, 150.0].
- ATR-sanity band: [4.0, 50.0].
- Risk dollars: 300.
- Contract max: 12 (NOT 15 — anti-drift assertion).
- DLL: 2.
- Max-per-day: 1.
- EOD-flat seconds before close: 90.
- Time exit: 90 min.
- Monday skip: true.
- FILL_ASSUMPTION key registered.

### 14.3 Synthetic behavior tests

New test module at
`nb_lib/tests/test_prior_day_value_area_rejection_behavior.py`:

- VA computation: known midpoint-volume input → known VAH/VAL/POC.
- Outside-value detection: high>VAH sets above, low<VAL sets below.
- Two-consecutive-close trigger: two adjacent closes inside value
  fire setup; non-adjacent does not.
- Pullback detection: 1-min close inside + wick ≤ 2pt fires; outside
  tolerance does not.
- Per-day dedup: second signal on same day is rejected.
- Monday skip: weekday==0 returns empty.
- Stop-band guard: stop=7.5 rejected, stop=8.0 accepted, stop=100
  accepted, stop=100.5 rejected.
- TP-distance guard: tp=4.9 rejected, tp=5.0 accepted, tp=150
  accepted, tp=150.5 rejected.
- DLL: third trade on day with 2 prior losses is rejected.
- Sizing: stop=50pt → 3 contracts; stop=5pt would size to 30 contracts
  but capped at 12 (out of band anyway).
- Long bracket order: stop < entry < tp1 < tp2.
- Short bracket order: stop > entry > tp1 > tp2.
- BE arm: after TP1 fill, stop moves to entry; strict tighten-only.

Target ~30-40 tests across the two modules; new total ~547-557.

### 14.4 In-sample run plan

- Window: 2024-08-01 → 2026-01-31 (full in-sample).
- Strategy main: `nb_lib/scripts/prior_day_value_area_rejection_canonical_alpha.py`.
- Output: `prior_day_value_area_rejection_trades.csv` + log CSV.
- Compliance: Apex 50K EOD eval preset.
- Friction: BAND_B.
- Expected trade count: 80-100 (per Section 7.2 / Section 7.7).
- Run time estimate: 5-10 minutes wall-clock.

Pass criteria evaluated against Section 7 in the in-sample run
report.

---

## 15. Selection Bias Notes

Honest acknowledgment of the selection-bias chain:

1. **Project-level selection bias**: 9 prior canonical alphas failed
   Apex eval before this candidate. The methodology infrastructure
   (template v2, R4 probe convention, this admissibility-clean
   pipeline) was developed in response to those failures.
2. **Phase 0 v2 selection**: the candidate was selected for retrofit
   from a pool of ~15 untested-ideation entries. Selection criterion
   was "R4-data-derivability" — candidates with measurable predicates
   suitable for probe extrapolation. This means structurally well-
   defined candidates were preferred over loosely-specified ones, a
   real bias.
3. **First-ADMISSIBLE selection**: of two candidates in the first
   retrofit batch, this one passed all 5 requirements; the other
   (gap_fill_pressure) was CONDITIONALLY ADMISSIBLE with R1 partial.
   We chose to advance the fully-ADMISSIBLE candidate.
4. **Mean-reversion-class bias**: the closest tested relative
   (vwap_stretch_snapback) failed in-sample. We chose to test a
   different mean-reversion mechanism rather than wait for a more
   different class candidate.

What this DOES mean:
- The candidate has the cleanest methodology trail of any tested.
- The candidate cleared structural admissibility gates that 4 prior
  candidates failed.
- The candidate's R4 expectation is data-grounded (probe + preflight).

What this DOES NOT mean:
- The candidate is guaranteed to succeed in-sample.
- The methodology gates are predictive of P&L (they are not — they
  are necessary, not sufficient).
- Methodology-clean candidates have better edge than methodology-
  unclean ones (untested hypothesis).

Section 7 pass criteria are the same as for any other candidate.
Methodology cleanliness gets the candidate to in-sample testing; it
does not lower the in-sample bar.

---

## 16. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | `untested-ideation` | Wiki entry created in Codex batch 2 (Market Profile / auction theory class). |
| 2026-05-14 | `untested-ideation` (retrofit v2) | Retrofitted to template v2. R4 probe ran on 5-day window: 2 signals, sparsity sparse-boundary. R2 quantified: $300 risk, cluster/floor 0.75. |
| 2026-05-14 | `phase-0-admissible` | Phase 0 v2 evaluation complete. **ADMISSIBLE FOR PHASE 1** — first ADMISSIBLE verdict in 5 Phase 0 evaluations. All 5 requirements met. |
| 2026-05-14 | `phase-1-preflight-passed` | Phase 1 entry preflight complete over full in-sample (469 trading days; 374 eligible). 137 signals, 22.0/60-day. Probe extrapolation [12, 48] validated. Direction balance 41.6/58.4. Stop-distance discovery: mean 70.7pt range [8.75, 251.25] — drove the stop-band guard requirement. |
| 2026-05-14 | `spec-drafted-final` | FINAL spec drafted from Phase 1 preflight findings. First candidate to clear methodology-clean pipeline (Phase 0 v2 admissible + Phase 1 preflight passed + probe extrapolation predicted reality). Stop-band guard [8, 100], TP-distance guard [5, 150], daily loss limit (2), max-one-per-day, Monday skip incorporated from preflight. Zero v2.4 specialists (deliberate). OOS-ELIGIBLE if Section 7 pass criteria met (NOT bypass). Length 4200 words. |
