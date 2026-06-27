# A-Share Historical Panel Coverage Audit

- overall_passed: false
- blocking_reasons: ['price_history_symbols_minimum=false', 'symbols_with_120d_history_minimum=false', 'symbols_with_250d_history_minimum=false']
- warnings: 3
- coverage: {'price_history_min_date': '2023-01-03', 'price_history_max_date': '2026-06-26', 'price_history_trading_days': 841, 'price_history_symbols': 10, 'adjusted_price_symbols': 10, 'daily_basic_symbols': 10, 'financial_symbols': 1237, 'symbols_with_20d_history': 10, 'symbols_with_60d_history': 10, 'symbols_with_120d_history': 10, 'symbols_with_250d_history': 10, 'symbols_with_3y_history': 10, 'symbols_with_5y_history': 0, 'adjusted_price_coverage_ratio': 1.0, 'daily_basic_history_coverage_ratio': 1.0, 'financial_quarter_coverage_ratio': 0.028407, 'symbols_with_12_financial_quarters': 0, 'financial_quarter_target_symbol_count': 5867}

## Boundary
- Data ingestion only.
- No stock scores generated.
- No candidates generated.
- No virtual portfolios generated.
- Official forward dry-run status unchanged.
- Day2 was not executed.
- run-daily was not called.
- No broker is connected.
- No real orders were placed.
- Third-party code was not merged into the main flow.
- This is not a model profit guarantee.
- Live trading ready: false.
