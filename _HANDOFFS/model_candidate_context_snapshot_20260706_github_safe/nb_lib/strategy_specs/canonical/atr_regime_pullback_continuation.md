---
status: "implementation-pending"
---

# ATR Regime Pullback Continuation Canonical Alpha — Strategy Specification (FINAL)

**Strategy ID**: atr_regime_pullback_continuation
**Version**: 1.0
**Status**: implementation-pending
**Lineage**: nb_lib-native, first multi-timeframe canonical alpha
**Date created**: 2026-05-12
**Date updated**: 2026-05-12
**Authors**: Strategic Claude + operator
**Library version**: nb_lib v2.3 (post simulator-extension 2026-05-12; tests 298/298)
**Verification trail**: candidate wiki entry
`nb_lib/strategy_specs/candidates/atr_regime_pullback_continuation.md` →
this FINAL spec → upcoming implementation iteration.

---

## 0. Methodology framing (read first)

### 0.1 Why this strategy is being tested

This is an **infrastructure-first iteration**. The operator has
acknowledged that the strategy itself is unlikely to demonstrate
edge — the PRJ_3 raw-signal diagnostic
(`nb_lib_prj3_raw_signal_diagnostic_report.md`) materially refuted
the regime-conditional continuation hypothesis at sub-minute
granularity, and the four prior nb_lib-native canonical strategies
all failed Apex 50K eval at ~$-2K cumulative. Nevertheless, the
build is being undertaken because the iteration validates and
exercises a substantial body of reusable infrastructure:

- ATR-scaled bracket primitive (Section 10)
- ATR-percentile regime gate primitive (Section 5)
- Choppiness Index regime gate primitive (Section 5)
- Multi-timeframe bar coordination + lookahead audit pattern
  (Section 3)
- 5-tier conviction classifier as a reusable scaffold (Section 9)
- 2-level volatility multiplier (Section 9)
- Fixed-risk-dollar sizing per-trade (Section 9)
- Cushion-based intraday sizing (Mechanic 1, Section 9)
- Post-lock cushion sizing (Mechanic 2, Section 9 + 11) —
  exercises the newly-added `is_locked()` / `is_eval_passed()` /
  `advance_to_pa()` library methods (`nb_lib/compliance/reporting.py`
  lines 346-446)
- Watch-window 1-second validation pattern (Section 8)
- Multi-timeframe lookahead audit, extending the 4-surface pattern
  established in PRJ_3 (Section 12)

### 0.2 Epistemic status: curve-fit risk acknowledged

The strategy has **six adaptive layers**:

1. ATR-scaled brackets (Level 1, continuous adaptive)
2. ATR-percentile regime gate (Level 2, discrete threshold)
3. Choppiness gate (Level 2, discrete threshold)
4. 5-tier conviction classifier (Level 2, multi-threshold)
5. 2-level vol multiplier (Level 2, single threshold)
6. Cushion-based risk adjustment Mechanic 1 + 2 (Level 1,
   continuous adaptive)

By the methodology repertoire's framework
(`nb_lib/strategy_specs/candidates/_METHODOLOGY_repertoire.md`
Section 1), this is firmly in Level 2 territory with Level 1
mixed in — high curve-fit risk. Every parameter in this spec is
**PRE-COMMITTED**: tier thresholds, ATR multipliers, cushion
formula constants, watch-window duration, regime gate cutoffs.
No parameter may be tuned during implementation or testing. If
in-sample results look promising, a **held-out OOS cohort
validation is mandatory** (Section 13) before any deployment
consideration. The OOS window 2026-02-01 → 2026-05-04 is reserved
and may NOT be loaded during in-sample work.

### 0.3 Expected outcome priors (honest)

- **60%**: no in-sample edge. Matches the PRJ_3 raw-signal
  diagnostic refutation; matches the tested-rejected fleet's
  $-2K Apex outcome pattern.
- **25%**: edge appears in-sample but fails OOS. Selection on
  noise; the six adaptive layers compound to find spurious
  in-sample signal.
- **10%**: edge appears in-sample and survives OOS. Genuine
  multi-timeframe regime-conditioned continuation edge.
- **5%**: edge with execution issues. Bracket mechanics break
  under specific volatility regimes (e.g., the 0.75×ATR TP1 fills
  too tightly on real wide-range bars; or the watch window's
  skip condition fires excessively).

### 0.4 What this iteration validates beyond strategy edge

Regardless of strategy edge outcome, the implementation iteration
validates that the listed infrastructure (Section 0.1) works
correctly. Each piece becomes a reusable primitive that subsequent
strategies can consume without re-deriving. The retrospective
written after the implementation iteration must explicitly
distinguish "strategy edge" findings from "infrastructure
validation" findings.

---

## 1. Spec metadata

- **Name**: ATR Regime Pullback Continuation Canonical Alpha
- **Strategy ID**: atr_regime_pullback_continuation
- **Version**: 1.0
- **Created**: 2026-05-12
- **Updated**: 2026-05-12
- **Status**: implementation-pending
- **In-sample window**: 2024-08-01 → 2026-01-31 (RTH sessions
  only, US/Eastern)
