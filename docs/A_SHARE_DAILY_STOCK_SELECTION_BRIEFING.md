# A-Share Daily Stock Selection Briefing

`v0.7.7-a-share-daily-stock-selection-briefing` generates a daily Chinese research briefing for the project owner.

The briefing answers: what candidate directions, virtual portfolios, industry exposure, and main risks does the A-share full-market research system show today?

It does not answer what to buy, what to sell, how much capital to allocate, or how to operate a real account.

## Commands

```powershell
python -m trading_core.cli build-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26
```

The default `as_of_date` is `2026-06-26`. The builder requires exact existing artifacts by default. Use `--allow-latest-artifact-date` only when explicitly accepting the latest complete artifact date on or before the requested date.

## Inputs

- v0.7.3 feature artifacts
- v0.7.4 score artifacts
- v0.7.5 candidate artifacts
- v0.7.6 virtual portfolio artifacts
- candidate, score, feature, and portfolio audit artifacts

The builder reads existing artifacts only. It does not regenerate scores, candidates, or virtual portfolios.

## Outputs

- `data/equity_briefings/daily/YYYY-MM-DD/daily_stock_selection_briefing.json`
- `data/equity_briefings/daily/YYYY-MM-DD/briefing_manifest.json`
- `data/equity_briefings/daily/YYYY-MM-DD/briefing_source_trace.json`
- `data/equity_briefings/daily/YYYY-MM-DD/briefing_boundary_check.json`
- `outputs/equity_briefings/daily/YYYY-MM-DD/DAILY_STOCK_SELECTION_BRIEFING.md`
- `outputs/equity_briefings/daily/YYYY-MM-DD/BRIEFING_SOURCE_TRACE.md`
- `data/equity_data_quality/a_share_daily_stock_selection_briefing_audit.json`
- `outputs/audit/A_SHARE_DAILY_STOCK_SELECTION_BRIEFING_AUDIT.md`

## Required Sections

- 今日总体结论
- 数据日期和覆盖状态
- 长期研究候选 Top 10
- 中期研究候选 Top 10
- 短期研究候选 Top 10
- 多周期共振候选
- 风险降级股票摘要
- 长期/中期/短期虚拟组合摘要
- 行业分布和集中度
- 风险与流动性提示
- 数据与审计状态
- 不要误读
- 下一步跟踪建议
- 明确免责声明

## Boundary

The briefing is not trading advice. It does not generate new scores, candidates, virtual portfolios, buy/sell signals, order previews, broker artifacts, real orders, profit claims, live-trading readiness, `run-daily`, or official forward dry-run day2 artifacts.

Virtual portfolio tracking and the paper ledger are implemented in v0.7.8. The briefing remains information-only; tracking outputs are separate virtual-only artifacts under `data/equity_portfolio_tracking/` and `outputs/equity_portfolio_tracking/`.
