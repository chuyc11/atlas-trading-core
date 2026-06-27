# A-share Feature Readiness Audit

The v0.7.1.2 feature readiness audit decides whether the historical data foundation is sufficient to enter:

```text
v0.7.2-a-share-tradable-universe-filter
v0.7.3-a-share-multi-horizon-feature-engineering
```

It does not calculate features and does not generate scores, recommendations, candidates, watchlists, or virtual portfolios.

## Readiness Checks

| Readiness flag | Requirement |
|---|---|
| `tradable_universe_filter_ready` | enough 20d, 60d, and 120d history |
| `short_horizon_feature_ready` | enough 60d history |
| `mid_horizon_feature_ready` | enough 250d history |
| `long_horizon_feature_ready` | 250d history plus adjusted prices and financial quarters |
| `walk_forward_validation_ready` | normally false here; later validation owns this |

## Recommendation Logic

If `overall_passed=true` and `tradable_universe_filter_ready=true`, the audit recommends `v0.7.2-a-share-tradable-universe-filter`.

If `overall_passed=false`, the audit recommends `v0.7.1.3-a-share-historical-data-source-upgrade`. It must not recommend v0.7.2 while readiness is false.

After v0.7.2 passes its own tradable universe audit, the next recommendation moves to `v0.7.3-a-share-multi-horizon-feature-engineering`. v0.7.2 does not itself calculate features, scores, candidates, watchlists, or portfolios.

## v0.7.2 Result

The v0.7.2 tradable universe audit passed for `as_of_date=2026-06-26`:

```text
equity_master_symbols = 5867
input_symbols = 5867
strict_tradable_count = 3676
caution_count = 0
excluded_count = 2191
unknown_status_count = 0
recommended_next_version = v0.7.3-a-share-multi-horizon-feature-engineering
```

## v0.7.3 Result

The v0.7.3 multi-horizon feature audit passed for `as_of_date=2026-06-26`:

```text
strict_tradable_count = 3676
short_horizon_feature_coverage = 1.0
mid_horizon_feature_coverage = 1.0
long_horizon_feature_coverage = 1.0
risk_feature_coverage = 1.0
liquidity_feature_coverage = 1.0
industry_feature_coverage = 1.0
fundamental_feature_coverage = 1.0
short_horizon_mandatory_field_coverage = 1.0
mid_horizon_mandatory_field_coverage = 1.0
long_horizon_mandatory_field_coverage = 0.98669
risk_mandatory_field_coverage = 1.0
liquidity_mandatory_field_coverage = 1.0
industry_mandatory_field_coverage = 1.0
fundamental_mandatory_field_coverage = 0.708806
recommended_next_version = v0.7.4-a-share-long-mid-short-scoring-system
```

v0.7.3 still does not generate scores, recommendations, candidates, watchlists, virtual portfolios, broker instructions, real orders, `run-daily`, profit claims, or live-trading readiness.

## v0.7.4 Result

The v0.7.4 scoring audit passed for `as_of_date=2026-06-26`:

```text
strict_tradable_count = 3676
scored_symbols = 3676
long_score_symbols = 3676
mid_score_symbols = 3676
short_score_symbols = 3676
composite_score_symbols = 3676
overall_passed = true
blocking_reasons = []
recommended_next_version = v0.7.5-a-share-candidate-generation-system
```

v0.7.4 generates scores only. It does not generate recommendations, candidates, watchlists, virtual portfolios, broker instructions, real orders, `run-daily`, profit claims, live-trading readiness, or official forward dry-run day2 artifacts.

## Forbidden Claims

The audit keeps the following claims forbidden:

```text
guaranteed profit
model can make money
AI selected profitable stocks
live trading ready
real orders placed
broker connected
scores generated
candidates generated
virtual portfolio generated
保证盈利
一定赚钱
实盘就绪
真实下单
已连接券商
已生成股票推荐
已生成候选股
已生成评分
```

## Boundary

The audit must keep these false:

```text
scores_generated
candidates_generated
virtual_portfolio_generated
day2_executed
run_daily_called
broker_connected
real_orders_placed
model_profit_guaranteed
live_trading_ready
```
