---
name: "OFRT v0 — Overnight-Fade RTH Tilt"
tagline: "Fade the overnight return on RTH: enter at 09:30 open in the direction opposite the Globex 18:00->09:30 close-open change, hold-to-close (no intraday stop)."
status: "tested-informational-rejected"
created: 2026-06-28
updated: 2026-07-02
source: "External literature — Lou-Polk-Skouras (JFE 2019), Cooper-Cliff-Gulen (2008), Hendershott-Livdan-Rösch (JFE 2020). Compass artifact banked at `nb_lib/strategy_specs/source_artifacts/compass_overnight_intraday_directional_bias_mnq_20260628.md`."

markets: ["MNQ"]
session: "RTH"
time_of_day: "entry 09:30, exit 15:55 (hold-to-close)"
hold_duration: "intraday full-day"

signal_type: "overnight-return fade (directional tilt on RTH open)"
indicators: ["Globex 18:00->09:30 close-open change", "gap size / ADR(20)"]
timeframes_used: ["1-second (fills)", "session-level (signal)"]

brackets: "NONE (no intraday stop; hold to 15:55)"
position_sizing: "1 MNQ contract for screen"

canonical_spec: null
implementation: "strategy_ofrt_v0.py (vault root)"
related_candidates: []

test_results:
  in_sample_n: 370
  in_sample_pnl_dollars: 15823
  in_sample_pf: 1.31
  in_sample_win_rate: 0.519
  out_of_sample_tested: false
  max_drawdown_dollars: -5839.50
  apex_50k_eod_trailing_breach: true

tags:
  - rth-only
  - intraday-full-day
  - directional-tilt
  - overnight-fade
  - no-intraday-stop
  - literature-derived
  - apex-non-deployable
---

# OFRT v0 — Overnight-Fade RTH Tilt

## 1. Thesis

Overnight (Globex 18:00 ET → 09:30 ET close-open change) positioning tends to unwind during the cash session. Enter at 09:30 open in the direction **opposite** the overnight return; exit at 15:55 (hold-to-close, no intraday stop). Variant A is the naive always-fade; Variant B applied a literature-prescribed gap-size conditioning (small fades / large continues) that turned out to be reversed for MNQ.

## 2. In-sample results (LOCKED, cost-aware)

- **Variant A (naive fade):** N=370, mean +$21.4/trade gross (+$19.6 cost-aware), t=1.76, **p≈0.078**, WR 51.9%, PF 1.31, total +$15,823 (`_worker_reports/STRATEGY_ofrt_v0_in_sample_results.md`).
- **Variant B (gap-conditioned per literature):** essentially null, mean +$2.5, p=0.88 — literature's "small fade, large continue" secondary claim is reversed for MNQ (LARGE gaps fade the strongest at 58.7% fade-hit rate).
- **Direction-of-effect regression:** slope = −0.126 (matches literature), R²=0.006, p=0.13.

## 3. Quant review verdict (2026-06-28, `_worker_reports/TASK_016_ofrt_quant_review_findings.md`)

Verbatim from §8 of that report:

> `ofrt_v0` is **not a tradeable Apex strategy as-is**. It is a real research signal worth keeping on the board because the all-day overnight-fade direction reproduces the original report and the LARGE-gap fade bucket is strongly positive in-sample. But the actual risk stats change the status materially: max daily-close drawdown is **$5,839.50 at 1 MNQ**, the Apex 50K EOD trailing simulation breaches, the distribution is highly right-skewed and top-day-dependent, and the no-stop design exposes the account to intraday adverse excursions larger than the drawdown budget.

> Single most important next step: do **not** spend OOS or promote this raw version. First build a pre-committed, risk-contained version of the same primary hypothesis, with the risk-control rule chosen before running and judged against survivability first.

## 4. Why closed for deployment

- **Max daily-close drawdown $5,839.50 at 1 MNQ** exceeds the Apex 50K EOD trailing-drawdown budget ($2,500). Simulated Apex trailing-DD **breaches** on this in-sample series.
- No intraday stop → intraday adverse excursions demonstrably exceed the drawdown budget even on days that closed positive.
- Right-skewed / top-day-dependent distribution — LARGE-gap fade bucket carries the aggregate, which is exactly the concentration profile the methodology's Pattern-9 / Section 15B screens flag as non-deployable at achieved trade count.
- Borderline p≈0.078 on the naive Variant A is in-sample-only; would not survive OOS multiplicity adjustment without materially larger effect size.

## 5. What survives as CONTEXT

- The **primary literature direction (fade overnight on MNQ)** is confirmed in-sample as directionally correct — slope negative, 53.2% fade-hit rate, LARGE-bucket fade PF 1.86.
- The **secondary literature conditioning (large gaps continue) is reversed for MNQ** — bank as a corrected sub-hypothesis for any future pre-registered test on a new market or under a risk-contained wrapper.
- The **compass artifact** (`nb_lib/strategy_specs/source_artifacts/compass_overnight_intraday_directional_bias_mnq_20260628.md`) remains a valid research input; it did its job.

## 6. What would open it back up

Per the quant-review's "single most important next step" — a new candidate spec, pre-committed BEFORE running, with:

- Explicit risk containment (stop, position-size cap, daily-loss halt) chosen upfront and judged against survivability first, not net.
- Different name (this candidate is closed; a risk-contained variant is a separate hypothesis and consumes its own trial slot).
- No use of the OFRT_v0 in-sample numbers as evidence — the effect must be re-established on a clean substrate.

## 7. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-06-28 | tested-not-deployable | Built and in-sample-tested (`strategy_ofrt_v0.py`, `_worker_reports/STRATEGY_ofrt_v0_in_sample_results.md`). Variant A marginal (p≈0.078); Variant B null. |
| 2026-06-28 | tested-not-deployable | Snapshot-rendered for visual review (`_worker_reports/TASK_015_ofrt_snapshots_findings.md`); 6 trades × 1m/5m/30m. |
| 2026-06-28 | tested-informational-rejected | Quant review (`_worker_reports/TASK_016_ofrt_quant_review_findings.md`) declared raw form "not a tradeable Apex strategy as-is" — Apex EOD trailing-DD breaches at 1 MNQ. |
| 2026-07-02 | tested-informational-rejected | Candidate spec banked (this file) mirroring the quant-review verdict. |
