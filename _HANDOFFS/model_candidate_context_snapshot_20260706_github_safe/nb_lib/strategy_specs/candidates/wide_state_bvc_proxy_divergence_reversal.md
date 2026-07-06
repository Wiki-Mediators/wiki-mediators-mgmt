---
name: "Wide-State BVC-Proxy Divergence Reversal"
tagline: "Cheap proxy test for wide-state order-flow divergence using OHLCV-derived BVC delta."
status: "tested-informational-rejected"
created: 2026-05-20
updated: 2026-05-20
source: "Operator direction 2026-05-20; proxy precursor to wide_state_delta_divergence_reversal because current data is OHLCV-only."

markets: ["MNQ"]
session: "RTH"
time_of_day: "09:30-12:00 ET"
hold_duration: "intraday"

signal_type: "mean-reversion"
indicators: ["SMA(20) 2-min", "SMA(200) 2-min", "ATR(14) 2-min", "BVC proxy delta", "proxy delta ratio"]
timeframes_used: ["1-second source", "2-minute derived"]

brackets: "structure anchored for R4; targets deferred"
position_sizing: "fixed-risk-dollar"

canonical_spec: "../canonical/wide_state_bvc_proxy_divergence_reversal_spec_FINAL.md"
implementation: "../../scripts/wide_state_bvc_proxy_divergence_reversal_canonical_alpha.py"
related_candidates:
  - "wide_state_delta_divergence_reversal"
  - "wide_opening_window_reversal_long"
  - "wide_opening_window_reversal_short"
  - "footprint_orderflow_reference"

test_results:
  in_sample_n: 279
  in_sample_pnl_dollars: -18261.50
  in_sample_pf: 0.61
  in_sample_win_rate: null
  out_of_sample_tested: false
  out_of_sample_n: null
  out_of_sample_pnl_dollars: null
  out_of_sample_pf: null
  multistart_pass_rate: "0/12 active; 12/12 failed"

admissibility:
  r2_apex_survival:
    risk_dollars_per_trade: null
    expected_stop_distance_pts_range: null
    expected_loss_dollars_per_trade: null
    worst_plausible_cluster_n: null
    worst_plausible_cluster_dollars: null
    cluster_vs_floor_ratio: null
    favorable_first_week_independent: null
    r2_variance_probe_version: null
    r2_variance_probe_script: null
    r2_variance_probe_output: null
    r2_variance_pf_simulated: null
    r2_variance_win_rate: null
    r2_variance_max_consecutive_losses: null
    r2_variance_max_running_drawdown_dollars: null
    r2_variance_trailing_dd_breach: null
    r2_variance_verdict: null
  r4_signal_frequency:
    probe_convention_version: "v1.2"
    probe_script: "nb_lib/scripts/probe_r4_wide_state_bvc_proxy_divergence_reversal.py"
    probe_output: "nb_lib/probe_results/wide_state_bvc_proxy_divergence_reversal_r4_probe.json"
    probe_window_start: "2024-09-09"
    probe_window_end: "2024-10-04"
    probe_n_signals_observed: 89
    probe_signals_passing_fill_guards: 63
    probe_attrition_rate: 0.2921
    probe_p95_drift_pts: 34.1
    probe_low_confidence_attrition: false
    probe_n_long: 44
    probe_n_short: 45
    probe_distinct_days_with_signal: 18
    expected_signals_per_60_trading_days: [99, 398]
    sparsity_class: "dense"
    sparsity_class_rationale: "63 passing signals over 19 trading days; dense but below round-number overtrading red flag."

tags:
  - rth-only
  - intraday
  - mean-reversion
  - bvc-proxy
  - order-flow-proxy
  - not-real-delta
  - template-v2
---

# Wide-State BVC-Proxy Divergence Reversal

## 0. Admissibility summary

