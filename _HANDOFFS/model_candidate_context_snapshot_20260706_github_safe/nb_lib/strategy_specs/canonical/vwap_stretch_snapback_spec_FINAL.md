---
status: "spec-drafted"
---

# VWAP Stretch Snapback Canonical Alpha — Strategy Specification (FINAL)

**Strategy ID**: vwap_stretch_snapback
**Version**: 1.0
**Status**: spec-drafted (implementation pending)
**Lineage**: nb_lib-native; first mean-reversion canonical alpha
**Date created**: 2026-05-12
**Date updated**: 2026-05-12
**Authors**: Strategic Claude + operator (Autoclaude spec-drafting iteration)
**Library version**: nb_lib v2.3 (tests 310/310 at spec drafting moment)
**Verification trail**: candidate wiki entry
`nb_lib/strategy_specs/candidates/vwap_stretch_snapback.md` →
this FINAL spec → upcoming implementation iteration.

---

## 0. Methodology framing (read first)

### 0.1 Signal-class hypothesis test

The 6-fleet pattern established by 2026-05-12 refutes
trend-continuation on MNQ at 1-minute / 5-minute granularity: six
nb_lib-native canonical alphas (noise_brk, prj3, ema_trend,
atr_regime_pullback_continuation, atr_regime_pullback_tight_target,
and one prior fleet member) have all converged on
Apex-eval-failure at approximately $-1.6K to $-2.1K cumulative on
the in-sample window, account FAILED via drawdown breach. The
convergence suggests the failure is a property of the design
space at this stage, not a property of any specific signal.

This strategy tests **mean-reversion as a fundamentally different
hypothesis**. The signal-generation mechanism is structurally
distinct from every prior nb_lib-native canonical:

| Family | Signal class | Status |
|---|---|---|
| noise_brk | Breakout (9:36 noise-band) | tested-rejected |
| prj3 | Fractal pullback continuation | tested-rejected |
| ema_trend | EMA-slope continuation | tested-rejected |
| atr_regime_pullback_continuation | Multi-timeframe regime-gated continuation | tested-rejected |
| atr_regime_pullback_tight_target | Single-target fork of above | tested-rejected |
| **vwap_stretch_snapback** | **Mean-reversion (VWAP stretch + rejection)** | **this spec** |

Either outcome is informative:

- If `vwap_stretch_snapback` shows in-sample edge → genuine
  cross-class result; mean-reversion may work at this granularity
  where trend-continuation does not.
- If it fails → the negative-edge hypothesis (the
  fleet's failure is a property of the methodology's adaptive-layer
  approach, not the signal class) gains weight, suggesting deeper
  methodology revision is needed before more candidate
  generation.

### 0.2 Risk tier values are PLACEHOLDER — acknowledged

The session-vol-scaled risk ladder ($200 / $350 / $500 / $700
across the four ATR-percentile quartiles) uses **round-number
values chosen for simplicity**. They are NOT calibrated from data
analysis. Future library-level calibration research could refine
these via legitimate methodology (e.g., Version A1: pure ATR
distribution statistics targeting stable per-trade dollar variance).

For this iteration, the placeholder values are sufficient because:

1. Round numbers are less curve-fit-prone than tuned values.
2. The strategy's hypothesis under test is **signal edge**, not
   risk-tier optimization.
3. If the signal has edge, the exact risk-tier values barely matter
   (the edge would survive across plausible perturbations of the
   ladder).
4. If the signal has no edge, no risk-tier configuration rescues it.

The risk ladder is therefore explicitly **uncalibrated and locked
for this iteration**. No tuning permitted during implementation or
testing.

### 0.3 Adaptive layers and curve-fit risk

