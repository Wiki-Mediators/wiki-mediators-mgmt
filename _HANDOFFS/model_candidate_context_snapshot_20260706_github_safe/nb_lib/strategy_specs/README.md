# nb_lib strategy specs

Strategy specs for nb_lib-native strategies. Each spec is the
authoritative description of the strategy; implementations under
`nb_lib/scripts/` build against the spec.

When a spec lives here, it is treated as the canonical record for the
strategy. The project-root copy at `C:/VMShare/NT8lab/<name>_spec_FINAL.md`
is the working / review copy; this directory holds the in-tree
companion that ships alongside the implementation. The two should be
kept identical for a given strategy version.

## Directory structure

- `_METHODOLOGY_INTUITION.md` -- connective-tissue reference explaining
  why the gates, registry, and composition-node category exist. Read
  this before adding new methodology artifacts or bypassing gates.
- `_REGIME_CONDITIONED_MANAGEMENT_WORKFLOW.md` -- workflow for reusable
  management routers: causal realized-volatility regime first,
  HMM/Markov deferred, and overlay validation instead of standalone P&L.
- `_MANAGEMENT_OBSERVER_MEMORY_LAYER.md` -- active management-system
  pivot: observer-first trade-path diagnosis, falsifiable predictions,
  counterfactual replay scoring, poor-entry triage, and a queryable
  management memory store.
- `_EXTERNAL_METHOD_REFERENCES.md` -- verified external-method reference
  index for management geometry, synthetic-path threshold work, stop
  policy evidence, volatility management, and overfit discipline.
  Citation context only; local `nb_lib` results remain authoritative.
- `canonical/` -- specs for strategies positioned as canonical baselines
  in the validated fleet.
- `composition_nodes/` -- non-entry conditioning artifacts such as
  regime filters, direction gates, confidence scalers, and future
  strategy routers. These do not produce trades directly; they are
  validated by overlay experiments against existing entry strategies.
- `candidates/` -- ideation and lifecycle records. Tested strategies
  mirror into `canonical/` while keeping their candidate history.

## Current contents

- `canonical/noise_brk_canonical_alpha.md` -- noise-band breakout at
  9:36 ET (ADR(20) * 0.25 anchored to RTH open). Implementation:
  `nb_lib/scripts/noise_brk_canonical_alpha.py`.
- `canonical/prj3_canonical_alpha.md` -- fractal-pullback strategy
  (9:30-10:00 trend establishment + 11-bar fractal swing detection;
  10:00-12:00 asymmetric proximity wait + single-bar confirmation;
  T+2-second entry). Mixed bar resolution: SECOND bars for trend and
  execution, MINUTE bars for fractal and pullback. Implementation:
  `nb_lib/scripts/prj3_canonical_alpha.py`. Post-lookahead-fix result:
  tested-rejected.
- `canonical/g2_canonical_alpha.md` -- legacy active-fleet G2 bridge:
  non-calendar long-only continuation runner. Requires first-half-hour
  RTH return > 31.83 points, enters after 10:30 ET, uses one 25-point
  stop and EOD flat. Implementation:
  `nb_lib/scripts/g2_canonical_alpha.py`. The 2026-05-27 nb_lib bridge
  rerun reproduced the per-trade empirical canonical exactly:
  n=118, +$38,766.30 at 15c, PF 1.53, but stored 89 off-tick stop
  exits. Engine-integrity fix 2026-06-16 consolidated bridge P&L through
  conservative tick-rounded `compute_realistic_pnl()`: corrected rerun
  n=118, +$38,526.00 at 15c, PF 1.53, 0 off-tick exits. See
  `_MANAGEMENT_OBSERVER_MEMORY_LAYER.md` Section 1B.
- `canonical/savor_wilson_v2a_canonical_alpha.md` -- legacy active-fleet
  v2a bridge: long-only FOMC/NFP/OPEX catalyst-day strategy with fixed
  stop, BE at +6pt, and swing-low trail after +20pt MFE.
  Implementation: `nb_lib/scripts/v2a_canonical_alpha.py`. The
  2026-05-27 nb_lib bridge rerun reproduced the per-trade empirical
  canonical exactly: n=40, +$4,239.00, PF 1.73, but stored 40 off-tick
  stop-class exits. Engine-integrity fix 2026-06-16 consolidated bridge
  P&L through conservative tick-rounded `compute_realistic_pnl()`:
  corrected rerun n=40, +$4,095.00, PF 1.69, 0 off-tick exits. See
  `_MANAGEMENT_OBSERVER_MEMORY_LAYER.md` Section 1B.
- `canonical/ema_trend_canonical_alpha.md` -- EMA-slope mid-morning
  trend strategy (20-period EMA on 5-minute closes; signal at
  11:10:00 ET when slope and price agree). Mixed bar resolution:
  5-MINUTE bars for EMA, SECOND bars for execution. Implementation:
  `nb_lib/scripts/ema_trend_canonical_alpha.py`. Lookahead-free clean
  rebuild of a legacy direction mode that previously lived in
  `engine_ib.py`; runtime assertions enforce that the EMA never
  references data after the 11:10 signal time. In-sample window
  2024-08-01 -> 2026-01-31; OOS 2026-02-01 -> 2026-05-04 reserved.
