# A Share Remediation Schema

v0.8.4 writes machine-readable remediation artifacts under `data/equity_owner_remediation/daily/<as_of_date>/`.

Required JSON artifacts:

- `remediation_config.json`
- `remediation_input_availability.json`
- `issue_catalog.json`
- `warning_remediation_map.json`
- `blocking_remediation_map.json`
- `alert_remediation_map.json`
- provider, data freshness, schema coverage, workflow, dashboard, and monitoring remediation guides
- `safe_owner_action_checklist.json`
- `manual_verification_checklist.json`
- `non_actionable_issue_list.json`
- `dry_run_remediation_plan.json`
- `remediation_priority_summary.json`
- `remediation_source_trace.json`
- `remediation_boundary_check.json`
- `remediation_manifest.json`
- `remediation_summary.json`

All action items default to `allowed_to_execute_automatically=false`. The dry-run remediation plan records `commands_to_review` and keeps `commands_executed=[]`.
