# Ninja Traitorate — Methodology Reference

This is a permanent reference, not a session checkpoint. It documents the
testing methodology, conventions, and anti-patterns we've built up across
sessions. New sessions should read this before doing strategy research.

The strategies come and go. The methodology is the durable asset.

For research-with-agents discipline patterns that apply across projects
(LLM Wiki pattern, gate-not-rescue rule, no-retroactive-rewrite,
structured templates, etc.), see `_FRAMEWORK/PATTERNS.md`. Those are
general principles; specifics in this methodology reference take
precedence on conflicts.

---

## 1. Architecture overview

**`prj_realsim.py`** is the central simulation engine. ~100KB. Handles:

- Loading 28M+ rows of 1-second OHLC data from databento DBN files
- Pre-grouping into 430+ trading days (one-time cost, then fast)
- Per-strategy entry-detection logic (NB, TP closed, TP partial, TP_v2, VWAP)
- Unified `manage_position()` for stop / BE / TP1 / TP2 / trail logic
- Auth-delay model (auto vs click with reflex variance)
- Realism axes: slippage, commission, base latency, reflex jitter
- Bucket-window date filtering (training/test/validation per family)
- Trade output to CSV with rich per-leg detail
- Per-run summary text file with exit breakdown

**Strategy modules** live in NinjaScript (`PRJ_*.cs`) for live execution.
The realsim engine and the .cs files are separate codebases — same logic
in two languages. Keeping them in sync requires care.

**Helper scripts** live alongside `prj_realsim.py`:

- Per-strategy gauntlet runners (`*_train.py`, `*_test.py`, `*_validate_final.py`)
- Detective-analysis scripts (`*_detective.py`)
- Battery runners (multi-config sweeps within budget discipline)
- Bucket usage trackers (JSON files that prevent budget overruns)

---

## 2. Realism axes

The engine models five sources of friction. All locked at deploy-honest values.

### Slippage
`SLIPPAGE_PTS = 0.25` per stop/EOD exit. Applied as price worsening on
fills that aren't TP1/TP2 limit fills. TP1/TP2 limit fills get 0 slippage
(limit orders fill at the exact level or not at all).

### Commission
`COMMISSION = 0.35` per contract per side. Charged twice per trade
(entry + exit). For the 7+8 contract VWAP/TP split, that's 15 × $0.35 × 2
= $10.50 per round-trip in commission alone.

### Base machine latency
`BASE_DELAY_DEFAULT_BARS = 1` (1-second bar). Models the system's own
reaction time after a signal: poll cadence, ATM submission roundtrip,
broker acknowledgement. Setting `--base-delay-bars 2` reproduces an older
convention in `prj7_simulate` / `PRJ3_verify` (ENTRY_DELAY=2).

### Auth-mode reflex variance
`AuthDelayModel` adds a HUMAN-component delay on top of base latency.
- `auto`: 0 seconds (no human in loop, fully automated firing)
- `click`: 0.5-1.5 second uniform reflex, with a 1-in-20 distraction
  override that bumps reflex to 2.0 seconds.

The reflex draw uses a seeded RNG (`RANDOM_SEED = 20260424`). Re-runs
with the same seed produce identical click-mode delays — important for
reproducibility.

### Random seed determinism
All randomized components (currently just reflex) flow through one seed.
Lock the seed once. If an experiment requires varying it, do so explicitly
and document why.

---

## 2A. Engine-integrity rerun rule

Any pre-2026-06-16 result computed through `compute_realistic_pnl()`
predates the conservative worse-fill rounding upgrade and may shift
slightly, in the conservative direction, if re-run. Before reviving or
relying on any such finding -- specifically ORWS v2 base-hit,
objective-level liquidity sweep, tight-opening-window breakout, or any
`realdata_validation` output -- re-run it on the corrected engine first
and confirm the conclusion still holds. Do not trust the old absolute
number.

This rule does not invalidate old findings by itself. The expected shift
is small and conservative. The discipline is: verify before relying on
old absolute P&L, especially when the finding is being promoted, compared
against a newer result, or used to justify fresh implementation work.

The 2026-06-16 bridge-execution fix already re-verified the active
management findings it touched directly: Step 3 v0.2 delayed-BE, Step 3
v0.3 regime-conditioned BE, and the V4A/V4D geometry rebuild.

---

## 3. Bucket discipline

The single most important methodology choice we've made. Three principles.

### Three buckets per strategy family

For each strategy family, we partition history into:

- **Training** (~70%): exploration. Run anything you want here. Surface
  patterns, test heuristics, sweep parameters within reason. Multiple
  looks allowed.

- **Test** (~20%): one-shot per (strategy, anchor, parameter-set) tuple.
  Records pre-committed candidates from training. Validates whether
  training-discovered patterns generalize.

- **Validation** (~10%): one-shot per strategy family, EVER. Final
  out-of-sample. Burned only on the candidate that survived training+test.

We've now run this structure for VWAP and NB. The bucket dates
themselves are calendar-aligned to allow cross-family comparison
(e.g., training_nb and training_vwap cover the same Aug 2024 - Sep 2025
period, just labeled separately).

### Why three, not two

Two buckets (train/test) have a known failure mode: each "test" run
informs your next training tweak, and you converge to a config that
passes test by accident across many tries. Validation prevents this by
being sealed. Once you've selected a candidate from train+test, validation
gives you an honest read uncontaminated by your selection process.

### Budget tracking

Each strategy family has a `*_bucket_usage.json` tracker. Test_* and
validation_* slots are explicitly recorded as consumed. Final-validation
scripts refuse to re-run if the budget is already spent. This is
discipline enforced in code, not just in head.

---

## 4. Pre-commitment protocol

For any test that consumes test or validation budget:

1. **Write down the configuration** before running. Strategy, auth, mgmt,
   anchor, all parameters. Locked. No changing.
2. **Write down the criteria** before running. Edge metrics (legs, WR, PF,
   net) with specific thresholds. Deployability tag (DD ranges → account
   sizes).
