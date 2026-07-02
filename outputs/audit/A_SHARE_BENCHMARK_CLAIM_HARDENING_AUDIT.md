# A-Share Benchmark Claim Hardening Audit

- overall_passed: True
- blocking_reasons: []
- warnings_count: 2

## Claim Guard
- benchmark_relative_claim_allowed: False
- real_performance_claim_allowed: False
- live_trading_claim_allowed: False
- investment_advice_claim_allowed: False
- simulated_performance_claim_allowed_with_disclaimer: True

## Benchmark Status
- csi300_benchmark_status: warning
- csi500_benchmark_status: warning
- csi1000_benchmark_status: warning
- equal_weight_universe_benchmark_status: passed

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
