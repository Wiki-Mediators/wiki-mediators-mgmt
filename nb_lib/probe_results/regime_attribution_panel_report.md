# Regime Attribution Panel Report

## Declaration Header - Written Before Aggregate Scoring

Created: 2026-07-05T22:54:46
OOS cutoff: trades dated 2026-02-01 or later excluded before scoring.
Included strategies: 22
Axis state count per strategy: 11
Declared cell count: 242
Correction: Benjamini-Hochberg FDR across declared cells; cells with n<5 receive p_raw=1.0
P-value method: deterministic sign-flip Monte Carlo, seed=20260706, one-sided mean>0
Survivor bar: n>=30, net_pnl>0, PF>=1.20, pnl_excluding_top_trade>0, fdr_q<=0.05

### Included Strategies

- `orws_v2_base_hit` (opening_range): 178 deduped in-sample trades from 12 file(s).
  - Note: First-target ORWS family; closure has predicate/R1 caveats in prior notes.
- `orws_original` (opening_range): 178 deduped in-sample trades from 12 file(s).
  - Note: Original ORWS marginal-registry multistart; predicate-loose closure caution.
- `opening_range_response_tree` (opening_range): 121 deduped in-sample trades from 12 file(s).
- `opening_range_failure_continuation_long` (opening_range): 38 deduped in-sample trades from 12 file(s).
- `objective_level_liquidity_sweep_reversal_family` (level_response): 185 deduped in-sample trades from 12 file(s).
- `candidate_a_level_response` (level_response): 252 deduped in-sample trades from 1 file(s).
- `liquidity_zone_rejection_router` (level_response): 575 deduped in-sample trades from 1 file(s).
- `candidate_c5_loose_vwap_sneaky_level` (level_response): 515 deduped in-sample trades from 1 file(s).
- `vwap_zscore_mean_reversion_fade` (mean_reversion): 950 deduped in-sample trades from 1 file(s).
- `candidate_c2_context_baseline` (mean_reversion): 515 deduped in-sample trades from 1 file(s).
- `candidate_c3_htf_vwap_reclaim` (mean_reversion): 48 deduped in-sample trades from 1 file(s).
- `first_hour_momentum_acceptance` (momentum): 150 deduped in-sample trades from 1 file(s).
- `noise_area_intraday_momentum` (momentum): 302 deduped in-sample trades from 1 file(s).
- `market_intraday_momentum_close_auction` (momentum): 379 deduped in-sample trades from 1 file(s).
- `candidate_f_late_day_momentum` (momentum): 40 deduped in-sample trades from 1 file(s).
- `candidate_d_regime_time_mtf_pullback` (momentum): 128 deduped in-sample trades from 1 file(s).
- `mgmt_v2a_immediate_be_trail` (management_policy): 40 deduped in-sample trades from 1 file(s).
- `mgmt_v2a_regime_delay_be_trail` (management_policy): 40 deduped in-sample trades from 1 file(s).
- `mgmt_v4d_immediate_be_only` (management_policy): 40 deduped in-sample trades from 1 file(s).
- `mgmt_v4_regime_delay_be_only` (management_policy): 40 deduped in-sample trades from 1 file(s).
- `mgmt_g2_original_no_be_3c` (management_policy): 118 deduped in-sample trades from 1 file(s).
- `mgmt_g2_progress_protection_3c` (management_policy): 118 deduped in-sample trades from 1 file(s).

### State Axes

- `prior_trend_state`: TREND_UP, TREND_DOWN, ROTATIONAL
- `prior_vol_state`: HIGH_VOL, LOW_VOL
- `entry_time_bucket`: open_0930_1030, mid_1030_1400, late_1400_1600
- `direction_vs_prior_trend`: with_prior_trend, against_prior_trend, rotational_or_unknown

Aggregate scoring has not yet been written above this line.

## Whole-Panel Results

Headline: **MIXED: POSITIVE CELLS EXIST, NONE SURVIVE FDR**
Tagged in-sample trades: 4950
Cells scored: 242
Cells surviving corrected panel screen: 0