3. **Verify every input file covers the locked window.** Before a sealed
   test, list every file the policy reads (price data, ATR/history,
   calendars, regime maps, cost parameters, model artifacts) and confirm
   each covers the full OOS window using the same convention as the
   in-sample run. Missing input coverage must be fixed and frozen before
   scoring, not patched inside the scoring run.
4. **Run the test once.** No re-running with different config to see if
   it does better.
5. **Read the result against the locked criteria.** The result is what it is.

Pre-commitment scripts (e.g., `prj_realsim_*_validate_final.py`) bake this
into code: they construct the command, run it once, parse the output
against locked criteria, write to the budget tracker, refuse to re-run.

### Graded reporting, not binary

Pass/fail is too coarse. Three-tier grading is more honest:

- **PASS** — meets all criteria
- **NEAR-MISS** — within 10% of one criterion (real tweak candidate)
- **FAIL** — misses by >10%

Within FAIL, distinguish:
- **HARD FAIL** — PF < 1.0 with significant net loss, or WR < 20%
- **MARGINAL FAIL** — small negative, low PF
- **MIDDLE FAIL** — below threshold but not catastrophic

Different actions follow from different fail modes. Hard fail = real
evidence against this config. Marginal = ambiguous, may be regime.

---

## 5. The "criteria are choices, not laws" lesson

We learned this the hard way. We set criteria (WR ≥ 28%, PF ≥ 1.3, etc.)
based on intuition + early data. Applied them to validation. VWAP failed.
Then we ran NB through the same gauntlet — and **NB also failed our
criteria**, despite being deployed in production and profitable.

**The criteria were miscalibrated for the strategy class.**

### What this taught us

- Pre-committed criteria SHOULD be informed by a known-deployable
  reference point, not picked from the air
- A strategy in production gives you a calibration target: if your
  criteria reject your own working strategy, the criteria are too strict
- "Failing validation" can mean "criteria too strict" rather than
  "strategy has no edge"
- Recalibration based on a known-deployable reference is NOT curve-fit;
  picking thresholds that just happen to make the candidate pass IS

### Practical rule

Before locking criteria for a new test, ask: would these criteria reject
NB (our known-deployable benchmark)? If yes, the criteria are too strict.
Soften them. If they would reject NB AND the candidate is meant to be in
the same class as NB, that's a misalignment worth fixing.

---

## 6. Edge vs deployability — separate questions

These are different questions. Don't bundle them.

**Edge:** does the strategy generate positive expectancy out-of-sample?
Measured by WR, PF, net.

**Deployability:** can this fit on the account / firm / position-size
configuration we have? Measured by max DD against account-size DD
buckets (50K-ok, 100K-ok, 150K-ok, needs-adapt).

A strategy can pass edge and fail deployability (real but needs bigger
account). Or pass deployability and fail edge (won't lose much but won't
make money either). Both pieces of information matter.

Reporting should show BOTH. Don't gate one on the other. A NEAR-MISS on
edge with 50K-ok deployability is a tweak candidate worth investigating.

### Two-axis verdict framing (hardened 2026-06-09)

Do not treat Apex's $2K trailing drawdown rule as if it were a property
of the strategy. It is a property of one deployment vehicle.

Every management-research verdict should separate two axes:

1. **Edge axis**: does the rule add risk-adjusted P&L on holdout in a
   generic cash-account framing? Evaluate return per unit of additional
   drawdown, partition consistency, and substrate replication.
2. **Deployability axis**: can that same rule survive the specific
   Apex EOD 50K constraints under worst-plausible sequencing? Evaluate
   trailing drawdown, daily loss, and account-death risk separately.

A rule can be **edge-positive** and **Apex-needs-containment** at the
same time. That is not a failed rule. It is an edge with a deployment
packaging problem. The next question becomes whether drawdown
containment, sizing, branch disabling, or a different vehicle can carry
the edge without destroying it.

Operational ground truth:

```text
A drawdown increase that fails Apex is information about Apex fit,
not automatic evidence that the edge is bad.
```

When a result reports increased max DD, ask in sequence:

1. Given the P&L gain, is the added drawdown favorable on a
   return-per-risk basis?
2. Would Apex's specific trailing mechanic survive the drawdown in
   worst-case ordering?

If the answer is yes to the first and no to the second, record the
verdict as edge-positive / deployability-needs-containment, not as a
single-axis "risk unresolved" failure.

### Deployability tag thresholds (locked)

- DD ≤ $2,000 → 50K-deployable (Apex 50K EOD trail)
- DD ≤ $4,000 → 100K-deployable
- DD ≤ $6,000 → 150K-deployable
- DD > $6,000 → needs adaptation (smaller size, trail variant, etc.)

These are real prop firm rules, not arbitrary. The 50K Apex rule with
$500 buffer is the binding constraint for our default fleet.

### Apex 50K EOD V4.0 limitation (recorded 2026-05-01)

The full reference note lives at:
`Apex Trader Funding 50K EOD account rules after the March 2026 overhaul.MD.txt`

For future deployability calls, "50K-deployable" means the backtest max DD
fits inside the $2,000 EOD trailing drawdown constraint. It does NOT by
itself mean the strategy is Performance Account viable under the March 1,
2026 Apex V4.0 rules.

The extra constraints that matter for this lab:

- 50K EOD eval: $3,000 target, $2,000 EOD trail, $1,000 daily loss limit.
- Eval size: up to 6 mini contracts / 60 MNQ micros.
- PA starts smaller: Level 1 begins at 2 minis / 20 MNQ micros, with a
  maximum of 4 minis / 40 MNQ micros at Level 4.
- PA safety net / lock logic means profit below roughly $52,100 is not
  withdrawable cushion. Minimum $500 payout requires about $52,600 balance.
- PA payouts are capped at six withdrawals / $13,000 total extraction; the
  PA then closes permanently.
- Automation is allowed in eval but banned in PA except for copying one's
  own trades across one's own accounts. Any production plan that depends on
  unattended auto-trading is therefore eval-compatible but PA-limited.

Practical interpretation: when a strategy uses eval-size exposure, report
two separate conclusions:

