# A-SHARE-V27-AUDIT

- overall_passed: True
- blocking_reasons: []
- warnings_count: 1
- owner_readiness_state: blocked
- owner_operationally_acceptable: False
- live_trading_ready: False
- full_pytest_run: False
- full_pytest_passed: False

## Artifact Checks
- json_count: 12
- markdown_count: 6
- audit_markdown_count: 1
- all_json_present: True
- all_markdown_present: True
- json_budget_passed: True
- markdown_budget_passed: True
- audit_markdown_budget_passed: True

## Quality Checks
- v26_baseline_verified: True
- strategy_lifecycle_registry_generated: True
- virtual_canary_governance_result_generated: True
- transition_evidence_result_generated: True
- simulation_active_strategy_registry_generated: True
- owner_lifecycle_dashboard_generated: True

## Forbidden Checks
- real_trading_active_state_present: False
- real_canary_state_present: False
- broker_active_state_present: False
- transition_evidence_fabricated: False
- canary_evidence_fabricated: False
- promotion_generates_real_trade: False
- demotion_generates_sell_signal: False
- rollback_generates_real_trade: False
- simulation_active_generates_real_order: False
- full_pytest_run: False
- owner_readiness_gate_rerun: False
- controlled_gate_reevaluation_run: False
- new_gate_score_generated: False
- new_gate_decision_generated: False
- threshold_lowered: False
- waiver_applied: False
- broker_connected: False
- real_account_data_read: False
- real_orders_placed: False
- real_order_preview_generated: False
- buy_sell_signals_generated: False
- old_run_daily_called: False
- day2_executed: False
- live_trading_ready: False
- silent_scheduler_installed: False
- daemon_installed: False