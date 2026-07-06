# R1 Evidence Diagnostic Convention

**Version**: **v1.2** (revised 2026-05-25; project methodology v1.5+
update — adds predicate-match requirement, entry-point anchoring,
structural stop/target requirement; flags ORWS R1 as contaminated
and triggers re-audit of all v1.0/v1.1 R1 measurements)
**v1.1**: 2026-05-25 — low-confidence flag, per-class lookahead
override, compound-filter pre-check
**v1 created**: 2026-05-25 (methodology v1.4 R1-first triage)
**Purpose**: Empirically test the candidate's edge thesis BEFORE any
other gate. R1 diagnostic measures reversion/continuation rate at
the candidate's signal point; pre-committed thresholds decide MET /
PARTIAL / NOT MET.

This convention is a SPEC, not a running script. Each candidate gets
a one-off diagnostic script written to this convention. The script
runs before R4 probe; its JSON output gates the rest of the pipeline.

> **2026-05-25 audit alert (v1.2)**: the ORWS R1 diagnostic
> (`diagnostic_orws_failed_break_reversion.py`) measured a LOOSER
> predicate than the candidate's actual entry. It counted any 1-min
> close back inside the OR within 30 min of a single break bar. The
> candidate's actual entry requires TWO CONSECUTIVE closes back
> inside before firing. These are not the same predicate. The
> 79.5% R1 figure overstates the v2 signal's edge — the corrected
> v2 base-hit multistart (-$1,307.70, PF 0.95, 5/12 profitable;
> 2026-05-25) is the cleanest empirical evidence. v1.2 introduces
> the **predicate-match requirement** to prevent this contamination
> recurring, and flags existing v1.0/v1.1 R1 outputs for audit.

---

## Why an R1 diagnostic convention exists

Three case studies established the pattern:

| Candidate | R1 reversion @ 30min | Downstream outcome |
|---|---|---|
| opening_range_width_switch (OR-break) | **79.5%** (MET) | Reached implementation; Apex-failed at $603 net / $2,000.50 max DD |
| prior_day_value_area_rejection | (no R1 diagnostic) | Reached implementation; tested-rejected PF 1.17, n=14 |
| prior_day_close_rejection_fade | **38.9%** (NOT MET) | Closed at R1 gate; ~6h pipeline saved |
| first_loss_reversal_day | **45.1%** (NOT MET) | Closed at R1 gate; ~8h pipeline saved |

The pattern is clear: a candidate with R1 reversion < 60% has weak
empirical edge support. Running the full R4 probe + Phase 0 + Phase 1
preflight + variance preflight + spec drafting + implementation is
wasted work when R1 alone can refute the thesis cheaply.

**Methodology v1.4 reverses the v1.3 pipeline order**: R1 diagnostic
runs FIRST (gate), R4 probe runs SECOND (only if R1 ≥ 60%). The
empirical evidence is that R1 diagnostic is more discriminative AND
cheaper than R4 probe at the discriminative step.

---

## Pipeline order (v1.4)

| Step | Stage | Cost | Gate behavior |
|---|---|---|---|
| 1 | Wiki entry authored (template v2) | author time | — |
| 2 | **R1 evidence diagnostic** | ~15 min Codex + ~3 min compute | NEW v1.4 gate: < 60% → CLOSE |
| 3 | R4 probe v1.2 | ~10 min Codex + ~1 min compute | only if R1 ≥ 60% |
| 4 | Phase 0 v2 review | ~10 min | only if R4 acceptable |
| 5 | Phase 1 entry preflight | ~15 min Codex + ~5 min compute | only if Phase 0 admissible |
| 6 | R2 variance preflight v1 | ~20 min Codex + ~3 min compute | only if Phase 1 passes |
| 7 | FINAL spec drafting | ~30-45 min | only if variance preflight passes |
| 8 | Implementation + in-sample | ~2-3 hours | only if FINAL spec drafted |