- **OOS reserved window**: 2026-02-01 → 2026-05-04 (DO NOT load
  during in-sample work)
- **Library version**: nb_lib v2.3 (commit-equivalent: after
  simulator-extension iteration 2026-05-12; tests 298/298;
  contains `is_locked`, `is_eval_passed`, `advance_to_pa`
  methods on `ComplianceTracker`)
- **Data source**: `nb_lib.scripts.prj3_canonical_alpha.load_seconds`
  (matches tested-fleet convention; silently skips 7 in-sample
  OPEX days per
  `_METHODOLOGY_data_store.md` Section 2)
- **Account preset**: `apex_50k_eod_eval` (Rithmic variant) initially;
  may transition to `apex_50k_eod_pa` mid-stream via
  `tracker.advance_to_pa()` if `tracker.is_eval_passed()` returns
  True

---

## 2. Signal window definitions per timeframe

The strategy operates across four timeframes simultaneously.
Every signal-evaluation moment T is anchored to a 1-second bar
close.

| Timeframe | Role | Last-completed bar at T | Max staleness |
|---|---|---|---|
| 30-minute | Trend qualification | bar ending at last 30-min boundary ≤ T | up to 30 min |
| 5-minute | Regime gates, ATR, pullback detection | bar ending at last 5-min boundary ≤ T | up to 5 min |
| 1-minute | Reversal candle detection | bar ending at last 1-min boundary ≤ T | up to 1 min |
| 1-second | Execution, watch window | bar ending exactly at T | 0 (bar is T) |

**RTH session boundaries**: 09:30:00–16:00:00 US/Eastern.
Half-days: per `TradingCalendar.get_session_close(date)` (13:00 on
known half-days).

**Critical: "most recent COMPLETED bar"**. At signal moment T, the
spec NEVER reads any bar whose close timestamp is > T. The 30-min
bar evaluated at T = 11:23:17 ET is the bar [10:30, 11:00); the
[11:00, 11:30) bar is still forming. The 5-min bar is [11:20,
11:25); the [11:25, 11:30) bar is still forming. The 1-min bar is
[11:22, 11:23); the [11:23, 11:24) is still forming. This is the
multi-timeframe lookahead discipline (Section 12).

---

## 3. Phase 0 — multi-timeframe bar availability + lookahead audit

### 3.1 Bar-availability mapping

At any signal evaluation moment T (1-second bar close):

| Timeframe | Last available bar | Bar close = | Why this prevents lookahead |
|---|---|---|---|
| 30-min | floor(T / 30min) - 1 | floor(T / 30min) | Bar that just completed; never the one forming |
| 5-min | floor(T / 5min) - 1 | floor(T / 5min) | Same logic; close == next bar's open |
| 1-min | floor(T / 1min) - 1 | floor(T / 1min) | Same logic |
| 1-sec | the bar ending exactly at T | T | T is the close timestamp |

