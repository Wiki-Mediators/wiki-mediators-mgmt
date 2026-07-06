---
status: "spec-drafted-final-bypass-proxy"
---

# Wide-State BVC-Proxy Divergence Reversal FINAL Spec

**Strategy ID:** `wide_state_bvc_proxy_divergence_reversal`  
**Status:** SPEC-DRAFTED-FINAL-BYPASS-PROXY  
**Created:** 2026-05-20  
**Canonical path:** `nb_lib/strategy_specs/canonical/wide_state_bvc_proxy_divergence_reversal_spec_FINAL.md`  
**Candidate lineage:** `nb_lib/strategy_specs/candidates/wide_state_bvc_proxy_divergence_reversal.md`  
**Bypass authorization:** Operator decision 2026-05-20 to proceed from strict-sigma BVC R4 directly to informational FINAL spec, implementation, and multistart.

---

## METHODOLOGY DISCLOSURE - READ FIRST

This is a **BVC-PROXY BYPASS spec**. It is not a real order-flow spec.

BVC proxy delta is estimated from OHLCV bar returns and volume. It is a
model of participation pressure, not measured aggressor-side delta.
Therefore:

1. Positive results do **not** validate the real footprint / delta divergence mechanism.
2. Positive results can justify acquiring real tick/aggressor-side data or treating BVC as its own price-volume proxy signal.
3. Negative results are ambiguous because mechanism failure and proxy failure are not separable.
4. OOS is sealed; this informational bypass cannot graduate.

The core question is narrow: **does strict BVC-proxy divergence confirmation reduce the 11/12 Apex-failure pattern of the price-only wide reversal family?**

Price-only comparison anchor:

| Strategy | n | P&L | PF | Failed starts |
|---|---:|---:|---:|---:|
| `wide_opening_window_reversal_family` | 354 | $-14,054.50 | 0.75 | 11/12 |

---

## 0. Outcome Priors And Scope

| Outcome | Prior | Meaning |
|---|---:|---|
| No improvement vs price-only | 0.45 | Proxy divergence does not rescue wide-state reversal |
| Survival improvement but weak PF | 0.30 | Fewer failures, PF still below deployable |
| Registry-useful proxy edge | 0.15 | PF [1.05, 1.50), lower failure count, composition candidate only |
| Strong informational proxy edge | 0.05 | PF >= 1.50 and materially better survival, still not real-delta validation |
| Implementation/proxy flaw | 0.05 | BVC or fill mechanics prove unsuitable |

Strict R4 result after using `sigma.shift(1)`:

| Metric | Value |
|---|---:|
| Structural signals | 89 |
| Passing fill guards | 63 |
| Long / short | 44 / 45 |
| Distinct signal days | 18 / 19 |
| Sparsity class | dense |

The strict normalization did not materially change the prior run.

---

## 1. Strategy Thesis

The failed price-only wide reversal family faded wide SMA20/SMA200
extensions using price anatomy alone. This proxy variant asks whether
participation disagreement helps: if price makes a fresh wide-state
extreme but BVC proxy delta fails to confirm, the extension may be more
likely to reverse toward the moving-average cluster.

Short side: SMA20 far above SMA200, price extended above SMA20, current
bar makes a new high, but BVC proxy delta is weaker than the prior
lookback high or negative.

Long side: SMA20 far below SMA200, price extended below SMA20, current
bar makes a new low, but BVC proxy delta is stronger than the prior
lookback low or positive.

Counter-hypothesis: the proxy merely re-labels volatile price movement
and produces dense signals without improving expectancy.

---

## 2. Entry Signal And Timing

```text
instrument: MNQ
session: RTH
scan_window_et: 09:30:00 through 12:00:00
primary_timeframe: 2-minute bars derived from 1-second OHLCV
directions: two-sided
max_structural_signals_per_day: 6
entry_timeout_bars: 3
```

Bars are labeled by left edge. A 2-minute bar at `09:30:00` covers
`[09:30:00, 09:32:00)` and is only tradable after `09:32:00`.

Entry orders are stop-market reversal entries armed at:

```python
eligible_ts = signal_ts + 1 second
cancel_ts = signal_ts + 6 minutes
```

No predicate may inspect any bar whose right edge is after `signal_ts`.

---

## 3. Strict BVC Proxy Convention

```python
ret = close.diff()
sigma = rolling_std(ret, 20 bars).shift(1)
z = clip(ret / sigma, -6, 6)
buy_fraction = normal_cdf(z)
bvc_proxy_delta = volume * (2 * buy_fraction - 1)
bvc_delta_ratio = bvc_proxy_delta / volume
```

