---
type: methodology-repertoire
version: 1
created: 2026-05-12
updated: 2026-05-12
status: working-draft
related_skills:
  - "../../../skills_inventory_nb_lib.md"
---

# Strategy Design Repertoire (Working Draft v1)

## Purpose and Caveats

A methodology reference for strategy design. When designing new
strategies, this document catalogs:

- Patterns we've established or are considering
- Indicators we have available (and useful ones we don't)
- Methodology safeguards for each adaptive complexity level

**Epistemic status.** This is a working framework. Sections marked
EMPIRICALLY-GROUNDED are based on tested fleet experience
(variant_1, noise_brk, prj3, ema_trend — all four nb_lib-native
canonical strategies tested-rejected against Apex 50K eval at
~$-2K cumulative loss). Sections marked WORKING-FRAMEWORK are
conceptually useful but not yet validated against empirical
results from this fleet. Treat the framework as evolving.

**Key principle.** More adaptive parameters = more curve-fit risk.
A strategy with five adaptive elements has more degrees of freedom
than five separate single-element strategies — but only when those
elements are independent. Combined adaptive elements that interact
create implicit selection bias that's harder to audit than
explicit parameter sweeps. Pre-commit every parameter before
seeing in-sample results, and never silently retune.

**What this is not.** This is not a list of strategies. Strategy
candidates live alongside this file in `candidates/`. This is the
toolkit those candidates draw from.


## Section 1: Dynamic Adaptation Levels (CORE; full draft)

**Status:** EMPIRICALLY-GROUNDED for Level 1 (all four tested
strategies failed Level 1 implementations); WORKING-FRAMEWORK for
Levels 2 and 3.

The repertoire distinguishes three levels of adaptive complexity.
Higher levels offer more flexibility but compound curve-fit risk.

### Level 1: Volatility-Adaptive (deterministic)

Parameters scale continuously with a measured input (typically
ATR or a volatility proxy). The functional form is fixed and
pre-committed; only the input value varies bar-by-bar or
day-by-day.

**Examples from the wiki:** `vwap_stretch_snapback` uses an
ATR(20)-scaled stop (a single multiplier, pre-committed).
`atr_ratio_expansion_scalp` uses a multiplier on
`ATRRatio(5,20)`. The PRJ_6 NoiseBrk live strategy uses ATR
percentile bands for breakout-band width.

**When appropriate:** virtually always preferred over fixed
brackets when volatility ranges across the in-sample window are
wide. The four tested fixed-point strategies (PRJ_3 30pt,
noise_brk 32pt, ema_trend 30pt, variant_1 fixed) all hit the
same pattern: too tight on high-vol days, too loose on low-vol
days. ATR-scaling does NOT guarantee positive edge but removes
that specific vol-mismatch failure mode.

**Safeguards:**

- Pre-commit ATR period AND multiplier in writing before any
  in-sample fitting. Document both in the spec frontmatter.
- Runtime assertions on ATR inputs (per the ema_trend / PRJ_3
  origin-check pattern) so a stale or NaN ATR cannot silently
  produce a zero-width stop.
- Use the same ATR for sizing and stop placement when possible
  — internal consistency, fewer parameters.

### Level 2: Regime-Conditional (discontinuous)

A regime classifier (binary or k-class) gates whether the
strategy runs, and may switch between behavior modes. The classifier
itself is pre-committed; the strategy's per-bar logic does not
adapt continuously.

**Examples:** `atr_regime_pullback_continuation` requires
ATR percentile in a designated band before any signal fires.
`prior_close_magnet_vol_filter` uses an ATR-regime gate.
`opening_range_width_switch` switches behavior based on
opening-range width percentile.

**When appropriate:** when the edge concept genuinely behaves
differently across regimes (e.g., breakouts in low-vol contract
phases versus high-vol expansion phases). Use sparingly — each
added regime threshold is a parameter degree of freedom.

**Safeguards:**

- Pre-commit regime thresholds BEFORE in-sample testing. Round
  numbers (25th, 50th, 75th percentile) are preferred over
  fine-tuned thresholds (37th, 62nd) which scream curve-fit.
- DO NOT in-sample-tune thresholds, then re-test. If a regime
  threshold needs adjusting, document the adjustment and run
  the held-out cohort separately.
- If budget allows, reserve a held-out cohort specifically for
  threshold selection (separate from the OOS deployability
  cohort).
- Each regime split halves available sample size in worst case;
  ensure n per regime is methodologically defensible (~50+).

### Level 3: Continuously Adaptive (bar-by-bar state)

Strategy state updates each bar based on running calculations
(e.g., trailing swing trail, running break-even shift, dynamic
profit-target ladder). Highest curve-fit risk because every
state-update rule is itself a parameter.

**Example:** `developing_swing_trail_vol_cap` proposes a developing
5-minute swing as a trailing exit (bar-by-bar state update),
gated by an ATR-percentile cap. Note the gating: the exit logic
is continuously adaptive, but a Level 2 gate constrains *when*
it operates — a deliberate complexity boundary.

**When appropriate:** rarely. Reserve for situations where lower
levels demonstrably leave edge on the table AND you have
budget to validate the additional parameters via multistart and
OOS cohorts.

**Safeguards:**

- Strict pre-commit of ALL state-update rules. No "tune the
  trail factor on in-sample data."
- Cannot include parameters chosen by inspection of in-sample
  trade behavior (a very common silent curve-fit).
- Runtime state-machine invariants as assertions (e.g., "trail
  level is monotonic in trade direction"). State bugs are easy
  to introduce and hard to detect after the fact.
- Combining Level 3 with Level 2 gates (as
  `developing_swing_trail_vol_cap` does) is a defensible
  pattern: contain Level 3 complexity inside a Level 2 cage.


## Section 2: Position Sizing Patterns (CORE; full draft)

**Status:** EMPIRICALLY-GROUNDED for fixed-contract (entire
tested fleet); WORKING-FRAMEWORK for the others.

Position sizing determines dollar risk per trade. For Apex 50K
EOD eval at 15-MNQ default sizing, every pattern below interacts
with the $2K trailing drawdown floor and $1K daily-loss limit.

### Fixed-contract

Simplest. Always trade N contracts. The four tested nb_lib
strategies all ran 15 MNQ.

**Apex implications:** per-trade dollar risk equals
`15 contracts × stop_distance × $2/point`. For a 30pt fixed
stop, that's $900 per trade — 45% of the $2K trailing buffer
in one loss. Two consecutive max losses (~$1,800) eliminates
the buffer for almost any subsequent path.

**When appropriate:** prototyping. Useful as a baseline so
sizing-pattern comparisons isolate the sizing variable. Not
appropriate for production deployment of a strategy with
variable stop distance.

### Fixed-risk-dollar

`contracts = $risk_budget / (stop_distance × $2)`, rounded down,
with a max-contracts cap.

Mathematically equivalent to volatility-scaled when stop is
ATR-based — same formula, different framing.

**Apex implications:** dollar risk per trade becomes constant
regardless of vol regime. This is desirable for trailing-drawdown
management: the buffer depletes predictably rather than in
vol-correlated lumps.

**Caveat:** the cap matters. Without a cap, very tight stops on
low-vol days produce mega-positions. The cap should be set by
absolute contract count (e.g., 20 MNQ max) or by daily loss
ceiling, not by post-hoc "looked unreasonable in backtest"
inspection.

**Recommended pattern:** when in doubt, fixed-risk-dollar with a
cap. It is the closest thing the repertoire has to a default.

### Volatility-scaled

When the volatility input is ATR and the stop is ATR-based, this
is identical to fixed-risk-dollar. Treating it as a separate
pattern is mostly framing — useful to surface the connection.

### Kelly-fraction

Theoretically optimal for log-utility wealth. In practice,
requires accurate estimates of win-rate and payoff distribution,
both of which are notoriously fragile out-of-sample. Even
fractional-Kelly (e.g., 0.25 Kelly) inherits the estimation
problem.

**Recommendation:** do NOT use without separate validation of
win-rate / payoff stability across in-sample sub-periods. Not
appropriate for our current sample sizes.

### Tiered-by-setup-quality

Different size for "AA+", "A", "B" setups, where the tier is
defined by some pre-trade quality metric (e.g., signal strength
score, regime confirmation count).

**The edge concept is real**: higher-conviction trades probably
do have higher expected returns. The serious risk is selection
bias: if tier thresholds are calibrated on in-sample results
(consciously or not), the tier becomes a curve-fit dressed as
"setup quality."

**Safeguards:** pre-commit the quality metric AND its tier
thresholds. Round numbers preferred. Held-out cohort for tier
threshold validation. Skip if you cannot defend the metric in
writing before in-sample testing.


## Section 3: Stop Placement Patterns (CORE; full draft)

**Status:** EMPIRICALLY-GROUNDED for fixed-point (negative
result across four strategies); WORKING-FRAMEWORK for the
others.

### Fixed-point

A constant point distance from entry. PRJ_3 used 30pt; noise_brk
used 32pt; ema_trend used 30pt; variant_1 used a fixed bracket.
All four failed Apex 50K eval at ~$-2K cumulative.

**The empirical pattern:** when the bracket doesn't adapt to
volatility, it is too tight on high-vol days (premature stop-outs
on noise) and too loose on low-vol days (unnecessarily large
losses when the thesis is invalidated quickly). The asymmetry
compounds — the high-vol losses arrive faster than the low-vol
wins.

**When (rarely) appropriate:** as a baseline for comparison, OR
when the strategy's thesis is anchored to a specific dollar
risk per trade and the trader explicitly accepts the vol-mismatch
trade-off.

### ATR-scaled

`stop = entry +/- multiplier × ATR(period)`. The conventional
default is 1.5×ATR(14), though 1.0–2.5× is the common practical
range. PRJ_6 NoiseBrk live uses ATR-percentile-derived band
widths.

**When appropriate:** as the default for any strategy where the
edge concept does not specifically depend on a structural level.
Adapts automatically to regime shifts.

**Pre-commit requirements:** ATR period and multiplier, both
documented in the spec before in-sample fitting. Resist the
temptation to "see which multiplier works best" — that is the
specific Level 1 curve-fit failure mode.

### Level-based (structural)

Stop placed where the trade thesis is invalidated — typically
just past a recent swing extreme, VAH/VAL, prior-day high/low,
or a round number. This is a different *concept* from vol-based
stops: it answers "if price reaches X, my thesis is wrong"
rather than "how much dollar risk am I taking."

**When appropriate:** strategies where the entry logic
explicitly references a level (e.g.,
`prior_day_value_area_rejection`, `failed_orb_fade`,
`round_number_rejection_microfade`). The structural stop
respects the trade's logical premise.

**Complement, not replacement:** a structural stop can be paired
with a vol-based maximum-loss cap. If the structural level is
unusually far (high-vol day), the cap converts it to fixed-risk.

### Trailing variants

- **Chandelier exit:** highest-high − N × ATR (long); converse
  for short. Standard since Le Beau / Lucas.
- **Percentage trail:** fixed percentage from running peak.
  Simple, vol-blind — same critique as fixed-point.
- **Swing-based trail:** trail to most-recent confirmed
  swing extreme. `developing_swing_trail_vol_cap` proposes
  this, gated by Level 2 ATR-percentile cap.

**Curve-fit risk:** any trail parameter (lookback length,
ATR multiplier, swing confirmation count) is a degree of
freedom. Pre-commit. Two- or three-multiplier sweeps in
in-sample run a real risk of finding the cherry-picked one.

### Relationship to position sizing

Stop distance × contracts × point-value = dollar risk. The
sizing pattern and the stop pattern must be designed together,
not separately. The cleanest pattern: ATR-scaled stop +
fixed-risk-dollar sizing. They use the same volatility input
and produce a regime-invariant dollar risk.


## Section 4: Profit Target Patterns (lighter)

**Status:** WORKING-FRAMEWORK.

- **Fixed-point:** constant point target. Inherits the same
  vol-mismatch problem as fixed-point stops. Discouraged.
- **ATR-multiples:** `target = entry ± multiplier × ATR`.
  Pairs naturally with ATR-scaled stops; produces a fixed R-
  multiple (e.g., 1.5R target if multiplier matches 1.5× stop).
- **R-multiples:** target expressed as multiple of stop
  distance. `take_profit = entry ± 1.5 × stop_distance`. Bracket
  symmetric regardless of underlying stop mechanism.
- **Level-based:** target at POC, VAH/VAL, prior-day extreme,
  next round number. Pairs naturally with level-based entries.
- **Trailing-only (no target):** let the trail handle exits.
  Higher reliance on trail discipline. Suits Level 3 adaptive
  exits (`developing_swing_trail_vol_cap`).
- **Partial scale-outs:** half off at 1R, runner trails. Adds
  bracket complexity; each scale point is a parameter to
  pre-commit.

**Safeguard:** the asymmetry of fixed-target + trailing-stop
versus trailing-stop + no-target affects win-rate distribution
in ways that look like edge but are bracket geometry. Hold
brackets fixed across in-sample variations; do not "find the
target that works best."


## Section 5: Entry Timing Patterns (lighter)

**Status:** EMPIRICALLY-GROUNDED for the lookahead lesson;
WORKING-FRAMEWORK for the rest.

- **At-signal (signal-bar close):** fill at the close of the
  bar on which the signal fires.
- **T+N-second delay:** fill N seconds after the signal time
  (typical N: 1–5s). Captures realistic execution slippage.
- **Pullback-and-retest:** wait for a partial retracement and
  re-confirmation before entering. Adds a parameter (retracement
  depth).
- **Breakout-confirmation:** require a second close beyond the
  breakout level. Adds a parameter (confirmation count).
- **Time-window filter:** signal only valid inside a specific
  RTH window (e.g., 09:45–14:30 ET). Avoids open/close noise.

**Lookahead caution (PRJ_3 Canonical Alpha audit, 2026-04
through 2026-05):** when the signal references a value
computable only at bar close (e.g., a confirmation close above
prior swing), the signal timestamp must be the bar's CLOSE
time, not its OPEN. The PRJ_3 pre-fix used left-edge timestamps
for close-based confirmations — internally an apparent edge
(n=169) that collapsed (n=9) once the signal time was shifted
to bar-close. Robustness tests (repro + OOS + multistart 17/17)
all shared the same lookahead and so were not independent
confirmation. Always run the 4-surface lookahead audit
(signal_ts vs decision-knowability, indicator warmup, fill
attribution, exit attribution) before claiming an edge.


## Section 6: Regime Classification Approaches (lighter)

**Status:** WORKING-FRAMEWORK. None of the tested fleet used
regime classifiers; all candidate use is theoretical.

- **Volatility regimes:** `ATRPercentile`, `ATRZScore`,
  `ATRRatio(short, long)`. Most commonly used in the candidate
  pool. Round-number percentile cutoffs preferred (25/50/75).
- **Trend regimes:** ADX (NOT in nb_lib), `ChoppinessIndex`,
  `HurstExponentDFA`. Choppiness near 60+ generally indicates
  range; near 38 indicates trend. Hurst > 0.5 trending; < 0.5
  mean-reverting; these are noisy estimators at intraday
  windows.
- **Time-of-day regimes:** open hour (09:30–10:30), midday
  (11:30–13:30), close hour (15:00–16:00) all have distinct
  volatility and microstructure profiles. Used implicitly via
  `time_of_day` frontmatter window in most candidates.
- **Event regimes:** FOMC days, NFP days, OPEX days
  (TradingCalendar event tags). Per HANDOFF Calendar
  Limitations, FOMC/NFP/OPEX tags are accurate; CPI/GDP are
  over-tagged ~2.2–2.3× and need external data acquisition if
  date-precision matters.

**Safeguard:** every regime threshold is a hidden parameter.
Pre-commit ALL of them. A "trend regime" defined as ADX > 25
on the 30-min bar is two parameters (indicator + threshold +
timeframe). Treat regime gates with the same audit rigor as
entry rules.


## Section 7: Risk Management Patterns (lighter)

**Status:** EMPIRICALLY-GROUNDED for the Apex 50K constraints;
WORKING-FRAMEWORK for the rest.

- **Heat cap (max simultaneous open risk):** sum of open-trade
  stop-distance-to-dollar exposures must not exceed cap.
  Relevant when a strategy holds multiple positions.
- **Daily loss limit:** stop trading after N daily loss. For
  Apex 50K, the natural limit is $1K (DLL) — but most evaluators
  recommend a stricter operator-side limit (e.g., $700) to leave
  headroom.
- **Per-trade $-cap:** `min(stop-distance-implied risk,
  hard cap)`. Pairs with fixed-risk-dollar sizing; converts
  outlier-stop-distance trades to fixed-loss trades.
- **Trailing-drawdown circuit breaker:** the post-FAILED outer-
  loop fix (methodology debt J#3 closed 2026-05-09) added
  `if tracker.state == AccountState.FAILED: break` to all three
  nb_lib-native consumer scripts. This ensures no synthetic
  compliance-forced trades pollute post-FAILED statistics.
  Production strategies should adopt this pattern.
- **Equity-curve filtering:** suspend trading after losing
  streak; resume after recovery. Highly susceptible to
  curve-fit and to forward-bias when "streak" is defined
  post-hoc. Use with extreme caution.

**Apex 50K specific implications.** $2K trailing drawdown at
15-MNQ default = $13.33 per contract per point lost. A single
30pt loss (~$900) is 45% of the buffer. Sizing patterns that
reduce per-trade variance (fixed-risk-dollar) are operationally
preferred for the eval profile over patterns that produce
high variance (fixed-contract with vol-mismatched stops). All
four tested strategies failed the eval at ~$-2K.


## Section 8: Indicator Catalog (lighter; tabular)

**Status:** EMPIRICALLY-GROUNDED inventory of nb_lib; the "NOT
in nb_lib" table is a methodology checklist for future strategy
needs.

### A. Currently in nb_lib

| Indicator | Description | Common params | Library status |
|---|---|---|---|
| ATR | Average True Range, volatility measure | period=14, smoothing=Wilder | `nb_lib.indicators.ATR` |
| ADR | Average Daily Range, simpler vol measure | period=20 | `nb_lib.indicators.ADR` |
| VWAP | Volume-Weighted Average Price | 3 anchors: rth/premarket/eth | `nb_lib.indicators.VWAP` |
| EMA | Exponential Moving Average | period varies | `nb_lib.indicators.EMA` |
| SMA | Simple Moving Average | period varies | `nb_lib.indicators.SMA` |
| ATRPercentile | ATR rank in trailing history | window=60, period=14 | `nb_lib.indicators.ATRPercentile` |
| ATRZScore | ATR Z-score vs trailing mean | window=60, period=14 | `nb_lib.indicators.ATRZScore` |
| ATRRatio | Short/long ATR ratio, regime change detector | short=5, long=20 | `nb_lib.indicators.ATRRatio` |
| ChoppinessIndex | Trend vs range regime (Dreiss 1993) | period=14 | `nb_lib.indicators.ChoppinessIndex` |
| RollingStdev | Windowed std deviation | window varies | `nb_lib.indicators.RollingStdev` |
| SessionStdev | Session-anchored std | per-session | `nb_lib.indicators.SessionStdev` |
| BollingerWidth | Bollinger Band width | period, stdev_mult | `nb_lib.indicators.BollingerWidth` |
| KeltnerWidth | Keltner Channel width | ATR-based | `nb_lib.indicators.KeltnerWidth` |
| DonchianWidth | Donchian Channel width (highest-high − lowest-low) | period | `nb_lib.indicators.DonchianWidth` |
| MassIndex | Volatility expansion (Dorsey 1992) | period=25 | `nb_lib.indicators.MassIndex` |
| VortexIndicator | Trend direction + strength | period=14 | `nb_lib.indicators.VortexIndicator` |
| HurstExponentDFA | Trending vs mean-reverting regime | window | `nb_lib.indicators.HurstExponentDFA` |
| AmihudIlliquidity | Liquidity-proxy regime | window | `nb_lib.indicators.AmihudIlliquidity` |
| RealizedVariance | High-freq volatility (Andersen 1999) | window | `nb_lib.indicators.RealizedVariance` |
| RealizedRange | HF volatility (Christensen-Podolskij 2007) | window | `nb_lib.indicators.RealizedRange` |
| BipowerVariation | Jump-robust volatility (BNS 2004) | window | `nb_lib.indicators.BipowerVariation` |
| PermutationEntropy | Randomness measure (Bandt-Pompe 2002) | order, window | `nb_lib.indicators.PermutationEntropy` |
| HARVarianceFeatures | HAR variance model (Corsi 2009) | multiple windows | `nb_lib.indicators.HARVarianceFeatures` |
| compute_true_range | Wilder TR helper | per bar | `nb_lib.indicators.true_range` |

### B. Commonly used but NOT in nb_lib

| Indicator | Description | When useful | Library status |
|---|---|---|---|
| ADX | Trend strength (Wilder 1978) | trend-following strategies needing strength filter | NOT in nb_lib; would need building |
| DI+ / DI- | Directional movement components | trend direction with ADX | NOT in nb_lib |
| RSI | Relative Strength Index (Wilder 1978) | oscillator for mean-reversion | NOT in nb_lib (surprisingly missing) |
| MACD | Moving Average Convergence Divergence | trend + momentum signal | NOT in nb_lib (surprisingly missing) |
| Stochastic Oscillator | %K/%D oscillator | overbought/oversold | NOT in nb_lib |
| Volume Profile / POC / VAH / VAL | Auction market structure | level-based strategies (`prior_day_value_area_rejection`, `vwap_band_acceptance_regime`) | NOT in nb_lib; flagged for primitive promotion if multiple strategies need |
| TPO Profile | Time-Price-Opportunity profile | market profile analysis | NOT in nb_lib |
| Floor Trader Pivots | Classic S/R levels (R1/R2/S1/S2/PP) | level-based strategies | NOT in nb_lib; trivially derivable |
| Anchored VWAP | VWAP from arbitrary anchor (not just session start) | event-anchored fair value | nb_lib has session VWAP; not arbitrary anchors |
| Fibonacci Retracement Levels | Retracement levels from swing | level-based pullback entries | NOT in nb_lib |
| Cumulative Volume Delta | Buy vs sell volume cumulative | order flow proxy | NOT in nb_lib; requires bid/ask tick data |
| Order Flow / Footprint | Per-bar bid/ask volume detail | microstructure strategies | NOT in nb_lib; requires tick data we don't have |
| Pivot Highs/Lows (fractal) | Swing detection | PRJ_3 used this inline | helper exists inline in PRJ_3; not promoted to library yet |

Promotion to nb_lib follows the N≥3 gate (skills_inventory Skill 3
— architectural-boundaries): an indicator should be used by at
least three distinct strategies before being promoted from inline
helper to library primitive.


## Appendix A: Methodology Patterns from Past Iterations

Established patterns from the iteration history. One-line each;
full context in the cited iteration report.

- **4-surface lookahead audit** — for any new strategy, inspect
  signal_ts vs decision-knowability, indicator warmup, fill
  attribution, exit attribution. Origin:
  `nb_lib_prj3_raw_signal_diagnostic_report.md`.
- **Origin check (Stage 0a)** — before fitting, verify each
  indicator's first valid bar timestamp matches expected warmup.
  Origin: ema_trend / PRJ_3 origin-check pattern.
- **Research-mode outer loop** — methodology debt J#3 closed
  2026-05-09. Outer loop must check `tracker.state ==
  AccountState.FAILED` and break before constructing new
  TradeLifecycle. Pre-fix produced synthetic post-FAILED
  compliance-forced trades.
- **Runtime assertions in production** — non-trivial preconditions
  (ATR non-NaN, stop distance positive, etc.) should be runtime
  assertions, not "we'll catch it in review."
- **Robustness-tests-share-bug lesson** — PRJ_3 multistart 17/17
  pass + OOS pass + repro pass all shared the same lookahead
  bug. Internal consistency is NOT independent confirmation;
  audit the surface itself.
- **Wiki-as-ideation-pipeline** — strategy candidates in
  `candidates/` are progressively triaged via Dataview queries
  on YAML frontmatter. See `candidates/README.md`.
- **Conditional-stage-with-grep-gate** — for iterations whose
  later stages depend on whether earlier-stage findings match
  certain patterns, gate via grep and skip the dependent stage
  with explicit "skipped — reason" report entry.
- **Snapshot-first methodology** — every modification iteration
  begins with a timestamped snapshot under
  `_snapshots/nb_lib_v<version>_<task>_<YYYYMMDD>_<HHMM>/`
  (rounded to 5-minute boundary).
- **Reduced regression scope** — documentation-only or surgical
  iterations skip baselines that cannot be mathematically
  affected. Trade-off explicitly per-iteration.


## Appendix B: Cross-References to Skill Files

### Skill files in project / wiki

- **`skills_inventory_nb_lib.md`**: project-root reference
  artifact (25,282 bytes; mtime 2026-05-09). Documents 8 skills
  not yet implemented as SKILL.md files: Layer 1 general
  (agent-iteration-orchestration, strategy-spec-development,
  architectural-boundaries, halt-discipline-pattern,
  spec-verification-pass) and Layer 2 nb_lib-specific
  (nb-lib-conventions, apex-4.0-deployability, nb-lib-data-
  hygiene). Located at:
  `C:/VMShare/NT8lab/skills_inventory_nb_lib.md`.
  Cross-references: Skill 3 (architectural-boundaries, N≥3
  promotion gate) is referenced by Section 8 of this repertoire;
  Skill 7 (apex-4.0-deployability) overlaps with Section 7's
  Apex 50K specific implications.

### Skill files in Claude Code's local skills directory

- None found. `C:/Users/meme/.claude/skills/` does not exist.
  Only plugin-marketplace SKILL.md files were present under
  `C:/Users/meme/.claude/plugins/...`, none related to nb_lib
  or trading.

### Other methodology-tagged files in project (informational)

- **`ninja-traitorate-methodology-reference.md`** (root,
  41,876 bytes, mtime 2026-05-01). The NoiseBrk live-trading
  framework authority per root CLAUDE.md. Out of scope for
  this nb_lib-focused repertoire but documented here so future
  readers do not conflate the two methodology layers.

### How to use these alongside the repertoire

Skill files describe HOW we work (iteration discipline, halt
classification, architectural promotion gates). This repertoire
describes WHAT design choices are available to a strategy and
what their methodology risks are. Both serve as references;
overlap (e.g., Section 7's drawdown-circuit-breaker and Skill 7's
apex-4.0-deployability) is intentional. When a skill file and
the repertoire disagree, the skill file wins for process
questions; the repertoire wins for design choices.
