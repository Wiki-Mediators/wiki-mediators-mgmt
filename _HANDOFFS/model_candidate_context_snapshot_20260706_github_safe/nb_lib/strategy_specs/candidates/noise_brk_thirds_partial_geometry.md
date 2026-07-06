---
name: "noise_brk thirds-partial geometry"
tagline: "noise_brk with a 5/5/5 thirds partial-take at +30/+50/runner instead of the live TP1+10/TP2+80 split; tests whether middle-distance trims capture gains the wider runner gives back."
status: "screen-failed-pre-build"
created: 2026-06-30
updated: 2026-06-30
source: "Session 2026-06-30 trim-while-green hypothesis. The contaminated overlay sim (probe_level_context_sizing_overlay_on_nb.py, trim_only_15c branch) suggested ~+167% net vs baseline — but the result is methodologically contaminated because the recorded NB pnl already includes the live TP1 partial. The CLEAN form of that hypothesis is a STRATEGY redesign of NB's partial-take geometry, not an overlay on top of the existing one. This candidate is that redesign."

# Market and timing
markets: ["MNQ"]
session: "RTH"
time_of_day: "09:36 ET fire (inherited from noise_brk canonical)"
hold_duration: "intraday"

# Signal characteristics
signal_type: "single-sided breakout"
indicators: ["ADR(20)", "first-6-minute single-sided band break"]
timeframes_used: ["1-second"]

# Execution
brackets: "fixed-point partials over ATR-scaled signal"
position_sizing: "fixed-contracts (15 at entry, thirds 5/5/5)"

# Cross-references
canonical_spec: "../canonical/noise_brk_canonical_alpha.md"
implementation: null
related_candidates: []
test_results:
  in_sample_n: null
  in_sample_pnl_dollars: null
  in_sample_pf: null
  in_sample_win_rate: null
  out_of_sample_tested: false

tags:
  - rth-only
  - intraday
  - breakout
  - exit-geometry-variant
  - nb-family
  - screen-required
---

# noise_brk thirds-partial geometry

## 0. Methodology framing (read first)

This is **NOT** an overlay test. It is a **strategy redesign of NB's partial-take geometry**. A test of this candidate consumes test-bucket budget against the NB strategy family per §3 bucket discipline. Before running the test, decide:

- Are we willing to spend an NB test slot on a partial-geometry variant?
- If this variant tests positive, does it REPLACE live NB or run as a parallel sleeve?
- If it tests negative, what does that tell us beyond "+30/+50 partials don't beat +10/+80 partials" for this exact entry mechanism?

The originating hypothesis came from a contaminated in-session simulation (see §2). The hypothesis is plausible, but the supporting "+167% net" number from that sim is **NOT TRUSTABLE** and must be banked as motivation only, never quoted as evidence.

## 1. Thesis

NB's current exit geometry pulls 7 of 15 contracts at TP1 = ±10 points (close in), then sends the remaining 8 contracts as a runner all the way to TP2 = ±80 points (far). The runner is a long stretch. Many NB trades reach +30 or +50 favorable, then reverse without reaching +80 — the runner gives back the middle-distance gain it had in hand.

**Thesis:** A thirds split (5 / 5 / 5) at +30 / +50 / runner-to-NB's-TP2-or-trail captures middle-distance gains the live runner forfeits, at the cost of:
- giving up the early TP1+10 partial,
- adding two partial-take events instead of one (compliance + execution friction).

The hypothesis is that the middle-of-the-trade lock-in dominates the lost TP1 income on NB's trade distribution. The session 2026-06-30 contaminated sim suggests it may; only a clean test will say.

## 2. Evidence basis (and what's contaminated)

**Available evidence:**

- The in-session trim simulation (`probe_level_context_sizing_overlay_on_nb.py`, branch `trim_only_15c`) reported net +$45,133 vs baseline +$16,917 (+167%), max DD −$1,548 vs baseline −$934 (+66% worse), Apex margin +$952 vs +$1,566 (smaller but positive). 254 in-sample trades.
- **Contamination:** the simulation treated NB's recorded `pnl` as if it were a flat 15-contract trade and applied trim ON TOP of NB's already-existing TP1 partial. That double-counts the partial-take mechanic. The headline net number overstates by an unquantified amount.
- The MFE statistics in `trades_atr20.json` are clean — they reflect what the trade saw in points before turning. Those are the load-bearing inputs for the clean version of this test.

