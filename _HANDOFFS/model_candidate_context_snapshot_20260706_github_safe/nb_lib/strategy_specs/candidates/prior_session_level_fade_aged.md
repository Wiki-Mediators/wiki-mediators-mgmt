---
name: "Prior-Session Level Fade (aged)"
tagline: "Fade yesterday's RTH high/low when tagged >4h into the level's life (afternoon tests)."
status: "candidate-validated-in-principle-unconfirmed"   # status NAME unchanged; underlying evidence is now weaker — see §3a
created: 2026-06-25
updated: 2026-06-26   # data-integrity correction banked (TASK_014)
source: "PROBE_005 surfaced PRIOR-session level slice (age>4h) as the cleanest cell in a 4-way react/break/sweep/chop classification of 828 touches across 12 type×age cells; PROBE_006 ran a single pre-committed +EV fade test on that one slice."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "afternoon tests only — by construction, age>4h means touches occur >4h after session open, so practically 13:30-16:00 ET"
hold_duration: "intraday"

# Signal characteristics
signal_type: "level-fade / mean-reversion at obvious liquidity"
indicators: ["prior-session RTH high (PDH)", "prior-session RTH low (PDL)"]
timeframes_used: ["1-second source", "1-minute decision grid"]

# Execution (pre-committed in PROBE_006; do NOT tune)
brackets: "fixed-point (10-pt stop, 20-pt target)"
position_sizing: "fixed-contracts"

# Cross-references
canonical_spec: null
implementation: null
source_artifact: "_worker_reports/PROBE_006_prior_level_fade_EV_findings.md (+ PROBE_005 machinery)"
related_candidates:
  - "failed_orb_fade"
related_probes:
  - "probe_005_liquidity_levels.py"
  - "probe_006_prior_level_fade_EV.py"

# Test status — IN-SAMPLE ONLY. OOS PARTIALLY SEEN (see §3a).
test_results:
  in_sample_window: ["2024-08-01", "2026-01-30"]    # strict in-sample, hard-cut < 2026-02-01

  # CORRECTED strict in-sample numbers (see §3a for contamination history)
  in_sample_n: 48
  in_sample_n_caveat: "tiny — ~1 trade every 2 weeks; effective power is low; partial OOS-seal compromise (14 touches already seen)"
  variant_b_target_or_stop:
    mean_pts: 4.15
    mean_pts_cost_aware: 2.41
    median_pts: 0.88
    win_rate: 0.521
    pf: 1.87
    total_pts: 199.5
    se_mean: 2.10
    t_vs_zero: 1.98
    p_vs_zero: 0.048            # right at the 5% line, not comfortably under it
    p_vs_pseudo_welch: null     # NOT RE-RUN on strict-in-sample; original 0.046 used contaminated data

  # Variant A: same loader contamination applies; exact corrected values not computed in TASK_014.
  # Original (contaminated) values preserved under superseded_* below.

  # SUPERSEDED original PROBE_006 numbers (preserved for auditability; do NOT cite as current evidence)
  superseded_2026_06_25_original_PROBE_006:
    note: "Reported in the original PROBE_006 findings file (2026-06-25). PROBE_006's data load did NOT hard-cut at 2026-02-01, so 14 of the 62 touches were from the sealed OOS period. Corrected numbers above use a strict in-sample loader."
    in_sample_n: 62
    variant_a_window_end:
      mean_pts: 6.80
      mean_pts_cost_aware: 5.05
      win_rate: 0.355
      pf: 2.05
      p_vs_zero: 0.084
      p_vs_pseudo_welch: 0.276
    variant_b_target_or_stop:
      mean_pts: 5.57
      mean_pts_cost_aware: 3.82
      win_rate: 0.565
      pf: 2.28
      p_vs_zero: 0.003
      p_vs_pseudo_welch: 0.046

  pseudo_baseline_n: 62           # original (contaminated) pseudo baseline N — same caveat
  pseudo_variant_a_mean_pts: 1.07
  pseudo_variant_a_cost_aware: -0.68
  pseudo_variant_b_mean_pts: 0.37
  pseudo_variant_b_cost_aware: -1.38
  pseudo_strict_in_sample_rerun: null   # NOT re-run on strict in-sample data in TASK_014

  cost_proxy_pts_per_trade: 1.75
  out_of_sample_tested: false           # NOT a clean OOS test, but see partial_oos_seen below
  out_of_sample_n: null
  partial_oos_seen:
    n_touches: 14
    note: "14 of PROBE_006's original 62 touches were from the sealed OOS period (2026-02-01 → 2026-06-19). The OOS seal for THIS specific slice is therefore partially compromised — those 14 touches are no longer truly unseen for this hypothesis."
  multistart_pass_rate: null

