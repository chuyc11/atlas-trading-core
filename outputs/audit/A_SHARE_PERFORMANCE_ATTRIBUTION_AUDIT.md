# A-Share Performance Attribution Audit

- target_version: v0.7.12-a-share-performance-attribution-and-risk-diagnostics
- as_of_date: 2026-06-26
- overall_passed: true
- blocking_reasons: []
- warnings: 1

## Availability Checks
- structural_diagnostics_available: True
- realized_performance_attribution_available: True
- limited_history: True
- limited_history_correctly_flagged: True

## Reconciliation Checks
- holding_weights_reconcile: True
- industry_weights_reconcile: True
- score_bucket_weights_reconcile: True
- risk_bucket_weights_reconcile: True
- liquidity_bucket_weights_reconcile: True

## Boundary
- performance_attribution_only: True
- risk_diagnostics_only: True
- research_only: True
- virtual_only: True
- real_portfolio_generated: False
- buy_sell_signals_generated: False
- order_preview_generated: False
- broker_connected: False
- real_orders_placed: False
- run_daily_called: False
- day2_executed: False
- model_profit_guaranteed: False
- live_trading_ready: False
- historical_performance_fabricated: False
- future_data_used: False
- attribution_used_as_trade_signal: False
- official_forward_dry_run_status_unchanged: True

Recommended next version: v0.8.0-a-share-daily-data-refresh-and-provider-hardening