- **R1 (edge thesis)**: This candidate is a cheap proxy for the real order-flow idea in `wide_state_delta_divergence_reversal`. The thesis is that wide-state price extensions become more fadeable when price makes a new extreme without confirming estimated aggressive participation.
- **R2 (Apex survival)**: Not yet admissibility-complete. This entry is intentionally stopped at the R4 proxy-frequency question before any FINAL spec or P&L work.
- **R3 (management lifecycle)**: No adaptive management is specified. Any later spec would choose stops, targets, and lifecycle behavior only after proxy R4 is reviewed.
- **R4 (signal frequency)**: R4 v1.2 probe on 2024-09-09 through 2024-10-04 fired 89 structural BVC-proxy signals, with 63 passing fill guards across 18 signal days. Long/short split was balanced at 44/45. Sparsity class is dense, not sparse; extrapolated 60-day range is [99, 398].
- **R5 (direction handling)**: Two-sided by design: short in wide-upside exhaustion and long in wide-downside exhaustion. Any direction asymmetry in proxy signals is diagnostic, not a permission slip for post-result direction filtering.

## 1. Thesis

This is a **BVC-PROXY** of an order-flow mechanism, not a real-delta strategy.

The real candidate, `wide_state_delta_divergence_reversal`, requires aggressor-side tick data. The current project store is MNQ 1-second OHLCV, which cannot reconstruct measured bid/ask aggressor volume. This proxy candidate substitutes Bulk Volume Classification (BVC) estimated delta for real footprint delta so the project can run a cheap first look before buying or building true tick-footprint infrastructure.

Mechanism hypothesis: when SMA20 and SMA200 are far apart, price is already in a wide state. If price pushes to a fresh extreme but BVC proxy delta fails to confirm, the extension may be losing participation and may reverse toward the SMA cluster.

Counter-hypothesis: BVC is only a model of buy/sell pressure inferred from bar returns. In fast or choppy MNQ conditions it may identify price-shape artifacts rather than true aggressive-flow divergence.

**PROXY RESULT INTERPRETATION:** positive equals "worth acquiring real tick data to test properly"; negative is ambiguous because it may mean the mechanism is bad or the BVC proxy is a poor approximation of real delta.

## 2. Mechanism

- Wide SMA separation marks expanded state where the price-only wide reversal family tried, and failed, to fade extension.
- New price extreme marks the moment a continuation trader might chase.
- BVC proxy delta estimates whether the new extreme is supported by inferred buy/sell pressure.
- Divergence means the price extreme is not confirmed by proxy delta: lower proxy delta on a higher high, higher proxy delta on a lower low, or an outright sign flip against the price extreme.
- Break of the divergence bar defines the reversal attempt.

## 3. Signal logic

**Pre-committed R4 proxy predicates:**

- Build 2-minute bars from MNQ 1-second OHLCV.
- Compute SMA20, SMA200, and ATR14 on 2-minute bars.
- Compute BVC proxy delta on 2-minute bars:
  - `return = close - previous_close`
  - `sigma = rolling_std(return, 20 bars)`
  - `buy_fraction = normal_cdf(return / sigma)`
  - `proxy_delta = volume * (2 * buy_fraction - 1)`
- Scan completed 2-minute bars from 09:30 through 12:00 ET.
- Wide-upside short setup:
  - `SMA20 > SMA200`
  - `abs(SMA20 - SMA200) / ATR14 >= 1.00`
  - `close - SMA20 >= 0.50 * ATR14`
  - current high is a new high versus prior 5 completed 2-minute bars
  - proxy delta is below the prior 5-bar proxy-delta high, or proxy delta is negative
  - reversal entry reference is divergence-bar low minus one MNQ tick
- Wide-downside long setup:
  - `SMA20 < SMA200`
  - `abs(SMA20 - SMA200) / ATR14 >= 1.00`
  - `SMA20 - close >= 0.50 * ATR14`
  - current low is a new low versus prior 5 completed 2-minute bars
  - proxy delta is above the prior 5-bar proxy-delta low, or proxy delta is positive
  - reversal entry reference is divergence-bar high plus one MNQ tick

The R4 probe counts these signals only. It does not measure P&L, commission, slippage, management, or Apex outcome.

## 4. Exit logic

No FINAL exit logic is specified. The R4 probe uses structural stop anchors and generic fill-geometry guards only:

