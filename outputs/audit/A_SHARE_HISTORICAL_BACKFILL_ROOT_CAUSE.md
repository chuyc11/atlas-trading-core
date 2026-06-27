# A-Share Historical Backfill Root Cause

- target_version: v0.7.1.2-a-share-historical-data-provider-expansion
- equity_master_symbols: 5867
- historical_price_symbols: 10
- backfill_input_symbols: 10
- backfill_queue_symbols: 5516
- suspected_root_causes: ['historical price panel coverage is below release threshold', 'backfill input universe was materially smaller than equity master', 'legacy v0.7.1.1 manifest did not record a full-market symbol queue']
- confirmed_root_causes: ['controlled sample or max-symbols run overwrote historical price panel with about 10 symbols', 'full-market queue exists but historical provider coverage has not been materialized into the price panel']
- symbol_limit_detected: true

## Provider Attempts
- {'eastmoney_kline_public_http': {'attempted_symbol_count': 10, 'succeeded_symbol_count': 10, 'failed_symbol_count': 0}}

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