Each gate is cheaper than the next; closing early saves downstream
work. R1 at gate 2 is the cheapest discriminative check.

---

## What the diagnostic does

**Measures**: For each qualifying signal-eligible event in a 6-month
in-sample window, simulate forward 30 minutes on 1-sec bars. Does
price reach the candidate's structural reversion target BEFORE hitting
the candidate's structural adverse stop?

**Aggregate**: reversion rate, stop rate, neither rate, direction
breakdown, median time-to-revert.

**Verdict** (pre-committed thresholds):
- **≥ 70% reversion**: R1 MET
- **60–70% reversion**: R1 PARTIAL
- **< 60% reversion**: R1 NOT MET (close candidate at this gate)

---

## (v1.2) Predicate-match requirement — MANDATORY

The R1 diagnostic must measure the candidate's **actual entry
predicate**, not a looser proxy. If the candidate's wiki Section 3
declares a multi-bar confirmation, regime gate, or sequence requirement
as part of signal-fire, the R1 diagnostic must require all of those
conditions before counting an event as "qualifying."

### Three sub-requirements

**(a) Entry-predicate match.** The qualifying-event condition in
the R1 diagnostic must be the SAME predicate the candidate uses to
trigger entry — including any N-bar confirmation, regime filter,
volume gate, or sequence requirement. If the candidate enters on
"two consecutive closes back inside OR," the R1 diagnostic must
require two consecutive closes back inside OR before counting the
event. It must NOT count the first close-back-inside as the
qualifying event, because that's not when the trade fires.

**(b) Entry-point anchoring.** The forward-lookahead window starts
from the candidate's **simulated entry timestamp** (i.e., where a
real-time trader would enter, accounting for bar-close timing — see
v1.2 timestamp section below), not from an earlier reference event
like "first break" or "first reclaim." Anchoring on an earlier event
counts reversion that has already happened by the time entry would
fire.

**(c) Structural stop/target, not 1R/1R.** The reversion outcome must
be measured against the candidate's **actual structural stop and
target** as defined in the wiki / spec, not a normalized 1R/1R
geometry. The 1R/1R criterion in the v1 spec was a simplification
that masked asymmetric stop:target geometry. If the candidate's
structural stop is at the failed extreme (often 8-120pt from entry)
and its structural target is the OR midpoint (often 2-10pt from
entry mid-reversion), R1 must measure with those distances, not a
1R/1R proxy.

### Why this matters

The looser the qualifying-event predicate, the higher the R1
reversion rate — but the lower the relevance to the candidate's
actual trades. A diagnostic that counts "any close inside the OR
within 30 min of a single break bar" will produce a higher reversion
rate than a diagnostic that counts "the OR midpoint reached before
the failed extreme, starting from a 2-bar reclaim entry point."

The first measures OR-stickiness-as-phenomenon. The second measures
the candidate's actual edge. Only the second is admissible as R1
evidence under v1.2.

### (v1.2) Timestamp convention requirement

`nb_lib` resampling uses `label="left", closed="left"` — every 1-min
bar's index timestamp T represents the bar covering `[T, T+1)`. The
bar's close value is the price at T+1 but is indexed by T.

R1 diagnostics must reflect this in three ways:

