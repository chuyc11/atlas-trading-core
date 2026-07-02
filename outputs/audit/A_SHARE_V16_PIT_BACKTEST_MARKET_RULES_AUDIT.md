# A-Share v1.6 PIT Backtest Market Rules Audit

- overall_passed: True
- blocking_reasons: []
- warnings_count: 0

## Artifact Checks
- json_count: 17
- markdown_count: 8
- audit_markdown_count: 1
- all_json_present: True
- all_markdown_present: True

## Quality Checks
- point_in_time_data_registry_generated: True
- dataset_feature_label_version_registry_generated: True
- leakage_lookahead_survivorship_guard_generated: True
- event_driven_replay_result_generated: True
- a_share_market_rule_registry_generated: True
- virtual_broker_rule_hardening_result_generated: True
- transaction_cost_slippage_result_generated: True
- benchmark_index_source_result_generated: True
- paper_ledger_replay_consistency_result_generated: True
- backtest_trust_scorecard_generated: True
- owner_trust_dashboard_generated: True
- lookahead_bias_guard_passed: True
- a_share_market_rules_covered: True
- t_plus_one_rule_checked: True
- price_limit_rule_checked: True
- suspension_rule_checked: True
- lot_size_rule_checked: True
- virtual_broker_rule_audit_passed: True
- paper_ledger_replay_passed: True
- artifact_integrity_sweep_passed: True
- protected_path_sweep_passed: True
- safety_boundary_sweep_passed: True

## Forbidden Checks
- point_in_time_visibility_fabricated: False
- backtest_results_fabricated: False
- simulated_fills_fabricated: False
- benchmark_index_data_fabricated: False
- transaction_cost_fabricated: False
- future_data_usage_detected: False
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