tags:
  - rth-only
  - intraday
  - mean-reversion
  - level-fade
  - liquidity-attention
  - small-n
  - in-sample-only
  - unconfirmed
  - borderline-significance     # added 2026-06-26: corrected p ≈ 0.048 vs zero
  - partial-oos-seal-compromise  # added 2026-06-26: 14 OOS touches already seen in PROBE_006
---

# Prior-Session Level Fade (aged)

## ⚠️ STATUS — read this before reading the numbers

**`candidate-validated-in-principle-unconfirmed`** — status NAME unchanged, but the **underlying evidence is now meaningfully weaker than originally reported**. A data-integrity correction was banked on 2026-06-26 (TASK_014 / §3a): PROBE_006's original numbers included 14 OOS touches. The strict-in-sample slice is **N=48 (not 62)**, mean **+4.15 pts (not +5.57)**, PF **1.87 (not 2.28)**, one-sample p vs zero **≈ 0.048 (not 0.003)** — right at the 5% line. Combined with N=48 + post-hoc-cell-selection + bimodal distribution, the **forking-paths-corrected evidence is weak**. **The "do not build on this; confirm in a new market" stance is now stronger, not weaker.**

This is still a candidate, NOT a strategy, NOT a deployable edge. It is one small-N, post-hoc-selected, in-sample slice that *just barely* cleared a one-sample test on borderline-significant, single-test evidence. It is **validated-in-principle** — plausible enough to deserve further work — but **NOT confirmed**, and **the OOS seal for this specific slice is partially compromised** (14 touches already seen).

If you are a future agent (Codex, Claude, or any model) reading this and considering acting on the numbers: **do not build a strategy from this spec yet.** Read §3a, §5, and §6 first.

---

## 1. What it is (one paragraph)

A fade of *aged* prior-session liquidity levels: yesterday's RTH high (PDH)
and yesterday's RTH low (PDL). When price tags one of those levels **more
than 4 hours into the level's life** (born_ts = session open, so age>4h
means roughly 13:30 onward — the *afternoon test* scenario), the trade
fades the level — short if it was tagged from below (testing as
resistance) or long if tagged from above (testing as support). Held with
a fixed 10-pt stop beyond the level; exited at +20 pts in the fade
direction OR at +30 min mark-to-market. The candidate was identified from
PROBE_005's level-effect classification (real, p≈2.3×10⁻⁷ across all
levels) by isolating the single type×age cell with the highest
clean-react rate; PROBE_006 then ran a fixed-parameter fade-EV test on
that one cell.

## 2. Exact pre-committed parameters (reproducible)

Touch-detection machinery is **identical to PROBE_005 / PROBE_006**.
Do **not** re-derive — point at and reuse the scripts:
- `probe_005_liquidity_levels.py` — level/swing/touch state machine
- `probe_006_prior_level_fade_EV.py` — fade trade model on the slice

Key params (all FIXED, do NOT tune):