1. **Signal-fire time is the LAST predicate bar's close-time, not
   start-time.** If the candidate's entry predicate completes at
   the close of bar `[T, T+1)`, the signal-fire timestamp is T+1
   (the bar's right edge), and the simulated entry happens at the
   open of the NEXT bar (`[T+1, T+2)`) — typically at T+1+1sec on
   1-sec data.

2. **The lookahead window is measured from the simulated entry
   timestamp**, not from the predicate-bar's left-label. A 30-min
   window from a left-labeled bar T covers minutes T to T+30; from
   the simulated entry at T+1, it covers T+1 to T+31. The two are
   not the same.

3. **Same-bar lookahead bias is forbidden.** No outcome may depend
   on data from the predicate-bar itself or any bar with index ≤
   the predicate-bar's left-label. The first observable post-entry
   data is the close of the bar at index T+1 (i.e., the price at
   T+2).

The 2026-05-25 v2 base-hit implementation had a documented
left-labeled timestamp bug (signal fired at T rather than T+1). The
R1 ORWS diagnostic does not have the same execution bug (it doesn't
simulate execution), but its lookahead-window math was internally
consistent only because both anchor and window used the same
left-labeled T — a coincidence, not a discipline. v1.2 makes the
discipline explicit.

### Audit obligation for existing R1 measurements

All R1 measurements taken under v1.0 / v1.1 conventions must be
re-checked against the v1.2 predicate-match requirement. The audit
question for each is:

1. Does the diagnostic's qualifying-event condition match the
   candidate's full entry predicate (including N-bar confirmation,
   regime filters, sequence rules)?
2. Does the lookahead anchor match the simulated entry timestamp,
   not an earlier reference event?
3. Does the outcome use the candidate's structural stop/target,
   not 1R/1R?

A "no" on any of (1)-(3) marks the R1 result as **contaminated**.
Contaminated MET verdicts are downgraded to **INCONCLUSIVE** until
re-measured under v1.2. Contaminated NOT MET verdicts generally
stand (predicate-loosening inflates reversion rates, so tightening
to v1.2 would push them further below 60%), but a re-measurement
note should be appended to the candidate wiki for audit trail.

**ORWS is the first known contaminated MET verdict**: its diagnostic
counted "any close inside OR" rather than the 2-bar reclaim required
by the entry predicate. The 79.5% figure is now treated as
INCONCLUSIVE pending a v1.2 re-measurement. The corrected v2 base-hit
multistart (-$1,307.70, PF 0.95) is the cleanest empirical evidence
for the candidate's actual edge.

---

---

## What the R1 diagnostic does NOT do

- **Not a full P&L simulation.** No friction, no compliance, no
  partial-fill mechanics, no BE arm. Reversion-vs-stop binary
  outcome only.
- **Not a frequency estimate.** R4 probe handles that.
- **Not a variance estimate.** R2 variance preflight handles that.
- **Not a regime split.** Aggregate over the 6-month window only.

The R1 diagnostic answers ONE question: does the candidate's
participant-behavior story (rejection / reversal / acceptance / etc.)
translate into a measurable empirical edge at 1R target / 1R stop
geometry?

If the answer is no (< 60% reversion), the thesis is refuted at the
cheapest gate. Higher gates can't fix a refuted thesis.

---

## Diagnostic script contract

### File location

`nb_lib/scripts/diagnostic_<prefix>_<predicate>_reversion.py`

Where `<prefix>` is an abbreviation of the candidate ID (e.g.,
`orws` for opening_range_width_switch, `pdcrf` for
prior_day_close_rejection_fade, `flrd` for first_loss_reversal_day)
and `<predicate>` is the candidate's signal-fire predicate name
(e.g., `failed_break_reversion`, `close_rejection_reversion`,
`failed_impulse_reversion`).

### Length and complexity

- Target: 150-250 lines including imports and a single `main()`.
- Hard cap: 300 lines.
- Single file. Reuses existing nb_lib helpers; no new library
  primitives.

### Inputs

- **Sample window**: 2024-08-01 → 2025-01-31 (6 months in-sample,
  ~125 trading days). This is the project-pinned R1 window for
  cross-candidate comparison.
- **1-sec MNQ data** via `load_seconds(DATA_DIR)`.
- **Per-candidate predicates** from the wiki Section 3.

### Predicate scope

The diagnostic counts ONLY qualifying signal events that survive the
candidate's pre-committed predicates AND a stop-band guard. The stop
band should match the candidate's spec (or wiki R2 frontmatter) so
that the diagnostic measures structurally tradeable events, not
all signal-eligible bars.

