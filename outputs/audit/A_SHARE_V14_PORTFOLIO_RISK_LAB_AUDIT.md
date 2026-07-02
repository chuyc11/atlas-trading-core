# A-Share v1.4 Portfolio Risk Lab Audit

- overall_passed: True
- blocking_reasons: []
- warnings_count: 0

## Artifact Checks
- json_count: 18
- markdown_count: 8
- audit_markdown_count: 1
- all_json_present: True
- all_markdown_present: True
- json_artifact_budget_passed: True
- markdown_artifact_budget_passed: True

## Quality Checks
- portfolio_risk_scorecard_generated: True
- exposure_concentration_result_generated: True
- correlation_diversification_result_generated: True
- capacity_liquidity_result_generated: True
- turnover_cost_slippage_result_generated: True
- simulated_allocation_result_generated: True
- simulated_rebalance_plan_generated: True
- multi_strategy_portfolio_result_generated: True
- stress_scenario_result_generated: True
- risk_limit_guardrail_result_generated: True
- owner_portfolio_risk_dashboard_generated: True
- portfolio_risk_monitoring_alerts_generated: True
- capacity_estimate_is_simulated: True
- liquidity_estimate_is_simulated: True
- allocation_is_simulated: True
- rebalance_plan_is_simulated: True
- stress_result_is_simulated: True
- artifact_integrity_sweep_passed: True
- protected_path_sweep_passed: True
- safety_boundary_sweep_passed: True

## Forbidden Checks
- real_portfolio_advice_generated: False
- real_allocation_instruction_generated: False
- real_rebalance_instruction_generated: False
- real_trade_instruction_generated: False
- strategy_real_trading_active_state_present: False
- broker_connected: False
- real_account_data_read: False
- real_orders_placed: False
- real_order_preview_generated: False
- buy_sell_signals_generated: False
- owner_readiness_gate_rerun: False
- controlled_gate_reevaluation_run: False
- new_gate_score_generated: False
- new_gate_decision_generated: False
- old_run_daily_called: False
- day2_executed: False
- live_trading_ready: False

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