| Parameter | Value |
|---|---|
| Level types in scope | `PRIOR` (prior-RTH-session high and low) only — 1H/2H/4H swings are out-of-slice |
| Touch tolerance | 3 pts (bar extreme within 3 pts of level) |
| Touch dedup | suppress next touch on same level until price clears by ≥10 pts AND 30-min window elapsed |
| Level invalidation | prior-bar close beyond level by ≥15 pts |
| Slice filter | `age_at_touch > 4 h` (240 min) since session open |
| Fade direction | counter to approach (from below → short; from above → long) |
| Entry price | the level (fill at touch within 3-pt tolerance) |
| Stop | 10 pts beyond level in the penetration direction |
| Target (Variant B only) | 20 pts in the fade direction |
| Forward window | 30 min, capped at session close |
| Same-bar target+stop tie | STOP wins (conservative) |
| Position size | 1 contract MNQ ($2/pt) |
| Cost proxy | 1.75 pts/trade (~$3.50 round-trip retail commission + slippage) |
| RNG seed (pseudo baseline) | `20260625` |

## 3. Result, with both variants (CORRECTED — strict in-sample)

In-sample window: 2024-08-01 → 2026-01-30 RTH (data loader **strictly hard-cuts at < 2026-02-01**, runtime asserted). See §3a for the contamination history.

### 3.1 Variant B — `+20 target / −10 stop` (the headline)

| | **Real, strict in-sample (N=48)** | (superseded — contaminated, N=62) |
|---|---:|---:|
| Mean pts/trade (gross) | **+4.15** | (+5.57) |
| Mean pts/trade (cost-aware) | **+2.41** | (+3.82) |
| Median pts | **+0.88** | (+5.50) |
| Win rate | **52.1%** | (56.5%) |
| Profit factor | **1.87** | (2.28) |
| Total pts | **+199.5** | (+345.25) |
| SE of mean | **2.10** | (1.84) |
| t vs zero | **1.98** | (3.03) |
| **p vs zero (one-sample)** | **≈ 0.048** (right at the 5% line) | (0.003) |
| p vs pseudo (Welch) | NOT RE-RUN on strict in-sample | (0.046 — contaminated) |

### 3.2 Variant A — window-end mark-to-market (also contaminated, exact strict numbers not re-computed)

The same loader contamination affects Variant A. The CFLR investigation in TASK_014 did not re-compute Variant A's strict-in-sample numbers (only Variant B). The **superseded** (contaminated) Variant A numbers were:

| | (superseded — contaminated, N=62) |
|---|---:|
| Mean pts/trade (gross) | (+6.80) |
| Mean pts/trade (cost-aware) | (+5.05) |
| Win rate | (35.5%) |
| Profit factor | (2.05) |
| p vs zero (one-sample) | (0.084 — marginal) |
| p vs pseudo (Welch) | (0.276 — n.s.) |

**Variant A's strict-in-sample values are unknown** as of TASK_014. Assume similarly weakened until a re-run is performed.

### 3.3 Pseudo baseline (matched-random) — NOT RE-RUN on strict in-sample

The pseudo-level baseline that produced the originally-reported Welch p=0.046 also ran on the contaminated 62-touch slice. **It has not been re-computed on the strict in-sample 48-touch slice.** The p≈0.046 from §3.1's superseded column should NOT be treated as the strict-in-sample value.

### 3.4 What this means

The headline finding survives only barely. Variant B's one-sample test against zero is **at p ≈ 0.048 — right on the 5% line, not comfortably under it**. Without a re-run of the pseudo baseline on strict in-sample data, the test against random is unknown but plausibly weakened similarly. The transferable observation is still that this is the only MNQ-RTH directional slice in six probes that produced any positive in-sample expectancy after costs — but the magnitude of "any" is now meaningfully smaller.

## 3a. Data-integrity correction (2026-06-26)

**The error.** PROBE_006's data loader did not enforce a hard-cut at 2026-02-01. It loaded the full 2024-08-01 → 2026-06-19 RTH window and detected touches across all of it. The touches that fell into the OOS-sealed window (2026-02-01 → 2026-06-19) were included in the reported N=62 slice.