**What the contamination does NOT invalidate:**

- The qualitative observation that many NB trades reach +30 / +50 favorable then reverse without reaching +80 (this is what MFE distribution shows directly).
- The structural argument that a 5/5/5 thirds split has more middle-distance lock-in than 7/8 with TP1+10.

**What the contamination DOES invalidate:**

- Any specific net / DD / PF number from the trim sim. We cannot quote those as evidence for the build.

## 3. Strategy logic

**Same as `noise_brk_canonical_alpha`** in every respect EXCEPT the partial-take geometry:

- Entry: identical (9:36 ET single-sided break of ADR(20)-scaled noise band; see canonical §3 Phases 0-2).
- Stop: identical (entry ± 32 points; see canonical §5 Mechanism 1).
- MIN_HOLD: identical (10 bars before TPs become live; see canonical §6).
- EOD flat: identical (canonical §7).
- Compliance accounting (Model 2): identical (canonical §8).

**Differences (this candidate):**

### Position sizing

- **15 contracts at entry** (same as canonical).
- Subdivision: **5 / 5 / 5** (instead of canonical's 7 / 8).

### Exit management

| Mechanism | Canonical NB | This candidate |
|---|---|---|
| Stop | entry ± 32 pts → exit ALL remaining | identical |
| Partial 1 (TP1) | entry ± **10 pts** → close **7 contracts** | entry ± **30 pts** → close **5 contracts** |
| Partial 2 (TP_MID) | (does not exist) | entry ± **50 pts** → close **5 contracts** |
| Runner exit (TP2) | entry ± 80 pts → close 8 contracts | entry ± 80 pts → close **5 contracts** |
| EOD flat | flatten remaining at session close | identical |

### Exit-reason string mapping (to be aligned with canonical §11 if/when built)

To preserve NB's auditable exit-reason vocabulary, the new partial events need a deterministic naming convention. Suggested:

- `tp30+...` where `tp30` indicates the +30 partial fired before the terminating exit.
- `tp30+tp50+...` where both middle partials fired.
- `tp30+runner_be`, `tp30+tp50+runner_be`, `tp30+tp50+tp2` etc.

Exact strings to be decided with the engine implementer; the principle is to preserve traceability across all 2-of-3 / 3-of-3 partial-firing combinations.

## 4. Required screen

This candidate falls under §15B mechanism-class screening, but only partially — the entry mechanism is the already-validated NB signal, so the question is not "does the mechanism class work" but "does the exit redesign add value on this mechanism's existing trades."

**Recommended pre-build screen** (cheaper than a full realsim build):

1. Use the existing `trades_atr20.json` MFE/MAE per trade as the proxy.
2. For each in-sample trade, compute what the new partial geometry would have realized:
   - 5 contracts at the live engine's behavior up to +30, then locked at +30 if reached (MFE ≥ 30).
   - 5 contracts at +50 if reached (MFE ≥ 50).
   - 5 contracts at the trade's actual terminating outcome (TP2 / stop / BE / EOD) — using the engine's per-contract gross dollars at exit, NOT including the live TP1+10 partial since we're replacing it.

The CRITICAL fix vs. session 2026-06-30's contaminated sim:
- Subtract out the +10 partial's contribution to recorded `pnl` BEFORE scaling. NB's recorded `pnl` at 15 contracts = 7 × (TP1+10 outcome) + 8 × (runner outcome). The clean per-contract gross for the runner portion is `(pnl − 7 × tp1_gross_per_contract) / 8`. Without this correction, you re-apply NB's TP1 lock-in on top of your new partials and the result is meaningless.
- OR (simpler, slightly different question): re-run the realsim engine directly with the new partial config; do not derive from the recorded ledger. This is the cleanest path and the one the build-implementer should probably take.

**Hard rule:** do NOT promote any cleaned-up sim number until the realsim engine has run with the new config end-to-end and the result is reproducible.

## 5. Open methodology questions (for the next reviewer)

- **Partial-take granularity.** Is 5/5/5 the right split, or 6/5/4 / 4/5/6 / 3/6/6? Decide BEFORE running the screen — a tested grid of splits is multi-trial fishing.
- **Fixed-points vs ATR-scaled partials.** +30 / +50 are fixed-point figures. NB's stop and bands are ATR(20)-scaled. Should the partials be ATR-scaled too (e.g., +0.75 ADR / +1.25 ADR), or stay fixed-points? The contaminated sim used fixed-points; that should be the first-tested form for traceability.
- **Trail vs hard TP2 for the runner.** The current spec keeps NB's hard TP2 at +80 for the runner's exit. Is a structural trail (e.g., trail by ATR from running max) a better runner exit? This is a SEPARATE candidate, not a tweak to this one.
- **Compliance impact.** Adding a second partial-take event changes the compliance-checkpoint cadence under Apex 4.0. The compliance evaluator in the engine needs to confirm it sees and records all three partial events correctly. Not a strategy question, but a build-side prerequisite.
- **Does this candidate REPLACE live NB or run as a parallel sleeve?** Answer must be locked before consuming the NB test bucket — the test budget interpretation depends on it.

## 6. Test plan (when authorized)

1. Confirm decision on §5 questions, especially fixed-points vs ATR-scaled partials and replace-vs-parallel.
2. Lock the parameter set (5/5/5 + +30/+50/+80 fixed-points + NB stop and MIN_HOLD).
3. Run on the **test bucket** of NB's bucket usage tracker (one-shot per pre-committed config).
4. Read against criteria calibrated to NB's live deployable profile (NOT against the contaminated sim's +$45k figure).
5. Update `noise_brk_bucket_usage.json` to record the consumption.

