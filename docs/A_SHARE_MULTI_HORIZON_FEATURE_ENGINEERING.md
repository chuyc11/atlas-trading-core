# A-Share Multi-Horizon Feature Engineering

`v0.7.3-a-share-multi-horizon-feature-engineering` builds feature-only tables for the strict A-share tradable universe.

It is not scoring, recommendation, candidate generation, watchlist generation, virtual portfolio generation, broker integration, real order placement, `run-daily`, profit validation, or live-trading readiness.

## Commands

```powershell
python -m trading_core.cli build-a-share-multi-horizon-features --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-multi-horizon-features --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-multi-horizon-features --as-of-date 2026-06-26
```

By default, the builder requires an exact `strict_tradable_universe.json` for the requested `as_of_date`. `--allow-latest-tradable-universe` may be used for explicit historical catch-up runs, but the release-default path remains fail-closed.

## Artifacts

Machine-readable feature artifacts are written under `data/equity_features/daily/YYYY-MM-DD/`:

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

Human-readable reports are written under `outputs/equity_features/daily/YYYY-MM-DD/`:

- `FEATURE_GENERATION_SUMMARY.md`
- `FEATURE_FIELD_COVERAGE.md`

Audit artifacts are:

- `data/equity_data_quality/a_share_multi_horizon_feature_audit.json`
- `outputs/audit/A_SHARE_MULTI_HORIZON_FEATURE_AUDIT.md`

## Release Evidence

The release run for `as_of_date=2026-06-26` passed:

```text
strict_tradable_count = 3676
feature_symbols = 3676 for every feature group
symbol_coverage = 1.0 for every feature group
short_horizon_mandatory_field_coverage = 1.0
mid_horizon_mandatory_field_coverage = 1.0
long_horizon_mandatory_field_coverage = 0.98669
risk_mandatory_field_coverage = 1.0
liquidity_mandatory_field_coverage = 1.0
industry_mandatory_field_coverage = 1.0
fundamental_mandatory_field_coverage = 0.708806
overall_passed = true
blocking_reasons = []
recommended_next_version = v0.7.4-a-share-long-mid-short-scoring-system
```

The fundamental table intentionally allows partial field coverage because valuation percentile fields remain nullable placeholders until a later data-quality/scoring stage.

## Audit Gates

Symbol coverage thresholds:

- short, mid, risk, liquidity: at least 95% of strict universe
- long: at least 90%
- industry: at least 80%
- fundamental: at least 60%

Mandatory field coverage thresholds:

- short, mid, risk, liquidity: at least 90%
- long: at least 80%
- industry: at least 70%
- fundamental: at least 50%

The audit also checks:

- feature symbols are a subset of strict tradable universe
- excluded symbols are absent
- no duplicate symbol rows
- all required fields are present
- numeric feature values are finite
- manifest source dates do not exceed `as_of_date`
- no score or signal columns are present
- no rank columns are present except `stock_rank_in_industry_by_return_20d`, `stock_rank_in_industry_by_return_60d`, and `stock_rank_in_industry_by_return_120d`
- forbidden positive wording is absent

## Boundary

These flags must remain false:

```text
scores_generated
candidates_generated
watchlist_generated
virtual_portfolio_generated
day2_executed
run_daily_called
broker_connected
real_orders_placed
model_profit_guaranteed
live_trading_ready
```

The only allowed next step from a passing v0.7.3 audit is a future scoring/research stage such as `v0.7.4-a-share-long-mid-short-scoring-system`.
