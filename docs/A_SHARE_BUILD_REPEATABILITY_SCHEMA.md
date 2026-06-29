# A-Share Build Repeatability Schema

Required JSON artifacts:

- `repeatability_config.json`
- `repeatability_input_availability.json`
- `repeatability_date_alignment.json`
- `protected_path_pre_run_snapshot.json`
- `repeat_build_execution_plan.json`
- `repeat_build_execution_record.json`
- `repeat_build_workflow_result.json`
- `protected_path_post_run_snapshot.json`
- `protected_path_modification_check.json`
- `first_build_artifact_snapshot.json`
- `second_build_artifact_snapshot.json`
- `build_vs_build_comparison.json`
- `repeatability_drift_summary.json`
- `deterministic_field_normalization.json`
- `repeatability_warning_comparison.json`
- `repeatability_source_trace.json`
- `repeatability_boundary_check.json`
- `repeatability_manifest.json`
- `repeatability_summary.json`

`repeatability_config.json` fixes `workflow_mode=build_from_existing_data`, `allow_business_output_drift=false`, `allow_protected_path_modifications=false`, `allow_public_network_refresh=false`, `allow_full_research_run=false`, `allow_broker=false`, `allow_real_orders=false`, `allow_order_preview=false`, `allow_buy_sell_signals=false`, and `allow_old_run_daily=false`.