1. **Eval deployability**: can it pass within $2,000 trail and $1,000 DLL?
2. **PA deployability**: can the same edge survive Level-1 sizing and payout
   constraints?

If the edge requires the full 6-contract eval size, tag it as
`50K-eval-only` until retested at PA Level 1 sizing. The 100K account may be
structurally better when the 50K PA's 2-contract start breaks the strategy's
expected-value profile.

---

## 7. Detective analysis pattern

When training results are mixed (some cells positive, some negative),
detective analysis surfaces structural patterns before pre-committing
heuristics.

### Procedure

1. Load all trade CSVs from training (multiple cells)
2. Tag each trade with derived features: day-of-week, time-of-day bucket,
   ATR regime quartile, direction, exit type
3. Cross-tabulate: feature × outcome (mean P&L, WR, etc.)
4. Two-way matrices: strategy × anchor, dow × strategy, ATR × strategy
5. Outliers: best/worst single trades, best/worst dates, regime days
   (where all cells lost or all won — macro-event signal)
6. Output text reports + raw all-trades CSV for slicing

### Discipline

- Detective output is **diagnostic, not prescriptive**
- Patterns surfaced are **hypotheses for test bucket**, not deployment
  decisions
- Pick **at most ONE** structural pattern to test, not stack many
- "Looks interesting" isn't enough — pattern must be visible across
  multiple cells AND make structural sense

### What counts as structural

- Pattern visible across MOST cells (not just the leader): structural
- Pattern visible in ONE cell: incidental, ignore
- Pattern with a plausible market mechanism (e.g., 9:50 chop after open
  auction): more likely real
- Pattern with no mechanism (e.g., "negative on Tuesdays specifically"):
  treat with extra suspicion

---

## 8. ATR-management design

Two management modes are supported in `prj_realsim.py`:

### Fixed mode
Locked values: `stop=25, TP1=10, TP2=80, BE_trig=6` (points). Same for
both NB and TP/VWAP families. Contract splits differ (NB: 3+3, TP/VWAP: 7+8).

### ATR-scaled mode
Multipliers applied to daily ATR(20):
- `ATR_MULT_STOP    = 0.25`
- `ATR_MULT_TP1     = 0.10`
- `ATR_MULT_TP2     = 0.80`
- `ATR_MULT_BE_TRIG = 0.06`

Calibrated so that at typical MNQ regime (ATR≈100), ATR-mgmt produces
values close to fixed-mgmt. Adapts proportionally on quiet (ATR<60) or
volatile (ATR>140) days.

### Validity bounds
ATR mode falls back to fixed if computed ATR is outside `[ATR_MIN_VALID,
ATR_MAX_VALID] = [30, 250]`. This is a deployment safety check — a glitchy
ATR of 5 or 500 won't produce absurd stops.

### Why locked, not swept
The multipliers are pre-committed. We do not sweep them. Picking them by
"what training shows works best" IS curve-fit. We test ATR-mgmt as ONE
configuration. If it improves results, it's a real finding. If not, no
amount of multiplier tuning makes it real.

---

## 9. Trail-method conventions

Multiple deployable trailing-stop conventions are registered in
`TRAIL_METHODS`. Each is a fully pre-specified configuration.

### Deployability constraint

**Trail updates MUST happen at intervals of at least 5-10 seconds, ideally
1 minute (60 seconds).** Tick-by-tick trailing is gaming the system —
brokers rate-limit modifications, the live system can't do thousands of
updates per second cleanly, and backtests would produce results that
don't translate.

Our convention: **trail levels recompute only at 1-minute bar close**
(60-second cadence). This is enforced in `precompute_trail_for_day()` —
the trail level for any 1-second bar within minute M is the level
computed at minute M-1's close.

### Activation rule

Trails activate ONLY after BE arms (after MFE reaches BE trigger AND
BE_DELAY_BARS have passed). Pre-BE stop logic is unchanged. Trail
replaces the flat-BE stop.

### Ratchet only

Trail can only TIGHTEN, never loosen. Once the trail level moves to X
(better than entry for the position), it cannot move back. This is the
standard convention for trailing stops.

### Methods registered

- `fixed` — baseline, no dynamic trail (BE flat after arm)
- `atr_levels` — baseline, ATR-scaled mgmt levels (no dynamic trail)
- `chan_14_3` — canonical Chandelier Exit (LeBeau, lookback 14m, mult 3.0)
- `chan_14_2` — tighter chandelier (mult 2.0)
- `chan_14_4` — wider chandelier (mult 4.0)
- `chan_pred_5s` — chandelier with 5-second lead estimate
- `swing_low_14m` — pure swing-low/high trail (no ATR)
- `ema_9_1m` — 9-period EMA on 1-min closes
- `two_stage_4_2` — chandelier mult 4.0 pre-TP1, 2.0 post-TP1
- `chan_capped` — chandelier capped to entry +/- 1.0 × daily ATR(20)

### Predictive variant

`chan_pred_5s` adds an early estimate at second 55 of each minute, using
partial-minute data to predict the level the chandelier will move to at
minute close. This is latency-hiding (gets the modification on the book
before the actual minute closes), NOT lookahead. The estimate uses only
data available at second 55. If the estimate is wrong, the actual close
overrides it 5 seconds later.

---

## 10. Anti-patterns and lessons learned

Sessions burned ourselves on each of these. Documented to prevent repeats.

### Lookahead via labeling
PRJ_2 forecaster trained labels on data containing the answer. Caught
when out-of-sample performance was suspiciously good. **Rule:** train
labels must use only data available at the moment of the prediction.
Audit labeling code carefully when results look too good.

### Identical results across "different" variants
PRJ_3 had two variants returning identical PnL down to the cent. Yellow
flag: either the variants are functionally identical OR the variant
selection is no-op. **Rule:** if two configs that should differ produce
identical numbers, stop and investigate before celebrating.

