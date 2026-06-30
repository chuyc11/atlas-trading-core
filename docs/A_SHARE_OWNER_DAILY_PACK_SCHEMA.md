# A-Share Owner Daily Pack Schema

The v0.8.11 daily pack writes these JSON artifacts under `data/equity_owner_daily_pack/daily/YYYY-MM-DD/`:

- `daily_pack_config.json`
- `daily_pack_input_availability.json`
- `daily_pack_source_resolution.json`
- `daily_pack_date_alignment.json`
- `owner_daily_status_brief.json`
- `owner_daily_runbook.json`
- `owner_operations_decision_pack.json`
- `owner_next_step_checklist.json`
- `research_output_digest.json`
- `candidate_tracking_digest.json`
- `virtual_portfolio_digest.json`
- `warning_issue_digest.json`
- `safe_action_digest.json`
- `monitoring_remediation_ops_digest.json`
- `protected_path_digest.json`
- `source_trace_digest.json`
- `boundary_digest.json`
- `daily_pack_artifact_navigation.json`
- `daily_pack_source_trace.json`
- `daily_pack_boundary_check.json`
- `daily_pack_manifest.json`
- `daily_pack_summary.json`

Required config invariants:

- `target_version=v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack`
- `source_workflow_mode=build_from_existing_data`
- `decision_pack_type=owner_operations_decision_pack`
- `not_investment_decision_pack=true`
- `rerun_build_from_existing_data=false`
- `rerun_ops_refresh=false`
- `execute_remediation_actions=false`
- `send_external_notifications=false`
- `allow_public_network_refresh=false`
- `allow_full_research_run=false`
- `allow_broker=false`
- `allow_real_orders=false`
- `allow_order_preview=false`
- `allow_buy_sell_signals=false`
- `allow_old_run_daily=false`
- `execute_official_forward_dry_run_day2=false`

Valid modes:

- `validate_daily_pack_inputs`
- `resolve_daily_pack_sources`
- `build_owner_daily_runbook`
- `build_owner_operations_decision_pack`
- `audit_existing_daily_pack`
