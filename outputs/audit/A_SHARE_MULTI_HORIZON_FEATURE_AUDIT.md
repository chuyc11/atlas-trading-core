# A-Share Multi-Horizon Feature Audit

- target_version: v0.7.3-a-share-multi-horizon-feature-engineering
- as_of_date: 2026-06-26
- requested_as_of_date: 2026-06-26
- overall_passed: true
- blocking_reasons: []
- warnings: 0
- counts: {'strict_tradable_count': 3676, 'short_horizon_feature_symbols': 3676, 'short_horizon_feature_rows': 3676, 'mid_horizon_feature_symbols': 3676, 'mid_horizon_feature_rows': 3676, 'long_horizon_feature_symbols': 3676, 'long_horizon_feature_rows': 3676, 'risk_feature_symbols': 3676, 'risk_feature_rows': 3676, 'liquidity_feature_symbols': 3676, 'liquidity_feature_rows': 3676, 'industry_feature_symbols': 3676, 'industry_feature_rows': 3676, 'fundamental_feature_symbols': 3676, 'fundamental_feature_rows': 3676}
- coverage: {'short_horizon_feature_coverage': 1.0, 'mid_horizon_feature_coverage': 1.0, 'long_horizon_feature_coverage': 1.0, 'risk_feature_coverage': 1.0, 'liquidity_feature_coverage': 1.0, 'industry_feature_coverage': 1.0, 'fundamental_feature_coverage': 1.0, 'short_horizon_mandatory_field_coverage': 1.0, 'mid_horizon_mandatory_field_coverage': 1.0, 'long_horizon_mandatory_field_coverage': 0.98669, 'risk_mandatory_field_coverage': 1.0, 'liquidity_mandatory_field_coverage': 1.0, 'industry_mandatory_field_coverage': 1.0, 'fundamental_mandatory_field_coverage': 0.708806}
- no_future_leakage: {'passed': True, 'manifest_no_future_leakage': True, 'source_dates': {'max_price_date_used': '2026-06-26', 'max_adjusted_price_date_used': '2026-06-26', 'max_daily_basic_date_used': '2026-06-26', 'max_financial_ann_date_used': '2026-06-04', 'max_industry_effective_date_used': '2026-06-26'}, 'future_dates': {}, 'as_of_date': '2026-06-26'}
- forbidden_columns: {'score_columns_present': {}, 'rank_columns_present': {}, 'signal_columns_present': {}, 'allowed_feature_rank_columns_present': {'industry': ['stock_rank_in_industry_by_return_20d', 'stock_rank_in_industry_by_return_60d', 'stock_rank_in_industry_by_return_120d']}}

## Boundary
- Feature engineering only.
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