**The scale.** 14 of the original 62 touches (~23%) were from the sealed OOS period. The strict-in-sample slice (data loader hard-cut < 2026-02-01) contains **N=48**.

**How it was discovered.** While investigating CFLR_v0 (a single-rule variation of Variant B; see §6a), the assistant noticed that a hard-cut loader produced 48 touches, not 62. Re-derivation of the strict in-sample baseline produced the corrected numbers now in §3.1. Documented in detail at `_worker_reports/STRATEGY_cflr_v0_in_sample_results.md` §2.

**Consequence 1 — the candidate is weaker than banked.** The corrected one-sample t-test against zero is t ≈ 1.98, p ≈ 0.048. That is right at the conventional 5% line, not the much more comfortable p ≈ 0.003 originally reported. Combined with the small-N and the post-hoc cell selection caveats (still present), the **forking-paths-corrected evidence is weak**. This makes the standing "do not build on this; confirm on fresh data" stance *stronger*, not weaker.

**Consequence 2 — partial OOS-seal compromise.** PROBE_006 effectively *already looked at* 14 OOS touches for this exact hypothesis. The OOS seal for THIS specific slice is therefore partially compromised — those 14 touches are no longer truly unseen for the prior-level-fade hypothesis. A future Option (a) OOS spend must account for this (see §6).

**Why this can't recur.** Strict in-sample loaders (e.g., `strategy_aft_or_break_v0.py`, `strategy_cflr_v0.py`) hard-cut at the OOS boundary in the loader AND assert `df.index.max() < OOS_BOUNDARY` at runtime. PROBE_006 should be retrofitted with the same pattern if it is ever re-run. As a general rule going forward: any code path that consumes a "strict in-sample only" guarantee should enforce it at the loader and assert it at runtime — not in commentary in the spec.

## 4. Honest status line

**Validated-in-principle: yes.** This is the *first* MNQ-RTH-OHLCV signal
in six probes that survived a baseline + cost proxy on a fixed-parameter
test.

**Confirmed: no.** Single small-N in-sample test with non-trivial
post-hoc-selection exposure (see §5).

**The transferable takeaway is the LEVEL-ATTENTION concept**, not this
specific fade. PROBE_005's chi-squared on the full 828-touch
classification is highly significant (p≈2.3×10⁻⁷) — obvious liquidity
levels DO behave differently from random prices on MNQ RTH (more
clean-react, less chop). The PRIOR · age>4h fade is the one cell in that
classification where the structural effect lined up with a simple fixed-
parameter directional trade model and produced a positive EV after costs.

## 5. Caveats — load-bearing, do not soften

These caveats are the difference between "deserves follow-up" and "ready
to build." A future agent who reads §3 and §4 without §5 will reach
the wrong conclusion.

- **N = 62 is tiny.** Frequency works out to ~1 trade every 2 weeks. Even
  a robust true edge would produce noisy in-sample mean estimates at this
  sample size. The 95% CI on Variant B's mean pts/trade easily includes
  values close to zero.
- **p ≈ 0.046 vs pseudo is AT the 5% line.** A single-test result that
  just clears the conventional threshold is the most fragile kind of
  positive result. Practically, it's roughly equivalent to "could
  reasonably go either way on a rerun."
- **Post-hoc cell selection.** The cell `PRIOR · age>4h` was chosen
  because PROBE_005 surfaced it as the cleanest of ~12 type×age cells.
  The trade-model parameters (10/20/30 etc.) were pre-committed BEFORE
  the EV test, but the **cell itself was not blind.** The effective
  multiple-comparisons correction would push the nominal p meaningfully
  higher than 0.046.
- **Bimodal P&L distribution.** The per-trade P&L distribution is mass at
  −10 (stops) and mass at +20-ish (targets), with a thin tail at the
  window-end variant. Welch's t-test assumes normality; this is
  violated. A robust median-shift test (Mann-Whitney) tells broadly the
  same directional story, but the parametric p-values are softer than
  they look.
