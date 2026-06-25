# Daily Market Data Snapshot

The daily market data snapshot reads local authorized historical packages and emits a pinned daily research snapshot. It does not call external APIs and does not download real-time market data.

## Inputs

- `data/market/historical/authorized/HIST-ETF-OHLCV-CN-HK-V1.csv`
- `data/market/historical/authorized/HIST-BENCHMARK-INDEX-CN-HK-V1.csv`
- `data/global_briefing/normalized/GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl`
- `data/system/ashare_trading_calendar_contract.json`
- `data/strategies/baseline_strategy_registry.json`

## Outputs

- `data/daily_workflow/snapshots/daily_market_data_snapshot-YYYY-MM-DD.json`
- `outputs/daily_workflow/DAILY_MARKET_DATA_SNAPSHOT-YYYY-MM-DD.md`

## Checks

- latest available trading date
- explicit `as_of_date`
- universe symbol coverage
- OHLCV completeness
- benchmark availability
- risk proxy availability
- source paths and hashes in downstream freeze manifest
- no external download
- no run-daily
- no main ledger write

