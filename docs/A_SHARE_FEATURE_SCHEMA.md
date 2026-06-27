# A-Share Feature Schema

This document records the v0.7.3 feature artifacts that feed v0.7.4 scoring.

## Feature Directory

`data/equity_features/daily/YYYY-MM-DD/`

Required feature files:

- `short_horizon_features.parquet`
- `mid_horizon_features.parquet`
- `long_horizon_features.parquet`
- `risk_features.parquet`
- `liquidity_features.parquet`
- `industry_features.parquet`
- `fundamental_features.parquet`
- `feature_manifest.json`
- `feature_field_coverage.json`
- `feature_generation_summary.json`

## Common Columns

Each feature parquet includes:

- `as_of_date`
- `symbol`
- `name`
- `exchange`
- `board`
- `industry_level_1`
- `industry_level_2`
- `feature_group`
- `source`
- `created_at`

## Use In v0.7.4

v0.7.4 consumes these features to build score artifacts under `data/equity_scores/daily/YYYY-MM-DD/`.

Feature fields are objective inputs. They are not scores, recommendations, candidates, watchlists, portfolios, broker instructions, real orders, buy/sell signals, or profit claims.
