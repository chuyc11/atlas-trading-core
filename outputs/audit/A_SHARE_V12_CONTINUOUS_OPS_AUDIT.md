# A-Share v1.2 Continuous Ops Audit

- overall_passed: True
- blocking_reasons: []
- warnings_count: 6

## Schedule
- local_schedule_policy_generated: True
- trading_day_run_plan_generated: True
- scheduler_template_plan_generated: True
- silent_scheduler_installation: False
- schedule_dry_run_passed: True
- run_lock_and_idempotency_checked: True

## Claim Guard
- benchmark_relative_claim_allowed: False
- real_performance_claim_allowed: False
- live_trading_claim_allowed: False
- investment_advice_claim_allowed: False

## Owner Readiness
- owner_readiness_state: blocked
- owner_operationally_acceptable: False
- source_readiness_score: 54
- minimum_owner_readiness_score: 75
- score_gap: 21

## Major Areas
- local_schedule_policy_generated: True
- trading_day_run_plan_generated: True
- scheduler_template_plan_generated: True
- schedule_dry_run_passed: True
- run_lock_and_idempotency_checked: True
- continuous_ops_run: True
- stage_dependency_graph_generated: True
- stage_timing_summary_generated: True
- retry_recovery_plan_generated: True
- simulated_account_history_generated: True
- simulated_account_continuity_passed: True
- paper_ledger_continuity_passed: True
- virtual_broker_reconciliation_passed: True
- benchmark_claim_guard_continuity_generated: True
- operator_runbook_generated: True
- incident_register_generated: True
- monitoring_alerts_generated: True
- strategy_governance_continuity_generated: True
- llm_rl_continuous_governance_generated: True
- artifact_index_generated: True
- artifact_health_passed: True
- platform_health_report_generated: True
- safety_boundary_sweep_passed: True

## Boundary
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
