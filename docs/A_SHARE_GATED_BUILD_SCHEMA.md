# A-Share Gated Build Schema

Daily JSON artifacts live under `data/equity_current_day_builds/daily/YYYY-MM-DD/`.

Required artifacts:

- `gated_build_config.json`
- `gated_build_input_availability.json`
- `gated_build_date_alignment.json`
- `preflight_gate.json`
- `gated_build_execution_plan.json`
- `gated_build_execution_record.json`
- `build_from_existing_data_workflow_result.json`
- `build_from_existing_data_audit_link.json`
- `build_artifact_index.json`
- `validate_vs_build_comparison.json`
- `artifact_drift_summary.json`
- `gated_build_warning_summary.json`
- `gated_build_source_trace.json`
- `gated_build_boundary_check.json`
- `gated_build_manifest.json`
- `gated_build_summary.json`

Reports live under `outputs/equity_current_day_builds/daily/YYYY-MM-DD/`.

The audit lives at `data/equity_data_quality/a_share_gated_build_from_existing_data_audit.json`.

