# A-Share Data Refresh Schema

Primary data directory:

- `data/equity_data_refresh/daily/YYYY-MM-DD/`

Primary report directory:

- `outputs/equity_data_refresh/daily/YYYY-MM-DD/`

Required datasets:

- `equity_master`
- `daily_price`
- `adjusted_price`
- `daily_basic`
- `index_price`
- `industry_classification`
- `financial_indicators`
- `trading_calendar`

Required artifacts:

- `data_refresh_config.json`
- `date_resolution.json`
- `provider_registry_snapshot.json`
- `provider_health_check.json`
- `provider_execution_log.json`
- `dataset_refresh_plan.json`
- `dataset_refresh_result.json`
- `dataset_schema_validation.json`
- `dataset_freshness_validation.json`
- `dataset_coverage_summary.json`
- `data_gap_report.json`
- `provider_fallback_report.json`
- `data_refresh_source_trace.json`
- `data_refresh_manifest.json`
- `data_refresh_boundary_check.json`
- `data_refresh_summary.json`

The schema supports local legacy column aliases such as `date` for `trade_date`, `is_trading_day` for `is_open`, and `adj_close` for `adjusted_close`. Alias use is recorded as a schema fallback decision.