- **In-sample only — but with PARTIAL OOS-SEAL COMPROMISE for this slice.** PROBE_006's original run looked at 14 OOS touches for this exact hypothesis before the contamination was discovered (see §3a). Independent OOS confirmation has not been *deliberately* spent, but those 14 touches are no longer truly unseen — the seal is partially leaked for this specific slice.
- **Data-integrity correction made the headline weaker.** The 2026-06-26 strict-in-sample correction (§3a) moved the one-sample p from 0.003 → 0.048, mean from +5.57 → +4.15 pts, PF from 2.28 → 1.87. Each of these movements alone would warrant a heavier caveat; together they make the evidence *borderline*. A future agent must internalize §3a's corrected numbers, NOT the superseded §3.1-column numbers.

If you are about to act on §3's numbers without internalizing these caveats AND §3a, stop and re-read.

## 6. Open next moves (for whoever picks this up)

The operator decided **Option (b)** as the active next move — but **kept
Option (a) open as a future option**. Both are listed; do not silently
foreclose either.

- **(b) — chosen as active next move:** carry the *idea* (level-attention
  + aged-fade) to a less-efficient / higher-frequency market where it
  would fire hundreds of times instead of 62. The signal density on
  another instrument (e.g. a less-traded micro future, or a non-US RTH
  market with similar enough OHLCV liquidity dynamics) gives the
  statistical power N=62 cannot give. **Goal: confirm or refute on a
  larger sample where one test reaches real power.**
- **(a) — kept open, partially compromised, NOT yet deliberately spent:** spend the OOS seal (2026-02-01+) on a one-shot MNQ confirmation with the **EXACT frozen parameters** in §2. **Caveat now heavier than originally banked:** per §3a, 14 OOS touches were already looked at by PROBE_006 before the contamination was discovered. A clean Option (a) test must therefore EITHER (i) be run on strictly post-2026-02-01 touches that were NOT among PROBE_006's already-seen 14 (identify and exclude them), OR (ii) explicitly treat the OOS-seal-for-this-slice as weakened and discount the confirmation value accordingly. Honest pre-warning: OOS N will be small too (rough estimate ~15-20 trades over the ~4-month OOS window, possibly fewer after excluding the seen 14), so even a pass has limited power; a clean pass alongside (b) would be more convincing than either alone. **Criterion for that test, if and when it happens, must be pre-committed before looking:** suggested threshold = "cost-aware mean > 0 pts AND real beats pseudo at p < 0.05 on OOS, on a touch set that excludes (or formally discounts) the 14 already-seen touches."
- **Tooling stays transferable regardless of fork.** The probe harness,
  the level/swing machinery in `probe_005_liquidity_levels.py`, the
  fade-EV model in `probe_006_prior_level_fade_EV.py`, and the
  fixed-y-axis replay viewer all carry to a new instrument with
  parameter swaps. (Note: any reuse of `probe_006_prior_level_fade_EV.py` should retrofit the strict-in-sample loader pattern from `strategy_cflr_v0.py` — see §3a.)

## 6a. Pre-registered hypotheses for the new market

These are pre-registrations to test on the higher-frequency / less-efficient market chosen for Option (b). NOT changes to anything on MNQ. The bright line stays bright. From PROBE_007 + STRATEGY_cflr_v0:

