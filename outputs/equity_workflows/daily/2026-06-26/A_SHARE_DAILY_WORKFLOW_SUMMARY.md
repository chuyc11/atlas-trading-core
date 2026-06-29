# A 股每日研究工作流汇总

- 日期: 2026-06-26
- 模式: validate_existing_artifacts
- 总体状态: 通过
- research_only: true
- virtual_only: true
- not_order_instruction: true
- not_real_trade: true
- not_profit_guarantee: true
- not_live_trading_ready: true

## 阶段状态

| 阶段 | 名称 | 状态 | 警告 | 阻断 |
|---|---|---|---:|---:|
| stage_00_preflight | preflight | passed | 1 | 0 |
| stage_01_data_readiness | data_readiness | passed | 0 | 0 |
| stage_02_tradable_universe | tradable_universe | passed | 1 | 0 |
| stage_03_feature_engineering | feature_engineering | passed | 0 | 0 |
| stage_04_scoring | scoring | passed | 1 | 0 |
| stage_05_candidate_generation | candidate_generation | passed | 0 | 0 |
| stage_06_virtual_portfolio_construction | virtual_portfolio_construction | passed | 3 | 0 |
| stage_07_daily_briefing | daily_briefing | passed | 5 | 0 |
| stage_08_virtual_portfolio_tracking | virtual_portfolio_tracking | passed | 1 | 0 |
| stage_09_workflow_audit | workflow_audit | passed | 0 | 0 |
| stage_10_owner_summary | owner_summary | passed | 0 | 0 |

## 关键产物

- briefing: data/equity_briefings/daily/2026-06-26/briefing_manifest.json
- tracking: data/equity_portfolio_tracking/daily/2026-06-26/tracking_manifest.json
- workflow source trace complete: true
- upstream audits passed: true

## 候选池与组合

- candidate_counts: {'long': 30, 'mid': 30, 'short': 30, 'extended': 300}
- portfolio_navs: {'long': 1000000.0, 'mid': 1000000.0, 'short': 1000000.0}

## 警告与阻断

- warnings: ['fundamental score confidence is partial', 'git status is not clean; release gate must be checked after implementation commit', 'index benchmark data unavailable for CSI300/CSI500/CSI1000 placeholders', 'long_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps', 'market cap used daily_basic_panel fallback because historical daily_basic market cap is unavailable', 'mid_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps', 'raw industry_level_1 contains Unclassified; briefing disclosed fallback industry bucket usage', 'short_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps']
- blocking_reasons: []

## 边界摘要

- 本阶段只做 A 股研究工作流编排。
- 不调用旧 run-daily。
- official forward dry-run 状态保持不变。
- day2_executed: false。
- broker_connected: false。
- real_orders_placed: false。
- buy_sell_signals_generated: false。
- order_preview_generated: false。
- model_profit_guaranteed: false。
- live_trading_ready: false。

下一建议版本: v0.7.10-a-share-benchmark-data-and-performance-comparison
