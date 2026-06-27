# A-share Tradable Universe Filter

`v0.7.2-a-share-tradable-universe-filter` builds the daily A-share universe that may be used by later feature engineering. It is filter-only.

It is not stock selection. It does not generate LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, candidates, watchlists, virtual portfolios, broker instructions, real orders, `run-daily` output, or official forward dry-run day2 artifacts.

## Commands

```powershell
python -m trading_core.cli build-a-share-tradable-universe --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-tradable-universe --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli build-and-audit-a-share-tradable-universe --as-of-date 2026-06-26
```

Use `--allow-previous-trading-day true` only when a non-trading as-of date should explicitly roll back to the previous trading day. Otherwise non-trading dates fail closed.

## Inputs

- `data/equity_universe/equity_master.parquet`
- `data/equity_universe/trading_calendar.parquet`
- `data/equity_market/history/daily_price_history_panel.parquet`
- `data/equity_market/history/adjusted_price_history_panel.parquet`
- `data/equity_market/history/daily_basic_history_panel.parquet`
- `data/equity_market/daily_basic_panel.parquet` as market-cap fallback when historical market-cap fields are unavailable
- `data/equity_industry/industry_classification.parquet`
- `data/equity_fundamental/history/basic_financials_history_panel.parquet`
- `data/equity_data_quality/a_share_historical_backfill_symbol_manifest.json`
- historical coverage and feature-readiness audits

## Filters

The filter applies these layers and records reasons per symbol:

- universe eligibility
- ST and risk warning
- listing age, default minimum 120 trading days
- suspension and missing as-of price
- 20d and 60d effective trading observation counts
- 20d and 60d average amount liquidity thresholds
- total and circulating market-cap thresholds
- low close price threshold
- OHLCV price sanity
- one-word limit up/down risk
- 20d, 60d, 120d, and 250d history coverage

## Buckets

- `strict_tradable_universe`: passes all critical filters and is the default input for future scoring.
- `caution_universe`: observation-only names with non-fatal uncertainty; not a default scoring input.
- `excluded_universe`: explicitly blocked names with primary and full exclusion reasons.
- `unknown_status_universe`: names with missing critical fields that cannot be judged safely.

## Artifacts

Machine-readable artifacts:

- `data/equity_selection/daily/2026-06-26/filter_config.json`
- `data/equity_selection/daily/2026-06-26/tradable_universe.json`
- `data/equity_selection/daily/2026-06-26/tradable_universe.parquet`
- `data/equity_selection/daily/2026-06-26/strict_tradable_universe.json`
- `data/equity_selection/daily/2026-06-26/caution_universe.json`
- `data/equity_selection/daily/2026-06-26/excluded_universe.json`
- `data/equity_selection/daily/2026-06-26/unknown_status_universe.json`
- `data/equity_selection/daily/2026-06-26/filter_reason_breakdown.json`
- `data/equity_selection/daily/2026-06-26/tradable_universe_manifest.json`
- `data/equity_data_quality/a_share_tradable_universe_audit.json`

Human-readable artifacts:

- `outputs/equity_selection/daily/2026-06-26/TRADABLE_UNIVERSE_REPORT.md`
- `outputs/equity_selection/daily/2026-06-26/FILTER_REASON_BREAKDOWN.md`
- `outputs/audit/A_SHARE_TRADABLE_UNIVERSE_AUDIT.md`

## Release Evidence

For `as_of_date=2026-06-26`:

```text
equity_master_symbols = 5867
input_symbols = 5867
strict_tradable_count = 3676
caution_count = 0
excluded_count = 2191
unknown_status_count = 0
audit_overall_passed = true
blocking_reasons = []
recommended_next_version = v0.7.3-a-share-multi-horizon-feature-engineering
```

Warning: market cap used `daily_basic_panel` fallback because historical daily basic market-cap fields are unavailable.

## Boundary

The audit requires these to remain false: scores generated, candidates generated, watchlist generated, virtual portfolio generated, day2 executed, run-daily called, broker connected, real orders placed, model profit guaranteed, and live trading ready.

