# A 股 Gated Build-from-Existing-Data Dry-Run 报告

- **版本**: v0.8.7-a-share-gated-current-day-build-from-existing-data-dry-run
- **日期**: 2026-06-26
- **生成时间**: 2026-06-29T18:41:40.445612Z

## 1. Dry-run 总览

- **总体状态**: 通过
- **Preflight Gate**: 通过
- **Workflow 状态**: passed
- **Workflow 审计**: 通过
- **对比完成**: 是
- **Drift 状态**: clean

## 2. Preflight Gate 结果

- **通过**: True
- **Blocking**: []
- **Warnings**: []
- **Health Score**: 65

## 3. 执行命令

```bash
python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode build_from_existing_data
```

- **退出码**: 0
- **耗时**: 162.206s

## 4. Workflow 审计结果

- **审计路径**: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\equity_data_quality\a_share_current_day_research_run_audit.json
- **通过**: True
- **Blocking**: []
- **Stages Passed**: 12
- **Stages Failed**: 0

## 5. 关键产物

- **Artifacts Generated**: 19

## 6. Validate vs Build 对比

- **对比完成**: True
- **Business Output Drift**: []
- **Missing Artifacts**: []

## 7. Drift 摘要

- **状态**: clean
- **Drift Categories**: ['no_drift']

## 8. Warning / Blocking

- **Blocking Reasons**: []
- **Warnings**: ['daily_basic:required_field_all_null', 'fundamental score confidence is partial', 'git status is not clean; release gate must be checked after implementation commit', 'index benchmark data unavailable for CSI300/CSI500/CSI1000 placeholders', 'long_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps', 'market cap used daily_basic_panel fallback because historical daily_basic market cap is unavailable', 'mid_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps', 'raw industry_level_1 contains Unclassified; briefing disclosed fallback industry bucket usage', 'short_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps', 'trading_calendar:exchange_level_calendar_collapsed_to_trade_date']

## 9. 安全边界

- **Research Only**: True
- **Virtual Only**: True
- **Broker Connected**: False
- **Real Orders Placed**: False
- **Buy/Sell Signals Generated**: False
- **Old run-daily Called**: False

## 10. 下一步建议

- 推荐下一版本: v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability

## 11. 免责声明

本报告为研究流程的 dry-run 产物，不构成投资建议。
不授权任何交易、不下单、不连接券商。
不保证盈利，不实盘就绪。
所有产物仅供项目负责人安全排查使用。
