# A股 owner monitoring summary

## 1. 今日监控总览
- 监控状态: passed_with_warnings
- 运行历史观察数: 1
- 趋势分析可用: False

## 2. 运行历史状态
- 当前 warning 数: 11
- 当前 blocking 数: 0

## 3. Alert 状态
- critical alerts: 0
- warning alerts: 0
- known non-blocking alerts: 0
- external notifications sent: False

## 4. Warning 趋势
- trend status: insufficient_history
- current warnings: 11

## 5. Blocking 趋势
- trend status: insufficient_history
- current blockers: 0

## 6. Provider 健康趋势
- current status: available
- trend status: insufficient_history

## 7. Workflow 健康趋势
- current status: passed
- trend status: insufficient_history

## 8. Dashboard 健康趋势
- current status: passed
- trend status: insufficient_history

## 9. 本地 alert 事件
- BLOCKING_AUDIT_FAILURE: not_triggered / critical
- DATA_REFRESH_FAILURE: not_triggered / critical
- CURRENT_DAY_RUN_FAILURE: not_triggered / critical
- OWNER_DASHBOARD_FAILURE: not_triggered / critical
- BOUNDARY_VIOLATION: not_triggered / critical
- BROKER_OR_ORDER_SURFACE_DETECTED: not_triggered / critical
- OLD_RUN_DAILY_DETECTED: not_triggered / critical
- DAY2_EXECUTED_DETECTED: not_triggered / critical
- FORBIDDEN_WORDING_DETECTED: not_triggered / critical
- WARNING_COUNT_INCREASE: insufficient_history / warning
- REPEATED_KNOWN_WARNING: insufficient_history / known_non_blocking
- PROVIDER_HEALTH_DEGRADED: insufficient_history / warning
- DATA_FRESHNESS_DEGRADED: insufficient_history / warning
- MISSING_REQUIRED_ARTIFACT: not_triggered / critical
- TREND_ANALYSIS_INSUFFICIENT_HISTORY: insufficient_history / informational

## 10. 安全边界状态
- boundary passed: True
- broker connected: False
- real orders placed: False
- old run daily called: False

## 11. 下一步建议
- 继续积累运行历史；当观察数达到阈值后再判断 warning 与健康趋势。
- v0.8.4 应把常见 warning 和失败状态整理成本地 remediation runbook 与安全 checklist。

## 12. 免责声明
- 本报告只用于研究系统健康监控，不是交易指令。
- 本阶段不生成买卖信号，不连接券商，不读取真实账户，不下真实订单，不发送外部通知。