The strategy uses **four adaptive layers** (intentionally fewer
than atr_regime's six):

1. ATR-scaled stops (Level 1, continuous adaptive)
2. Level-based targets — psychological 50/100-point anchors
   (Level 2, discrete)
3. Session-vol-scaled risk tiers (Level 2, four discrete tiers
   on ATR percentile)
4. Mechanic 1 — intraday cushion sizing (Level 1, continuous
   adaptive)

By the methodology repertoire's framework
(`nb_lib/strategy_specs/candidates/_METHODOLOGY_repertoire.md`
Section 1), this is Level 1 + Level 2 territory but with fewer
parameters than the atr_regime spec. Every parameter is
**PRE-COMMITTED**. No tuning during implementation or testing.

If in-sample results look promising, **held-out OOS validation
is MANDATORY** (Section 13) before deployment consideration.
The OOS window 2026-02-01 → 2026-05-04 is reserved and may NOT
be loaded during in-sample work.

### 0.4 Expected outcome priors (honest)

- **50%**: no in-sample edge. The negative-edge hypothesis extends
  from trend-continuation to mean-reversion at this granularity.
- **25%**: in-sample edge fails OOS. Selection on noise; mean-
  reversion's apparent in-sample signal does not survive.
- **15%**: in-sample edge survives OOS. Mean-reversion has real
  edge at this granularity where trend-continuation does not.
- **10%**: execution-mechanic break or signal frequency too low.
  Bracket geometry fails (e.g., psychological-level TP1 lands
  outside the entry-VWAP corridor too often, or signal frequency
  is < 0.5 trades/day average leading to insufficient n).

### 0.5 Simplicity over complexity (intentional)

The strategy uses **fewer adaptive layers than atr_regime** by
design. Tests whether a simpler architecture with a different
signal class produces edge. If signal class is the determinant of
edge, the simpler design suffices. If layer count is the
determinant, this candidate should fail similarly to atr_regime
even with a different signal — and that itself is information.

### 0.6 What this iteration validates beyond strategy edge

Regardless of edge outcome, the upcoming implementation iteration
exercises and validates:

- First nb_lib-native canonical mean-reversion signal pipeline
- VWAP-anchored target geometry as a reusable bracket primitive
- Psychological-level (50/100-pt) target-anchor algorithm
- Session-vol-scaled risk tier scaffold (placeholder values now,
  reusable structure for future calibrated versions)
- Simpler 4-layer adaptive design (vs atr_regime's 6) as a
  reference point in the layer-count / edge calibration

---

## 1. Spec metadata

- **Name**: VWAP Stretch Snapback Canonical Alpha
- **Strategy ID**: vwap_stretch_snapback
- **Version**: 1.0
- **Created**: 2026-05-12
- **Updated**: 2026-05-12
- **Status**: spec-drafted (implementation pending)
- **In-sample window**: 2024-08-01 → 2026-01-31 (RTH sessions
  only, US/Eastern)
- **OOS reserved window**: 2026-02-01 → 2026-05-04 (DO NOT load
  during in-sample work)
- **Library version**: nb_lib v2.3 (tests 310/310 at spec
  drafting)
- **Data source**: `nb_lib.scripts.prj3_canonical_alpha.load_seconds`
  (matches tested-fleet convention)
- **Account preset**: `apex_50k_eod_eval` (Rithmic variant);
  eval-only scope for this iteration. Mechanic 2 (post-lock
  cushion sizing) is OUT OF SCOPE; PA transition logic may
  optionally exercise the simulator-extension API end-to-end but
  no PA-phase sizing logic is implemented.

---

## 2. Signal window definitions per timeframe

The strategy operates across three timeframes simultaneously. Every
signal-evaluation moment T is anchored to a 1-minute bar close.

| Timeframe | Role | Last-completed bar at T | Max staleness |
|---|---|---|---|
| 5-minute | ATR for bracket sizing; ATR percentile | bar ending at last 5-min boundary ≤ T | up to 5 min |
| 1-minute | Primary signal — VWAP stretch, rejection candle, prior_close | bar ending exactly at T (T is bar's right-edge) | 0 (bar is T) |
| 1-second | Execution; entry fill at T+1s | bar ending exactly at T+1s | 0 |

**RTH session boundaries**: 09:30:00 – 16:00:00 US/Eastern.
Half-days: per `TradingCalendar.get_session_close(date)` (13:00 on
known half-days; EOD-flat buffer applies relative to the
calendar-provided close).

**No 30-minute trend qualification.** No multi-timeframe trend
coordination beyond using 5-min ATR for bracket sizing. The
strategy is single-timeframe-primary at 1-minute.

**Critical: "most recent COMPLETED bar".** At signal moment T (1-min
bar's right-edge), the 5-min bar used for ATR is the one ending at
the most recent 5-min boundary ≤ T. The 1-min bar evaluated at T
**is the bar that just completed** — its right-edge IS T. The
1-second bar at T+1s is strictly AFTER T (its close timestamp is T+1s).

---

## 3. Multi-timeframe bar availability + lookahead audit

### 3.1 Bar-availability mapping

At signal evaluation moment T (1-minute bar's right-edge):

| Timeframe | Last available bar | Bar close = | Why this prevents lookahead |
|---|---|---|---|
| 5-min | floor(T / 5min) - 1 | floor(T / 5min) | Bar that just completed; never the one forming. Note: if T is exactly on a 5-min boundary, the bar at [T-5min, T) is just-completed and is the bar used. |
| 1-min | bar ending at T | T | T IS the close timestamp of the just-completed 1-min bar |
| 1-sec (execution) | bar ending at T+1s | T+1s | Strictly AFTER T; observable only at T+1s |

Implementation pattern (per the established lookahead-fix
discipline from PRJ_3 and atr_regime): the `signal_ts` used to
identify any bar from a multi-bar series MUST be the **right-edge
timestamp** (bar's close).

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
```

`label="left"` plus `closed="left"` matches the existing nb_lib
convention. The bar at index `t` covers `[t, t + duration)` and is
observable only at `t + duration`.

### 3.3 At-T query semantics

When evaluating signal at 1-minute close T:

```python
# Most-recent-completed 5-min bar:
last_5m = five_min_df[five_min_df.index + pd.Timedelta(minutes=5) <= T].iloc[-1]
# The 1-min bar evaluated AT T is the bar ending at T itself:
last_1m = minutes_df.loc[T - pd.Timedelta(minutes=1)]  # left-edge label
# prior_1m for rejection-candle definition:
prior_1m = minutes_df.loc[T - pd.Timedelta(minutes=2)]
```

The 1-min bar's left-edge label is `T - 1min`; its right-edge is
`T`. This is the right bar to read because `T` is by construction
the signal-evaluation moment.

### 3.4 Lookahead audit reasoning (production-path discipline)

Per the methodology repertoire's runtime-assertions pattern, the
implementation MUST include the following audit assertions:

```python
# 5-min staleness:
assert last_5m.name + pd.Timedelta(minutes=5) <= T
# 1-min bar IS the one ending at T (right-edge identity):
assert last_1m.name + pd.Timedelta(minutes=1) == T
# prior_1m strictly precedes last_1m:
assert prior_1m.name + pd.Timedelta(minutes=1) == last_1m.name
# Entry fill bar strictly AFTER T:
# (asserted at the moment of entry-fill resolution)
```

Indicator sanity assertions (Section 12) also fire on every signal
evaluation.

---

## 4. Phase 1 — signal definition

### 4.1 Indicators (computed on most recent COMPLETED bar)

- `SessionVWAP` — session-anchored at 09:30 ET on 1-min bars
  (`nb_lib.indicators.VWAP` with anchor=`rth`)
- `SessionStdev` — cumulative stdev of 1-min closes since the
  09:30 ET session anchor (`nb_lib.indicators.SessionStdev`)
- `ATR(20)` Wilder smoothing on 5-min bars
  (`nb_lib.indicators.ATR` with period=20, smoothing="wilder")
- `ATRPercentile` over trailing 60 RTH sessions on 5-min ATR
  (`nb_lib.indicators.ATRPercentile` with `atr_period=20,
  percentile_lookback=60 RTH sessions × 78 bars/session = 4680
  bars, smoothing="wilder"`)

### 4.2 Stretch metric

At signal moment T:

```python
stretch_sigma = (last_1m.close - session_vwap_at_T) / session_stdev_at_T
```

Positive: price stretched above VWAP. Negative: stretched below.

If `session_stdev_at_T` is NaN or zero (early-session warmup),
SKIP the bar. Stretch is undefined.

### 4.3 LONG signal conditions (stretched below VWAP, reject up)

At signal moment T (1-min bar's right-edge), ALL must hold:

1. `stretch_sigma <= -2.0` (price ≥ 2σ below VWAP at last 1-min
   close)
2. Current 1-min bar is a REJECTION candle:
   - `last_1m.close > last_1m.open` (positive body)
   - `last_1m.low < prior_1m.close` (printed a lower low than the
     prior 1-min bar's close)
3. Session time gate: `09:35 ET ≤ T < 15:55 ET`
   - First 5 minutes excluded for VWAP/SessionStdev warmup +
     first-bar noise.
   - 15:55 ceiling = 5 minutes before the EOD-flat 90-second
     buffer (15:58:30 ET on regular days); avoids opening trades
     that immediately force-flat.
4. ATR regime gate: `0.10 ≤ atr_percentile ≤ 0.95`
   - Lower bound: ATR not so low that bracket geometry collapses
     into commission noise.
   - Upper bound: ATR not so high that the 1.0×ATR stop balloons
     beyond reasonable per-contract risk under fixed-risk sizing.

### 4.4 SHORT signal conditions (stretched above VWAP, reject down)

Symmetric:

1. `stretch_sigma >= +2.0`
2. Current 1-min bar is a REJECTION candle:
   - `last_1m.close < last_1m.open` (negative body)
   - `last_1m.high > prior_1m.close` (printed a higher high than
     the prior 1-min bar's close)
3. Same session time gate (09:35 ≤ T < 15:55).
4. Same ATR regime gate (0.10 ≤ atr_percentile ≤ 0.95).

### 4.5 At-most-one-trade-per-day-per-direction

Per the candidate file Section 3 (and prudent for a mean-reversion
strategy): each direction (long, short) fires **at most once per
RTH session**. After a LONG fires on a given day, no further LONG
signals are accepted for that day; SHORT remains eligible. After a
SHORT fires, no further SHORT signals for that day; LONG remains
eligible. After both have fired, the day is closed for new
signals.

This rule prevents back-to-back fade attempts when the first fade
fails (a classic mean-reversion pathology).

### 4.6 Runtime assertions (Section 12.2 sanity)

```python
assert isinstance(stretch_sigma, float)
assert atr_5m > 0.0, "ATR cannot be zero at signal evaluation"
assert 0.0 <= atr_percentile <= 1.0, f"ATR percentile out of range: {atr_percentile}"
assert pd.notna(session_vwap_at_T) and pd.notna(session_stdev_at_T)
```

### 4.7 Pre-committed values + rationale

- **2.0σ stretch threshold**: standard 2-sigma boundary for
  statistical stretch under near-normal close distributions.
  Round-number; less curve-fit-prone than tuned values.
- **Rejection-candle definition (body sign + extreme vs prior_close)**:
  the body-sign requirement ensures the candle visibly reversed
  intrabar; the extreme-beyond-prior_close requirement ensures
  the candle actually extended the stretch before reversing
  (avoids "inside-bar at the extreme" false signals).
- **09:35 lower bound on time**: 5-minute warmup for
  SessionVWAP and SessionStdev. Choosing 09:35 (one 1-min bar
  past 09:34's right-edge) gives 5 1-min closes of session data
  before stretch is measurable.
- **15:55 upper bound on time**: leaves at least 3.5 minutes for
  the trade to develop before the 15:58:30 EOD-flat compliance
  fire. Avoids "entry immediately flatted by EOD" trades that
  add commission drag without expectancy.
- **ATR percentile band 0.10-0.95**: wider than atr_regime's
  0.50-0.90 because mean-reversion can work in lower-volatility
  regimes too. Upper bound trimmed slightly below 1.0 to exclude
  the highest-vol days where intraday VWAP loses its anchor
  property.

---

## 5. Phase 2 — entry timing (T+1 second mechanic)

### 5.1 Entry fill mechanic

At signal moment T (1-min bar's right-edge timestamp; e.g.,
`pd.Timestamp("2024-09-15 10:23:00", tz="US/Eastern")`):

- Entry fills at the **next 1-second bar after T** — i.e., the
  1-sec bar whose close timestamp is **T + 1 second** (e.g.,
  `2024-09-15 10:23:01`).
- **No watch window.** This is the key simplification vs the
  atr_regime family. The 1-min rejection candle is the confirming
  bar; the immediate next 1-sec close is the entry.
- Entry price = the 1-sec bar's `close`.
- Use `nb_lib.execution.resolve_entry_fill` with appropriate
  args, OR direct index lookup of the 1-sec bar at `T + 1 second`
  (whichever pattern the implementation chooses; both are
  documented in `nb_lib/execution.py`).

### 5.2 Lookahead audit (key reasoning)

At signal moment T, the 1-min rejection bar is provably complete:
its left-edge label is `T - 1min`, right-edge is T, and the bar
was derived from 1-second OHLCV via the standard resample. The
next 1-second bar (whose left-edge label is T, close at T+1s) is
strictly AFTER T. The signal observation and the entry decision
both occur at T; the entry fill happens AT T+1s. Lookahead-clean.

### 5.3 Entry slippage

The empirical-params friction (BAND_B; Section 11) applies
entry slippage at the entry-fill bar per the standard nb_lib
convention.

### 5.4 Runtime assertion

```python
assert entry_ts == signal_t + pd.Timedelta(seconds=1), (
    f"entry_ts {entry_ts} must equal signal_t {signal_t} + 1 second"
)
```

### 5.5 Pre-committed values + rationale

- **T+1 second fill (no watch window)**: the mean-reversion thesis
  is that the rejection candle ITSELF is the reversal signal. A
  watch window would re-validate that the price didn't continue
  in the original direction during the watch — but if it did,
  the mean-reversion thesis was already wrong, and the watch
  would just add latency. The simpler immediate fill makes the
  test cleaner.

---

## 6. Brackets — Stop (ATR-scaled)

ATR = 5-min `ATR(20)` Wilder value at signal moment T (Section 4.1
indicator). Stop distance is locked at T and does NOT update
during the trade.

### 6.1 Stop placement

For LONG entry at `entry_price`:

- **Stop**: `entry_price - 1.0 × atr_5m`

For SHORT entry at `entry_price`:

- **Stop**: `entry_price + 1.0 × atr_5m`

### 6.2 Pre-committed value + rationale

- **1.0 × ATR(20) on 5-min**: matches the
  `atr_regime_pullback_tight_target` fork's stop multiple (also
  1.0x). The choice is anchored to the mean-reversion thesis:
  the stop sits beyond the stretch extreme by approximately one
  ATR, accommodating typical intraday noise without inviting
  multi-ATR adverse excursions.

### 6.3 Runtime assertion

```python
if side == "long":
    assert stop_price < entry_price
else:
    assert stop_price > entry_price
```

(Bracket-order assertion combined with TP1/TP2 in Section 8.)

---

## 7. Brackets — TP1 (psychological-level anchor)

### 7.1 TP1 algorithm

TP1 anchors to the **nearest 50-point psychological level between
entry and VWAP**, with 100-point levels emerging naturally as a
subset (every 100 is also a 50).

```python
def compute_tp1(entry_price: float, vwap: float,
                direction: str) -> float:
    """TP1 = nearest 50-point psychological level between entry
    and VWAP. If none exists in the corridor, fall back to the
    midpoint (entry + vwap) / 2.

    100-point levels are implicit (a 100-pt level is also a 50-pt
    level); the "100 weighs more" property emerges from observation
    frequency, not from algorithmic preference.
    """
    if direction == "long":
        # Long stretches BELOW VWAP, so expect entry < vwap.
        if entry_price >= vwap:
            return (entry_price + vwap) / 2.0  # degenerate fallback
        levels = psychological_levels_between(entry_price, vwap)
        if levels:
            return float(min(levels))  # first 50-pt level above entry
        return (entry_price + vwap) / 2.0
    else:  # short
        # Short stretches ABOVE VWAP, so expect entry > vwap.
        if entry_price <= vwap:
            return (entry_price + vwap) / 2.0
        levels = psychological_levels_between(vwap, entry_price)
        if levels:
            return float(max(levels))  # first 50-pt level below entry
        return (entry_price + vwap) / 2.0


def psychological_levels_between(low: float, high: float) -> list[float]:
    """All 50-point levels strictly in (low, high). 100-point
    levels are a subset (every 100 is divisible by 50).
    """
    levels = []
    start = int(low / 50) * 50 + 50
    for level in range(start, int(high) + 1, 50):
        if low < level < high:
            levels.append(level)
    return levels
```

### 7.2 TP1 fill behavior

- **50% of position closes at TP1.** (Specifically:
  `tp1_close_contracts = max(1, contracts // 2)` with the
  safeguard that `tp1_close_contracts < contracts` so the runner
  has at least 1 contract. If `contracts == 1`, no partial close
  is possible and the position runs as a single contract directly
  to TP2 or stop.)
- Remaining contracts continue toward TP2 (Section 8).

### 7.3 Pre-committed values + rationale

- **50-point psychological levels (with 100-pt as natural subset)**:
  on MNQ, 50-point levels at typical price magnitudes (18,000-21,000)
  occur every ~0.25%. Common round-number behavior at these levels
  is well-documented across price-action literature; 100-pt levels
  carry additional weight because they're observed more frequently
  (every 100 is also a 50).
- **Midpoint fallback when no level exists in the corridor**: this
  occurs when the entry-to-VWAP distance is less than 50 points
  (e.g., a small stretch in a tight session). The midpoint is a
  deterministic, geometry-only fallback that does not require an
  external reference.
- **50% partial close**: matches the prj3 / atr_regime fleet
  convention; provides ~50% win-rate contribution if the signal
  has any edge while preserving runner upside.

### 7.4 Runtime assertions

```python
assert tp1_price is not None
if direction == "long":
    assert entry_price < tp1_price <= vwap_at_signal or tp1_price == (entry_price + vwap_at_signal) / 2.0
else:
    assert vwap_at_signal <= tp1_price < entry_price or tp1_price == (entry_price + vwap_at_signal) / 2.0
```

---

## 8. Brackets — TP2 (VWAP target) and BE arm

### 8.1 TP2

- **LONG**: `tp2 = vwap_at_signal_moment` (the SessionVWAP value
  from the most recent 1-min bar at T)
- **SHORT**: `tp2 = vwap_at_signal_moment` (same)

Runner (remaining 50% after TP1 partial fires) closes at TP2.

### 8.2 BE arm

Single-shot per trade. Triggered when intrabar high (long) or low
(short) reaches the midpoint between entry and TP1:

```python
be_arm_price = entry + direction * (tp1_price - entry) / 2
# When mfe reaches be_arm_price, move stop:
if direction == "long":
    new_stop = entry_price + 0.0625  # = +0.25 ticks @ 0.25-pt tick
else:
    new_stop = entry_price - 0.0625
```

The BE offset of **+0.25 ticks beyond entry** (`= +0.0625` for
MNQ's 0.25-pt tick size; sign flips for shorts) prevents being
stopped at exact breakeven by friction.

### 8.3 Bracket-order assertion (Section 12.5)

```python
if side == "long":
    assert stop_price < entry_price < tp1_price <= tp2_price, (
        f"LONG bracket order violation: stop={stop_price}, "
        f"entry={entry_price}, tp1={tp1_price}, tp2={tp2_price}"
    )
else:
    assert stop_price > entry_price > tp1_price >= tp2_price, (
        f"SHORT bracket order violation: stop={stop_price}, "
        f"entry={entry_price}, tp1={tp1_price}, tp2={tp2_price}"
    )
```

Note `<=` / `>=` between TP1 and TP2: in the edge case where TP1's
midpoint fallback coincides with VWAP (e.g., a stretch so small
that the midpoint is essentially at VWAP), the two prices can be
nearly equal. Implementation should treat this case as a
single-target trade (full close at TP1=TP2).

### 8.4 Pre-committed values + rationale

- **VWAP as TP2 anchor**: directly reflects the mean-reversion
  thesis. "Snapback" means snap to fair value; VWAP IS the fair
  value reference.
- **BE arm at entry-TP1 midpoint**: midway to the partial provides
  a natural mid-trade protection without prematurely tightening.
  One-shot; never moves stop again after arming.
- **+0.25 ticks BE offset**: friction-aware (commission + slippage
  would scratch BE exactly to a small loss). Tiny positive offset
  preserves break-even net of friction.

---

## 9. Position sizing (session-vol-scaled with Mechanic 1)

### 9.1 Risk tier ladder (PLACEHOLDER values, acknowledged in Section 0.2)

Four discrete tiers based on 5-min `ATRPercentile` at signal moment:

| ATR percentile range | Tier label | Base risk dollars |
|---|---|---|
| `[0.00, 0.25)` | Low-vol | **$700** |
| `[0.25, 0.50)` | Lower-mid-vol | **$500** |
| `[0.50, 0.75)` | Upper-mid-vol | **$350** |
| `[0.75, 1.00]` | High-vol | **$200** |

```python
def risk_dollars_base(atr_percentile: float) -> float:
    """Session-vol-scaled base risk tier.

    PLACEHOLDER values per spec Section 0.2 — round numbers, not
    calibrated. Locked for this iteration.
    """
    assert 0.0 <= atr_percentile <= 1.0
    if atr_percentile < 0.25:
        return 700.0
    if atr_percentile < 0.50:
        return 500.0
    if atr_percentile < 0.75:
        return 350.0
    return 200.0
```

Rationale for the inverse-vol direction (lower ATR → larger risk
dollars): under fixed-risk sizing, contract count scales as
`risk_dollars / stop_distance_pts`. At LOW ATR, the stop is tight,
so a larger risk-dollar produces a moderate contract count. At
HIGH ATR, the stop is wide, so a smaller risk-dollar produces a
controlled contract count. This keeps notional exposure more
stable across regimes than a flat risk-dollar would.

### 9.2 Mechanic 1 (intraday cushion sizing)

```python
def intraday_adjustment(tracker_balance: float,
                       tracker_floor: float) -> float:
    """Mechanic 1: scale up risk when intraday cushion above floor
    exceeds the starting cushion of $2,000. Capped at +30%.
    """
    cushion = tracker_balance - tracker_floor
    if cushion > 2000.0:
        extra_room = min(cushion - 2000.0, 1500.0)
        return 1.0 + (extra_room / 5000.0)
    return 1.0
# Range: [1.00, 1.30]
```

### 9.3 Combined risk dollars

```python
risk_dollars = (
    risk_dollars_base(atr_percentile)
    * intraday_adjustment(tracker.balance, tracker.floor)
)
```

**Theoretical bounds**:

- Minimum: High-vol tier × no cushion bonus = $200 × 1.00 = **$200**
- Maximum: Low-vol tier × max cushion bonus = $700 × 1.30 = **$910**

Both bounds asserted at runtime (Section 12).

### 9.4 Mechanic 2 (post-lock cushion sizing) — OUT OF SCOPE

Per Section 1: this iteration is eval-only. Mechanic 2 is not
implemented. If `tracker.is_eval_passed()` returns True
mid-stream, the strategy MAY call `tracker.advance_to_pa()` for
end-to-end simulator-extension exercise, but the PA-phase sizing
remains at `intraday_adj` × `risk_dollars_base` (i.e.,
`post_lock_adj = 1.0` implicit).

### 9.5 Contract sizing

```python
stop_distance_pts = 1.0 * atr_5m  # Section 6.1
risk_per_contract = stop_distance_pts * POINT_VALUE  # $2/pt for MNQ
contracts = max(1, int(round(risk_dollars / risk_per_contract)))
contracts = min(contracts, tracker.preset["max_contracts_mnq"])
```

- Eval cap (`apex_50k_eod_eval`): 60 MNQ
- PA Level 1 cap (`apex_50k_eod_pa`): 20 MNQ (if PA transition
  fires mid-stream)

If math produces fewer than 1 contract, the trade fires at 1
(minimum). If math exceeds cap, the cap binds.

### 9.6 Partial close fraction (Section 7.2 cross-reference)

```python
tp1_close_contracts = max(1, contracts // 2)
if tp1_close_contracts >= contracts:
    tp1_close_contracts = max(1, contracts - 1)
if contracts == 1:
    tp1_close_contracts = 0  # no partial possible
    # Single contract runs directly to TP2 or stop.
```

Same convention as parent atr_regime canonical.

### 9.7 Pre-committed values + rationale (sizing layer)

- **Risk tier values ($200/$350/$500/$700)**: PLACEHOLDER per
  Section 0.2. Locked. No tuning.
- **Quartile percentile thresholds (0.25 / 0.50 / 0.75)**: pure
  quartile boundaries; round numbers; less curve-fit-prone.
- **Inverse-vol direction (low vol → larger risk dollar)**:
  designed to stabilize notional exposure across regimes (Section
  9.1 reasoning).
- **Mechanic 1 cap ($1,500 above starting cushion; +30% max)**:
  matches the atr_regime convention; conservative ceiling on
  upside-driven leverage growth.
- **POINT_VALUE = $2/pt for MNQ**: standard CME spec.

---

## 10. TradeLifecycle parameters

### 10.1 Lifecycle initialization

Use `nb_lib.lifecycle.TradeLifecycle`. Brackets, BE arm, and
runner are configured per Sections 6-8 using the partial-close
+ runner API (matches atr_regime parent's lifecycle wiring):

```python
life = TradeLifecycle(
    entry_ts=entry_ts,
    entry_price=entry_price,
    direction=direction_int,                # +1 for long, -1 for short
    stop_price=stop_price,                  # Section 6
    tp1_pts=abs(tp1_price - entry_price),   # Section 7
    tp2_pts=abs(tp2_price - entry_price),   # Section 8
    be_arm_pts=abs(tp1_price - entry_price) / 2.0,  # Section 8.2 midpoint trigger
    be_offset=direction_int * 0.0625,       # +0.25 ticks; sign flips for shorts
    session_close_time=session_close,
    eod_flat_seconds_before_close=EOD_FLAT_SECONDS_BEFORE_CLOSE,  # 90
    use_runner=True,                        # runner continues after TP1 partial
    runner_method="fixed_mfe",
    runner_trail_distance_pts=None,         # BE-only-runner mode (no fixed-MFE trail)
    compliance_check=compliance_check,
    contract_count=contracts,
    point_value=POINT_VALUE,
    tp1_close_contracts=tp1_close_contracts,  # Section 9.6
    empirical_params=EMPIRICAL_PARAMS,
    on_entry=on_entry,
    on_partial_fill=on_partial_fill,
    on_exit=on_exit,
    calendar=calendar,
    logger=logger,
)
```

### 10.2 Lifecycle behaviors enabled

- **TP1 partial**: 50% close at the psychological-level target
- **Runner**: remaining 50% continues toward TP2 (VWAP)
- **BE arm**: one-shot when MFE reaches half of `tp1_pts`
- **BE-only-runner**: `runner_trail_distance_pts=None` disables
  the fixed-MFE trail; runner exits via TP2 or BE-stop
- **EOD compliance**: 90-second buffer before session close
- **Compliance force-exit**: DLL, drawdown, EOD per combined
  compliance check (Section 11)

### 10.3 Exit-reason mapping (informational)

The lifecycle's exit-reason taxonomy applies here:

| Exit path | exit_reason |
|---|---|
| TP1 partial then TP2 runner | `tp1+tp2` |
| TP1 partial then runner stops at BE | `tp1+runner_be` |
| TP1 partial then EOD compliance | `tp1+eod_compliance` |
| Full stop (no TP1 fired) | `full_stop` |
| BE stop (no TP1 fired, but BE armed) | `be_stop` |
| EOD compliance with no TP1 | `eod_compliance` |
| DLL / drawdown compliance with no TP1 | `compliance_dll` / `compliance_drawdown` |
| TP1 partial then DLL / drawdown | `tp1+compliance_dll` / `tp1+compliance_drawdown` |

### 10.4 Pre-committed values + rationale

- **`use_runner=True` + 50% partial + `runner_trail_distance_pts=None`**:
  matches atr_regime parent's BE-only-runner configuration. Runner
  has no fixed-MFE trailing stop; only TP2 (VWAP), BE-stop (if BE
  armed), or compliance/EOD can exit it.
- **`fixed_mfe` runner_method**: the only currently-implemented
  runner method in nb_lib v2.3.

---

## 11. Friction and compliance

### 11.1 Friction (BAND_B parameters)

Matches the tested-rejected fleet (consistency across canonical
alpha builds):

- `stop_overshoot`: 1.16 pt (added to stop distance on stop-fills)
- `tp_slippage`: 0.0 pt (limit-style fills)
- `commission_per_contract_per_side`: $0.35
- `entry_slippage`: 0.5 pt (BAND_B convention)

Use `nb_lib.empirical.BAND_B_PARAMS`.

### 11.2 Compliance check construction

```python
from nb_lib.compliance.prop_firm import get_preset
from nb_lib.compliance.reporting import (
    AccountState, ComplianceTracker,
    make_combined_compliance_check,
    make_dll_compliance_check,
    make_drawdown_compliance_check,
    make_eod_compliance_check,
)
from nb_lib.calendar import TradingCalendar

calendar = TradingCalendar()
preset = get_preset("apex_50k_eod_eval")  # Rithmic variant
tracker = ComplianceTracker(preset, calendar=calendar)

compliance_check = make_combined_compliance_check([
    make_dll_compliance_check(tracker, preset),
    make_drawdown_compliance_check(tracker, preset),
    make_eod_compliance_check(tracker, preset),
])
```

### 11.3 Eval → PA transition (OPTIONAL exercise)

After each EOD `tracker.record_eod(...)`, optionally check:

```python
if tracker.is_eval_passed():
    pa_tracker = tracker.advance_to_pa()
    # Rebuild compliance_check with pa_tracker.
    # Subsequent days use pa_tracker as tracker.
```

If transition fires, sizing continues with `intraday_adj`
multiplier only; Mechanic 2 (post-lock cushion) is NOT
implemented this iteration.

### 11.4 EOD-flat behavior

`make_eod_compliance_check` enforces the preset's
`eod_flat_seconds_before_close` (90s). Open positions force-exit
at the EOD compliance bar's `close`. Exit reason is
`eod_compliance`.

### 11.5 Pre-committed values + rationale

- **`apex_50k_eod_eval` (Rithmic)**: matches tested-fleet
  baseline; apples-to-apples comparison.
- **90-second EOD-flat buffer**: preset default.
- **BAND_B friction**: tested-fleet consistency.

---

## 12. Runtime assertions (lookahead-free per timeframe)

Per the methodology repertoire's runtime-assertions-in-production
pattern, the implementation MUST include the following assertions
**in production code** (NOT just in tests). Each fires at every
signal-evaluation moment.

### 12.1 Timeframe staleness

```python
assert last_5m.name + pd.Timedelta(minutes=5) <= T, (
    f"5-min lookahead violation at {last_5m.name} vs T={T}"
)
assert last_1m.name + pd.Timedelta(minutes=1) == T, (
    f"1-min bar's right-edge {last_1m.name + 1min} must equal T={T}"
)
assert prior_1m.name + pd.Timedelta(minutes=1) == last_1m.name, (
    f"prior_1m must immediately precede last_1m"
)
```

### 12.2 Indicator sanity

```python
assert atr_5m > 0.0, "ATR cannot be zero at signal evaluation"
assert 0.0 <= atr_percentile <= 1.0, f"ATR percentile out of range: {atr_percentile}"
assert pd.notna(session_vwap_at_T), "VWAP NaN at signal moment"
assert pd.notna(session_stdev_at_T) and session_stdev_at_T > 0.0, (
    "SessionStdev NaN or zero at signal moment"
)
assert isinstance(stretch_sigma, float) and not pd.isna(stretch_sigma)
```

### 12.3 Tier boundary consistency

```python
tier = risk_dollars_base(atr_percentile)
if atr_percentile < 0.25:
    assert tier == 700.0
elif atr_percentile < 0.50:
    assert tier == 500.0
elif atr_percentile < 0.75:
    assert tier == 350.0
else:
    assert tier == 200.0
```

### 12.4 Sizing sanity

```python
assert 200.0 <= risk_dollars <= 910.0, (
    f"risk_dollars out of bounds: {risk_dollars} (expected [200, 910])"
)
assert 1 <= contracts <= tracker.preset["max_contracts_mnq"]
assert stop_distance_pts > 0.0
```

### 12.5 Bracket consistency

```python
if side == "long":
    assert stop_price < entry_price < tp1_price <= tp2_price
else:
    assert stop_price > entry_price > tp1_price >= tp2_price
```

### 12.6 Trade lifecycle invariants

```python
assert life.entry_ts == signal_ts + pd.Timedelta(seconds=1)
assert life.exit_ts > life.entry_ts
```

### 12.7 At-most-one-per-direction-per-day (Section 4.5)

Enforced via a per-session-day state flag tracked in
`trade_one_session`:

```python
day_long_fired: bool = False
day_short_fired: bool = False
# After a long signal fires and a trade is opened:
day_long_fired = True
# After a short signal fires:
day_short_fired = True
# Signal evaluation must check:
if trend_dir == "long" and day_long_fired:
    continue
if trend_dir == "short" and day_short_fired:
    continue
```

---

## 13. OOS reservation policy

### 13.1 Window definition

- **In-sample**: 2024-08-01 → 2026-01-31 (inclusive, US/Eastern
  RTH dates)
- **Held-out OOS**: 2026-02-01 → 2026-05-04 (inclusive,
  US/Eastern RTH dates) — **DO NOT load during in-sample work**

### 13.2 Implementation guard

```python
OOS_START = pd.Timestamp("2026-02-01", tz="US/Eastern")

def assert_in_sample(df: pd.DataFrame) -> None:
    """Fail-fast if loaded data extends past the in-sample boundary."""
    if df.empty:
        return
    if df.index.max() >= OOS_START:
        raise AssertionError(
            f"In-sample data extends through {df.index.max()}; OOS "
            f"boundary is {OOS_START}. Trim the loader's date range "
            f"before calling the in-sample runner (spec Section 13.2)."
        )
```

This assertion fires at the top of the in-sample test runner and
any time the strategy reads a DataFrame that should be
in-sample-only.

### 13.3 Post-test policy

If in-sample shows promise (PF ≥ 1.5 OR account-deployable result):

- **MANDATORY**: held-out validation on the OOS window with
  parameters FROZEN as-spec'd. No re-tuning.
- OOS run loads `start_date="2026-02-01"`, `end_date="2026-05-04"`,
  carries forward the in-sample-end `tracker` state, reports a
  separate results file.
- If OOS PF < 1.0 (or materially worse than in-sample): result is
  "in-sample noise, no edge"; candidate moves to
  `tested-rejected`.
- If OOS PF ≥ 1.0 AND in-sample PF ≥ 1.5: result is "preliminary
  edge candidate"; multistart validation required before
  deployment consideration.

### 13.4 Bucket accounting (mean-reversion family)

This is the **first** in-sample bucket consumption for the
mean-reversion signal class. A second mean-reversion candidate may
test a structurally different mean-reversion mechanism (different
stretch metric, different anchor, different reversal trigger);
a fork of THIS spec with re-tuned parameters does NOT count as
structurally different and would constitute methodology overrun.

---

## 14. Stage-by-stage iteration gates (upcoming implementation)

Each stage has a HARD-HALT condition. Test count must hold at
310/310 throughout (no test additions in the implementation
iteration unless explicitly noted).

### Stage A: Data prep (1-sec → 1-min → 5-min)
- Implement bar-resampling using parent canonical's helpers
  (`load_seconds`, `to_minutes`, `to_five_min`).
- Verify alignment: every 5-min bar contains 5 × 1-min bars.
- HALT-DATA-INCOMPLETENESS if any aggregated bar has fewer than
  expected sub-bar count.

### Stage B: Indicator precompute
- Compute SessionVWAP, SessionStdev on 1-min bars (session-anchored
  at 09:30 ET).
- Compute ATR(20) Wilder + ATRPercentile(60 sessions × 78 bars =
  4680 lookback) on 5-min bars.
- HALT-INDICATOR-NAN if warmup-window completion produces NaN at
  signal-eligible bars.

### Stage C: Signal detection
- Per-bar stretch_sigma + rejection-candle check (Section 4.3-4.4).
- HALT-LOOKAHEAD-VIOLATION if any signal references a bar whose
  right-edge > T.

### Stage D: Time-gate + ATR-percentile gate
- 09:35 ≤ T < 15:55 filter.
- 0.10 ≤ atr_percentile ≤ 0.95 filter.
- HALT-GATE-INVERSION if a signal passes both gates but stretch
  conditions don't match (logic error).

### Stage E: Per-direction-per-day deduplication
- Maintain `day_long_fired` / `day_short_fired` flags.
- Reset at each new RTH session start.
- HALT-DUPLICATE-SIGNAL if more than one trade per direction per
  day fires.

### Stage F: Entry fill (T+1 second)
- Direct index lookup of 1-sec bar at T + 1 second.
- Apply BAND_B entry_slippage.
- HALT-FILL-MECHANIC-VIOLATION if entry_ts != signal_ts + 1s.

### Stage G: Bracket construction
- Stop = entry ± 1.0 × atr_5m.
- TP1 = psychological_levels_between(entry, vwap) algorithm
  (Section 7.1).
- TP2 = vwap_at_signal_moment.
- BE arm = midpoint(entry, tp1); offset = ±0.0625.
- HALT-BRACKET-VIOLATION if stop/TP1/TP2 order is wrong.

### Stage H: Position sizing
- risk_dollars_base(atr_percentile) tier lookup.
- intraday_adjustment(balance, floor) Mechanic 1.
- Contracts = risk_dollars / (stop_distance × $2), capped.
- HALT-SIZING-OUT-OF-BOUNDS if risk_dollars outside [200, 910].

### Stage I: TradeLifecycle integration
- Build lifecycle per Section 10.1.
- Wire on_entry / on_partial_fill / on_exit callbacks.
- HALT-API-MISCONFIG if lifecycle raises on init.

### Stage J: Compliance integration
- Build combined compliance check.
- Optional eval→PA transition logic (Section 11.3).
- HALT-COMPLIANCE-COMPOSITION-FAILURE if compliance_check raises
  unexpectedly.

### Stage K: In-sample test
- Full 2024-08-01 → 2026-01-31 window.
- Generate results CSV at
  `C:/VMShare/NT8lab/vwap_stretch_snapback_trades.csv`.
- Apply Section 13.2 OOS guard.

---

## 15. Expected outcomes (honest priors, recap)

Per Section 0.4:

- **50%**: no in-sample edge. The negative-edge hypothesis
  extends from trend-continuation to mean-reversion at this
  granularity.
- **25%**: in-sample edge fails OOS.
- **15%**: in-sample edge survives OOS.
- **10%**: execution-mechanic break (e.g., TP1 lands outside the
  entry-VWAP corridor too often; psychological-level algorithm
  has an edge-case bug; signal frequency < 0.5 trades/day → n too
  low for statistical inference).

### 15.1 What signals "genuine edge"

- In-sample PF ≥ 1.5 across n ≥ 30 (mean-reversion strategies
  often have higher signal frequency than trend-continuation;
  expect n in the dozens-to-low-hundreds range).
- Win rate ≥ 50% (consistent with mean-reversion's typical
  higher-WR profile vs trend-continuation).
- Apex account remains ACTIVE or PASSES at end of in-sample.
- Edge holds across non-trivial sub-cohorts (e.g., long-only
  vs short-only; first-half vs second-half of in-sample).

### 15.2 What signals "selection bias"

- In-sample PF > 2.5 with n < 20: too few trades for the high PF
  to be statistically meaningful.
- Edge concentrated entirely in one direction (e.g., all longs
  win, all shorts lose): suggests the regime drove the result,
  not the signal.
- Edge concentrated in one quarter of the in-sample window:
  suggests the strategy worked for a specific market regime
  during that period only.

### 15.3 What signals "execution mechanic break"

- TP1 midpoint-fallback fires on > 30% of trades: the
  entry-to-VWAP corridor is regularly smaller than 50 points;
  the psychological-level anchor isn't doing meaningful work.
- TP1 fires on < 20% of trades: targets are too far; VWAP is
  pulling away faster than the trade can capture it.
- Signal frequency < 0.5 trades/day average: the ATR-percentile
  + stretch + rejection gate combination is over-restrictive.

---

## 16. What this iteration validates beyond strategy edge

Regardless of strategy outcome, the implementation iteration
validates and produces reusable infrastructure:

1. **First nb_lib-native mean-reversion canonical alpha**. Whether
   it succeeds or fails, the signal-class diversification is the
   information: the prior six canonicals were all
   trend-continuation; this is the first mean-reversion.

2. **VWAP-anchored target geometry**. The pattern "target =
   SessionVWAP at signal moment" becomes a reusable bracket
   primitive. Future mean-reversion candidates can consume this
   pattern without re-deriving the lookahead audit.

3. **Psychological-level target-anchor algorithm**
   (`psychological_levels_between` + `compute_tp1`). Becomes a
   reusable utility for any future strategy that wants to anchor
   TP1 to round-number levels. The 50-pt-with-100-pt-as-subset
   structure generalizes to other instruments (e.g., 10-pt with
   25-pt subset on ES).

4. **Session-vol-scaled risk tier scaffold**. The four-tier
   ATR-percentile ladder structure is reusable; the placeholder
   values are explicitly placeholder, and the scaffold itself
   becomes the canonical implementation point for future
   calibrated versions (Version A1 noted in Section 0.2).

5. **Simpler 4-layer adaptive design**. Reference point in the
   layer-count vs edge calibration. If the 6-layer atr_regime
   failed and the 4-layer vwap_stretch_snapback also fails (or
   succeeds), the comparison informs future
   adaptive-layer-count discipline.

6. **Single-timeframe-primary multi-timeframe-sizing pattern**.
   Signal is 1-minute primary; sizing uses 5-min ATR; execution
   is 1-second. This 3-timeframe split (without 30-min trend
   coordination) is a simpler pattern than atr_regime's 4-timeframe
   approach. Reusable for future single-timeframe-primary
   candidates.

7. **At-most-one-trade-per-direction-per-day enforcement**.
   Pattern for preventing mean-reversion back-to-back fade
   pathologies. Reusable for any future mean-reversion candidate.

If strategy edge is absent (50% expected), the value of this
iteration is the infrastructure. If edge appears, the
infrastructure is secondary but still banked. The retrospective
written after the implementation iteration must explicitly
distinguish "strategy edge" findings from "infrastructure
validation" findings.

---

**End of spec.** All parameters in Sections 4-11 are LOCKED.
Risk tier values in Section 9.1 are EXPLICITLY PLACEHOLDER per
Section 0.2 but are LOCKED for this iteration. No tuning during
implementation or testing. Any deviation requires a separate
iteration with explicit operator sign-off.