### Detection lag vs hold time
PRJ_7 trend-pullback live audit revealed a 60-second detection lag (script
polling cadence). Hold times were short enough that 60s lag wiped the
edge. **Rule:** measure detection-to-fill latency in production and ensure
it's small relative to typical hold time. The realsim engine models this
explicitly via `BASE_DELAY` + reflex.

### Tired-research bugs
Long sessions produce subtle bugs: format string crashes, no-op flags,
off-by-one errors. These don't reveal themselves on syntax check —
they reveal themselves at runtime. **Rule:** do a sanity-pass on output
before celebrating. If something looks too clean (zero stops fired, all
trades winning, identical numbers), investigate.

### "Spaghetti at the wall" needs discipline
Exploration mode (testing many configs cheaply) is legitimate. The trap is
treating exploration results as deployment evidence. **Rule:** exploration
runs use training+test buckets only. Validation buckets stay sealed for
ONE final candidate per strategy.

### Multi-comparison drift
Running 10 methods through 3 buckets gives 30 verdicts. Even with discipline,
expecting 1-2 false positives is realistic. **Rule:** read the matrix as
a whole. A method that improves training AND test consistently is more
trustworthy than one that does brilliantly on one bucket only.

### Anchor selection should match hypothesis
Sweeping all anchors (rth, pre_market, eth) for VWAP turned up patterns
incidental to the data, not the strategy. **Rule:** pick the anchor that
matches the strategy hypothesis. If reclaim/pre_market is the thesis,
test that. Don't test all 9 cells.

