# A-Share v1.3 Research Quality Lab Audit

- overall_passed: True
- blocking_reasons: []
- warnings_count: 16

## Artifact Checks
- json_count: 20
- markdown_count: 8
- audit_markdown_count: 1
- all_json_present: True
- all_markdown_present: True
- json_artifact_budget_passed: True
- markdown_artifact_budget_passed: True

## Quality Checks
- research_quality_scorecard_generated: True
- factor_quality_diagnostics_generated: True
- candidate_quality_diagnostics_generated: True
- strategy_lab_registry_expanded: True
- strategy_card_register_generated: True
- backtest_walkforward_oos_result_generated: True
- robustness_sensitivity_stress_result_generated: True
- overfitting_false_discovery_result_generated: True
- llm_proposal_quality_result_generated: True
- rl_policy_quality_result_generated: True
- shadow_canary_quality_gate_result_generated: True
- strategy_lifecycle_decision_result_generated: True
- research_quality_monitoring_alerts_generated: True
- owner_research_quality_dashboard_generated: True
- data_leakage_guard_passed: True
- lookahead_bias_check_passed: True
- survivorship_bias_warning_recorded: True
- overfitting_risk_classified: True
- robustness_score_generated: True
- strategy_promotion_hard_gate_generated: True
- strategy_rejection_hard_gate_generated: True
- strategy_rollback_gate_generated: True
- artifact_integrity_sweep_passed: True
- protected_path_sweep_passed: True
- safety_boundary_sweep_passed: True

## Forbidden Checks
- llm_proposals_are_trade_instructions: False
- rl_actions_are_real_account_actions: False
- rl_actions_are_real_orders: False
- strategy_real_trading_active_state_present: False
- real_performance_claim_allowed: False
- live_trading_claim_allowed: False
- investment_advice_claim_allowed: False
- external_notifications_sent: False
- silent_scheduler_installation: False
- daemon_installed: False

## Owner Readiness
- owner_readiness_state: blocked
- owner_operationally_acceptable: False
- source_readiness_score: 54
- minimum_owner_readiness_score: 75
- score_gap: 21

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
