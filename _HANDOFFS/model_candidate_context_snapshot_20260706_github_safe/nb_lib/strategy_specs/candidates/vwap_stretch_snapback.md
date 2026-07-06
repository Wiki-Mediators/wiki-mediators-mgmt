---
name: "VWAP Stretch Snapback"
tagline: "Fade statistically stretched moves back toward intraday fair value."
status: "tested-rejected"
created: 2026-05-12
updated: 2026-05-12
source: "Inspiration: common institutional VWAP reversion framework; not a single claimed paper."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:45-15:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "mean-reversion"
indicators: ["VWAP", "SessionStdev", "ATR(20) on 5-minute bars"]
timeframes_used: ["1-second", "1-minute", "5-minute"]

# Execution
brackets: "atr-scaled"
position_sizing: "fixed-risk-dollar"

# Cross-references (populated when relevant)
canonical_spec: "../canonical/vwap_stretch_snapback_spec_FINAL.md"
implementation: "../../scripts/vwap_stretch_snapback_canonical_alpha.py"
related_candidates: []

# Test status (only populated when status >= tested-*)
test_results:
  in_sample_n: 40
  in_sample_pnl_dollars: -1079.70
  in_sample_pf: 0.807
  in_sample_win_rate: 0.325
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: null

# Tags for organization (recommended controlled vocabulary in README)
tags:
  - rth-only
  - intraday
  - mean-reversion
  - vwap-based
  - atr-scaled
  - fixed-risk-dollar
---

# VWAP Stretch Snapback

## 1. Thesis

MNQ often overshoots during emotional morning or midday pushes,
especially when price gets far from session VWAP without fresh catalyst
follow-through. This candidate tests whether a volatility-normalized
VWAP stretch followed by local rejection can identify exhaustion rather
than blindly fading strength.

The idea is intentionally not a breakout continuation system. It asks
whether stretched price can revert toward intraday fair value under
non-trend or post-impulse digestion conditions.

## 2. Mechanism (what edge it captures)

- Uses RTH VWAP as an intraday fair-value anchor.
- Requires distance from VWAP to be statistically stretched relative to
  session dispersion.
- Waits for a rejection trigger instead of entering on the stretch
  itself.
- Uses ATR-scaled risk so wider volatility does not mechanically imply
  over-leverage.

## 3. Signal logic (entry conditions)

Compute RTH VWAP and rolling session standard deviation of close around
VWAP. A long setup occurs when price trades more than 2.0 standard
deviations below VWAP and then closes back above the prior 1-minute
high. A short setup is symmetric: price trades more than 2.0 standard
deviations above VWAP and then closes back below the prior 1-minute low.

Avoid the first 15 minutes of RTH and known catalyst blackout windows.
Candidate should likely be one trade per direction per day until proven
otherwise.

## 4. Exit logic (stops, targets, time-based exits)

Stop beyond the stretch extreme by 0.5 x ATR(20) on 5-minute bars. TP1
is the midpoint between entry and VWAP. TP2 is VWAP. Time exit after 45
minutes if neither target nor stop resolves the trade.

## 5. Position sizing

Use fixed dollar risk per trade, for example $400-$600 divided by stop
dollars, capped by the active Apex MNQ contract limit. Do not use fixed
15-contract sizing.

## 6. Required indicators / data

MNQ 1-second or 1-minute RTH bars, RTH VWAP, rolling session standard
deviation around VWAP, and ATR(20) on 5-minute bars. All required market
data appears available in the current MNQ store.

## 7. Differentiation (vs already-tested strategies)

The four tested strategies were morning direction-following or breakout
style systems using fixed-point brackets and fixed 15-contract sizing.
This candidate is a VWAP mean-reversion system, uses volatility-scaled
distance and stops, and waits for rejection after an extension rather
than entering with the move.

## 8. Required research before spec drafting

- Define exact session stdev calculation and warmup behavior.
- Decide whether VWAP distance should use close, high/low extreme, or
  both.
- Verify signal frequency after catalyst-window exclusion.
- Test whether trend-day filtering is required before any OOS use.
- Pre-commit the ATR period, stdev threshold, and time exit before
  implementation.

## 9. Source / references

Common institutional VWAP reversion framework and discretionary futures
mean-reversion playbook. No proprietary or peer-reviewed edge claim is
made here.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-12 | untested-ideation | 2026-05-12: created as untested-ideation by Codex 5.5 CLI batch. |
| 2026-05-12 | spec-drafted | FINAL spec drafted with hybrid brackets (ATR stop, level-based targets with psychological-level TP1 anchors) and session-vol-scaled risk (placeholder values acknowledged). T+1 second entry from 1-min bars derived from 1-sec source. See `../canonical/vwap_stretch_snapback_spec_FINAL.md`. |
| 2026-05-12 | implementation-in-progress | Strategy script implemented per FINAL spec at `../../scripts/vwap_stretch_snapback_canonical_alpha.py` (~878 lines including docstring/comments). 31 new tests added covering psychological-level algorithm, compute_tp1, risk tier ladder, intraday cushion, bracket ordering, rejection-candle detection, OOS guard, FILL_ASSUMPTIONS extension, and constants pinning; test count grew from 310 to 341. FILL_ASSUMPTIONS enum extended with `empirical_canonical_vwap_snapback` (additive). HANDOFF updated. Dry-run pipeline clean (data load + indicator precompute pass). In-sample test pending. |
| 2026-05-12 | tested-rejected | In-sample run COMPLETED. **No edge.** n=40 trades over 31 distinct days (active window 2024-08-26 to 2024-10-14 before account FAILED via compliance_drawdown breach). Total P&L $-1,079.70, PF 0.807, win rate 32.5%. Max DD $2,032.70. TP1+TP2 reach 12.5% (5 trades); full_stop 35%; be_stop 27.5%; tp1+runner_be 20%. TP1 psychological-level algorithm validated cleanly (14/14 fills landed on 50-pt levels, 6 on 100-pt; zero midpoint fallbacks). Per-day-direction-dedup enforcement verified (0 violations across 31 days; 9 days had both long+short). Direction asymmetry FLAGGED per spec Section 15.2: shorts -$2,227, longs +$1,148 — likely regime-driven (Aug-Oct 2024 uptrend) rather than strategy-design edge. Per spec Section 0.4 outcome priors: this is the 50%-prior "no-edge" category. Per Section 13.3: no OOS validation (gated on PF >= 1.5; missed by ~46%). 7-fleet failure pattern now spans two signal classes (6 continuation + 1 mean-reversion; all $-1.0K to $-2.1K Apex-eval-failure on in-sample). See `nb_lib_vwap_snapback_insample_results_report.md`. |