- Long stop anchor: divergence-bar low minus one tick.
- Short stop anchor: divergence-bar high plus one tick.
- Entry reference: break of divergence bar in reversal direction.

Any later FINAL spec must choose targets, time exits, and management before P&L testing.

## 5. Position sizing and Apex survival rationale

Not yet admissibility-complete. This candidate exists to answer R4 first: does BVC-proxy divergence occur often enough to justify further work?

If R4 is promising, a separate Phase 0 pass must quantify fixed-risk-dollar sizing, expected stop distance, and plausible cluster loss. The failed price-only wide reversal family is the closest negative reference, so any Apex survival thesis must explain why proxy-divergence filtering changes the loss-distribution shape rather than merely reducing signal count.

## 6. Required indicators / data

This candidate uses **OHLCV-derived BVC proxy delta, not real tick delta**.

Required:

- MNQ 1-second OHLCV from the Databento store.
- Derived 2-minute OHLCV bars.
- SMA20, SMA200, ATR14 on 2-minute bars.
- BVC proxy delta computed from standardized 2-minute close-to-close changes and total 2-minute volume.

Interpretation limits:

- BVC estimates buy/sell volume from price change; it does not observe aggressor side.
- BVC assumes price change reflects net aggressive pressure.
- The assumption degrades in fast, thin, or choppy conditions.
- A positive BVC-proxy result does not validate footprint order-flow divergence.
- A negative BVC-proxy result does not conclusively reject real delta divergence.

## 7. Differentiation

Versus `wide_opening_window_reversal_long` and `wide_opening_window_reversal_short`: this candidate adds proxy-divergence confirmation to the price-only wide-state reversal. The price-only family failed hard: aggregate `-$14,054.50`, PF `0.75`, and 11/12 failed starts in the informational multistart. This candidate tests whether a participation-disagreement gate would have reduced blind fading.

Versus `wide_state_delta_divergence_reversal`: this candidate is not the real order-flow strategy. It is a cheap precursor using BVC estimated delta because current project data lacks aggressor-side classification. The real-delta entry remains `untested-ideation` and data-acquisition-required.

## 8. Required research before spec drafting

- Review R4 proxy-frequency result.
- If R4 is not sparse, decide whether proxy evidence is strong enough to justify real tick-data acquisition.
- If real tick data is acquired, compare true delta divergence against BVC proxy divergence before any deployability conclusion.
- If proceeding with proxy only, write a separate methodology caveat explaining why proxy-derived participation is acceptable for a non-footprint strategy.

## 9. Source / references

Source is operator order-flow/footprint video synthesis on 2026-05-20 plus the failed price-only wide reversal family report. BVC is used here in the Easley, Lopez de Prado, and O'Hara sense: a bulk-volume model that estimates buy/sell pressure from standardized bar returns when transaction-level aggressor labels are unavailable.

This entry makes no claim that BVC is measured order flow.

## 10. Status history

| Date | Status | Notes |
|---|---|---|
| 2026-05-20 | `untested-ideation` | Proxy wiki entry authored separately from real-delta candidate. R4 BVC-proxy probe pending. Positive proxy result can only justify real tick-data acquisition; negative proxy result remains ambiguous. |
| 2026-05-20 | `r4-proxy-probed` | R4 v1.2 BVC-proxy probe completed with strict `sigma.shift(1)` convention: 89 fired, 63 passing fill guards, dense sparsity, balanced 44 long / 45 short. Strict normalization did not materially change the prior run. |
| 2026-05-20 | `tested-informational-rejected` | FINAL proxy spec drafted at `../canonical/wide_state_bvc_proxy_divergence_reversal_spec_FINAL.md`; implementation at `../../scripts/wide_state_bvc_proxy_divergence_reversal_canonical_alpha.py`; report at `../../../nb_lib_wide_state_bvc_proxy_divergence_reversal_multistart_informational_report.md`. Result: 279 trades, $-18,261.50, PF 0.61, 12/12 failed. Worse survival than price-only baseline (11/12 failed). Does not validate or reject real delta. |
