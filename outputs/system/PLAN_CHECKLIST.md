# Plan Checklist

## Scope
This checklist extracts the MVP requirements from the project plan.
This is an audit input. It does not start forward dry-run.
Plan alignment is an audit, not day 1 authorization.

## Requirements
- R001 trading_calendar_correct (data): required_before_day1=true
- R002 universe_versioning (data): required_before_day1=false
- R003 historical_daily_ohlcv_available (data): required_before_day1=true
- R004 adjusted_price_handling (data): required_before_day1=true
- R005 point_in_time_data_contract (data): required_before_day1=true
- R006 t_day_signal_t_plus_1_execution (execution): required_before_day1=true
- R007 suspension_handling (execution): required_before_day1=true
- R008 limit_up_limit_down_handling (execution): required_before_day1=true
- R009 st_and_new_listing_handling (execution): required_before_day1=false
- R010 board_lot_and_odd_lot_rules (execution): required_before_day1=true
- R011 fee_tax_slippage_model (execution): required_before_day1=true
- R012 cash_position_available_shares_accounting (accounting): required_before_day1=true
- R013 virtual_order_trade_ledger (accounting): required_before_day1=true
- R014 equity_curve_generation (reporting): required_before_day1=true
- R015 benchmark_comparison (reporting): required_before_day1=true
- R016 baseline_rule_strategies (strategy): required_before_day1=false
- R017 daily_report_generation (workflow): required_before_day1=true
- R018 parameter_data_code_versioning (governance): required_before_day1=false
- R019 protected_path_boundary (governance): required_before_day1=true
- R020 historical_replay_isolated_from_forward_dry_run (governance): required_before_day1=true
- R021 no_broker_no_live_trading_boundary (boundary): required_before_day1=true
- R022 no_rl_llm_trading_decision_boundary (boundary): required_before_day1=false
- R023 no_auto_promotion_boundary (boundary): required_before_day1=false
- R024 forward_dry_run_30_day_requirement (workflow): required_before_day1=true

## Boundary
- checklist only
- run-daily not called
- forward dry-run not started
- main ledger not written
