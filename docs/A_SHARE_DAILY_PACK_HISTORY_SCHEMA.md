# A-Share Daily Pack History Schema

Daily artifacts:

- `daily_pack_history_config.json`
- `daily_pack_history_input_availability.json`
- `daily_pack_history_source_resolution.json`
- `daily_pack_history_date_alignment.json`
- `daily_pack_run_record.json`
- `daily_pack_history_append_result.json`
- `daily_pack_history_snapshot.json`
- `owner_readiness_score.json`
- `owner_readiness_history.json`
- `owner_readiness_trend_sufficiency.json`
- `daily_pack_quality_baseline.json`
- `warning_issue_trend_baseline.json`
- `safe_action_trend_baseline.json`
- `protected_path_trend_baseline.json`
- `boundary_trend_baseline.json`
- `source_trace_quality_trend.json`
- `daily_pack_completeness_trend.json`
- `owner_next_step_trend.json`
- `daily_pack_history_source_trace.json`
- `daily_pack_history_boundary_check.json`
- `daily_pack_history_manifest.json`
- `daily_pack_history_summary.json`

History indexes:

- `daily_pack_history_index.json`
- `owner_readiness_history_index.json`
- `daily_pack_quality_history_index.json`
- `warning_issue_history_index.json`
- `safe_action_history_index.json`
- `protected_path_history_index.json`
- `boundary_history_index.json`
- `source_trace_quality_history_index.json`

Default parameters:

- `history_window_days=90`
- `minimum_required_observations=5`
- `baseline_window_observations=20`
- `append_only_history=true`
- `allow_rebuild_history=false`
- `allow_synthetic_history=false`
- `allow_future_dates=false`
