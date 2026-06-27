# A-share Feature Readiness Audit

The v0.7.1.1 feature readiness audit decides whether the historical data foundation is sufficient to enter:

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
| `walk_forward_validation_ready` | normally false in v0.7.1.1; later validation owns this |

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