**(v1.2) Predicate-match is mandatory** (see dedicated section
above). The qualifying-event condition must include every part of
the entry predicate the candidate uses to fire a trade — including
N-bar confirmation, regime filters, and sequence rules. Looser
proxies (e.g., "any close back inside OR" when the entry requires
2-bar reclaim) produce inflated R1 rates that don't translate to
candidate edge. Use the candidate wiki Section 3 as the source of
truth for the predicate stack.

### (v1.1) Compound-filter pre-check

When the candidate uses **compound regime gates** (e.g., AND of two
or more filters), the diagnostic should first measure the JOINT
pass rate of all regime gates. If the joint pass rate is below 10%
of trading days, flag as `compound_filter_over_restrictive` in the
JSON output.

When this flag is true, the R1 reversion rate is at risk of low
confidence even if individual events appear sufficient. The
diagnostic should still run and produce a verdict; the flag is
documentation that helps interpret a NOT MET or INCONCLUSIVE
verdict.

The compound-filter pre-check was motivated by APTH (ATR-percentile
≥ 0.70 AND Choppiness < 38 jointly passed only 2.5% of days). The
methodology lesson: AND-combining intuitive filters often produces
unintended over-restriction.

### (v1.1) Authoring checklist

Before running an R1 diagnostic on a new candidate, verify:

1. Predicates from wiki Section 3 are unambiguous.
2. Stop band guard matches wiki R2 frontmatter (or candidate spec
   if available).
3. Mechanism class is declared (fast-resolution / moderate / slow);
   default lookahead is set accordingly.