### "VWAP family closed" framing was wrong
Failure to clear arbitrary thresholds isn't strategy death. **Rule:**
thresholds are choices. A strategy that doesn't pass criterion X may pass
criterion Y, and the right calibration is informed by reference points
(like NB's actual production numbers).

### Edge and deployability are separate
Bundling them ("must pass edge AND fit 50K") rejected real edges that
just needed bigger accounts. **Rule:** report both, gate neither on the
other.

### Tired check-ins waste energy
Process-management overhead (asking "are you ready", "should we stop")
adds friction to the work. **Rule:** if a real correctness issue shows up,
flag it once, clearly. Otherwise execute.

---

## 11. NinjaScript / NT8 implementation rules

(Cross-reference: `nt8-backtest-engineering` skill in `/mnt/skills/user/`.)

Quick summary of the five non-negotiables for NT8 backtest .cs files:

1. **Single 1-second primary series** — no mixed timeframes
2. **Unreachable-TP-then-modify pattern** for MIN_HOLD enforcement
3. **FromEntrySignal exit routing** — never exit by direction alone
4. **Pure TimeSpan RTH gating** — not Time-of-Day comparisons
5. **Recent-data-only window** — filter to known-good date range

These are rules, not guidelines. The skill file documents them in detail
with pseudocode templates and diagnostic toolkit.

---

## 12. Skills inventory

User skills in `/mnt/skills/user/`:

- `nt8-backtest-engineering` — NT8 .cs file conventions, the five rules above

Public skills frequently used:

- `pdf` — read/extract PDFs (rule documents, prop firm changes)
- `xlsx` — spreadsheet creation/editing (results matrices, account ledgers)
- `docx` — formal documents
- `pptx` — slide decks
- `frontend-design` — UI work for forecaster/dashboards

---

## 13. Operational conventions

### File naming
- Output filenames include all variation axes:
  `realsim_summary_{strategy}_{auth}_d{base_delay}{_atrmgmt}{_trail-method}_{window}_{label}.txt`
- Different configs never overwrite each other

### Working directory
- Live work: `C:\VMShare\NT8lab\`
- Output: `C:\VMShare\NT8lab\prj_realsim\`
- Data: `C:\VMShare\NT8lab\databento\MNQ\ohlcv-1s\`

### Bucket usage tracking
- One JSON file per strategy family: `{family}_bucket_usage.json`
- Records every test_* and validation_* consumption
- Final-validation scripts check this file and refuse to re-run

### Deployment workflow
1. Strategy passes train+test buckets
2. **MANDATORY robustness checks** (see Section 15): bootstrap PnL CI,
   per-exit MFE analysis. Both must pass before validation.
3. RECOMMENDED robustness checks (run if marginal or structurally important):
   regime stratification, multi-seed stability, holdout-window robustness.
4. ONE shot on validation
5. If validation passes: paper trade on Sim101 for 10-20 days
6. If paper-trade matches validation: live deploy on appropriate account
7. Monitor first 30 live trades carefully

### Production-status doesn't change with retest
NB has been live and profitable. A failing retest under stricter criteria
doesn't unlive it — production track record is the deployment authority,
methodology is for COMPARISON.

---

## 14. Robustness discipline

The bucket discipline (training/test/validation) protects against one
specific failure mode: choosing a config that overfits the training data.
It does NOT protect against:

- Edge that's concentrated in a few lucky trades (fragile)
- Edge that depends on a specific regime that happened to dominate training
- Edge that comes from a quirk of the random reflex draw (click-mode only)
- Edge that exists only on the specific calendar window we tested

Robustness discipline addresses these. Five tools, two MANDATORY and three
RECOMMENDED, all in `prj_realsim_robustness.py`.

### MANDATORY (run for every candidate before validation)

**Bootstrap PnL confidence interval.** Resample trades with replacement,
report 5/25/50/75/95 percentiles of total net P&L. If the 5th percentile
is positive, the strategy is robust to which specific trades happened to
occur. If 5th percentile is negative but 25th is positive, real edge under
trade-luck variability. If even 25th is negative, the edge is concentrated
in a few trades and the strategy is fragile.
```
python prj_realsim_robustness.py bootstrap <trades_csv>
```

**Per-exit MFE analysis.** For each trade, log the maximum favorable
excursion (MFE) and compare to the captured P&L. For trail-fired exits
specifically, the captured/MFE ratio tells us if the trail is harvesting
real reversals (>50%) or just relabeling BE-flat exits (<25%).
```
python prj_realsim_robustness.py mfe_analysis <trades_csv>
```
Note: requires the engine to log MFE per trade. Trade CSVs from before
this feature was added will not work — re-run the engine.

### RECOMMENDED (run when result is marginal or finding is structurally important)

**Regime stratification.** Split results by ATR quartile, time-of-day,
day-of-week. If the strategy is positive in 3-4 of 4 ATR quartiles, robust.
If positive in only 1-2 quartiles, regime-dependent.
```
python prj_realsim_robustness.py regime_stratify <trades_csv>
```

**Multi-seed click-mode runs.** Click-mode results depend on the random
reflex-draw seed. Run 10 different seeds, report distribution. If the
spread is <50% of the median, edge survives reflex variability. If
spread >100% of median, much of the result is seed luck. Auto-mode is
deterministic so this only matters for click-mode candidates.
```
python prj_realsim_robustness.py multi_seed --n_seeds 10 --strategy nb --auth click ...
```

**Holdout-window robustness.** Pick 5 non-overlapping ~60-day windows
from full history. Run candidate on each. If positive on 4+ of 5, robust.
If positive on 0-1, not robust.
```
python prj_realsim_robustness.py holdout --windows 5 --strategy nb --auth auto ...
```

### Verdict criteria (locked, pre-committed)

| Tool | Criterion | Verdict |
|---|---|---|
| bootstrap | 5th percentile > 0 | ROBUST |
| bootstrap | 25th percentile > 0 | MOSTLY ROBUST |
| bootstrap | median > 0 only | FRAGILE |
| bootstrap | median < 0 | LUCKY |
| mfe_analysis | trail captures > 50% of MFE | TRAIL WORKING |
| mfe_analysis | trail captures < 25% of MFE | TRAIL NOT HELPFUL |
| regime_stratify | positive in 3+ of 4 ATR quartiles | ROBUST |
| regime_stratify | positive in 1-2 quartiles | REGIME-DEPENDENT |
| multi_seed | spread < 50% of median | STABLE |
| multi_seed | spread > 100% of median | SEED-DEPENDENT |
| holdout | positive in 4+ of 5 windows | ROBUST |
| holdout | positive in 0-1 windows | NOT ROBUST |

### Why this is mandatory now

Earlier sessions treated robustness as an afterthought — "if we have
time" rather than "before validation." This produced a result where we
spent validation budget on candidates whose edge was concentrated, regime-
dependent, or seed-lucky, and only learned afterward that the candidate
wasn't really there. **Bootstrap and MFE are cheap. Run them first.**

### Why bootstrap and MFE are mandatory but the others are not

Bootstrap is fast (seconds), runs on existing trade data (no re-run),
and catches the most common failure mode (concentrated edge). MFE catches
the second-most-common failure mode for management-technique changes
(relabeling vs real harvesting). The others are valuable but address
narrower issues that aren't always present (regime sensitivity, seed
dependence, calendar-luck). Making all five mandatory slows iteration
without proportional value. Two-and-three is the right balance.

---

## 15. Regime-conditional trail deployment

This section was added after session 20 produced two failed validations
(chan_14_3 on validation_vwap, chan_14_2 on validation_nb) that both
failed for the same structural reason: **the trail mechanism that drove
backtested edge improvement didn't activate in the live regime.** Together
with literature review of how practitioners actually use chandelier-style
exits, the findings produced a methodological gap that hadn't been named.

### The naming problem

Throughout sessions 18-20 we treated the trail-method dimension as a menu
of variants to pick from based on training+test performance. "Find the
best variant, deploy it." This frames the problem the way a backtester
naturally frames it.

The literature on chandelier exits is unanimous on a different framing:
**chandelier (and trailing stops generally) are regime-conditional tools,
not universal exits.** Every credible source — StockCharts, TrendSpider,
QuantifiedStrategies, NetPicks, the original LeBeau material via Elder —
states the same constraint:

- Designed for trending markets
- Ineffective in sideways/choppy markets
- Whipsaw in choppy markets produces sequences of small losses
- Pros add **market regime classification before deployment**, not just
  parameter tuning after deployment

We had built the registry but skipped the regime classification layer.
Trail variants got deployed indiscriminately on every trade regardless of
the day's character. When validation_vwap and validation_nb fell in
predominantly-choppy regimes (Feb-Apr 2026), every trail variant produced
either zero firings or the same near-zero firings.

The session 20 evidence: chan_14_3 and lebeau_22_2 produced **identical
P&L numbers to the cent** on validation_vwap. Both produced zero stop_trail
exits across 50 trading days. No multiplier, no lookback period, no
chandelier variant changes the result when the trail simply doesn't
activate.

### The actual problem statement

Trail mechanism failure modes break into two categories:

1. **Activation failure** — trail never reaches the conditions for firing
   (price never extends far enough past entry). What we observed.
2. **Activation in chop** — trail fires repeatedly on small reversals
   that aren't trend changes. Whipsaw losses.

Both are regime-fit failures. Neither is fixed by parameter tuning within
the trail family. Both are addressed by **gating trail deployment on a
prior regime classification.**

### Trail family taxonomy

The literature describes several distinct trail families. We had implemented
several (chandelier variants, EMA, swing-low) without documenting the
distinct regime profiles each is suited to. Naming them properly so future
work can choose by regime fit rather than by backtest performance:

**Chandelier family** (chan, lebeau, chan_pred): ATR-distance below the
running high-watermark over a lookback window. Strong in clearly trending
markets with steady extension. Weakens in chop because the lookback
high-watermark advances slowly while reversals can travel further than
the ATR-distance allows.

**EMA-following trails** (ema_9_1m): exits when price closes below a fast
moving average. Strong in steady trends with shallow pullbacks. Cuts
winners aggressively in volatile trends with deep pullbacks (the pullback
breaks the EMA before resuming higher). Tighter than chandelier.

**Swing-structural trails** (swing_low_14m): trail moves to the most recent
swing low/high in a lookback window. Strong in trends with clear pivot
structure. Weak in microstructure-driven moves where pivots are irregular.

**Two-stage trails** (two_stage_4_2): wide trail before partial profit-take,
tight trail after. Designed for catching big trends from the start while
locking in gains after the first scale-out. Inert when BE arms before TP1
(observed in our NB tests — pre-TP1 phase never activates).

**Time-decay trails** (not implemented): trail tightens as time-in-trade
extends. Premise: if a trade hasn't run by N minutes, probability of
extension drops, so cap give-back. Suited to scalping windows.

**Profit-conditional trails** (not implemented): trail behavior changes
based on multiple-of-R achieved. Below 1R: BE-flat only. 1R-2R: chandelier
mult 3.0. Above 2R: chandelier mult 2.0 (tightens approaching big gains).
Pro-discretionary convention. The closest relative we have is BE-arming
at MFE 6.

**Volume-conditional trails** (not implemented): trail high-watermark
advances only on bars with above-average volume. Filters trail-poisoning
from low-volume noise spikes.

**Anti-fragility partial-trim trails** (not implemented): trail trigger =
take half off, keep stop tight on remainder. Reduces exposure without
fully exiting. Common in pro discretionary work, less so in mechanical
systems.

### What's missing: the classification layer

The taxonomy above describes the trail tools. The missing piece is **what
regime is each tool suited to** and **how do we classify the current regime
before deployment.** Possible classifiers, in increasing order of
sophistication:

**Calendar-based** (cheapest):
- Day of week (we observed Thu/Fri stronger than Mon-Wed in 2024-2026)
- Macroeconomic event days (FOMC, CPI, NFP, GDP — block or restrict)
- Quad-witching / OPEX (predictable pinning behavior)
- Holiday-shortened sessions (thin liquidity, wider spreads)
- Post-holiday open (positioning reset, often trends)

**Pre-market signal**:
- Overnight gap size (large gap relative to ATR = trend-day signal)
- Pre-market VWAP slope (steep directional = continuation expected)
- Pre-market range vs ATR (compressed = breakout setup; extended = exhaustion risk)
- Asia/London session behavior carrying into US open

**Opening signal** (computed by ~9:35-9:45 ET, before our entry windows):
- First 5-minute range relative to ATR (wide = trend day, narrow = chop)
- First 15-minute range relative to recent average
- First-bar volume vs typical
- Initial drive direction relative to pre-market

**Intraday profile** (computed dynamically):
- Volume profile shape — single-distribution (TPO concept) suggests trending,
  double-distribution suggests rotational
- Cumulative delta direction
- Realized vol vs implied (when options data accessible)

The classifier doesn't have to be perfect. Even a binary "looks trending /
looks choppy" tag computed by 9:35 ET would dramatically change which
trail family deploys.

### How this changes the methodology

The pre-commitment protocol from Section 4 still applies: pick a classifier
+ trail family combination, lock it before testing, single-shot validation.
But the unit of testing shifts. Instead of "test trail variant A vs trail
variant B," the unit becomes "test trail variant A WITH classifier X vs
trail variant A WITH classifier Y" — or "trail variant A on classified-
trending-only days vs trail variant A on all days."

This adds dimensions to the experiment matrix. Honest acknowledgment: the
combinatorial cost grows. But the alternative (continuing to test trail
variants without classification) is what produced two failed validations
in session 20.

### Next-session opening work

Three concrete items for the next session that touches this dimension:

**1. Build a session classifier prototype.** Start with the cheapest layer
— pre-market gap and first-15-min range, computed as one binary tag per
trading day. Add the tag as a column to the trade CSV so existing batteries
can stratify by it.

**2. Re-stratify existing trade CSVs by the classifier.** Don't re-run
backtests. Just re-read the existing data with classifier tags. Are
trail-fire rates dramatically different on classified-trending vs
classified-chop days?

**3. If yes (trail fires concentrated on classified days):** design a
classifier-gated variant. Strategy fires entry signals as before, but the
trail mechanism is conditional — trending day → chandelier deploys; chop
day → fixed mgmt only. Test the gated variant on training+test as a fresh
candidate. New independence layer means fresh validation eventually
warranted.

**4. If no (classifier doesn't separate trail-firing days):** the
classifier needs work, OR the regime structure isn't classifier-detectable
with cheap signals. Either way, we know more than we did.

### What this section is NOT

This is not a license to add 50 new variants and re-run validation.
It's a research framework that says: before adding more variants of the
same family, address the classification gap that's causing variant
testing to fail consistently.

If validation_vwap_v2 ever exists (post-Apr-15-2026 fresh data), the
candidate that earns it must be a classifier-gated strategy, not another
naked-trail variant.

### Honest credit for the gap

The methodology reference, until session 20, treated trail design as a
parameter optimization problem. The literature treats it as a
regime-classification problem. We were doing the wrong kind of work
at the wrong level of abstraction. Session 20's two validation failures
made the gap visible. The lesson is recorded so future sessions don't
repeat it.

### Strategy-class-aware classification (refinement after diagnostic)

This subsection was added after the classifier diagnostic produced an
unexpected result: on VWAP test_vwap, the v1 classifier was **massively
inverted**. Days tagged "chop" produced +$4,191 net at +$349/trade across
12 entries; days tagged "trending" produced -$428 across 10 entries. The
classifier was anti-correlated with profitability.

Tracing the failure honestly: the classifier wasn't broken. **The framing
was wrong for this strategy class.**

Section 15 above describes chandelier exits as trending-day tools and
proposes building a trending-day classifier to gate their deployment.
That framing is correct **for trend-following strategies** that profit
when price extends in one direction. It is the OPPOSITE of what's needed
for **mean-reversion strategies** that profit when price oscillates
around a reference level.

VWAP reclaim/pre_market is a mean-reversion strategy. It triggers when
price reclaims pre-market VWAP after extending away. The profitable
trades happen when price continues back through VWAP and oscillates —
which is rotational, two-sided, "chop"-character behavior. Strong
trending days do not produce mean-reversion opportunities; they produce
one-sided continuation.

When we measured volume profile concentration as a "trending signal"
(Section 15 above, v2 classifier), single-distribution shapes were
correctly tagged as trending — but for VWAP reclaim, those are
**negative** signals. We measured the right shape with the wrong sign
for this strategy class.

#### The refinement: classify by strategy class

The trail-deployment classification question is not "is today a trending
day?" Universally. It depends on what kind of edge the strategy is
trying to capture.

Two strategy classes need opposite classifiers:

**Trend-following strategies** (NB noise breakout, breakout continuation,
moving-average pullback, etc.). Profit from sustained directional moves.
Want trail to deploy on trending days. Want chop days filtered out.

**Mean-reversion strategies** (VWAP reclaim, range-fade, oversold/
overbought bounces, etc.). Profit from rotation and oscillation around
reference levels. Want trail to deploy on rotational/two-sided days.
Want strong-trend days filtered out (or at minimum, not gated against).

The same set of price-and-volume signals can serve either classifier;
the **interpretation flips by strategy class**:

| Signal                         | Trend-follow tag | Mean-reversion tag |
|--------------------------------|-------------------|---------------------|
| Large overnight gap            | trending          | reverting?          |
| Wide opening range             | trending          | reverting?          |
| High pre-market volume         | trending          | reverting?          |
| Single-distribution VP shape   | trending          | NOT-reverting       |
| Double-distribution VP shape   | NOT-trending      | reverting           |
| Wide pre-market range          | (neutral)         | REVERTING (room)    |
| Distance from VWAP at open     | (neutral)         | REVERTING (extension)|

Some signals (gap, OR range, opening volume) are ambiguous — they can
indicate "this is a directional event-driven day" which could either be
trend-continuation OR provide setup for fade/reversion, depending on
follow-through. Other signals (volume profile distribution shape, distance
from anchor) are MORE diagnostic for one class than the other.

The session 20 v1/v2 classifiers used trend-follow signals interpreted as
trend-follow tags. We deployed them against a mean-reversion strategy
(VWAP reclaim). The inversion observed in the diagnostic is the predicted
result of that mismatch.

#### Practical implications for the methodology

**1. Tag every strategy by class.** Add a `strategy_class` field to each
strategy registered: `trend_follow`, `mean_reversion`, or `mixed`. This
must be declared BEFORE classifier work begins.

NB noise breakout: `trend_follow`. Profits from breakout continuation.
VWAP reclaim/pre_market: `mean_reversion`. Profits from VWAP-anchor return.
TP family (closed): `trend_follow` (was momentum-based).
Trend-pullback (PRJ_7, closed): `trend_follow` (continuation entry).

**2. Pick the classifier signal direction by strategy class.** A signal
that says "today is trending" enables trail deployment on trend-follow
strategies AND blocks deployment on mean-reversion strategies. Same
signal, opposite gating.

**3. Build per-class classifier registries.** Future classifier work
should produce two parallel registries:
   - `trend_classifier_v*` — gates trend-follow strategy trail deployment
   - `meanrev_classifier_v*` — gates mean-reversion strategy trail deployment

Don't reuse one classifier across strategy classes. The v1 inversion on
VWAP test_vwap is the empirical evidence for why.

**4. Re-evaluate existing classifier work under this lens.** v1, v2,
v2_tight, v3_and were all built as trend classifiers. Their empirical
performance against trend-follow strategy data (NB chan_14_2) showed
positive trail-fire spreads (+5 to +10pp range). Their performance
against the mean-reversion strategy (VWAP reclaim) showed inverted
spreads (-10pp on test_vwap). Both findings are consistent with
signal-direction-by-class theory.

**5. Mean-reversion classifier signals worth investigating.** Distinct
from trend-follow signals:
   - Pre-market range size (bigger = more rotation room)
   - Distance from anchor VWAP at trigger time (bigger = bigger reversion target)
   - Two-sided rotation count in pre-market (acceptances and rejections)
   - Double-distribution detection in volume profile (rotational signature)
   - Realized vol / implied vol ratio (high = mean reversion regime)

Don't assume same signals will work — strategy class changes which
signals are diagnostic.

#### What this means for next-session opening work

The previous "next-session opening work" listed in Section 15 above is
NOT discarded but is **strategy-class-scoped**:

For NB (trend-follow): the v1/v2 classifier work continues as designed.
Cross-reference shows positive trail-fire spread; this is the right
direction. Tighten thresholds, validate, gate.

For VWAP reclaim (mean-reversion): start over with a mean-reversion
classifier. v1/v2 are not salvageable for this strategy class — they're
inverted. Build mean-reversion classifier candidates using the signals
above. Cross-reference against existing VWAP trade data.

#### Why this refinement matters beyond chandelier

The framework refinement extends past trail design. **Any strategy-level
filtering choice is strategy-class-conditional.** Entry filters, time-
of-day windows, day-of-week filters, news-event blocks — all of them
have potentially opposite ideal settings for trend-follow vs
mean-reversion strategies.

If we ever build a meta-strategy that runs both NB and VWAP reclaim
simultaneously, day classification might gate one ON while gating the
other OFF — same signal, opposite direction. This is normal and
expected once strategy class is properly named.

#### Honest credit for the second gap

Section 15 above identified one gap: missing classification layer.
Section 15.refinement (this subsection) identifies a second gap:
**classification needed strategy-class awareness.** Both gaps were
present in the methodology before session 20. Both were exposed by
session 20's empirical work. Both are now named.

The pattern: **the methodology reference is most valuable when it
captures what the data forced us to learn.** Failures and surprises
that change framing are higher-value than successes that confirm it.

---

## 15A. Management dominance: losers declare themselves early (added 2026-05-25)

This is a framework-level structural finding surfaced by the Step 1F
precursor work on the management-observer research line. It belongs
in the methodology reference because it changes how we should frame
future strategy / management work, not just because it is a single
strategy result.

### The structural property

Across the MNQ fleet, **losing trades declare themselves early.**
Quantified across 13 classifiable families with existing trade logs:

- **11 of 13** families have median loser duration **≤ 300 seconds**.
- Several families resolve losers in **under a minute**: PRJ_3
  canonical alpha p50 ≈ 1s (tight management), G1 (g_momentum 10:00)
  p50 ≈ 27s, G2 (g_momentum 10:30) p50 ≈ 52s, PRJ_3 single-contract
  repro p50 ≈ 59s.
- **Only 2 of 13** are slow-bleed: `atr_regime_pullback_continuation`
  (median loser duration ≈ 796s) and the original
  `opening_range_width_switch` (p50 ≈ 335s).
- 2 of 15 evaluated families had insufficient losers (n<10) to
  classify (`mhw`, `prior_day_value_area_rejection`).

Basis: median loser duration from each family's existing trade CSV,
deduped by entry timestamp + direction + entry price where multi-leg
files exist. Full table:
`nb_lib/probe_results/step1f_fast_stop_taxonomy.csv`. Classification
script: `nb_lib/scripts/step1f_fast_stop_vs_slow_bleed_taxonomy.py`.

This is consistent with three earlier independent sightings the
project recorded but did not generalize:

- Value Migration Runner Phase 1 (2026-04, n=25): explicit time-to-
  stop distribution — 18 full stops; 6 immediate (≤10 min); 3 slow
  (>60 min).
- Savor-Wilson V4 Phase 1
  (`savor_wilson_v4_phase1_report.md`, 2026-04-30): "V4D's mean
  duration is just 10.2 min because BE stops hit fast."
- G2 level-ratchet research
  (`session_history/2026-05-02_fleet_eval_custom_strategy_checkpoint.md`):
  "mechanism rarely engages on G2 because 88 of 118 trades hit fast
  initial stops before levels can be cleared with acceptance"
  (74.6% fast-stop rate).

The Step 1F precursor's contribution was to measure this across
every family with trade data and to identify the pattern as
near-universal rather than family-specific.

### The corollary: exit geometry can dominate entry selection

The cleanest demonstration is the Savor-Wilson V4 pair, which holds
ENTRY SIGNAL FIXED and varies management geometry only:

| Variant | Management geometry | Mean duration | Net | WR |
|---|---|---:|---:|---:|
| V4D | fast-stop / BE active | 10.2 min | -$3,180 | 2.5% |
| V4A | slow-stop / no-BE-no-trail | 40.7 min | +$9,907 | 30% |

Same entries, different management. Outcome flips from clearly
losing to clearly winning. Source:
`savor_wilson_v4_phase1_report.md` (2026-04-30 session).

The interpretation that the Step 1F precursor banks: **for these
MNQ strategies, management geometry can be at least as important
as entry selection, and possibly more so.** Most losers under the
fleet's default tight-stop / BE-arm management would have been
exited as small wins or break-even under a slower geometry. Stop
discipline is not free.

### The management implication (research hypothesis, not deployed)

Stated as a research direction for future management work, NOT as
a validated rule:

> The highest-value management lever for this fleet may be NOT
> strangling trades before they can work, rather than detecting
> bad entries per se.

This is the opposite framing from the poor-entry-triage observer
direction (which detects bad entries early so they can be
de-risked). Both framings can be true simultaneously: trades that
are truly hopeless after a few minutes ARE worth de-risking, but
the fleet's current default management may also be exiting too
many "would-have-worked-if-given-room" trades as fast stops. The
two effects interact and any counterfactual scoring (Step 3 of the
management-observer launch sequence) must measure them jointly.

### What this changes for future work

- New strategy designs should explicitly evaluate
  multiple-management-geometries early, not just one default
  management. Savor-Wilson V4D vs V4A is precedent.
- Anti-patterns Section 10 should be read with the understanding
  that "fast stops" / "loss clusters" / "compliance bust" failures
  are often joint failures of entry-AND-management, not entry-alone.
- The poor-entry-triage diagnostic in
  `_MANAGEMENT_OBSERVER_MEMORY_LAYER.md` Section 10A is a
  validated observation, but acting on it requires Step 3
  counterfactual scoring — particularly because the structural
  TP1+BE floor on G2 means "underwater at 300s" overlaps with
  "hasn't yet locked in TP1+BE protection." Cutting those trades
  costs the favorable outcome on borderline cases.

### Cross-reference

Detailed work, including pre-committed believe-it bar, partition
discipline, and replication tally:
`nb_lib/strategy_specs/_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`,
Section 10A (poor-entry triage, Steps 1 through 1F-precursor).

---

## 15B. Mechanism-class screening before full builds

Before spending a full build on a new intraday futures strategy, run the
mechanism-class screen when a cheap proxy trade list can be produced.
The report card lives in
`nb_lib/strategy_specs/source_artifacts/compass_mechanism_class_screening_protocol_20260621.md`
and executable helpers live in `nb_lib/screening.py`.

The screen is a pre-build triage layer, not a validation layer. It asks
whether the mechanism class is worth building at all across five axes:
skew/concentration, cost-distance, frequency-power,
regime-concentration, and cross-correlation. Any RED on
skew/concentration, cost-distance, or frequency-power is a hard
do-not-build signal unless the operator explicitly records a new thesis
for overriding it. RED on regime-concentration or cross-correlation is
a caution flag: the idea may still be useful as context or a sleeve, but
not as a standalone deployable edge or claimed diversifier.

This section exists because the 2026-06 strategy-generation arc produced
three reusable failure lessons:

- low-frequency candidates can be directionally interesting but
  statistically underpowered relative to skew-adjusted MinTRL;
- tight scalps can be eaten by MNQ friction under the cost-distance
  speed limit;
- convex breakout/momentum books can print positive net while being
  carried by one month or one day, making the mechanism
  non-deployable at the achieved trade count.

Future candidate prompts should therefore request a cheap proxy screen
before a full build whenever the entry mechanism is new or the expected
frequency/cost-distance profile is uncertain.

---

## 16. What would make us start over

This methodology will eventually need updates. Triggers for revision:

- A new platform or broker with different latency characteristics
- A new prop firm rule structure that changes deployability tags
- A bug in the realsim engine that invalidates past results
- A genuinely new strategy class that doesn't fit current criteria
  (in which case we add a new criteria set, not break the old one)

Until then, this document is the starting point for new sessions. Read
first, then strategy work. Strategy findings go in dated session checkpoints.
Methodology updates go here.
