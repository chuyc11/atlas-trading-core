# A-share Historical Panel Backfill

v0.7.1.2 extends the v0.7.1 single-day A-share data foundation into historical panels for later tradable-universe filtering and multi-horizon feature engineering.

v0.7.1.1 correctly failed closed after a controlled 10-symbol historical run. v0.7.1.2 diagnoses that blocker, builds a full-market queue from `data/equity_universe/equity_master.parquet`, and materializes full-market historical panels with checkpoint/resume evidence.

This is historical data backfill only. It does not generate LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, stock candidates, watchlists, virtual portfolios, broker instructions, real orders, `run-daily` output, or official forward dry-run day2 artifacts.

## Default Window

```text
target_start_date = 2021-01-01
minimum_start_date = 2023-01-01
end_date = 2026-06-26
```

The target is five years of price and adjusted-price history. The minimum release gate is at least three years of price history for enough symbols to support later filters and short/mid-horizon features.

## Commands

```powershell
python -m trading_core.cli a-share-historical-backfill-plan
python -m trading_core.cli diagnose-a-share-historical-backfill-coverage
python -m trading_core.cli build-a-share-historical-backfill-symbol-queue
python -m trading_core.cli backfill-a-share-historical-panels-full-market --target-start-date 2021-01-01 --minimum-start-date 2023-01-01 --end-date 2026-06-26 --batch-size 100 --max-symbols 0 --resume --retry 2
python -m trading_core.cli audit-a-share-historical-panel-coverage
python -m trading_core.cli audit-a-share-feature-readiness
```

Individual backfill commands:

```powershell
python -m trading_core.cli backfill-a-share-daily-price-history --start-date 2021-01-01 --end-date 2026-06-26
python -m trading_core.cli backfill-a-share-adjusted-price-history --start-date 2021-01-01 --end-date 2026-06-26
python -m trading_core.cli backfill-a-share-daily-basic-history --start-date 2023-01-01 --end-date 2026-06-26
python -m trading_core.cli backfill-a-share-financial-history --start-date 2021-01-01 --end-date 2026-06-26
```

## Artifacts

| Artifact | Purpose |
|---|---|
| `data/equity_data_quality/a_share_historical_backfill_plan.json` | target/minimum window, scope, and boundary contract |
| `data/equity_data_quality/a_share_historical_backfill_root_cause.json` | v0.7.1.1 coverage blocker diagnosis |
| `data/equity_data_quality/a_share_historical_backfill_symbol_queue.json` | full-market symbol queue sourced from equity master |
| `data/equity_data_quality/a_share_historical_backfill_checkpoint.json` | checkpoint/resume status for long backfills |
| `data/equity_data_quality/a_share_historical_backfill_symbol_manifest.json` | per-symbol provider/status/history coverage manifest |
| `data/equity_data_quality/backfill_batches/` | batch manifests for provider attempts |
| `data/equity_market/history/daily_price_history_panel.parquet` | daily OHLCV history |
| `data/equity_market/history/adjusted_price_history_panel.parquet` | adjusted-price history or raw fallback explicitly labeled |
| `data/equity_market/history/daily_basic_history_panel.parquet` | turnover-rate history with nullable valuation/market-cap fields when unavailable |
| `data/equity_fundamental/history/basic_financials_history_panel.parquet` | quarterly basic financial history |
| `data/equity_data_quality/a_share_historical_panel_coverage_audit.json` | release-gate coverage and provider evidence |
| `data/equity_data_quality/a_share_feature_readiness_audit.json` | readiness for v0.7.2 and v0.7.3 |

## Fail-Closed Rule

If public providers cannot satisfy the minimum release gate, the audit must set `overall_passed=false`, preserve blocking reasons, and no success release tag should be created. Single-day data must not be used as a fake historical panel.

v0.7.1.2 passes the minimum release gate with:

```text
price_history_symbols = 5516
price_history_trading_days = 1326
symbols_with_120d_history = 5441
symbols_with_250d_history = 5379
price_history_coverage_vs_equity_master = 0.940174
```

## Public Provider Caveat

The current price-history path uses Eastmoney public kline endpoints by symbol. This can be slow or rate-limited. `external_api_called=true` means public historical data download only; it does not mean real-time trading data, account access, broker connectivity, order placement, or live readiness.