4. If compound regime gate: joint pass rate measured BEFORE R1 run.
   If joint < 10%, flag and proceed (don't pre-filter).
5. Stop-band, lookahead, and any override are pre-committed BEFORE
   running the diagnostic.
6. **(v1.2)** Qualifying-event predicate exactly matches the entry
   predicate from wiki Section 3 — including N-bar confirmation,
   regime filters, sequence rules. Looser-proxy predicates are
   forbidden.
7. **(v1.2)** Lookahead anchor is the simulated entry timestamp
   (after bar-close confirmation), not an earlier reference event.
8. **(v1.2)** Reversion outcome uses the candidate's structural
   stop and structural target, not 1R/1R.
9. **(v1.2)** Bar-close timing convention documented: `label="left",
   closed="left"` means signal-fire is at T+1 (bar close), not T
   (bar start). Simulated entry occurs in the bar following
   signal-fire.

### Output

Write to
`nb_lib/probe_results/<candidate_id>_r1_diagnostic.json` with schema:

```json
{
  "candidate_id": "<wiki filename without .md>",
  "diagnostic_type": "<predicate_name>_reversion_rate",
  "convention_version": "v1",
  "ran_at": "<ISO datetime>",
  "window_start": "2024-08-01",
  "window_end": "2025-01-31",
  "lookahead_minutes": 30,
  "stop_band_filter": [<low>, <high>],

  "n_days_eligible": <int>,
  "n_qualifying_events_total": <int>,
  "n_short_events": <int>,
  "n_long_events": <int>,
  "outcomes": {
    "revert": <int>,
    "stop": <int>,
    "neither": <int>
  },
  "reversion_rate_overall": <float>,
  "stop_rate_overall": <float>,
  "neither_rate_overall": <float>,
  "reversion_rate_short": <float>,
  "reversion_rate_long": <float>,
  "median_minutes_to_revert": <float|null>,

  "r1_verdict_thresholds": {"MET": 0.70, "PARTIAL": 0.60, "NOT_MET": "< 0.60"},
  "r1_verdict": "MET | PARTIAL | NOT MET",
  "sample_rows": [<list of up to 30 sample events for inspection>],
  "interpretation": "<short paragraph>"
}
```

### Pre-committed thresholds

| Reversion rate | n_qualifying_events | R1 verdict | Pipeline action |
|---|---|---|---|
| ≥ 0.70 | ≥ 15 | **MET** | Proceed to R4 probe |
| 0.60 ≤ rate < 0.70 | ≥ 15 | **PARTIAL** | Proceed to R4 probe but flag |
| < 0.60 | ≥ 15 | **NOT MET** | **CLOSE candidate** at this gate |
| any | **< 15** | **INCONCLUSIVE** | **(v1.1)** Close or extend window per operator |

These thresholds are project-methodology-pinned and must NOT be
changed candidate-by-candidate. The 0.60 floor is just above the
50% null with a 10% margin for false-positive selection.

**(v1.1) Low-confidence flag**: when `n_qualifying_events < 15`, the
R1 result is statistically unreliable (95% CI is wide enough to span
both MET and NOT MET regions). The verdict is **INCONCLUSIVE**
rather than NOT MET, even if rate < 60%. Practical handling: the
operator may close the candidate (no edge demonstrated) or extend
the diagnostic window to increase n. **Default action: close**,
because failure to clear n=15 in 126 days of 1R/1R-tradable events
itself indicates the mechanism produces signals too sparsely to be
worth pipeline investment.

The low-confidence flag was motivated by APTH (n=8) and FHREB (n=2)
closures where rate was technically below 60% but the small sample
made the verdict statistically unstable.

### Lookahead window

**Default: 30 minutes.** Same as ORWS, PDCRF, FLRD diagnostics for
cross-candidate comparability.

**(v1.1) Per-candidate-class default override**: pre-committed
class-level lookahead defaults are now documented for slow-resolution
mechanisms:

| Mechanism class | Default lookahead | Examples |
|---|---|---|
| fast-resolution rejection | 30 min | OR-break (ORWS), close-rejection (PDCRF) |
| moderate-resolution | 60 min | IB-extension, failed-impulse-reversal |
| slow-resolution compression/expansion | 90 min | compression-break (LCB), expansion breakout |

The class override applies automatically; the candidate's wiki
Section 3 should declare its mechanism class. A non-default override
within a class requires explicit pre-commitment in the wiki BEFORE
the diagnostic runs.

**Post-hoc lookahead extension is HARD-HALT-POST-HOC-TUNING**:
extending lookahead after seeing a result is the exact
discipline-failure the project methodology was designed to prevent.

**(v1.1) "Neither" rate as informational signal**: when `neither_rate
> 0.25` AND verdict is NOT MET, the diagnostic report should flag
"possible lookahead-window mismatch" — the mechanism may have edge
on a longer timeframe but the pinned lookahead can't see it. This
is documentation, not a verdict override.

### Outcome categories

For each qualifying event:

- **revert**: price reached 1R reversion target (= candidate's TP1
  at 1R, or candidate's structural target if known) WITHIN the
  lookahead window, BEFORE reaching the 1R adverse stop.
- **stop**: price reached 1R adverse stop first.
- **neither**: lookahead window expired with neither hit.

Same-bar ambiguity rule: if a single 1-sec bar's range includes
both target and stop, count as **stop** (conservative).

### OOS safety

The diagnostic script MUST include:

```python
WINDOW_END_HARD_CAP = date(2026, 1, 31)
assert WINDOW_END <= WINDOW_END_HARD_CAP
```

OOS leak = HARD-HALT-OOS-LEAK.

### Cost budget

- Diagnostic compute: under 5 minutes wall-clock.
- Authoring time: ~15 minutes (similar shape across candidates;
  template the prior diagnostic for the new candidate).

### Determinism

Diagnostic must be deterministic — same window + same data + same
predicates = byte-identical JSON (modulo `ran_at`).

---

## "Neither" rate as a methodology signal

For ORWS (79.5% revert) and PDCRF (38.9% revert), the "neither" rate
was ~0%. Most events resolved within 30 min.

For FLRD (45.1% revert), the "neither" rate was **31.4%**. This was
informative: the mechanism is structurally slow (median 10 min to
revert, vs ORWS's 2 min). A high "neither" rate suggests the
diagnostic window may be inappropriate, BUT this doesn't change the
verdict — the 30-min threshold is pinned for cross-candidate
comparability.

**Recommended convention**: when "neither" > 25%, document the
slow-resolution caveat in the diagnostic report. Future v1.5
convention iterations may allow per-candidate-class lookahead
calibration, but only if pre-committed.

---

## How the diagnostic differs from the variance preflight (v1.3)

| | R1 diagnostic (v1) | R2 variance preflight (v1.3) |
|---|---|---|
| When in pipeline | Before R4 probe | After Phase 1 preflight |
| Window | 6 months (~125 days) | Full in-sample (~469 days) |
| Input | Predicates + stop-band | Phase 1 preflight signals (already filtered) |
| Measures | Binary revert vs stop | P&L distribution, max DD, trailing-DD breach |
| Discriminative for | R1 (edge thesis) | R2 (Apex survival) |
| Cost | ~10 min Codex + ~3 min compute | ~20 min Codex + ~3 min compute |
| Gate effect | NOT MET → close | FAIL → spec revision before FINAL |

Both gates are cheap relative to implementation; both are necessary.
The R1 diagnostic catches "no edge" candidates; the variance
preflight catches "edge exists but trailing-DD geometry breaches Apex"
candidates (the ORWS pattern).

---

## Case studies

### Case 1: opening_range_width_switch (R1 MET — CONTAMINATED under v1.2)

R1 reversion = 79.5% over 161 OR-break events / 127 days. Symmetric
up/down (79.7/79.3). Median minutes-to-revert: 2.

Outcome: R1 supported the thesis. Candidate proceeded through R4
probe + Phase 0 + Phase 1 preflight + FINAL spec + implementation.
In-sample test produced PF 1.07 with positive net P&L but Apex bust
via trailing-DD geometry — the variance preflight gate (added in
v1.3 after this case study) would have caught this pre-implementation.

**(2026-05-25 v1.2 contamination flag)** The ORWS R1 diagnostic used
a LOOSER qualifying-event predicate than the candidate's actual
entry. It counted any 1-min close back inside OR within 30 min of
the first break bar as a "reversion." The candidate's actual entry
requires TWO CONSECUTIVE closes back inside OR before firing. The
v2 base-hit candidate (which keeps ORWS's entry predicates and only
changes risk/exit geometry) failed in-sample with the bug-free
implementation: -$1,307.70, PF 0.95, 5/12 profitable. This is the
cleanest evidence that the 79.5% R1 figure does NOT reflect the
candidate's actual edge.

The 79.5% R1 verdict is **DOWNGRADED to INCONCLUSIVE** under v1.2
until a re-measurement is run with predicate-match (2-bar reclaim
requirement, entry-timestamp anchor, structural stop/target). Until
then, the "ORWS singularity" narrative (1 MET out of 14 R1
measurements) is suspect.

**Methodology lesson**: R1 MET under v1.0/v1.1 predicate-loose
conventions does NOT guarantee the candidate's actual entry has
edge. Predicate-match (v1.2) closes this gap. Going forward, R1
diagnostics must mirror the candidate's full entry predicate, not
a looser proxy.

### Case 2: prior_day_close_rejection_fade (R1 NOT MET, closed at gate)

R1 reversion = 38.9% over 18 wick-rejection events / 126 days. Short
33% / long 50% (small samples).

The candidate was authored AFTER prior_day_value_area_rejection
tested-rejected; the wiki explicitly framed the bet as "single
precise level behaves differently from value-area band." R1 data
refuted that bet: single-price rejections continue more often than
they revert.

Outcome: candidate closed at R1 gate. ~6h downstream pipeline saved.

**Methodology lesson**: explicit hypothesis-vs-data contrast at R1
discriminates clean closures from speculative pursuits.

### Case 3: first_loss_reversal_day (R1 NOT MET, closed at gate)

R1 reversion = 45.1% over 51 failed-impulse events / 107 days.
"Neither" rate 31.4% — slow-resolution mechanism flagged.

Outcome: candidate closed at R1 gate without R4 probe. ~8h
downstream pipeline saved. R1-first triage pattern validated.

**Methodology lesson**: the R1 30-min lookahead may undercount
slow-resolution mechanisms, but post-hoc extension is forbidden
(HARD-HALT-POST-HOC-TUNING). The pinned threshold preserves
cross-candidate comparability.

### Case 4: opening_range_width_switch_v2_base_hit (v1.2 trigger)

The v2 base-hit candidate inherited ORWS's entry predicates
unchanged (2-bar reclaim after a break) but changed risk to $200
and exits to full-position at OR midpoint. Pipeline executed by
parallel agent on 2026-05-25:

1. R2 variance preflight v1.3 PASSED (PF 1.6137, max DD $965.75)
2. FINAL spec drafted
3. First 12-start in-sample multistart APPARENT-PASSED (+$9,487,
   PF 1.35, 9/12 profitable)
4. Pre-OOS audit caught left-labeled 1-min timestamp bug (signal
   bar's start used instead of completed-bar timestamp)
5. Corrected 12-start in-sample multistart FAILED: 329 trades,
   -$1,307.70, PF 0.95, 5/12 profitable, worst start max DD
   $1,699.30. Direction split: long +$446.30 PF 1.04, short
   -$1,754.00 PF 0.87.

The corrected result is the cleanest empirical evidence for the
ORWS-family entry predicate under bug-free execution. The
substantial swing between buggy ($9,487) and corrected (-$1,307)
runs from a single timestamp-labeling fix demonstrates how
sensitive the signal is to look-ahead bias.

This case study triggered v1.2's predicate-match requirement. The
contamination chain was: R1 measured "any reclaim within 30 min"
→ produced 79.5% → inflated confidence in the entry predicate's
edge → spec and implementation built on that confidence → buggy
implementation appeared to work → bug fix revealed there was no
edge in the actual entry predicate.

**Methodology lesson**: when a candidate's R1 predicate doesn't
match its entry predicate, the R1 measurement is not informative
about the candidate's actual edge. v1.2 requires the match. Where
no v1.2-compliant R1 exists, the candidate's edge claim is
unsubstantiated and the corrected in-sample multistart is the
falsification.

Report: `nb_lib_opening_range_width_switch_v2_base_hit_multistart_report.md`.
Audit trail: `_R1_EVIDENCE_DIAGNOSTIC_CONVENTION.md` v1.2 (this section).

---

## How to use the diagnostic for retrofitting

If an existing candidate already has R4 probe + Phase 0 + Phase 1
preflight artifacts AND a known R1 gap (PARTIAL or unmeasured):

1. Write the R1 diagnostic per this convention.
2. Run it.
3. If MET (≥70%): R1 partial → MET; previous CONDITIONALLY ADMISSIBLE
   verdict may flip to ADMISSIBLE. Re-evaluate Phase 0.
4. If PARTIAL (60-70%): R1 stays partial; verdict unchanged but
   strengthened with data.
5. If NOT MET (<60%): R1 refuted; verdict downgrades to
   INADMISSIBLE if other gaps exist.

---

## How to use the diagnostic when authoring new candidates

1. Author the wiki entry with template v2 frontmatter, including a
   pre-committed predicate stack in Section 3.
2. Pre-commit the stop-band guard (or note "TBD: derived from R4
   probe").
3. Write and run R1 diagnostic.
4. If R1 < 60%: close the candidate. Do NOT proceed to R4 probe.
5. If R1 ≥ 60%: proceed to R4 probe.

This order saves R4 probe authoring time when R1 already refutes.

---

## Frontmatter integration (template v2)

Template v2 frontmatter extended with R1 diagnostic fields (added
under `admissibility`):

```yaml
admissibility:
  r1_edge_thesis:
    r1_diagnostic_convention_version: "v1"
    r1_diagnostic_script: "<path>"
    r1_diagnostic_output: "<path>"
    r1_diagnostic_window: ["2024-08-01", "2025-01-31"]
    r1_lookahead_minutes: 30
    r1_n_qualifying_events: <int>
    r1_reversion_rate: <float>
    r1_neither_rate: <float>  # informational; high (>25%) flags slow-resolution
    r1_verdict: "MET | PARTIAL | NOT MET"
  r2_apex_survival:
    ...  # (existing fields, see _R2_VARIANCE_PROBE_CONVENTION.md)
  r4_signal_frequency:
    ...  # (existing fields, see _R4_PROBE_CONVENTION.md)
```

Backward compatibility: candidates evaluated under v1.3 (no R1
diagnostic) keep their existing frontmatter unchanged. The R1
diagnostic block is required for **new** candidates from v1.4 forward.

---

## Convention history

| Version | Date | Notes |
|---|---|---|
| v1 | 2026-05-25 | Initial convention. Authored after two consecutive R1-first triage closures (PDCRF + FLRD) demonstrated the pattern works. R1 diagnostic moves to step 2 in the pipeline, ahead of R4 probe. Three case-study verdicts documented (ORWS MET, PDCRF/FLRD NOT MET). Pre-committed thresholds (MET ≥70%, PARTIAL 60-70%, NOT MET <60%) and 30-min lookahead are now project-methodology-pinned. Post-hoc lookahead extension is HARD-HALT-POST-HOC-TUNING. |
| v1.1 | 2026-05-25 | Methodology v1.5 incremental update. Added: (1) **R1 low-confidence flag** when `n_qualifying_events < 15` — verdict becomes INCONCLUSIVE rather than NOT MET. Motivated by APTH (n=8) and FHREB (n=2) closures where small samples made verdict statistically unreliable. (2) **Per-class lookahead defaults**: fast-resolution 30min (default), moderate 60min, slow-resolution compression/expansion 90min. Motivated by LCB (91% "neither" at 30min, median 27 min) showing lookahead-window mismatch on slow mechanisms. (3) **Compound-filter pre-check**: candidates with compound regime gates measure joint pass rate first; flag if <10% of days qualify. Motivated by APTH (2.5% joint pass). (4) **"Neither" rate informational signal** when >25% AND verdict NOT MET: documentation, not verdict override. ORWS R1 regime-stability test (2026-05-25) confirmed methodology v1.4 baseline is robust before v1.5 calibration. |
| v1.2 | 2026-05-25 | **Predicate-match requirement** (mandatory). Triggered by ORWS v2 base-hit case study: the v1.0 ORWS R1 diagnostic counted "any close inside OR within 30 min of a single break" but the candidate's actual entry requires "2 consecutive closes back inside OR" — different predicates. The corrected v2 base-hit in-sample multistart (-$1,307.70, PF 0.95) showed no actual edge. Three sub-requirements added: (a) **Entry-predicate match**: qualifying-event condition must include every part of the entry predicate (N-bar confirmation, regime filters, sequence rules). Looser proxies forbidden. (b) **Entry-point anchoring**: lookahead window starts from simulated entry timestamp (post-bar-close), not earlier reference event. (c) **Structural stop/target**: outcomes measured against candidate's actual structural stop and structural target, not 1R/1R proxy. Also added (d) explicit **timestamp convention requirement** documenting `label="left", closed="left"` and that signal-fire is the LAST predicate bar's close-time (T+1), not start-time (T). **Audit obligation**: all v1.0/v1.1 R1 measurements must be re-checked against v1.2; contaminated MET verdicts downgrade to INCONCLUSIVE pending re-measurement. **ORWS 79.5% R1 is the first known contaminated MET, downgraded to INCONCLUSIVE.** Implication: the "ORWS singularity" claim (1 MET out of 14 measurements) is suspect until all 14 are audited; predicate mismatches may have inflated ORWS's R1 relative to filter-augmented candidates measured under different criteria. |
