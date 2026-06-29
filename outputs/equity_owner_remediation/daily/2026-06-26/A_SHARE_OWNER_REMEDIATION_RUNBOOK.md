# A股 Owner Remediation Runbook

## 1. 今日修复总览
- as_of_date: 2026-06-26
- issue_count: 17
- automatic_action_count: 0
- 本阶段只生成修复手册和安全检查清单，不执行 remediation action。

## 2. 当前 issue 摘要
- warning / schema_issue: daily_basic:required_field_all_null
- warning / unknown_issue: fundamental score confidence is partial
- warning / unknown_issue: index benchmark data unavailable for CSI300/CSI500/CSI1000 placeholders
- warning / unknown_issue: long_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- warning / unknown_issue: market cap used daily_basic_panel fallback because historical daily_basic market cap is unavailable
- warning / unknown_issue: mid_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- known_non_blocking / known_non_blocking_issue: portfolio observation history is below the minimum required window
- known_non_blocking / known_non_blocking_issue: portfolio relative metrics limited by first-day initialization
- warning / unknown_issue: raw industry_level_1 contains Unclassified; briefing disclosed fallback industry bucket usage
- warning / unknown_issue: short_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- warning / schema_issue: trading_calendar:exchange_level_calendar_collapsed_to_trade_date
- warning / unknown_issue: WARNING_COUNT_INCREASE
- known_non_blocking / known_non_blocking_issue: REPEATED_KNOWN_WARNING
- warning / provider_issue: PROVIDER_HEALTH_DEGRADED
- warning / freshness_issue: DATA_FRESHNESS_DEGRADED
- informational / insufficient_history_issue: TREND_ANALYSIS_INSUFFICIENT_HISTORY
- known_non_blocking / known_non_blocking_issue: insufficient_history_for_trends

## 3. P0 blocking 修复手册
- None

## 4. P1 warning 排查手册
- fundamental score confidence is partial
- index benchmark data unavailable for CSI300/CSI500/CSI1000 placeholders
- long_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- market cap used daily_basic_panel fallback because historical daily_basic market cap is unavailable
- mid_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- raw industry_level_1 contains Unclassified; briefing disclosed fallback industry bucket usage
- short_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- WARNING_COUNT_INCREASE
- PROVIDER_HEALTH_DEGRADED
- DATA_FRESHNESS_DEGRADED

## 5. P2 known non-blocking 说明
- daily_basic:required_field_all_null
- portfolio observation history is below the minimum required window
- portfolio relative metrics limited by first-day initialization
- trading_calendar:exchange_level_calendar_collapsed_to_trade_date
- REPEATED_KNOWN_WARNING

## 6. P4 等待更多历史数据事项
- TREND_ANALYSIS_INSUFFICIENT_HISTORY
- insufficient_history_for_trends

## 7. 数据刷新问题排查
- 查看 freshness、schema、coverage 和 provider artifacts；只做验证，不自动刷新。

## 8. Provider 问题排查
- 查看 provider health 与 fallback report，确认是否为已知降级。

## 9. Workflow 问题排查
- 查看 current-day manifest、audit 和 source trace。

## 10. Dashboard / Monitoring 问题排查
- 查看 dashboard audit、monitoring audit、alert event log 与 boundary check。

## 11. 安全边界
- 本手册是研究系统健康排查材料，不是交易指令。
- 本阶段不连接券商，不读取真实账户，不下真实订单，不生成订单预览，不生成买卖信号。

## 12. 下一步建议
- v0.8.5 可把 refresh、current-day、dashboard、monitoring、remediation 聚合成 daily ops command center。

## 13. 免责声明
- This runbook is not an investment recommendation.
- This runbook does not authorize trades.
- This runbook does not connect broker.
- This runbook does not place orders.