1. **Aged-level effect carries.** Same 4-way classification (BREAK / SWEEP-REVERSE / CLEAN-REACT / CHOP) on touches of aged prior-session H/L vs matched random-price baseline. Pass criterion: chi-square p < 0.05 AND CLEAN-REACT rate at real levels > random.
2. **Loser-MFE retracement signal (FULL_VINDICATION %).** Among stopped-fade trades, % that reach +20 fade-direction MFE within the same 30-min window. PROBE_007 observed 70.4% on the MNQ slice. Pass criterion: >50% AND distinguishable from a matched-random baseline.
3. **CFLR confirmation filter (added 2026-06-26 from `strategy_cflr_v0.py`).** Rule: at the touch bar T, require T.close to be on the FADE side of the level by ≥ 1 pt; otherwise skip. Trade geometry otherwise identical to Variant B.
   - **In-sample numbers (`strategy_cflr_v0.py`, < 2026-02-01):** N=34, mean +9.68 pts (+7.93 cost-aware), WR 70.6%, PF 4.29, p<0.0001 vs zero.
   - **DO NOT BELIEVE THE EFFECT SIZE.** CFLR_v0's rule was designed AFTER seeing the in-sample wick anatomy (PROBE_007) and the in-sample touch behavior (PROBE_006). Forking-paths exposure is strong. The mechanism is **near-tautological in-sample**: the rule skips touches where the bar's close was already past the level, which by construction are also the touches most likely to fire the 10-pt stop. The structural fact (close-through-level → likely stop) plausibly generalizes; the **effect size** almost certainly does not.
   - **What to pre-register on the new market:** the *qualitative* hypothesis — "confirmation filtering (touch-bar close on fade side by ≥ 1 pt) elevates win rate by a meaningful margin." Pre-commit a pass criterion (e.g., cost-aware mean > 0 AND CFLR cost-aware mean > baseline cost-aware mean AND CFLR vs baseline p < 0.05 on independent data). Do NOT pre-commit a specific effect-size target derived from the +9.68 in-sample number.
4. **Time-of-day stratification.** Last-90-min vs rest. PROBE_007 observed 61.5% vs 44.9% on N=13 vs 49 (p=0.29). Pre-commit min N ≥ 50 per cell before reading.
5. **Negative control — no MNQ retuning.** No parameter from PROBE_006/007/cflr_v0/etc. will be re-tuned on MNQ data, including the OOS seal. If Option (a) is exercised, it uses Variant B's EXACT frozen parameters (not CFLR_v0's parameters — those are doubly post-hoc and would maximally degrade the confirmation value).

## 7. Cross-references

- **`_worker_reports/PROBE_005_liquidity_level_findings.md`** — the broad
  level-effect classification (real, but ambiguous tradeable shape).
- **`_worker_reports/PROBE_006_prior_level_fade_EV_findings.md`** — the
  original (contaminated) +EV check; **superseded headline numbers** are preserved here for auditability but should NOT be cited as current evidence — see §3a.
- **`_worker_reports/PROBE_007_fade_wick_diagnostic_findings.md`** — the wick anatomy of PROBE_006's slice; source of pre-registration hypotheses 2 and 4 in §6a.
- **`_worker_reports/STRATEGY_cflr_v0_in_sample_results.md`** — the data-integrity correction (§2 of that report) AND the source of pre-registration hypothesis 3 (CFLR) in §6a.
- **`_worker_reports/TASK_014_contamination_fix_findings.md`** — the documentation of this 2026-06-26 correction.
- **Session-broader result (six probes on MNQ-RTH-OHLCV):**
  - PROBE_001 (MTF trend alignment): flat both cuts.
  - PROBE_002 (pullback-reclaim continuation): flat both directions.
  - PROBE_003 (vol clustering): real (compressed mornings → smaller
    afternoons) — amplitude finding, not directional.
  - PROBE_004 (afternoon structure): no morning-conditioned asymmetry.
  - PROBE_005 (level reaction): structural effect real, ambiguous shape.
  - PROBE_006 (fade EV on the one slice): **this candidate.**
- **The picture:** MNQ-RTH-OHLCV is efficient on direction; clustering
  and level-sharpening are real but the **only cost-surviving
  directional slice** out of six probes is this one, and it is small-N.

---

## Inspection visuals

Two representative Variant-B trades (1 winner / 1 loser) were rendered
through the fixed-y-axis batch snapshot tool for the operator's eye —
see TASK_013's findings report for paths. These are
**intuition-building, NOT evidence.** The N=62 statistics in §3 are the
evidence base.
