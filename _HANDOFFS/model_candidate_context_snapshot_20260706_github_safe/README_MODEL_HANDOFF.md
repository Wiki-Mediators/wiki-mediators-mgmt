# Model Candidate Context Snapshot - GitHub Safe

Created: 2026-07-06
Purpose: management-vault/GitHub-safe subset of the local candidate context snapshot for handing to another model.

This is a copied snapshot. The live source of truth remains the vault files at their original paths. The full local snapshot is `_HANDOFFS/model_candidate_context_snapshot_20260706/`; this folder excludes files that tripped the management bridge high-entropy scanner.

## How to read

1. Start with `_PROJECT_ALTITUDE_MAP.md`.
2. Read `nb_lib/probe_results/survivor_ledger_20260622.md` plus its CSV/JSON siblings if present.
3. For exact strategy definitions, inspect `nb_lib/strategy_specs/candidates/` and `nb_lib/strategy_specs/canonical/`.
4. For measured results, inspect `nb_lib/probe_results/`.
5. For cold reviews and narrative verdicts, inspect `_worker_reports/`.

## Included

- Bootstrap/context files
- Strategy specs and source artifacts that passed the management bridge scanner
- Probe reports/CSVs/JSONs included in the local snapshot
- Relevant worker reports included in the local snapshot

## File count

Included files: 138

## Skipped for GitHub-safe management push

The following files were present in the local snapshot but excluded from this GitHub-safe copy because the management bridge flagged high-entropy-secret risk. The scanner values are not logged here.
- `nb_lib/strategy_specs/_MANAGEMENT_OBSERVER_MEMORY_LAYER.md`
- `nb_lib/strategy_specs/canonical/ema_trend_canonical_alpha.md`
- `nb_lib/strategy_specs/canonical/noise_brk_canonical_alpha.md`
- `nb_lib/strategy_specs/canonical/opening_range_width_switch_v2_base_hit_spec_FINAL.md`
- `nb_lib/strategy_specs/canonical/prj3_canonical_alpha.md`
- `nb_lib/strategy_specs/canonical/tight_opening_window_breakout_long_spec_FINAL.md`
- `nb_lib/strategy_specs/canonical/wide_opening_window_reversal_family_spec_FINAL.md`
- `nb_lib/strategy_specs/tools/mnq_replay_viewer.md`

## Included file list

