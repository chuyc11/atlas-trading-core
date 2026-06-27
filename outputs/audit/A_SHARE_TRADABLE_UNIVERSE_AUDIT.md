# A-Share Tradable Universe Audit

- target_version: v0.7.2-a-share-tradable-universe-filter
- as_of_date: 2026-06-26
- overall_passed: true
- blocking_reasons: []
- warnings: 1
- counts: {'equity_master_symbols': 5867, 'input_symbols': 5867, 'strict_tradable_count': 3676, 'caution_count': 0, 'excluded_count': 2191, 'unknown_status_count': 0}
- top_exclusion_reasons: {'total_mv_below_threshold': 1231, 'avg_amount_20d_below_threshold': 1052, 'circ_mv_below_threshold': 870, 'insufficient_250d_history': 488, 'insufficient_120d_history': 426, 'possible_suspension': 417, 'insufficient_60d_trading_observations': 408, 'insufficient_60d_history': 393, 'insufficient_20d_trading_observations': 379, 'insufficient_20d_history': 358, 'missing_price_on_as_of_date': 354, 'close_price_missing': 354, 'limit_status_unknown': 354, 'inactive': 351, 'amount_missing': 351}

## Boundary
- Tradable universe filter only.
- No stock scores generated.
- No candidates generated.
- No watchlist generated.
- No virtual portfolios generated.
- Official forward dry-run status unchanged.
- Day2 was not executed.
- run-daily was not called.
- No broker is connected.
- No real orders were placed.
- This is not a model profit guarantee.
- Live trading ready: false.
