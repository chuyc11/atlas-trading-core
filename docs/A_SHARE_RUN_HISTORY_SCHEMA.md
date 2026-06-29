# A-Share Run History Schema

v0.8.3 writes append-only run history under:

- `data/equity_owner_monitoring/history/run_history_index.json`
- `data/equity_owner_monitoring/daily/YYYY-MM-DD/run_history_update.json`
- `data/equity_owner_monitoring/daily/YYYY-MM-DD/run_history_snapshot.json`

Run history record fields:

- `run_id`
- `as_of_date`
- `resolved_as_of_date`
- `target_version`
- `source_dashboard_version`
- `source_current_day_version`
- `generated_at`
- `overall_status`
- `data_refresh_status`
- `current_day_run_status`
- `workflow_status`
- `dashboard_status`
- `blocking_count`
- `warning_count`
- `critical_alert_count`
- `warning_alert_count`
- `known_non_blocking_count`
- `audit_paths`
- `dashboard_paths`
- `source_trace_paths`
- `boundary_status`
- `recommended_next_version`

Default release behavior:

- append-only history
- no rebuild unless `--allow-rebuild-history`
- deduplicate identical `as_of_date + target_version + source_dashboard_hash`
- one observation is valid but not enough for trend analysis

For `2026-06-26`, `run_history_observation_count=1`, `trend_analysis_available=false`, and `insufficient_history_for_trends=true`.
