# A-Share Historical Backfill Symbol Queue

- target_version: v0.7.1.2-a-share-historical-data-provider-expansion
- source: data/equity_universe/equity_master.parquet
- queue_total_symbols: 5867
- eligible_price_backfill_symbols: 5516
- eligible_adjusted_price_backfill_symbols: 5516
- eligible_daily_basic_backfill_symbols: 5516
- ineligible_symbols: 351
- ineligible_reasons: {'inactive_or_delisted': 351}

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
