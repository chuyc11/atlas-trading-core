# A-Share Current-Day Run Schema

Primary data directory:

- `data/equity_current_day_runs/daily/YYYY-MM-DD/`

Primary report directory:

- `outputs/equity_current_day_runs/daily/YYYY-MM-DD/`

Required artifacts:

- `current_day_run_config.json`
- `current_day_readiness.json`
- `current_day_data_refresh_link.json`
- `current_day_workflow_plan.json`
- `current_day_workflow_execution.json`
- `current_day_stage_manifest.json`
- `current_day_artifact_index.json`
- `current_day_warning_summary.json`
- `current_day_source_trace.json`
- `current_day_boundary_check.json`
- `current_day_run_manifest.json`
- `current_day_summary.json`

Required audit:

- `data/equity_data_quality/a_share_current_day_research_run_audit.json`
- `outputs/audit/A_SHARE_CURRENT_DAY_RESEARCH_RUN_AUDIT.md`

The runner links to v0.8.0 data refresh artifacts and v0.7.9 workflow artifacts. It carries forward data refresh warnings into the current-day owner summary.

