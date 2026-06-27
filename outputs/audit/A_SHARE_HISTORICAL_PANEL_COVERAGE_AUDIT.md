# A-Share Historical Panel Coverage Audit

- overall_passed: true
- blocking_reasons: []
- warnings: 2
- coverage: {'price_history_min_date': '2021-01-04', 'price_history_max_date': '2026-06-26', 'price_history_trading_days': 1326, 'price_history_symbols': 5516, 'adjusted_price_symbols': 5516, 'daily_basic_symbols': 5516, 'financial_symbols': 5211, 'symbols_with_20d_history': 5509, 'symbols_with_60d_history': 5474, 'symbols_with_120d_history': 5441, 'symbols_with_250d_history': 5379, 'symbols_with_3y_history': 5132, 'symbols_with_5y_history': 4458, 'adjusted_price_coverage_ratio': 1.0, 'daily_basic_history_coverage_ratio': 1.0, 'financial_quarter_coverage_ratio': 1.0, 'symbols_with_12_financial_quarters': 5136, 'financial_quarter_target_symbol_count': 5867}
- coverage_global: {'equity_master_symbols': 5867, 'backfill_queue_symbols': 5516, 'price_history_symbols': 5516, 'price_history_coverage_vs_equity_master': 0.940174, 'price_history_coverage_vs_queue': 1.0, 'daily_basic_coverage_vs_equity_master': 0.940174, 'financial_coverage_vs_equity_master': 0.888188}

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
