# Source Artifacts

Raw operator-provided research artifacts archived for traceability. These
files are source material, not project verdicts. Working summaries and
local MNQ results remain in the strategy specs and methodology files.

## 2026-06-21 Compass Artifacts

- `compass_formula_level_menu_intraday_mnq_momentum_20260621.md`:
  formula-level menu for robustness, bracket math, bootstrap checks,
  concentration diagnostics, and first-passage framing. Used by the
  first-hour momentum acceptance robustness pass.
- `compass_carr_lopez_de_prado_reference_list_20260621.md`: citation
  hygiene and reference list for Carr-Lopez de Prado optimal trading
  rules, OU corridor work, stop-loss evidence, volatility management,
  Deflated Sharpe, and PBO.
- `compass_five_frequency_adequate_mnq_candidates_20260621.md`:
  external design menu for five frequency-adequate, cost-aware MNQ RTH
  intraday candidates. Used as source material for the first
  noise-area intraday momentum implementation.
- `compass_mechanism_class_screening_protocol_20260621.md`:
  five-axis pre-build report card for new intraday futures mechanism
  classes: skew/MinTRL, cost-distance, frequency-power,
  regime-concentration, and cross-correlation. Local executable helpers
  live in `nb_lib/screening.py`.

## 2026-06-22 Compass Artifacts

- `compass_order_flow_microstructure_nq_mnq_20260622.md`:
  order-flow and microstructure research map for NQ/MNQ. Key local
  implication: current OHLCV data is not enough for OFI/CVD/queue
  imbalance work; any build starts with a Databento cost/availability
  preflight for MBP/trades data, then a feature-pipeline screen before
  a strategy build.
- `compass_futures_prop_firm_deployment_let_it_breathe_20260622.md`:
  external futures prop-firm deployment guide for an MNQ
  let-it-breathe strategy profile. Covers Apex, Take Profit Trader,
  Lucid, TradeDay, Alpha Futures, Topstep, MyFundedFutures, and related
  drawdown/account-stage traps. Date-sensitive source material; verify
  live firm rules before any purchase or deployment decision.
- `compass_intraday_trend_continuation_mnq_candidate_menu_20260622.md`:
  external candidate menu for MNQ intraday trend-continuation on
  5/10/30-minute bars. Key local implication: naive continuous 5-minute
  trend following is a poor default; the most buildable contender is a
  regime/time-gated multi-timeframe pullback-resumption screen
  candidate, not a full strategy build yet.
- `compass_market_intraday_momentum_mnq_candidate_20260622.md`:
  external market-intraday-momentum research note for MNQ. Key local
  implication: the clean build is a once-daily, parameter-locked
  close-window momentum candidate using prior-close-to-10:00 return as
  direction, entry at 15:30 ET, flat by 15:58:30 ET, no stop, and
  conditioning variables recorded as labels rather than gates.
- `compass_no_target_no_trade_targetability_gate_mnq_20260622.md`:
  external targetability-gate research note for MNQ. Key local
  implication: "no target, no trade" is a lookahead-safe filter over
  existing entries, not an alpha source. Valid targets must be known at
  or before entry, reachable under current volatility/time remaining,
  and large enough relative to structural invalidation and costs.

## 2026-06-23 Opus Artifacts

- `opus_directional_bias_atlas_guardrails_20260623.md`: discussion note
  for a descriptive MNQ directional-bias atlas. Key local implication:
  before building another clever entry, map unconditional and
  state-conditioned RTH drift while guarding against the beta trap
  (overnight vs intraday decomposition, net-of-baseline returns) and
  the multiple-comparisons trap (Bonferroni/FDR, whole-panel read).
