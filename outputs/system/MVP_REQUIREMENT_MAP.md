# MVP Requirement Map

## Scope
This map links checklist requirements to candidate repo evidence.
It does not start forward dry-run.

## Requirements
- R001 trading_calendar_correct: evidence=3 missing=0 manual_review_required=true
- R002 universe_versioning: evidence=2 missing=0 manual_review_required=true
- R003 historical_daily_ohlcv_available: evidence=3 missing=0 manual_review_required=true
- R004 adjusted_price_handling: evidence=2 missing=0 manual_review_required=true
- R005 point_in_time_data_contract: evidence=2 missing=0 manual_review_required=true
- R006 t_day_signal_t_plus_1_execution: evidence=2 missing=0 manual_review_required=true
- R007 suspension_handling: evidence=2 missing=0 manual_review_required=true
- R008 limit_up_limit_down_handling: evidence=2 missing=0 manual_review_required=true
- R009 st_and_new_listing_handling: evidence=2 missing=0 manual_review_required=true
- R010 board_lot_and_odd_lot_rules: evidence=3 missing=0 manual_review_required=true
- R011 fee_tax_slippage_model: evidence=2 missing=0 manual_review_required=true
- R012 cash_position_available_shares_accounting: evidence=3 missing=0 manual_review_required=true
- R013 virtual_order_trade_ledger: evidence=2 missing=0 manual_review_required=true
- R014 equity_curve_generation: evidence=2 missing=0 manual_review_required=true
- R015 benchmark_comparison: evidence=2 missing=0 manual_review_required=true
- R016 baseline_rule_strategies: evidence=2 missing=0 manual_review_required=true
- R017 daily_report_generation: evidence=3 missing=0 manual_review_required=true
- R018 parameter_data_code_versioning: evidence=2 missing=0 manual_review_required=true
- R019 protected_path_boundary: evidence=2 missing=0 manual_review_required=false
- R020 historical_replay_isolated_from_forward_dry_run: evidence=2 missing=0 manual_review_required=true
- R021 no_broker_no_live_trading_boundary: evidence=2 missing=0 manual_review_required=true
- R022 no_rl_llm_trading_decision_boundary: evidence=2 missing=0 manual_review_required=true
- R023 no_auto_promotion_boundary: evidence=2 missing=0 manual_review_required=true
- R024 forward_dry_run_30_day_requirement: evidence=3 missing=0 manual_review_required=false

## Boundary
- requirement map only
- run-daily not called
- forward dry-run not started
- main ledger not written