Outputs:
- `nb_lib/probe_results/regime_attribution_panel_tagged_trades.csv`
- `nb_lib/probe_results/regime_attribution_panel_cells.csv`
- `nb_lib/probe_results/regime_attribution_panel_summary.json`

## Corrected Survivors

No cells survived the pre-committed corrected panel screen.

## Positive Cells That Did Not Survive Correction

- `mgmt_v2a_regime_delay_be_trail` / `entry_time_bucket=late_1400_1600`: n=40, net=$9,172.50, PF=2.18, mean=$229.31, raw_p=0.0490, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `noise_area_intraday_momentum` / `prior_vol_state=LOW_VOL`: n=190, net=$7,725.00, PF=1.20, mean=$40.66, raw_p=0.2064, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `mgmt_g2_original_no_be_3c` / `entry_time_bucket=mid_1030_1400`: n=118, net=$7,705.20, PF=1.53, mean=$65.30, raw_p=0.0880, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `mgmt_g2_original_no_be_3c` / `direction_vs_prior_trend=rotational_or_unknown`: n=77, net=$6,253.80, PF=1.67, mean=$81.22, raw_p=0.1019, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `mgmt_g2_original_no_be_3c` / `prior_vol_state=HIGH_VOL`: n=33, net=$5,894.70, PF=2.51, mean=$178.63, raw_p=0.0825, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `mgmt_g2_original_no_be_3c` / `prior_trend_state=ROTATIONAL`: n=74, net=$5,777.10, PF=1.64, mean=$78.07, raw_p=0.1054, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `orws_original` / `entry_time_bucket=open_0930_1030`: n=164, net=$5,410.60, PF=1.25, mean=$32.99, raw_p=0.1214, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `orws_original` / `prior_trend_state=TREND_UP`: n=59, net=$5,141.10, PF=1.81, mean=$87.14, raw_p=0.0410, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `orws_original` / `direction_vs_prior_trend=against_prior_trend`: n=32, net=$4,161.90, PF=2.16, mean=$130.06, raw_p=0.0455, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `mgmt_v2a_immediate_be_trail` / `entry_time_bucket=late_1400_1600`: n=40, net=$4,095.00, PF=1.69, mean=$102.38, raw_p=0.1669, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `first_hour_momentum_acceptance` / `entry_time_bucket=mid_1030_1400`: n=150, net=$4,024.50, PF=1.24, mean=$26.83, raw_p=0.1059, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `first_hour_momentum_acceptance` / `prior_vol_state=LOW_VOL`: n=107, net=$3,964.80, PF=1.34, mean=$37.05, raw_p=0.0775, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `orws_original` / `prior_vol_state=HIGH_VOL`: n=40, net=$3,954.10, PF=1.86, mean=$98.85, raw_p=0.0675, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `mgmt_g2_progress_protection_3c` / `entry_time_bucket=mid_1030_1400`: n=118, net=$3,950.70, PF=1.49, mean=$33.48, raw_p=0.0465, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `orws_original` / `direction_vs_prior_trend=with_prior_trend`: n=51, net=$2,648.80, PF=1.49, mean=$51.94, raw_p=0.1419, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `first_hour_momentum_acceptance` / `prior_trend_state=ROTATIONAL`: n=93, net=$2,624.70, PF=1.25, mean=$28.22, raw_p=0.1429, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `mgmt_g2_progress_protection_3c` / `prior_vol_state=HIGH_VOL`: n=33, net=$2,560.20, PF=2.10, mean=$77.58, raw_p=0.0450, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `candidate_c5_loose_vwap_sneaky_level` / `prior_trend_state=TREND_DOWN`: n=62, net=$2,482.80, PF=1.48, mean=$40.05, raw_p=0.1159, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `candidate_c2_context_baseline` / `prior_trend_state=TREND_DOWN`: n=62, net=$2,482.80, PF=1.48, mean=$40.05, raw_p=0.1384, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- `first_hour_momentum_acceptance` / `direction_vs_prior_trend=rotational_or_unknown`: n=94, net=$2,435.10, PF=1.23, mean=$25.91, raw_p=0.1734, q=1.0000, interpretation=POSITIVE_BUT_NOT_SIGNIFICANT_AFTER_FDR.
- Additional positive-but-not-surviving cells omitted here; see `nb_lib/probe_results/regime_attribution_panel_cells.csv`.