The `sigma.shift(1)` rule is pre-committed. The current completed bar's
return is normalized only by volatility known before that bar formed.

This is still not true delta.

---

## 4. Entry Predicates

Shared wide-state classifier:

```python
ma_distance_atr = abs(sma20_2m - sma200_2m) / atr14_2m
wide_upside = sma20_2m > sma200_2m and ma_distance_atr >= 1.00
wide_downside = sma20_2m < sma200_2m and ma_distance_atr >= 1.00
```

Short predicate:

```python
state == wide_upside
close - sma20 >= 0.50 * atr14
high > max(prior_5_bars.high)
bvc_proxy_delta < max(prior_5_bars.bvc_proxy_delta) or bvc_proxy_delta < 0

entry_stop_price = bar.low - 0.25
initial_stop_price = bar.high + 0.25
```

Long predicate:

```python
state == wide_downside
sma20 - close >= 0.50 * atr14
low < min(prior_5_bars.low)
bvc_proxy_delta > min(prior_5_bars.bvc_proxy_delta) or bvc_proxy_delta > 0

entry_stop_price = bar.high + 0.25
initial_stop_price = bar.low - 0.25
```

The five-bar lookback uses completed bars strictly before the current
bar timestamp.

---

## 5. Risk And Position Sizing

```text
risk_dollars_per_trade = 300
point_value = 2.0
tick_size = 0.25
max_contracts = 12
stop_pts_min = 5.0
stop_pts_max = 50.0
daily_loss_limit = 2 realized losing trades
```

Contracts:

```python
contracts = floor(300 / (stop_pts * 2.0))
contracts = min(contracts, 12)
skip if contracts < 1
```

Stop-band and daily-loss guards are not tuning conveniences; they are
Apex survival controls learned from prior failures.

---

## 6. Management And Brackets

No adaptive specialists are used. Specialist count is deliberately zero.

```python
tp1 = 1.00R
tp2 = 2.25R
tp1_close_fraction = 0.50
be_arm = 1.50R
be_offset = 0.25 pt
runner_trail = fixed_mfe at 1.25R
max_hold = 20 minutes
```

If only one contract is used, there is no partial runner split.

Time exit reason:

```text
wide_state_bvc_proxy_time_exit_20m
```

---

## 7. Pre-Committed Informational Criteria

This bypass test cannot graduate. Criteria are informational:

| Verdict | Conditions |
|---|---|
| Informational rejected | PF < 1.05 or failed starts remain near price-only baseline |
| Registry-useful proxy | PF [1.05, 1.50), positive aggregate P&L, failed starts <= 3 |
| Strong proxy result | PF >= 1.50, n >= 80, failed starts <= 1 |
| Tick-data acquisition justified | Any positive result with material survival improvement vs 11/12 baseline |

The comparison that matters most:

```text
Did failed starts improve materially from 11/12?
```

---

## 8. OOS Guard

All runs are in-sample only:

```python
WINDOW_START = 2024-08-01
WINDOW_END = 2026-01-31
OOS_START = 2026-02-01
assert max_loaded_ts < OOS_START
```

The 12 monthly starts are August 2024 through July 2025, each capped at
42 trading days. No run may load data on or after 2026-02-01.

---

## 9. Multistart Configuration

```text
starts: 2024-08-01 through 2025-07-01 monthly
actual_start: first trading day at/after configured start
window: 42 trading days
account: fresh Apex 50K EOD ComplianceTracker per start
friction: BAND_B
reporting: aggregate PF/P&L/n, per-start table, direction attribution, exit reasons, Apex failure count
```

---

## 10. HARD-HALT Conditions

- HARD-HALT-OOS-LEAK: any data loaded at or after 2026-02-01.
- HARD-HALT-PROXY-AS-REAL: any text or report claiming BVC is measured delta.
- HARD-HALT-DIRECTION-FILTERING: dropping one side after seeing results.
- HARD-HALT-SIGMA-DRIFT: implementation not using `sigma.shift(1)`.
- HARD-HALT-SCOPE-CREEP: adding adaptive specialists or parameter tuning.

---

## 11. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-05-20 | spec-drafted-final-bypass-proxy | FINAL proxy spec drafted after strict BVC R4 confirmed no signal collapse. Informational multistart only; not OOS-eligible and not real-delta validation. |