Implementation pattern (per the PRJ_3 lookahead-fix lesson):
the `signal_ts` used to identify any bar from a multi-bar series
must be the **right-edge timestamp** (bar's close). A bar's
`open_ts` is left-edge; the bar's data is observable only at its
right edge.

### 3.2 Lookahead-free aggregation

All multi-timeframe aggregation is done from 1-second OHLCV via
sequential resampling:

```python
seconds_df = load_seconds(DATA_DIR)
# 1-min from 1-sec
minutes_df = seconds_df.resample("1min", label="left", closed="left").agg({
    "open": "first", "high": "max", "low": "min",
    "close": "last", "volume": "sum",
}).dropna()
# 5-min from 1-min
five_min_df = minutes_df.resample("5min", label="left", closed="left").agg({
    "open": "first", "high": "max", "low": "min",
    "close": "last", "volume": "sum",
}).dropna()
# 30-min from 5-min
thirty_min_df = five_min_df.resample("30min", label="left", closed="left").agg({
    "open": "first", "high": "max", "low": "min",
    "close": "last", "volume": "sum",
}).dropna()
```

`label="left"` plus `closed="left"` matches the existing nb_lib
`to_minutes` convention (`prj3_canonical_alpha.py:164-178`). The
bar at index `t` covers `[t, t + duration)`.

### 3.3 At-T query semantics

When evaluating signal at 1-second close T:

```python
# Most-recent-completed bar from any higher timeframe:
#   bars whose left-edge label + duration <= T
last_30m = thirty_min_df[thirty_min_df.index + pd.Timedelta(minutes=30) <= T].iloc[-1]
last_5m  = five_min_df[five_min_df.index + pd.Timedelta(minutes=5) <= T].iloc[-1]
last_1m  = minutes_df[minutes_df.index + pd.Timedelta(minutes=1) <= T].iloc[-1]
```

This formulation is auditable per the 4-surface lookahead pattern
(`_METHODOLOGY_repertoire.md` Appendix A): signal_ts vs
decision-knowability check passes when every read uses the
"label + duration ≤ T" gate.

---

## 4. Phase 1 — 30-minute trend qualification

### 4.1 Inputs

At signal moment T:

- Last completed 30-min bar's `close`
- 30-min EMA(20) computed on closes through last completed bar
- 30-min EMA(50) computed on closes through last completed bar
- 30-min VWAP for the current RTH session through last completed
  bar (anchor: today's 09:30 ET)

### 4.2 Trend qualification (LONG)

ALL three must hold on the last completed 30-min bar:

1. `last_30m.close > EMA20_at_last_30m`
2. `EMA20_at_last_30m > EMA50_at_last_30m`
3. `last_30m.close > VWAP_at_last_30m`

### 4.3 Trend qualification (SHORT)

Symmetric:

1. `last_30m.close < EMA20_at_last_30m`
2. `EMA20_at_last_30m < EMA50_at_last_30m`
3. `last_30m.close < VWAP_at_last_30m`

### 4.4 Runtime assertion

```python
assert last_30m.name + pd.Timedelta(minutes=30) <= T, (
    f"30-min lookahead violation: bar at {last_30m.name} not yet closed at T={T}"
)
assert not pd.isna(EMA20_at_last_30m), "EMA20 NaN at signal moment"
assert not pd.isna(EMA50_at_last_30m), "EMA50 NaN at signal moment"
```

**Warmup**: EMA(50) requires ≥50 prior 30-min bars. The strategy
SKIPS the first day of in-sample window for warmup. Cross-day EMA
state carries forward (no per-day reset for EMAs); VWAP is
session-anchored and resets at 09:30 each day.

### 4.5 Pre-committed values + rationale

- EMA(20) period: standard short-trend reference, ~10 hours of
  30-min data; pre-commits to "recent trend" without daily-bias
  flicker.
- EMA(50) period: standard medium-trend reference, ~25 hours;
  pre-commits to "multi-session bias."
- VWAP anchor: session-anchored 09:30 ET (matches nb_lib's
  default RTH VWAP).
- All three conditions required: removes single-indicator-alignment
  noise; trades only when 30-min frame is unambiguously biased.

---

## 5. Phase 2 — 5-minute regime gates

### 5.1 Indicators (computed on last completed 5-min bar)

- `ATR(20)` Wilder smoothing on 5-min bars (`nb_lib.indicators.ATR`)
- `ATRPercentile` over trailing 60 RTH sessions
  (`nb_lib.indicators.ATRPercentile` with `window=60, period=20`)
- `ChoppinessIndex(14)` on 5-min bars
  (`nb_lib.indicators.ChoppinessIndex`)

### 5.2 Gate conditions (must hold; otherwise SKIP)

```
0.50 ≤ ATR_percentile < 0.90
ChoppinessIndex < 45
```

### 5.3 Runtime assertions

```python
assert last_5m.name + pd.Timedelta(minutes=5) <= T, (
    f"5-min lookahead violation at {last_5m.name} vs T={T}"
)
assert 0.0 <= atr_percentile <= 1.0, f"ATR percentile out of range: {atr_percentile}"
assert 0.0 <= choppiness <= 100.0, f"Choppiness out of range: {choppiness}"
assert atr_5m > 0.0, "ATR cannot be zero at signal evaluation"
```

### 5.4 Pre-committed values + rationale

- `ATR(20)` Wilder: standard volatility measure; period 20 ≈ 100
  minutes of 5-min data, sufficient for stable estimate.
- `ATRPercentile window=60` RTH sessions: ~3 trading months of
  context; long enough to span vol-regime cycles.
- Lower bound 0.50: median + above; below this, ATR-scaled
  brackets are too tight for realistic price action.
- Upper bound 0.90: ceiling at top decile; extreme-vol days are
  excluded because bracket geometry breaks down (the 1.25×ATR
  stop becomes too wide for risk-dollar sizing to produce
  realistic contract counts).
- ChoppinessIndex `< 45`: choppy markets (CI > ~50) lack the
  directional persistence the strategy assumes. 45 is the Tier C
  ceiling (Section 9) — anything beyond is gated out.

---

## 6. Phase 3 — 5-minute pullback detection

### 6.1 Episode definition

A **pullback episode** begins when, after the last fresh trend
qualification (Phase 1 conditions become true), price first
touches one of the dynamic 5-min references:

- `EMA(20)` on 5-min bars
- 5-min VWAP (session-anchored, same as Phase 1's 30-min VWAP at
  the 09:30 anchor, but recomputed on 5-min bar weights)

A "touch" for LONG setup: any 5-min bar's `low ≤ ref AND
high ≥ ref` (the bar straddles or crosses ref). For SHORT:
symmetric.

The episode ENDS when either:
1. Price returns above (longs) / below (shorts) BOTH refs for
   ≥ 3 consecutive 5-min bars without re-touching during that
   span → "trend resumed cleanly without continuation entry"; OR
2. Trend qualification (Phase 1) breaks → "trend invalidated"

### 6.2 Reference-touch tracking

During an active episode, maintain a per-episode flag:

```python
episode = {
    "ema20_touched": bool,
    "vwap_touched": bool,
    "start_5m_ts": Timestamp,
    "trend_dir": "long" | "short",
    "trend_ts": Timestamp,  # when trend qualification became true
}
```

Tier classification (Section 9) reads these flags AT signal
moment T.

### 6.3 Pullback reference priority (for watch-window validation)

Priority for "which ref defines the pullback level":

1. If both `ema20_touched=True` AND `vwap_touched=True`:
   prefer VWAP (statistically stronger reference; matches
   convention in `_METHODOLOGY_repertoire.md` Section 8
   indicator-catalog VWAP entry).
2. If only EMA20 touched: use EMA20.
3. If only VWAP touched: use VWAP.

The chosen reference value used in Section 8's watch window is
the value at the LAST COMPLETED 5-min bar at signal moment T.

### 6.4 Runtime assertions

```python
assert episode["start_5m_ts"] <= T, "episode started in the future"
assert episode["trend_ts"] <= episode["start_5m_ts"], (
    "trend qualified after pullback episode began — order violation"
)
```

---

## 7. Phase 4 — 1-minute reversal candle

### 7.1 Definition for LONGS

A 1-min bar ending at timestamp T_1m is a reversal candle if ALL:

1. `close > open` (positive body)
2. `close > prior_1m.close` (higher close than prior 1-min bar)
3. `low ≤ pullback_ref + 0.25 × atr_5m AND low ≥ pullback_ref - 0.25 × atr_5m`

where `atr_5m` is the `ATR(20)` value from the last completed
5-min bar at T_1m, and `pullback_ref` is the value from Section
6.3 selected at T_1m.

### 7.2 Definition for SHORTS

Symmetric:

1. `close < open` (negative body)
2. `close < prior_1m.close` (lower close)
3. `high ≥ pullback_ref - 0.25 × atr_5m AND high ≤ pullback_ref + 0.25 × atr_5m`

### 7.3 Signal moment T

T = the 1-min reversal bar's RIGHT-EDGE timestamp (i.e., the close
of the reversal bar). This is the lookahead-correct definition:
the bar's close is observable at its right edge; the watch window
begins at T.

### 7.4 Runtime assertion

```python
assert last_1m.name + pd.Timedelta(minutes=1) == T, (
    f"reversal bar timestamp mismatch: {last_1m.name} + 1min != T={T}"
)
```

### 7.5 Pre-committed values + rationale

- `0.25 × ATR` proximity for the low/high near pullback_ref:
  ensures the reversal candle's wick actually visited the
  reference zone, not just closed near it. 0.25 chosen to be
  generous enough to catch genuine reactions without admitting
  "bar happened to be in the area without testing the ref."

---

## 8. Phase 5 — Watch window + entry timing

### 8.1 Watch window

After the 1-min reversal candle closes at T:

- Begin a 60-second watch window covering 1-second bars in
  `[T, T + 60s)`.
- During the watch: monitor each 1-second bar's CLOSE for the
  skip condition.

### 8.2 Skip condition

For LONGS:
- If any 1-sec bar's `close < pullback_ref` (the chosen reference
  from Section 6.3), SKIP the entry. The trade thesis is
  invalidated; price moved against the setup.

For SHORTS:
- If any 1-sec bar's `close > pullback_ref`, SKIP.

If skip condition fires at any second within the watch window,
the entire signal is abandoned (no entry, no record). The day's
remaining minutes can produce a fresh signal (new reversal candle
+ new watch window) but the strategy MAY operate at-most-once-per
pullback-episode (Section 8.4 below).

### 8.3 Entry fill

If watch window completes without skip:

- Entry fill at the 1-sec bar that closes at `T + 60 seconds`
  (inclusive boundary).
- Use `nb_lib.execution.resolve_entry_fill` with
  `fill_at_signal_plus_n_seconds=60` (or equivalent direct-index
  pattern documented in `nb_lib/execution.py`).
- Entry price = that 1-sec bar's `close`.
- Entry side: LONG or SHORT per the trend direction.

### 8.4 One signal per pullback episode

Per pullback episode (Section 6.1), the strategy fires AT MOST
ONE entry. Whether that entry hits TP/SL/EOD/compliance, the
episode is closed for new signals. The next signal opportunity
requires a fresh pullback episode (which requires Phase 1 trend
to either remain qualified across an end-of-episode return or
to be re-qualified after a break).

### 8.5 Runtime assertions

```python
assert watch_start_ts == T, "watch window must start at signal T"
assert watch_end_ts == T + pd.Timedelta(seconds=60), "watch window end mismatch"
assert entry_bar.name >= T + pd.Timedelta(seconds=59), (
    "entry fill must be at or after T+60 boundary"
)
```

---

## 9. Position sizing math

### 9.1 5-tier conviction classifier

Evaluated at signal moment T, using indicator values from the
last completed 5-min bar:

| Tier | ATR percentile ≥ | ChoppinessIndex < | Refs touched in episode |
|---|---|---|---|
| S+ | 0.85 | 28 | both EMA20 AND VWAP |
| S  | 0.75 | 32 | both EMA20 AND VWAP |
| A  | 0.65 | 38 | single (EMA20 XOR VWAP) |
| B  | 0.55 | 42 | single |
| C  | 0.50 | 45 | single |

Classifier algorithm (deterministic, top-down):

```python
def classify_tier(atr_pct, chop, ema_touched, vwap_touched):
    both = ema_touched and vwap_touched
    single = (ema_touched ^ vwap_touched)  # XOR
    if atr_pct >= 0.85 and chop < 28 and both:
        return "S+"
    if atr_pct >= 0.75 and chop < 32 and both:
        return "S"
    if atr_pct >= 0.65 and chop < 38 and single:
        return "A"
    if atr_pct >= 0.55 and chop < 42 and single:
        return "B"
    if atr_pct >= 0.50 and chop < 45 and single:
        return "C"
    return None  # SKIP signal
```

If `classify_tier(...)` returns None, the entire signal is
SKIPPED (no entry).

### 9.2 Vol multiplier

```python
def vol_multiplier(atr_pct):
    return 0.7 if atr_pct >= 0.80 else 1.0
```

### 9.3 Base risk by tier

| Tier | Base risk ($) |
|---|---|
| S+ | 900 |
| S  | 700 |
| A  | 500 |
| B  | 350 |
| C  | 250 |

### 9.4 Mechanic 1 (intraday cushion sizing)

```python
intraday_balance = tracker.balance + position_pnl_dollars  # account_value at T
cushion = intraday_balance - tracker.floor
if cushion > 2000:
    extra_room = min(cushion - 2000, 1500)  # cap at +$1500 above starting cushion
    intraday_adj = 1.0 + (extra_room / 5000.0)
else:
    intraday_adj = 1.0
# Range: [1.00, 1.30]
```

The starting cushion at $50,000 balance and $48,000 floor is
$2,000; adjustment kicks in once cushion exceeds that.

### 9.5 Mechanic 2 (post-lock cushion sizing)

```python
if tracker.is_locked():  # PA-phase, peak >= 52100
    post_lock_cushion = tracker.balance - tracker.floor  # floor pinned at 50100
    bonus = min((post_lock_cushion - 2000) / 3000.0, 0.50)
    post_lock_adj = 1.0 + max(0.0, bonus)
else:
    post_lock_adj = 1.0
# Range: [1.00, 1.50]
```

Pre-lock (eval phase OR PA phase before peak reaches $52,100),
post_lock_adj = 1.0 (neutral).

### 9.6 Combined risk dollars

```python
risk_dollars = base_risk[tier] * vol_multiplier(atr_pct) * intraday_adj * post_lock_adj
```

Theoretical bounds:

- Minimum: Tier C × Vol Hi (0.7) × intraday_adj=1.0 × post_lock_adj=1.0
  = $250 × 0.7 = **$175**
- Maximum: Tier S+ × Vol Mid (1.0) × intraday_adj=1.30 × post_lock_adj=1.50
  = $900 × 1.30 × 1.50 = **$1,755**

Both bounds asserted at runtime (Section 12).

### 9.7 Contract sizing

```python
stop_distance_pts = 1.25 * atr_5m  # from Section 10
risk_per_contract = stop_distance_pts * 2.0  # $2/pt for MNQ
contracts = max(1, int(round(risk_dollars / risk_per_contract)))
contracts = min(contracts, tracker.preset["max_contracts_mnq"])
```

- Eval cap (`apex_50k_eod_eval`): 60 MNQ
- PA Level 1 cap (`apex_50k_eod_pa`): 20 MNQ

If the math produces fewer than 1 contract, the trade fires at 1
(minimum). If it exceeds the cap, the cap binds.

### 9.8 Pre-committed values + rationale

- Tier thresholds (0.50/0.55/0.65/0.75/0.85 for ATR%; 28/32/38/42/45
  for Choppiness): round-number-preferred per repertoire Section 1
  Level-2 safeguards. NOT to be tuned during testing.
- Base risk ladder ($250/$350/$500/$700/$900): geometric-ish
  progression. Tier C is roughly half of B, etc. — pre-committed
  scaling.
- Vol multiplier (0.7 above 0.80 ATR%; else 1.0): single-threshold
  multiplier per repertoire Section 1 Level 2 minimal-parameter
  guidance.
- Mechanic 1 cap ($1,500 above starting cushion; +30% max): the
  cap prevents runaway sizing if balance grows materially.
- Mechanic 2 +50% max: lock state means cushion is durable; bigger
  bonus warranted.
- All values are NEW and untested. By design — they cannot be
  tuned during testing per the curve-fit-risk acknowledgment.

---

## 10. TradeLifecycle parameters

### 10.1 Brackets (ATR-scaled, locked at signal moment)

ATR = `atr_5m` value at signal moment T (Section 5 last completed
5-min bar). The same ATR value is used for both stop and target
distances; bracket distances are locked at T and do NOT update
during the trade (no trailing).

For LONG entry at `entry_price`:

- Stop: `entry_price - 1.25 × ATR`
- TP1: `entry_price + 0.75 × ATR`, closes 50% of contracts
- TP2: `entry_price + 2.50 × ATR`, closes remaining 50% (runner)
- BE arm trigger: when intrabar high reaches `entry_price + 0.50 × ATR`,
  move stop to `entry_price + 0.25 ticks` (1 tick = 0.25 pt for MNQ,
  so this is `entry_price + 0.0625`); apply ONCE per trade

For SHORT entry: symmetric (`-` becomes `+` and vice versa).

### 10.2 Friction (BAND_B parameters)

Matches the tested-rejected fleet (consistency across canonical
alpha builds):

- `stop_overshoot`: 1.16 pt (added to stop distance on stop-fills)
- `tp_slippage`: 0.0 pt (limit-style fills)
- `commission_per_contract_per_side`: $0.35

### 10.3 Runner mechanics

After TP1 fills:

- Remaining 50% of contracts trail OR run to TP2 unmodified by
  the BE arm (BE arm fires on the original position if not yet
  filled; once TP1 fills, the BE move is the same logic but
  applies to the runner's stop).
- BE arm applies to the runner's stop when intrabar reaches the
  trigger; stop becomes `entry_price + 0.25 ticks` for longs.

### 10.4 Pre-committed values + rationale

- 1.25 × ATR stop: ~Wilder-style; allows reasonable noise
  absorption while keeping per-contract risk bounded.
- 0.75 × ATR TP1: 0.6× of stop distance; provides ~50% win-rate
  contribution if signal has any edge; reduces variance.
- 2.50 × ATR TP2: 2× stop distance (1.25 × 2); ~1R partial + 2R
  runner gives ~1.5R blended target.
- 0.50 × ATR BE trigger: midway to TP1; preserves option value
  while protecting from full-stop draws.
- 0.25 tick BE offset: tiny positive offset prevents being-stopped-
  out-at-exact-breakeven (friction-aware).

---

## 11. Compliance and EOD handling

### 11.1 Compliance check construction

```python
from nb_lib.compliance import (
    ComplianceTracker, get_preset,
    make_combined_compliance_check,
    make_dll_compliance_check,
    make_drawdown_compliance_check,
    make_eod_compliance_check,
)
from nb_lib.calendar import TradingCalendar

calendar = TradingCalendar()
preset = get_preset("apex_50k_eod_eval")
tracker = ComplianceTracker(preset, calendar=calendar)

compliance_check = make_combined_compliance_check([
    make_dll_compliance_check(tracker, preset),
    make_drawdown_compliance_check(tracker, preset),
    make_eod_compliance_check(tracker, preset),
])
```

`compliance_check` is passed to `TradeLifecycle`'s `step()` for
intraday force-exits (DLL, drawdown, EOD-flat).

### 11.2 Eval → PA transition (optional, mid-stream)

After each EOD `tracker.record_eod(date, closing_balance, ts)`,
check:

```python
if tracker.is_eval_passed():
    pa_tracker = tracker.advance_to_pa()
    # Replace `tracker` with `pa_tracker` for subsequent days.
    # Reconstruct compliance_check with the new tracker.
    pa_preset = pa_tracker.preset
    compliance_check = make_combined_compliance_check([
        make_dll_compliance_check(pa_tracker, pa_preset),
        make_drawdown_compliance_check(pa_tracker, pa_preset),
        make_eod_compliance_check(pa_tracker, pa_preset),
    ])
    tracker = pa_tracker
```

After transition, subsequent sizing reads use `pa_tracker` (which
becomes `tracker`). `pa_tracker.is_locked()` returns True once
PA peak reaches $52,100, activating Mechanic 2.

### 11.3 EOD-flat behavior

`make_eod_compliance_check` enforces the configured
`eod_flat_seconds_before_close` (default 90s; gives 15:58:30 ET
on regular days; 12:58:30 on half-days via
`calendar.get_session_close(date)`).

Any open position is force-exited at the EOD compliance bar's
`close`. The exit reason is `eod_compliance` (vs lifecycle's
operational `eod`, which is bypassed when compliance fires
first).

### 11.4 Pre-committed values + rationale

- Apex 50K EOD Rithmic preset: matches tested-fleet baseline;
  apples-to-apples comparison with prior strategies' results.
- 90-second EOD-flat buffer: matches preset default.
- Eval → PA transition: optional; only fires if and when the
  strategy generates enough P&L to cross $53,000. If never
  triggered, strategy operates in eval mode entire window.

---

## 12. Runtime assertions (lookahead-free per timeframe)

Per the methodology-repertoire's runtime-assertions-in-production
pattern (Appendix A), the implementation MUST include the following
assertions in production code (NOT just in tests). Each fires at
every signal-evaluation moment.

### 12.1 Timeframe staleness

```python
assert last_30m.name + pd.Timedelta(minutes=30) <= T
assert last_5m.name + pd.Timedelta(minutes=5) <= T
assert last_1m.name + pd.Timedelta(minutes=1) <= T
```

### 12.2 Indicator sanity

```python
assert 0.0 <= atr_percentile <= 1.0
assert 0.0 <= choppiness <= 100.0
assert atr_5m > 0.0
assert not pd.isna(ema20_30m)
assert not pd.isna(ema50_30m)
assert not pd.isna(vwap_30m)
```

### 12.3 Tier classification consistency

```python
tier = classify_tier(atr_pct, chop, ema_touched, vwap_touched)
if tier == "S+":
    assert atr_pct >= 0.85 and chop < 28 and ema_touched and vwap_touched
if tier == "S":
    assert atr_pct >= 0.75 and chop < 32 and ema_touched and vwap_touched
if tier == "A":
    assert atr_pct >= 0.65 and chop < 38 and (ema_touched ^ vwap_touched)
if tier == "B":
    assert atr_pct >= 0.55 and chop < 42 and (ema_touched ^ vwap_touched)
if tier == "C":
    assert atr_pct >= 0.50 and chop < 45 and (ema_touched ^ vwap_touched)
```

### 12.4 Sizing sanity

```python
assert 175.0 <= risk_dollars <= 1755.0, f"risk_dollars out of bounds: {risk_dollars}"
assert 1 <= contracts <= tracker.preset["max_contracts_mnq"]
assert stop_distance_pts > 0
```

### 12.5 Bracket consistency

```python
if side == "long":
    assert stop_price < entry_price < tp1_price < tp2_price
else:
    assert stop_price > entry_price > tp1_price > tp2_price
```

### 12.6 Trade lifecycle invariants

```python
assert lifecycle.entry_ts >= signal_ts + pd.Timedelta(seconds=60)
assert lifecycle.exit_ts > lifecycle.entry_ts
```

---

## 13. OOS reservation policy

### 13.1 Window definition

- **In-sample**: 2024-08-01 → 2026-01-31 (inclusive, US/Eastern
  RTH dates)
- **Held-out OOS**: 2026-02-01 → 2026-05-04 (inclusive, US/Eastern
  RTH dates) — **DO NOT load during in-sample work**

### 13.2 Implementation guard

```python
OOS_START = pd.Timestamp("2026-02-01", tz="US/Eastern")
def assert_in_sample(df):
    assert df.index.max() < OOS_START, (
        f"In-sample run loaded data through {df.index.max()}; "
        f"OOS boundary is {OOS_START}. Use a date filter or trim the "
        f"loader's date range before calling this function."
    )
```

This assertion fires at the top of the in-sample test runner.

### 13.3 Post-test policy

If in-sample shows promise (PF ≥ 1.5 OR Apex-deployable result):

- **MANDATORY**: held-out validation on the OOS window with
  parameters FROZEN as-spec'd. No re-tuning.
- The OOS run loads `start_date="2026-02-01"`, `end_date="2026-05-04"`,
  carries forward the in-sample-end `tracker` state, and reports a
  separate results file.
- If OOS PF < 1.0 (or otherwise materially worse than in-sample),
  the result is "in-sample noise, no edge" and the candidate
  status moves to `tested-rejected`.
- If OOS PF ≥ 1.0 AND in-sample PF ≥ 1.5, the result is
  "preliminary edge candidate" and a third-cohort multistart
  validation is required before deployment consideration.

---

## 14. Stage-by-stage iteration gates (upcoming implementation)

Each stage has a HARD-HALT condition. Test count must hold at
298/298 throughout (no test additions in the implementation
iteration unless explicitly noted).

### Stage A: Multi-timeframe data prep
- Implement bar-resampling helper (use existing `to_minutes`
  convention; extend to 5m + 30m).
- Verify alignment: every 5-min bar contains exactly 5 minutes of
  underlying 1-min bars; every 30-min contains 6 × 5-min.
- HALT if any aggregated bar has fewer than the expected sub-bar
  count (data-completeness gate).

### Stage B: Trend qualification
- Compute 30-min EMA(20), EMA(50), VWAP series.
- Add runtime assertions on EMA freshness and VWAP anchor.
- HALT-LOOKAHEAD-VIOLATION if 30-min bar's right-edge > T.

### Stage C: Regime gates
- Compute 5-min ATR(20), ATRPercentile(60), ChoppinessIndex(14).
- HALT-RANGE-VIOLATION if any indicator out of expected range.

### Stage D: Pullback detection
- Implement episode tracking (begin/end semantics).
- Maintain reference-touch flags.
- HALT-ORDER-VIOLATION if trend_ts > episode start_ts.

### Stage E: 1-minute reversal candle
- Implement candle pattern detection per Section 7.
- HALT-MATCH-FAILURE if test cases reveal off-by-one or missing
  conditions.

### Stage F: Watch window + entry fill
- Implement 60-second watch with 1-sec skip condition.
- Use `resolve_entry_fill` for the actual T+60 fill price.
- HALT-FILL-MECHANIC-VIOLATION if entry timestamp is < T+60.

### Stage G: Tier classifier
- Implement deterministic `classify_tier`.
- HALT-CLASSIFY-INCONSISTENCY if tier returned but conditions
  not met (assertion in Section 12.3).

### Stage H: Vol multiplier + Mechanic 1 + 2
- Implement `vol_multiplier`, `intraday_adj`, `post_lock_adj`.
- Wire to tracker queries.
- HALT-SIZING-OUT-OF-BOUNDS if risk_dollars outside [175, 1755].

### Stage I: Contract sizing
- Implement `risk_dollars / (stop_distance × $2)` math.
- Apply contracts cap.
- HALT-CONTRACT-INVALID if contracts < 1 or > preset cap.

### Stage J: TradeLifecycle integration
- Build `TradeLifecycle` with brackets, BE arm, friction.
- HALT-BRACKET-VIOLATION if stop/TP order is wrong.

### Stage K: Compliance integration
- Build combined compliance check; wire to lifecycle.
- Implement optional eval→PA transition logic.
- HALT-TRANSITION-FAILURE if `advance_to_pa()` raises
  unexpectedly.

### Stage L: In-sample test
- Run full 2024-08-01 → 2026-01-31 window.
- Generate results CSV.
- Apply Section 13 OOS guard to verify no OOS data was loaded.

---

## 15. Expected outcomes (honest priors)

Per Section 0.3:

- **60%**: no in-sample edge. Strategy's six adaptive layers
  fail to find continuation signal at this granularity, mirroring
  PRJ_3's raw-signal refutation.
- **25%**: in-sample edge → OOS failure. The six adaptive layers
  curve-fit to in-sample noise; OOS reveals it.
- **10%**: in-sample edge → OOS survival. Genuine
  regime-conditioned continuation edge. Proceed to multistart
  validation cohort before deployment consideration.
- **5%**: in-sample edge with execution issues. Bracket mechanics
  break (0.75 × ATR TP1 fills too tightly OR watch-window
  skip-rate is too aggressive).

### 15.1 What signals "genuine edge"

- In-sample PF ≥ 1.5 across a non-trivial sample size (n ≥ 50).
- In-sample edge holds across multiple ATR-regime sub-cohorts
  (e.g., compare H1 vs H2 of in-sample; results should be
  directionally similar in PF).
- OOS PF ≥ 1.0 in the held-out window with parameters frozen.

### 15.2 What signals "execution mechanics breaking"

- TP1 fills excessively often (> 80% of trades touch 0.75×ATR
  before stop) — TP1 distance too tight; bracket geometry is
  the actual generator of the apparent edge, not signal quality.
- Watch-window skip rate > 70% — signal fires too often and gets
  rejected; the signal moment is leading rather than confirming.
- BE arm fires before TP1 on > 50% of trades — the BE-arm and
  TP1 distance need re-design (NOT for this iteration; defer).

### 15.3 What signals "selection bias"

- In-sample PF > 2.0 but OOS PF < 0.5: classic in-sample
  curve-fit signature. Treat as definitive no-edge.
- In-sample edge concentrated in 1-2 specific tier × vol combos
  (e.g., S+/Vol Mid alone accounts for 90% of P&L): the strategy
  works only in narrow regime; not robust.

---

## 16. What this iteration validates beyond strategy edge

Regardless of strategy outcome, the implementation iteration
validates and produces reusable infrastructure:

1. **Multi-timeframe coordination**: 30m + 5m + 1m + 1s
   bar-availability discipline. Pattern reusable for any future
   multi-timeframe strategy.

2. **5-tier conviction classifier scaffold** (Section 9.1): the
   `classify_tier(atr_pct, chop, ema_touched, vwap_touched)`
   function pattern is reusable; tier thresholds and base risk
   ladder become parameter inputs for any new tiered strategy.

3. **2-level volatility multiplier** (Section 9.2): the
   single-threshold pattern is reusable.

4. **Cushion-based sizing mechanics**: Mechanic 1 (intraday
   cushion) and Mechanic 2 (post-lock cushion) become the
   canonical implementation of cushion-aware risk adjustment.
   Reuses the simulator-extension methods (`is_locked()`,
   `is_eval_passed()`, `advance_to_pa()`).

5. **Watch-window validation pattern**: 60-second post-signal
   1-second monitoring with skip-on-adverse-close pattern.
   Reusable for any signal that benefits from a brief settle
   window.

6. **Fixed-risk-dollar sizing in production**: first nb_lib-native
   canonical strategy using `risk_dollars / (stop_distance ×
   point_value)` sizing. The tested-rejected fleet used
   fixed-contract sizing. This iteration establishes the
   risk-dollar convention.

7. **Multi-timeframe lookahead audit pattern**: extends the
   4-surface lookahead audit (PRJ_3 origin) to the multi-timeframe
   case. The pattern: at signal moment T, every cross-timeframe
   read must satisfy `bar_left_edge + bar_duration ≤ T`. This
   pattern becomes the methodology repertoire's Appendix A entry
   for "multi-timeframe-lookahead-audit" once this iteration
   completes.

8. **Eval → PA transition exercising the new simulator extension**:
   first production strategy using `is_eval_passed()` +
   `advance_to_pa()`. End-to-end shake-out of the simulator
   extension iteration's deliverables.

If strategy edge is absent (60% expected), this iteration's value
is the infrastructure. If edge appears, the infrastructure is
secondary to the strategy result, but the infrastructure is still
banked.

---

**End of spec.** Pre-committed parameters listed in Sections 4–11
are LOCKED. No tuning during implementation or testing. Any
deviation requires a separate iteration with explicit operator
sign-off.
