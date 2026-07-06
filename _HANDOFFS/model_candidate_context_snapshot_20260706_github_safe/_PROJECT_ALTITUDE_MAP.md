# Project Altitude Map

**Status**: living orientation note  
**Created**: 2026-05-27  
**Purpose**: preserve the broad project narrative so future agents do not
tunnel into one probe, one strategy, or one historical fleet framing.

General research-with-agents patterns: see `_FRAMEWORK/PATTERNS.md`.

## 1. Top-Level Thesis

The project is no longer only a search for a standalone MNQ entry edge.
The durable thesis is:

```text
Entry edges are thin, unstable, and often disappear under realistic
execution. The stronger remaining opportunity is management structure:
how risk is sized, de-risked, protected, and interpreted after entry.
```

Second durable ground truth:

```text
Apex is a deployment vehicle, not the definition of strategy edge.
A rule can be edge-positive in cash-account terms while still needing
drawdown containment before Apex deployment.
```

This does not mean entry research stops. It means entry candidates are
now treated as trade-producing substrates for a larger management and
composition system unless they independently clear the full methodology
pipeline.

## Current state — 2026-06-24

**Mechanism-free intraday-bias hypothesis: CLOSED for this window.** The
directional bias atlas (TASK_001, composition node) read
`pure_beta_no_intraday_edge`: intraday 09:30→16:00 is flat (mean −2.07 pt,
p=0.86), the long tilt is overnight beta (+18.3 pt, marginal), and zero of
39 cells survive Bonferroni/BH-FDR. There is no latent intraday drift for
a cleverer trigger to capture — the last escape hatch on the MNQ-OHLCV
thread is shut.

**All three live-capital integrity questions on the deployed `noise_brk`
edge: CLOSED on ground truth** (see
`_worker_reports/INTEGRITY_SWEEP_FINDINGS_2026-06-24.md`). Concentration
benign; ATR period research-14 vs live-20, period-robust; ATR causality
confirmed (no look-ahead). The live money is sound.

**The fork (open, parked by choice):** (a) declare the negative result
the deliverable and stop; (b) point the transferable tooling at a
less-efficient market; (c) relax "no new data" now that exhaustion is
proven. Option (d) "build the dumbest expression of a broad intraday
bias" is CLOSED — the atlas found no broad excess bias to express. The
fork is deliberately deferred while a Git-backed wiki infrastructure
(see `_FRAMEWORK/LAYER_ARCHITECTURE.md`) is built, with this project as
the test-bed for a reusable system. The research fork remains the next
real decision whenever attention returns to trading.

Layer 2 (the dumb logger) is built and running; Layers 3 (deriver) and
4 (distiller) are parked future work, triggered by accumulated material
rather than elapsed time — see `_FRAMEWORK/LAYER_ARCHITECTURE.md` §8
"When to build Layers 3 and 4" for the per-layer "earns its keep when"
conditions.

Eight MNQ-RTH-OHLCV probes (PROBE_001-008) + wick diagnostic (PROBE_007) +
one in-sample strategy build (CFLR_v0) complete. Five flat, two real-but-
structural (clustering, level-sharpening), one small-N borderline candidate
banked as `nb_lib/strategy_specs/candidates/prior_session_level_fade_aged.md`
(`status: candidate-validated-in-principle-unconfirmed`).

**Data-integrity correction (2026-06-26 / TASK_014):** PROBE_006's original
report claimed "naturally in-sample" but 14 of its 62 touches were OOS.
Strict in-sample is **N=48, mean +4.15 pts, PF 1.87, one-sample p ≈ 0.048 vs
zero** — right at the 5% line, not the originally-reported 0.003. The
candidate is **borderline-significant** and its OOS seal is **partially
compromised** for this specific slice (14 touches already seen). Read the
spec's §3a before citing any numbers. Active next move (Option b) is now
clearly preferred over Option (a) one-shot OOS spend; the transferable
*concept* (level-attention + aged-fade + the CFLR confirmation filter as a
pre-registered hypothesis) carries to a less-efficient / higher-frequency
market, where it would fire hundreds of times instead of 48.