## 7. Devil's-advocate

- The contaminated sim's "+167% net" looks like the kind of finding that screams "too good." Even after the contamination caveat, the structural argument is plausible — but if the clean test comes back near baseline or worse, that's the most likely outcome and should not be a surprise.
- NB has been deployed and works as-is. A redesign that doesn't decisively beat the live numbers (after Apex compliance checks pass) doesn't get deployed — it gets banked as a tested-rejected variant. The bar is higher than "marginally better than baseline" because re-deployment costs and live-edge disruption are non-trivial.
- The "trim while green" intuition is one of the oldest in trading folk wisdom. It's not novel evidence. It needs to clear a higher bar BECAUSE it's plausible — that's where the previously-overfit traps live.

## 8. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-06-30 | `untested-ideation-screen-required` | Created as the clean form of the trim-while-green hypothesis surfaced in session 2026-06-30. Contaminated overlay sim ruled out; this redesigns NB's partial geometry instead. Awaiting reviewer pass before authorizing a test-bucket consumption. |
| 2026-06-30 | `screen-failed-pre-build` | Descriptive MFE-bucket table (`probe_nb_mfe_bucket_descriptive_table.py`) showed COST bucket (reached +10, died before +30) is **76 trades / 29.9% of in-sample** — exactly the failure mode flagged in §0. GAIN bucket (reached +50 not +80) is only **14 trades / 5.5%**. Cost bucket is 5.4× larger than gain bucket by count. Naive per-trade arithmetic is roughly net-zero / mildly positive, but the structural argument against the candidate is strong: 76 "small green that fades" trades each currently lock +$140 at TP1+10; under this candidate those trades walk back to BE empty-handed. NB's TP1+10 placement is well-calibrated to the in-sample MFE distribution. Not testing. |

## 9. Verdict

DO NOT consume an NB test slot on this candidate. The MFE-distribution evidence is unambiguous: the cost bucket (76 trades) dominates the gain bucket (14 trades) by 5.4× count. NB's current TP1+10 is well-placed for MNQ's actual move distribution; pulling lock-in farther out forfeits real income on the modal "small green that fades" trade.

The underlying intuition ("trim while green captures middle-distance gains") is not invalidated as a concept — it's invalidated for this product, this entry mechanism, and these specific +30/+50 thresholds. A separate candidate that finds a different threshold structure (or a different base entry mechanism) is not ruled out by this finding.
