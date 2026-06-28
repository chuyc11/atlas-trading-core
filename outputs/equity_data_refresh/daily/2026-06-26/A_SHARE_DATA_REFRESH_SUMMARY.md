# A Share Data Refresh Summary

## 总体结论
- 数据日期: 2026-06-26
- 刷新模式: validate_existing_data
- resolved_as_of_date: 2026-06-26
- provider summary: {'registered': 7, 'enabled': ['local_file_provider', 'cached_panel_provider']}

## Dataset Status Table
| Dataset | Status |
|---|---|
| equity_master | passed |
| daily_price | passed |
| adjusted_price | passed |
| daily_basic | passed |
| index_price | passed |
| industry_classification | passed |
| financial_indicators | passed |
| trading_calendar | passed |

- schema validation summary: passed
- freshness validation summary: passed
- coverage summary: passed
- data gaps: {'missing_datasets': [], 'stale_datasets': [], 'lagged_datasets': ['equity_master', 'industry_classification', 'financial_indicators']}
- fallback decisions: fallback_used=False
- boundary summary: {'boundary_id': 'A-SHARE-DAILY-DATA-REFRESH-BOUNDARY-CHECK', 'target_version': 'v0.8.0-a-share-daily-data-refresh-and-provider-hardening', 'as_of_date': '2026-06-26', 'data_refresh_only': True, 'market_data_only': True, 'research_only': True, 'real_portfolio_generated': False, 'buy_sell_signals_generated': False, 'order_preview_generated': False, 'broker_connected': False, 'real_orders_placed': False, 'run_daily_called': False, 'day2_executed': False, 'model_profit_guaranteed': False, 'live_trading_ready': False, 'research_workflow_triggered': False, 'official_forward_dry_run_status_unchanged': True, 'forbidden_artifacts_present': [], 'forbidden_wording_positive_hits': [], 'overall_passed': True, 'blocking_reasons': [], 'warnings': ['daily_basic:required_field_all_null', 'trading_calendar:exchange_level_calendar_collapsed_to_trade_date']}
- warnings: ['daily_basic:required_field_all_null', 'trading_calendar:exchange_level_calendar_collapsed_to_trade_date']
- blocking reasons: []
- recommended next version: v0.8.1-a-share-current-day-research-workflow-runner

Disclaimer: Data refresh success is research data readiness only and is not live trading readiness.
