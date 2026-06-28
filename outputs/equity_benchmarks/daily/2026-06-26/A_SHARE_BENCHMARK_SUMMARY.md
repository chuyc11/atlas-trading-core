# A Share Benchmark Summary

## 总体结论
- 数据日期: 2026-06-26
- benchmark 数量: 6
- first_day_initialization: true
- performance_not_yet_observed: true
- limited_history_flagged: true

## Benchmark Availability
| Benchmark | Status | Days | Placeholder | Source |
|---|---|---:|---|---|
| CSI300 | available | 251 | false | local_index_price_panel |
| CSI500 | available | 251 | false | local_index_price_panel |
| CSI1000 | available | 251 | false | local_index_price_panel |
| CASH | available | 251 | false | cash_assumption_zero_return |
| EQUAL_WEIGHT_STRICT_TRADABLE | available | 296 | false | internal_equal_weight_as_of_universe |
| EQUAL_WEIGHT_CANDIDATE_POOL | available | 271 | false | internal_equal_weight_as_of_universe |

## 当前比较限制
- 当前组合跟踪仍处在首日初始化状态，组合层面的多日相对表现尚未被观测。
- 指数与等权 benchmark 的历史序列可以用于基准参照，但不应被解释为投资结论。
- tracking error、information ratio、correlation 会在组合历史达到最小天数后再启用。

## Boundary
- research_only: true.
- virtual_only: true.
- broker_connected: false.
- real_orders_placed: false.
- run_daily_called: false.
- day2_executed: false.
- model_profit_guaranteed: false.
- live_trading_ready: false.

Next recommended version: v0.7.11-a-share-multi-day-portfolio-performance-tracking