**Conversation archive track (2026-07-02):** created the separate local-only
archive repo `C:\VMShare\conversation_archive` and completed the one-shot
rescue of Claude Code, Codex, and Claude.ai export tape. Ongoing archive
infrastructure remains deferred with triggers booked in
`_FRAMEWORK/derived_layer_and_dumb_tool_roadmap.md`; the rationale and
deferral ledger are filed at
`_FRAMEWORK/conversation_archive_decision_record.md`.

**Research instruments (2026-07-02 inventory):** the canonical
realsim/backtest engine remains `C:\VMShare\NT8lab\prj_realsim_v2.py`;
the forward-only visual replay and snapshot data API live at
`C:\VMShare\NT8lab\tools\mnq_replay_viewer\app\server.py`; fixed
trade-review image batches are produced by
`C:\VMShare\NT8lab\tools\mnq_replay_viewer\batch_snapshot.py`; and the
pre-build mechanism-class gate is `C:\VMShare\NT8lab\nb_lib\screening.py`.
DBN-loading work should first run
`C:\VMShare\NT8lab\tools\env_check\databento_preflight.py` to catch the
workspace `databento\` namespace-shadowing trap. The replay viewer is
ready for manual replay / trade CSV inspection and 1m/5m/30m snapshots;
4h snapshots use the baseline cache but can still be expensive when
many source DBN segments are cold. Longer findings are in
`_worker_reports/TOOL_INVENTORY_2026-07-02.md`.

## 2. Current Fronts

### Front A: Deployment / Fleet Reality

The older trader-frame "3-strategy fleet" is not the current `nb_lib`
truth. On 2026-05-27 the historical PRJ_3 / G2 / v2a fleet was checked
inside the current `nb_lib` environment.

Current finding:

- PRJ_3 fails under lookahead-safe `nb_lib` and should not be counted as
  a viable current fleet leg.
- G2 survives as a positive bridge component only at reduced size.
- Savor-Wilson v2a survives as a sparse positive bridge component.
- The practical current replay substrate is the **two-strategy bridge
  fragment**: `G2 3c + v2a 15c`.

Reference:

- `nb_lib/strategy_specs/_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`
  section `1A. Viability Finding: Current nb_lib Replay Substrate`
- `nb_lib_g2_v2a_multistart_report.md`
- `prop_firm_deployment_map_2026_06.md` for a date-sensitive external
  map of prop-firm account structures. Treat it as deployment planning
  context only; verify live rules before purchase or deployment.

### Front B: Management Observer Research

The management pivot is active and has produced a banked observation:

```text
Underwater at checkpoint, especially around entry+300s, predicts worse
trade outcome across multiple historical families.
```

This is validated as an **observation**, not yet as a control policy.
The project must not jump from "diagnosis predicts outcome" to "flatten
the trade" without counterfactual scoring. TP1/BE geometry can make
above-water-at-checkpoint overlap with a locked profit floor, so action
testing must be stricter than observation testing.

First Step 3 action test now exists (2026-05-27):
`flatten_if_underwater_300s` on the current bridge substrate produced a
mild all-sample improvement (+$532.98) but failed the pre-committed
holdout (-$1,098.00 delta and worse drawdown). Blunt flattening is
therefore **not validated**. The observation remains useful; the action
does not.

Second Step 3 action test now exists (2026-05-27):
`delay_be_until_300s` on v2a produced a major same-entry P&L/PF
improvement (ALL +$4,980; HOLDOUT +$4,102.50), but with materially worse
HOLDOUT max drawdown and weak OPEX behavior. Under the two-axis verdict
frame, this is an **edge-positive geometry lead /
Apex-needs-containment** result, not a clean deployable policy. It
supports the thesis that protection timing matters more than blunt
flattening.

Third Step 3 action test now exists (2026-05-27):
`regime_conditioned_delay_be_300s` fixed the mapping before testing:
FOMC/NFP delay BE, OPEX immediate BE. On v2a it improved ALL by
+$5,077.50 and HOLDOUT by +$4,080.00 while leaving OPEX unchanged. On
the V4 BE-only lab it improved ALL by +$9,454.20 and HOLDOUT by
+$10,204.20. Under the two-axis verdict frame, this is
**edge-positive / Apex-needs-containment**: the edge axis is favorable,
while the deployability axis still needs drawdown containment before an
Apex 50K EOD vehicle can carry it.

OOS update (2026-06-20): the v0.3 OOS seal was spent on the frozen
2026-02-01 -> 2026-06-20-exclusive window. The first scoring attempt had
a procedural calendar-freeze defect, but a corrected frozen-calendar
rerun matched the quarantined values exactly. Final OOS verdict:
**OOS_EDGE_BUT_NOT_DEPLOYABLE**. B1 improved over an even worse B0, but
B1 itself was negative at every tested size (6c B1 n=10, -$477.00, PF
0.653, maxDD $1,372.80). v0.3 is not deployable on that OOS window and
must not be rescued by retuning calendar, delay, entry time, trail, cost
model, or contract size.

G2 overlay update (2026-06-20): the portable management lesson was
applied to G2 as progress-conditioned per-trade protection (BE after +1R
and 300s; trail after +2R with 1R distance). It reduced drawdown but
clipped too much of the EOD-runner edge. At 3c, P&L fell from +$7,705.20
to +$3,950.70 while maxDD improved from $1,626.00 to $1,044.90. Treat
this as an overlay-negative / runner-clipping warning, not a new
candidate policy.

O-U characterization update (2026-06-21): a pre-committed panel survey
of post-entry direction-adjusted mark-to-market paths across G2, v2a,
and seven graveyard/reference families found **NO_BROAD_STABLE_OU_PATTERN**.
0/9 included families met the OU-like screen (phi < 0.995, half-life
<= 300s, no-seam DF t-stat <= -2.9, and block stability). This blocks
treating Carr-Lopez de Prado OU threshold machinery as a generally
justified management framework for the existing MNQ family panel. A
future family-specific OU experiment would need a fresh pre-commitment
and cannot be justified by cherry-picking one cell from the panel.
Project-level read: management-as-return-source through generic
exit-timing rules is closed on these entries. Management remains open as
variance / tail / deployment-shape control; return-seeking work should
shift back toward entry quality or new substrates unless a future
pre-committed family-specific process study says otherwise.

Reference:

- `nb_lib/strategy_specs/_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`
- `nb_lib_management_step3_flatten_underwater_300s_report.md`
- `nb_lib_management_step3_delayed_be_v2a_report.md`
- `nb_lib_management_step3_regime_conditioned_be_report.md`

### Front B2: Management Geometry

The V4D/V4A geometry-dominance lead has been rebuilt fresh under
`nb_lib` as of 2026-05-27. This no longer rests only on old trade logs.

Fresh same-entry rebuild:

- V4A: 40 trades, +$4,716.30, PF 1.27, WR 27.5%
- V4D: 40 trades, -$4,239.60, PF 0.32, WR 2.5%
- Entries identical and ordered: true
- V4A - V4D delta: +$8,955.90

Interpretation: the old headline magnitude changed, but the core lesson
survived in the current engine. Management geometry can dominate the
same entry set. This should shape future Step 3 work: do not assume the
first counterfactual action should be blunt flattening. Compare action
policies against geometry-aware alternatives.

Reference:

- `nb_lib/scripts/savor_wilson_v4_geometry_nb_lib.py`
- `nb_lib_savor_wilson_v4_geometry_rebuild_report.md`

### Front C: Composition Architecture

The strategy wiki now contains more than entry candidates. It has
composition nodes and management nodes: regime routers, volatility
management routers, and observer-memory concepts.

These nodes are not standalone strategies. They are conditioning layers
validated by overlay experiments, replay, and counterfactual management
tests.

Reference:

- `nb_lib/strategy_specs/composition_nodes/`
- `nb_lib/strategy_specs/_REGIME_CONDITIONED_MANAGEMENT_WORKFLOW.md`
- `nb_lib/strategy_specs/_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`

Targetability update (2026-06-22): applying the v1
no-target/no-trade gate as an overlay on first-hour momentum did not
rescue that entry family. It cut the book from 150 trades to 12 and the
allowed subset was negative. Follow-up 5m snapshots showed the gate
behaving correctly as structural hygiene: most blocked trades were
standing directly beside a nearby objective level while risking 30
points. Banked lesson: targetability is not an edge source and should
not be used as an aftermarket rescue overlay on weak entries. It belongs
on candidates where the target is intrinsic to the thesis, such as
opening-range or prior-day-level response toward the next objective
level with invalidation at the level just respected. Screen any such
candidate first before composing the gate.

Level-response screen update (2026-06-23): the first such bare-entry
screen, prior-day/overnight break-retest continuation, produced 252
proxy trades but was rejected pre-build: +$165 net, PF 1.023, mean
+$0.65/trade, t-stat 0.151, best trade 80.3% of net, and max trade-day
Jaccard 0.663 against existing sleeves. Do not bolt targetability onto
that rejected construction as a rescue.

Directional-bias atlas note (2026-06-23): after repeated conditional
entry failures, the next genuinely different diagnostic is not another
trigger but a descriptive MNQ RTH directional-bias atlas. The atlas must
ask whether any mechanism-free directional drift exists after separating
overnight/beta drift from intraday drift and after accounting for
multiple comparisons. Read the whole panel; do not select the best cell.
Working spec:
`nb_lib/strategy_specs/composition_nodes/mnq_directional_bias_atlas.md`.

## 3. Current Strategic Posture

The project should keep three lanes alive:

1. **Viable substrates**: maintain a small set of clean, current,
   lookahead-safe trade producers for replay and management tests.
2. **Observer diagnostics**: add measurable path-state predicates and
   prove whether they add information beyond cheap baselines.
3. **Counterfactual management**: test exposure-reducing actions against
   real historical paths before allowing any control logic.

Avoid spending many sessions generating new entry strategies unless the
candidate serves one of those lanes or has a clearly new mechanism.

## 4. Current Useful Substrates

### Use

- `G2 canonical alpha at 3 contracts`
- `Savor-Wilson v2a canonical alpha at 15 contracts`
- G2/G2_BE historical trade logs for poor-entry triage research
- ORWS v2 base-hit historical trades for observer-origin diagnostics

### Use With Caution

- PRJ_3: useful as a failure/lookahead case study or historical
  diagnostic dataset, not as a current viable positive component.
- Legacy trader-frame v5: useful as historical context, not current
  `nb_lib` truth.

### Do Not Spend Without Decision

- The v0.3 policy-family OOS seal has been spent through
  2026-06-20-exclusive. Do not reuse that same window as clean OOS for a
  v0.3 rescue variant.
- Other candidate families still require explicit OOS authorization
  before touching `2026-02-01+` for results.

## 5. Open Management Questions

1. Does `checkpoint_adverse_unrealized_r` improve any exposure-reducing
   action, or is it only descriptive?
2. Does contraction / sweep / reclaim state add information beyond the
   bare underwater-at-checkpoint feature?
3. Does volatility regime change the meaning of early adverse movement?
4. Can the observer identify trades that should be left alone because
   adverse movement is only a bounded sweep inside a contraction box?
5. Given the fresh V4A/V4D same-entry result, which management geometry
   changes are actionably testable without overfit action policies?
6. For edge-positive management rules that increase drawdown, what
   containment overlay preserves return-per-risk while making the rule
   fit Apex EOD constraints?
7. For G2 specifically, can drawdown be controlled at the
   portfolio/exposure layer without clipping the per-trade EOD-runner
   payoff?

## 6. Recent Transcript Intake

The 2026-06-02 routine / mechanical trade plan transcript was captured
as process-discipline material, not as a new strategy. The useful lesson
is that preparation, execution-state checks, guardrails, journaling, and
review are part of the trading system boundary. Discretionary chart
concepts from the transcript (premium/discount, supply-demand zones,
liquidity sweep, market shift) should not enter the research pipeline
unless translated into objective predicates and tested against cheap
baselines.

Reference:

- `nb_lib/strategy_specs/_METHODOLOGY_INTUITION.md`
  section `2.7 Process discipline is part of the trading system`

The 2026-05-27 contraction / expansion / trend transcript was captured
as management-observer material, not as a fresh strategy. The useful
observable predicates are:

- `inside_contraction`
- `pre_acceptance_break`
- `sweep_against_entry`
- `reclaim_in_entry_direction`
- `accepted_against_entry`
- `expansion_in_favor`
- `expansion_against`

The project should not treat "market maker manipulation" as evidence.
Reports and code should use observable terms such as `sweep_reclaim`,
`false_break_reclaim`, and `acceptance_failure`.

Reference:

- `nb_lib/strategy_specs/_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`
  section `2A. Transcript Intake: Contraction, Liquidity Events, And
  Trade Management`

The 2026-06-30 external mean-reversion backtest video intake was
captured as context, not as a transferable MNQ finding. The source
study/video claim is daily-bar, cross-asset mean reversion; this
project is intraday MNQ with fixed per-trade friction and microstructure
effects. Disposition: the video supports process discipline and layered
framing only. Any MNQ-RTH mean-reversion idea must be converted into an
objective predicate and clear the Section 15B mechanism-class screen
before build.

Reference:

- `nb_lib/strategy_specs/source_artifacts/external_meanrev_video_intake_20260630.md`

The 2026-06-30 "sneaky pivot" transcript was captured as a candidate
seed, not as evidence. Its useful structure is objective-level response:
prior-session range high/low plus adjacent outer swing levels, a 15m
probe/rejection candle sequence, and target back toward the opposing
level. It has been distilled into a screen-required MNQ candidate,
`sneaky_pivot_15m_level_reversal.md`. Because the transcript includes
discretionary language such as "close enough," the first research step
must be a mechanical screen with fixed level tolerance, structural stop,
and targetability; do not promote it or use it as a rescue overlay before
that screen.

Reference:

- `nb_lib/strategy_specs/source_artifacts/sneaky_pivot_transcript_20260630.md`
- `nb_lib/strategy_specs/candidates/sneaky_pivot_15m_level_reversal.md`

## 7. Guardrails

- Preserve OOS. Do not touch `2026-02-01+` data for a new policy family
  without explicit OOS authorization; v0.3's OOS window is already spent
  and cannot be reused as a clean rescue surface.
- Keep gates as falsification tools, not search fitness functions.
- Compare rich diagnoses against cheap baselines before crediting them.
- Partition by day or coarser time blocks, not by correlated path
  samples.
- Treat perfect-looking cells as suspicious until checked.
- Do not revive old fleet claims without current `nb_lib` verification.

## 8. What Future Agents Should Do First

After reading the bootstrap files, read this map to understand the
current altitude:

1. Management structure is now the main research axis.
2. The viable current replay substrate is `G2 3c + v2a 15c`, not the
   old PRJ_3/G2/v2a fleet.
3. Poor-entry triage is validated as observation, not as an action.
4. New transcript ideas should become measurable observer predicates
   before becoming entry strategies.