- `_PROJECT_ALTITUDE_MAP.md` (19624 bytes)
- `AGENTS.md` (11137 bytes)
- `nb_lib/strategy_specs/_EXTERNAL_METHOD_REFERENCES.md` (7144 bytes)
- `nb_lib/strategy_specs/_METHODOLOGY_INTUITION.md` (20783 bytes)
- `nb_lib/strategy_specs/_R1_EVIDENCE_DIAGNOSTIC_CONVENTION.md` (30062 bytes)
- `nb_lib/strategy_specs/_R2_VARIANCE_PROBE_CONVENTION.md` (16197 bytes)
- `nb_lib/strategy_specs/_R4_PROBE_CONVENTION.md` (23334 bytes)
- `nb_lib/strategy_specs/_REGIME_CONDITIONED_MANAGEMENT_WORKFLOW.md` (10969 bytes)
- `nb_lib/strategy_specs/_TEMPLATE_v2_admissibility_ready.md` (10821 bytes)
- `nb_lib/strategy_specs/_V1_4_EDGE_STABILITY_REGIME_GATE.md` (9307 bytes)
- `nb_lib/strategy_specs/candidates/_EXAMPLE_atr_scaled_brackets.md` (9095 bytes)
- `nb_lib/strategy_specs/candidates/_MARGINAL_STRATEGIES_REGISTRY.md` (20699 bytes)
- `nb_lib/strategy_specs/candidates/_METHODOLOGY_data_store.md` (12032 bytes)
- `nb_lib/strategy_specs/candidates/_METHODOLOGY_repertoire.md` (26686 bytes)
- `nb_lib/strategy_specs/candidates/atr_compression_squeeze_break.md` (5993 bytes)
- `nb_lib/strategy_specs/candidates/atr_percentile_trend_day_hold.md` (6487 bytes)
- `nb_lib/strategy_specs/candidates/atr_ratio_expansion_scalp.md` (5187 bytes)
- `nb_lib/strategy_specs/candidates/atr_regime_pullback_continuation.md` (6963 bytes)
- `nb_lib/strategy_specs/candidates/atr_regime_pullback_tight_target.md` (14553 bytes)
- `nb_lib/strategy_specs/candidates/c2_midmorning_targetability_mean_reversion_screen.md` (3532 bytes)
- `nb_lib/strategy_specs/candidates/candidate_f_late_day_momentum_screen.md` (4012 bytes)
- `nb_lib/strategy_specs/candidates/CANDIDATE_TEMPLATE.md` (5174 bytes)
- `nb_lib/strategy_specs/candidates/choppiness_impulse_fade.md` (18823 bytes)
- `nb_lib/strategy_specs/candidates/closing_imbalance_drift_proxy.md` (4273 bytes)
- `nb_lib/strategy_specs/candidates/developing_swing_trail_vol_cap.md` (4623 bytes)
- `nb_lib/strategy_specs/candidates/ema_trend_canonical_alpha_SUPERSEDED.md` (101 bytes)
- `nb_lib/strategy_specs/candidates/ema_vwap_micro_pullback_scalp.md` (4924 bytes)
- `nb_lib/strategy_specs/candidates/es_leads_nq_divergence_reversion.md` (6550 bytes)
- `nb_lib/strategy_specs/candidates/failed_orb_fade.md` (5036 bytes)
- `nb_lib/strategy_specs/candidates/first_hour_momentum_acceptance_base_hit.md` (16784 bytes)
- `nb_lib/strategy_specs/candidates/first_hour_range_expansion_breakout.md` (7807 bytes)
- `nb_lib/strategy_specs/candidates/first_loss_reversal_day.md` (5048 bytes)
- `nb_lib/strategy_specs/candidates/footprint_confirmed_supply_demand_reaction.md` (3765 bytes)
- `nb_lib/strategy_specs/candidates/footprint_orderflow_reference.md` (5805 bytes)
- `nb_lib/strategy_specs/candidates/g2_canonical_alpha_SUPERSEDED.md` (94 bytes)
- `nb_lib/strategy_specs/candidates/gap_fill_pressure.md` (12462 bytes)
- `nb_lib/strategy_specs/candidates/gold_vs_nq_risk_off_rotation.md` (4649 bytes)
- `nb_lib/strategy_specs/candidates/htf_vwap_stretch_ltf_reclaim_mean_reversion_screen.md` (4642 bytes)
- `nb_lib/strategy_specs/candidates/initial_balance_midpoint_rotation.md` (5574 bytes)
- `nb_lib/strategy_specs/candidates/intraday_momentum_continuation_base_hit.md` (15367 bytes)
- `nb_lib/strategy_specs/candidates/liquidity_zone_rejection_router.md` (8685 bytes)
- `nb_lib/strategy_specs/candidates/loose_vwap_sneaky_level_hybrid.md` (4364 bytes)
- `nb_lib/strategy_specs/candidates/lunch_compression_break.md` (5120 bytes)
- `nb_lib/strategy_specs/candidates/market_intraday_momentum_close_auction.md` (8915 bytes)
- `nb_lib/strategy_specs/candidates/mnq_news_like_impulse_pullback.md` (10998 bytes)
- `nb_lib/strategy_specs/candidates/momentum_high_water_trail_post_1030.md` (15822 bytes)
- `nb_lib/strategy_specs/candidates/needle_drop_adaptive_management_classifier.md` (49267 bytes)
- `nb_lib/strategy_specs/candidates/news_first_pullback_momentum.md` (9632 bytes)
- `nb_lib/strategy_specs/candidates/noise_area_intraday_momentum.md` (9468 bytes)
- `nb_lib/strategy_specs/candidates/noise_brk_canonical_alpha_SUPERSEDED.md` (101 bytes)
- `nb_lib/strategy_specs/candidates/noise_brk_thirds_partial_geometry.md` (12406 bytes)
- `nb_lib/strategy_specs/candidates/objective_level_liquidity_sweep_reversal_family.md` (6901 bytes)
- `nb_lib/strategy_specs/candidates/ofrt_v0_overnight_fade_rth_tilt.md` (6055 bytes)
- `nb_lib/strategy_specs/candidates/opening_range_failure_continuation_long.md` (8035 bytes)
- `nb_lib/strategy_specs/candidates/opening_range_liquidity_sweep_reversal.md` (7832 bytes)
- `nb_lib/strategy_specs/candidates/opening_range_response_tree.md` (11368 bytes)
- `nb_lib/strategy_specs/candidates/opening_range_width_switch.md` (18364 bytes)
- `nb_lib/strategy_specs/candidates/opening_range_width_switch_v2_base_hit.md` (14662 bytes)
- `nb_lib/strategy_specs/candidates/pdh_pdl_liquidity_sweep_reversal.md` (7561 bytes)
- `nb_lib/strategy_specs/candidates/premium_discount_sweep_shift_continuation.md` (15792 bytes)
- `nb_lib/strategy_specs/candidates/prior_close_magnet_vol_filter.md` (5159 bytes)
- `nb_lib/strategy_specs/candidates/prior_day_close_rejection_fade.md` (9160 bytes)
- `nb_lib/strategy_specs/candidates/prior_day_extreme_acceptance_ladder.md` (5402 bytes)
- `nb_lib/strategy_specs/candidates/prior_day_overnight_level_response_continuation.md` (4673 bytes)
- `nb_lib/strategy_specs/candidates/prior_day_value_area_rejection.md` (14936 bytes)
- `nb_lib/strategy_specs/candidates/prior_session_level_fade_aged.md` (22472 bytes)
- `nb_lib/strategy_specs/candidates/prj3_canonical_alpha_SUPERSEDED.md` (96 bytes)
- `nb_lib/strategy_specs/candidates/README.md` (10305 bytes)
- `nb_lib/strategy_specs/candidates/regime_time_gated_mtf_pullback_continuation.md` (9976 bytes)
- `nb_lib/strategy_specs/candidates/round_number_rejection_microfade.md` (27372 bytes)
- `nb_lib/strategy_specs/candidates/round_number_vwap_liquidity_sweep_reversal.md` (7757 bytes)
- `nb_lib/strategy_specs/candidates/savor_wilson_v2a_canonical_alpha_SUPERSEDED.md` (108 bytes)
- `nb_lib/strategy_specs/candidates/sneaky_pivot_15m_level_reversal.md` (9263 bytes)
- `nb_lib/strategy_specs/candidates/stacked_imbalance_zone_retest.md` (3533 bytes)
- `nb_lib/strategy_specs/candidates/ten_fifteen_opening_drive_state_router.md` (5847 bytes)
- `nb_lib/strategy_specs/candidates/ten_fifteen_vwap_acceptance_pullback.md` (3852 bytes)
- `nb_lib/strategy_specs/candidates/tight_open_breakout_long.md` (10592 bytes)
- `nb_lib/strategy_specs/candidates/tight_open_breakout_orderflow_confirmed.md` (4346 bytes)
- `nb_lib/strategy_specs/candidates/tight_open_breakout_short.md` (10225 bytes)
- `nb_lib/strategy_specs/candidates/tight_opening_window_breakout_long.md` (10797 bytes)
- `nb_lib/strategy_specs/candidates/tight_opening_window_breakout_short.md` (8840 bytes)
- `nb_lib/strategy_specs/candidates/tight_problem_bar_removal_long.md` (10296 bytes)
- `nb_lib/strategy_specs/candidates/tight_problem_bar_removal_short.md` (10229 bytes)
- `nb_lib/strategy_specs/candidates/true_zone_liquidity_sweep_reference.md` (5900 bytes)
- `nb_lib/strategy_specs/candidates/variant_1_lifecycle.md` (5915 bytes)
- `nb_lib/strategy_specs/candidates/vwap_acceptance_first_pullback_base_hit.md` (13810 bytes)
- `nb_lib/strategy_specs/candidates/vwap_band_acceptance_regime.md` (5411 bytes)
- `nb_lib/strategy_specs/candidates/vwap_stretch_reclaim_mean_reversion_screen.md` (6718 bytes)
- `nb_lib/strategy_specs/candidates/vwap_stretch_snapback.md` (6590 bytes)
- `nb_lib/strategy_specs/candidates/vwap_zscore_mean_reversion_fade.md` (6624 bytes)
- `nb_lib/strategy_specs/candidates/wide_opening_window_reversal_long.md` (9585 bytes)
- `nb_lib/strategy_specs/candidates/wide_opening_window_reversal_short.md` (9683 bytes)
- `nb_lib/strategy_specs/candidates/wide_reversal_long.md` (10133 bytes)
- `nb_lib/strategy_specs/candidates/wide_reversal_short.md` (10285 bytes)
- `nb_lib/strategy_specs/candidates/wide_state_absorption_reversal.md` (3697 bytes)
- `nb_lib/strategy_specs/candidates/wide_state_bvc_proxy_divergence_reversal.md` (11537 bytes)
- `nb_lib/strategy_specs/candidates/wide_state_delta_divergence_reversal.md` (3805 bytes)
- `nb_lib/strategy_specs/canonical/atr_regime_pullback_continuation.md` (36438 bytes)
- `nb_lib/strategy_specs/canonical/atr_regime_pullback_tight_target.md` (17305 bytes)
- `nb_lib/strategy_specs/canonical/g2_canonical_alpha.md` (3264 bytes)
- `nb_lib/strategy_specs/canonical/momentum_high_water_trail_post_1030_spec_FINAL.md` (38134 bytes)
- `nb_lib/strategy_specs/canonical/needle_drop_v2_spec_FINAL.md` (30108 bytes)
- `nb_lib/strategy_specs/canonical/objective_level_liquidity_sweep_reversal_family_spec_FINAL.md` (15235 bytes)
- `nb_lib/strategy_specs/canonical/opening_range_failure_continuation_long_spec_FINAL.md` (5430 bytes)
- `nb_lib/strategy_specs/canonical/opening_range_response_tree_spec_FINAL.md` (7641 bytes)
- `nb_lib/strategy_specs/canonical/opening_range_width_switch_spec_FINAL.md` (29269 bytes)
- `nb_lib/strategy_specs/canonical/prior_day_value_area_rejection_spec_FINAL.md` (32031 bytes)
- `nb_lib/strategy_specs/canonical/round_number_rejection_microfade_spec_FINAL.md` (36492 bytes)
- `nb_lib/strategy_specs/canonical/savor_wilson_v2a_canonical_alpha.md` (3451 bytes)
- `nb_lib/strategy_specs/canonical/vwap_stretch_snapback_spec_FINAL.md` (44998 bytes)
- `nb_lib/strategy_specs/canonical/wide_state_bvc_proxy_divergence_reversal_spec_FINAL.md` (7972 bytes)
- `nb_lib/strategy_specs/composition_nodes/_CANDIDATE_SUPPORT_STACK.md` (9461 bytes)
- `nb_lib/strategy_specs/composition_nodes/intraday_target_invalidation_packet.md` (20138 bytes)
- `nb_lib/strategy_specs/composition_nodes/liquidity_zone_prior_router.md` (42317 bytes)
- `nb_lib/strategy_specs/composition_nodes/markov_daily_regime_router.md` (8539 bytes)
- `nb_lib/strategy_specs/composition_nodes/mnq_directional_bias_atlas.md` (7393 bytes)
- `nb_lib/strategy_specs/composition_nodes/opening_momentum_acceptance_router.md` (8042 bytes)
- `nb_lib/strategy_specs/composition_nodes/opening_range_rejection_state_router.md` (6244 bytes)
- `nb_lib/strategy_specs/composition_nodes/README.md` (7190 bytes)
- `nb_lib/strategy_specs/composition_nodes/realized_volatility_management_router.md` (8243 bytes)
- `nb_lib/strategy_specs/README.md` (4565 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_carr_lopez_de_prado_reference_list_20260621.md` (16673 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_five_frequency_adequate_mnq_candidates_20260621.md` (23971 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_formula_level_menu_intraday_mnq_momentum_20260621.md` (27193 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_futures_prop_firm_deployment_let_it_breathe_20260622.md` (24097 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_intraday_trend_continuation_mnq_candidate_menu_20260622.md` (22647 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_market_intraday_momentum_mnq_candidate_20260622.md` (15321 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_mechanism_class_screening_protocol_20260621.md` (3360 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_no_target_no_trade_targetability_gate_mnq_20260622.md` (26087 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_order_flow_microstructure_nq_mnq_20260622.md` (4418 bytes)
- `nb_lib/strategy_specs/source_artifacts/compass_overnight_intraday_directional_bias_mnq_20260628.md` (22780 bytes)
- `nb_lib/strategy_specs/source_artifacts/external_meanrev_video_intake_20260630.md` (3952 bytes)
- `nb_lib/strategy_specs/source_artifacts/opus_directional_bias_atlas_guardrails_20260623.md` (3161 bytes)
- `nb_lib/strategy_specs/source_artifacts/README.md` (3708 bytes)
- `nb_lib/strategy_specs/source_artifacts/RESEARCH_dependency_catalog_and_bootstrap_installer_20260629.md` (25821 bytes)
- `nb_lib/strategy_specs/source_artifacts/sneaky_pivot_transcript_20260630.md` (29791 bytes)
- `nb_lib/strategy_specs/Untitled.md` (5170 bytes)
- `ninja-traitorate-methodology-reference.md` (51809 bytes)
