---
title: External Mean-Reversion Backtest Video — Intake Note
status: catalogued-finding
created: 2026-06-30
source: external YouTube video (Brendan, "9,000 backtests with Claude")
intake_precedent: _PROJECT_ALTITUDE_MAP.md §6 (transcript intake — process material, not strategy)
related:
  - ninja-traitorate-methodology-reference.md (§15B mechanism-class screening)
  - nb_lib/strategy_specs/candidates/prior_session_level_fade_aged.md
---

# External Mean-Reversion Backtest Video — Intake Note

## What it is

A popular trading-content video that ran ~9,000 backtests across 30 assets and
15 years and concluded that **mean reversion is the only strategy family that
broadly survives "naked" testing**. Methodology shown: walk-forward, out-of-sample
split, six-filter funnel (Sharpe, drawdown, overfitting, min-trades), a bootstrap
reshuffle, and a "build on top" framework (base signal → risk/sizing →
uncorrelated signals → regime gate).

## Why the headline does NOT enter the pipeline

**Regime mismatch — load-bearing.** The study is **daily bars on equities / ETFs /
gold / oil / bonds / BTC-ETH**, and explicitly states it is **not intraday, not
futures, not options**. This project is intraday MNQ on 1-second OHLCV. "Mean
reversion survives broadly" is a daily-bar cross-asset finding and does not transfer
to intraday MNQ unscreened.

**Self-similarity does not imply edge-transfer.** The fractal/self-affine character
of price (same statistical *shape* across timeframes) is real, but it does not carry
the *edge* across scales, because two things are strongly scale-dependent:
- **Cost-distance.** MNQ friction (spread/commission/slippage) is roughly fixed per
  trade. It is a rounding error against a daily-bar move and can eat most of a
  1-second move. (Banked failure lesson: tight scalps die under the cost-distance
  speed limit.)
- **Microstructure.** Daily-scale moves are positioning; 1-second moves are order-book
  mechanics (bid-ask bounce, queue, latency). That layer is not fractal.

**We already have the stronger intraday answer.** The project independently drifted
toward mean-reversion-flavored ideas (VWAP reclaim; the aged level fade) and found the
nearest survivor **borderline (N=48, p≈0.048) and OOS-fragile** — exactly what you would
*not* see if the daily-bar edge transferred cleanly. Our own data outranks the video.

## What IS transferable

- **The layered framing** (base edge → risk/sizing → uncorrelated signals → regime
  gate) — already this project's thesis (management structure as the durable edge) and
  its composition-node / regime-router architecture.
- **Mean reversion as a strategy-*class* lens** — already in the methodology
  (`strategy_class`: trend_follow / mean_reversion / mixed; classifiers invert by class).
- **Process discipline** (walk-forward, OOS, bootstrap, multiple-testing correction,
  cost realism) — already banked here, in places more strictly (§15B screen, trial-budget
  multiplication).

So the video confirms the approach; it does not add a finding.

## Disposition

- **Do not cite the "mean reversion wins" conclusion as applicable to intraday MNQ.**
- Any mean-reversion entry idea must clear the **§15B cheap mechanism-class screen**
  before any build. Screen-before-build is a bright line, not a preference.
- A scoped Codex probe (pre-register an MNQ-RTH mean-reversion predicate → screen →
  honest BUILD / DON'T / CONTEXT-ONLY verdict; build only on green) is the active
  next step. If green, the project's *own validated result* — not the video — becomes
  the real incorporation.

## Note's main job

Defensive: stop the video's broad daily-bar claim from being re-cited later as if it
applied to MNQ. This is the same disposition as the §6 transcript intake — external
content captured as context, kept out of the research pipeline until translated into an
objective predicate and screened on our own data.
