# A Share Attribution Summary

## 总体结论
- 数据日期: 2026-06-26
- 归因模式: current_exposure_diagnostics
- 当前历史限制: only one portfolio observation; realized multi-day attribution is not available.
- long/mid/short 结构性归因摘要: structural exposure diagnostics are available for all virtual portfolios.
- 持仓贡献摘要: 80 virtual holdings, contribution status is limited-history.
- 行业贡献摘要: ['long_virtual_portfolio', 'mid_virtual_portfolio', 'short_virtual_portfolio']
- 评分桶贡献摘要: bucket edges [0, 20, 40, 60, 80, 100]
- 风险桶贡献摘要: risk downgraded symbols in portfolio []
- 流动性桶贡献摘要: ['long_virtual_portfolio', 'mid_virtual_portfolio', 'short_virtual_portfolio']
- benchmark-relative attribution status: index constituent exposure unavailable for CSI benchmarks; equal-weight exposure is structural.
- 关键风险诊断: {'long_virtual_portfolio': {'concentrated_top5': False, 'concentrated_industry': True, 'contains_risk_downgraded': False, 'contains_excluded_universe': False, 'low_liquidity_cluster': False, 'unclassified_industry_high': True}, 'mid_virtual_portfolio': {'concentrated_top5': False, 'concentrated_industry': True, 'contains_risk_downgraded': False, 'contains_excluded_universe': False, 'low_liquidity_cluster': False, 'unclassified_industry_high': True}, 'short_virtual_portfolio': {'concentrated_top5': False, 'concentrated_industry': True, 'contains_risk_downgraded': False, 'contains_excluded_universe': False, 'low_liquidity_cluster': False, 'unclassified_industry_high': True}}
- 免责声明: attribution diagnostics are research-only virtual outputs and not investment advice.
- recommended next version: v0.8.0-a-share-daily-data-refresh-and-provider-hardening
