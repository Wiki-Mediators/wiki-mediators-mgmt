---
name: "ATR Compression Squeeze-Break"
tagline: "When 30-min rolling range compresses below 0.35x ADR(20) for 15+ minutes, trade the directional break out of the compression box; target = 1x compression range."
status: "screen-failed-pre-build"
created: 2026-06-30
updated: 2026-06-30
source: "Session 2026-06-30 dealer's-choice probe. Mechanism class supported by Mandelbrot (vol cycling), Bollinger (squeeze), Carter (TTM squeeze), and NR4/NR7 practitioner work. Local evidence: PROBE_003 confirmed compressed mornings predict expanded afternoons in MNQ (p~5e-6)."

markets: ["MNQ"]
session: "RTH"
time_of_day: "10:30-15:00 ET"
hold_duration: "intraday"

signal_type: "volatility-expansion breakout"
indicators: ["ADR(20)", "30-min rolling range"]
timeframes_used: ["1-second", "1-minute"]

brackets: "structural (compression box) stop, 1x range target"
position_sizing: "fixed contracts for screen"

canonical_spec: null
implementation: null
related_candidates: []

test_results:
  in_sample_n: 364
  in_sample_pnl_dollars: -2042
  in_sample_pf: 0.918
  in_sample_win_rate: 0.505
  out_of_sample_tested: false

tags:
  - rth-only
  - intraday
  - volatility-expansion
  - breakout
  - non-overlapping-with-NB
  - screen-failed
---

# ATR Compression Squeeze-Break

## 1. Thesis

Volatility cycles between contraction and expansion. When the 30-minute rolling range compresses below 0.35× ADR(20) and holds for 15+ minutes, the market is "coiled." A subsequent directional break out of the compression box has follow-through; target = 1× compression range (Bollinger-style "expansion equals compression").

## 2. Evidence Basis

- **External literature:** Bollinger Bands squeeze (1993), Linda Raschke / Larry Connors NR4/NR7 patterns, John Carter's TTM Squeeze indicator. Vol cycling is a documented structural property of futures markets.
- **Local evidence:** PROBE_003 (`probe_003_vol_expansion.py`) confirmed (p≈5e-6, n≈380) that compressed mornings predict expanded afternoons in MNQ. The vol-cycling pattern IS present in this dataset.

## 3. Pre-committed parameters (LOCKED before screen)

| Parameter | Value |
|---|---|
| Window | 10:30 - 15:00 ET (post-NB, pre-EOD chop) |
| Compression definition | 30-min rolling range ≤ 0.35 × ADR(20) |
| Compression persistence | ≥ 15 consecutive 1m bars in compression |
| Break trigger | 1m close ≥ 2 ticks (0.50 pt) beyond compression box |
| Direction | WITH the break |
| Entry | next 1s open after break bar closes |
| Stop | opposite side of compression box ± 1 tick buffer |
| Target | 1× compression range beyond entry |
| Time exit | 15:55 ET |
| Frequency | one trade per session, first signal only |
| ADR(20) | trailing-20-session median RTH range |
| In-sample | strictly < 2026-02-01 (hard-cut + runtime assert) |
| Cost | $3.50/RT, $2/pt |

## 4. Screen Result — DO NOT BUILD

| Axis | Flag | Metric |
|---|---|---:|
| skew_concentration | **RED** | Sharpe = −0.039; observed Sharpe doesn't clear benchmark |
| cost_distance | **GREEN** | φ = 0.026 (mechanism produces large moves relative to friction) |
| frequency_power | **RED** | t = −0.75 (noise, not reliably negative) |
| regime_concentration | GREEN | all trades fell into one ADR bucket (calibration artifact, not informative) |
| cross_correlation | YELLOW | not measured |

Aggregate: n=364, net −$2,042, mean −$5.61/trade, WR 50.5%, Sharpe −0.04, skew −0.09, kurtosis 1.62.

Per-direction:
- Long: n=209, net −$2,254, WR 48.8%, PF 0.845 — directional loser
- Short: n=155, net +$212, WR 52.9%, PF 1.020 — essentially breakeven

## 5. Failure-shape notes (worth banking as context)

This is the **cleanest null shape** of the 2026-06-30 session's five trials:

- **t-stat near zero** (−0.75) — noise, not statistically reliable loss like the level-rejection trial (t=−3.12)
- **Skew near zero** (−0.09) and **kurtosis well-behaved** (1.62) — no pennies-in-front-of-steamroller profile like the PDH/PDL/PDC continuation (skew −10.5, kurt 205.6)
- **Cost-distance GREEN** (φ = 0.026) — mechanism produces $137 average expected gross move vs $3.50 friction; friction is not the killer

The mechanism produces large, well-shaped moves but the BREAK DIRECTION doesn't predict the EXPANSION DIRECTION cleanly enough as currently mechanized.

## 6. Plausible conditioning angles NOT tested (any of these would be a new trial)

These are observations from the failure shape, not pre-committed retunes — flagged for future session if anyone wants to revisit:

- **Mean-reversion of the break:** the long side reliably lost while the short side was breakeven. Possibly the initial break direction is contrarian on MNQ — fade the break instead of follow it.
- **Time-of-day conditioning:** the 10:30-15:00 window is broad. The mechanism might surface signal during the NY lunch period (12:00-13:30 ET) where compression-break has less momentum to fight.
- **Volume confirmation:** a volume-supported break has different statistical properties than a low-volume one; this trial used price-only break.
- **Multi-timeframe confirmation:** require concurrent compression on both 1m and 5m timeframes.

ANY of the above is a separate trial requiring multiplicity adjustment. Do NOT compose them all in one rerun — that's curve-fitting.

## 7. Status History

| Date | Status | Notes |
|---|---|---|
| 2026-06-30 | `screen-failed-pre-build` | Trial #1 of a new family (atr-compression-squeeze). Five-axis screen returned DO_NOT_BUILD on skew_concentration + frequency_power, but the failure shape is the cleanest of the session — small t-stat near zero, no fat tails, no skew problem, cost-distance excellent. Files: `probe_atr_compression_squeeze_break_screen.py`, `atr_compression_squeeze_break_screen_trades.csv`, `atr_compression_squeeze_break_screen_report.json`. Banking the conditioning angles in §6 as observations for any future revisit; this session does not pursue them to avoid multi-trial compounding. |