## Management-Divergence Read

No management-policy regime cell survived the corrected panel screen. This run does not provide a regime-composition explanation for the v2a/V4/G2 divergence.

## Per-Strategy Snapshot

| Strategy | Family | Trades | Net PnL | PF | Win Rate |
|---|---:|---:|---:|---:|---:|
| `candidate_a_level_response` | level_response | 252 | $165.00 | 1.02 | 38.9% |
| `candidate_c2_context_baseline` | mean_reversion | 515 | $-6,730.50 | 0.86 | 75.3% |
| `candidate_c3_htf_vwap_reclaim` | mean_reversion | 48 | $-2,089.80 | 0.61 | 72.9% |
| `candidate_c5_loose_vwap_sneaky_level` | level_response | 515 | $-6,730.50 | 0.86 | 75.3% |
| `candidate_d_regime_time_mtf_pullback` | momentum | 128 | $-455.75 | 0.93 | 34.4% |
| `candidate_f_late_day_momentum` | momentum | 40 | $-264.50 | 0.87 | 42.5% |
| `first_hour_momentum_acceptance` | momentum | 150 | $4,024.50 | 1.24 | 39.3% |
| `liquidity_zone_rejection_router` | level_response | 575 | $-4,667.00 | 0.73 | 53.6% |
| `market_intraday_momentum_close_auction` | momentum | 379 | $-3,718.00 | 0.77 | 45.9% |
| `mgmt_g2_original_no_be_3c` | management_policy | 118 | $7,705.20 | 1.53 | 22.9% |
| `mgmt_g2_progress_protection_3c` | management_policy | 118 | $3,950.70 | 1.49 | 32.2% |
| `mgmt_v2a_immediate_be_trail` | management_policy | 40 | $4,095.00 | 1.69 | 25.0% |
| `mgmt_v2a_regime_delay_be_trail` | management_policy | 40 | $9,172.50 | 2.18 | 45.0% |
| `mgmt_v4_regime_delay_be_only` | management_policy | 40 | $5,490.00 | 1.65 | 10.0% |
| `mgmt_v4d_immediate_be_only` | management_policy | 40 | $-3,975.00 | 0.38 | 2.5% |
| `noise_area_intraday_momentum` | momentum | 302 | $-467.70 | 0.99 | 32.5% |
| `objective_level_liquidity_sweep_reversal_family` | level_response | 185 | $-7,692.10 | 0.79 | 33.0% |
| `opening_range_failure_continuation_long` | opening_range | 38 | $-4,964.40 | 0.36 | 31.6% |
| `opening_range_response_tree` | opening_range | 121 | $-8,519.00 | 0.59 | 38.8% |
| `orws_original` | opening_range | 178 | $6,330.80 | 1.28 | 54.5% |
| `orws_v2_base_hit` | opening_range | 178 | $-638.00 | 0.95 | 55.6% |
| `vwap_zscore_mean_reversion_fade` | mean_reversion | 950 | $-16,722.00 | 0.81 | 23.9% |

## Notes And Caveats

- OOS was not touched for scoring; all trades dated 2026-02-01 or later were excluded before aggregation.
- State labels use the existing causal `h4_daily_classifier.csv` prior-day trend/vol labels plus entry-time fields from the trade logs.
- `entry_time_bucket` and `direction_vs_prior_trend` are simple v1 axes; they are not a Markov model.
- This diagnostic does not validate, promote, or revive any candidate. A survivor is only a recommendation to write a fresh conditional-candidate spec.
- ORWS-family rows retain prior predicate/R1 caveats; this panel does not repair predicate-loose closure evidence.
