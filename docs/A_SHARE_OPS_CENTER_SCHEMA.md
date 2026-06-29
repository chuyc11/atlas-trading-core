# A Share Ops Center Schema

v0.8.5 writes machine-readable ops artifacts under `data/equity_ops_center/daily/<as_of_date>/`.

Required artifacts:

- `ops_center_config.json`
- `ops_input_availability.json`
- `ops_date_alignment.json`
- `ops_plan.json`
- `ops_execution_record.json`
- `ops_health_score_card.json`
- `ops_module_status_matrix.json`
- `ops_issue_summary.json`
- `ops_action_summary.json`
- `ops_artifact_navigation.json`
- `ops_command_reference.json`
- `ops_owner_next_steps.json`
- `ops_source_trace.json`
- `ops_boundary_check.json`
- `ops_manifest.json`
- `ops_summary.json`

The release path keeps `commands_executed=[]`, `aggregate_existing_artifacts_only=true`, `automatic_action_count=0`, and `external_notifications_sent=false`.
