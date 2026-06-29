# A-Share Ops History Schema

Daily JSON artifacts live under `data/equity_ops_history/daily/YYYY-MM-DD/`.

Required daily artifacts:

- `ops_history_config.json`
- `ops_history_input_availability.json`
- `ops_run_record.json`
- `ops_history_append_result.json`
- `ops_history_snapshot.json`
- `ops_trend_baseline_config.json`
- `ops_trend_sufficiency.json`
- `ops_health_score_history.json`
- `ops_health_score_baseline.json`
- `ops_module_reliability_baseline.json`
- `ops_warning_recurrence_baseline.json`
- `ops_issue_recurrence_baseline.json`
- `ops_action_recurrence_baseline.json`
- `ops_boundary_history_snapshot.json`
- `ops_baseline_drift_snapshot.json`
- `ops_history_source_trace.json`
- `ops_history_boundary_check.json`
- `ops_history_manifest.json`
- `ops_history_summary.json`

History indexes live under `data/equity_ops_history/history/` and are append-only unless an explicit rebuild flag is supplied. The default release flow does not rebuild and does not synthesize observations.

