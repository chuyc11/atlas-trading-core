# A-Share Daily Workflow Stage Report

| order | stage_id | status | command | duration_seconds |
|---:|---|---|---|---:|
| 0 | stage_00_preflight | passed | python -m trading_core.cli preflight-a-share-daily-workflow --as-of-date 2026-06-26 | 0.000000 |
| 1 | stage_01_data_readiness | passed | verify historical A-share data panels | 0.000000 |
| 2 | stage_02_tradable_universe | passed | python -m trading_core.cli build-and-audit-a-share-tradable-universe --as-of-date 2026-06-26 | 28.011493 |
| 3 | stage_03_feature_engineering | passed | python -m trading_core.cli build-and-audit-a-share-multi-horizon-features --as-of-date 2026-06-26 | 88.334342 |
| 4 | stage_04_scoring | passed | python -m trading_core.cli build-and-audit-a-share-scores --as-of-date 2026-06-26 | 13.896827 |
| 5 | stage_05_candidate_generation | passed | python -m trading_core.cli generate-and-audit-a-share-candidates --as-of-date 2026-06-26 | 6.082343 |
| 6 | stage_06_virtual_portfolio_construction | passed | python -m trading_core.cli build-and-audit-a-share-virtual-portfolios --as-of-date 2026-06-26 | 0.430734 |
| 7 | stage_07_daily_briefing | passed | python -m trading_core.cli build-and-audit-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26 | 0.133327 |
| 8 | stage_08_virtual_portfolio_tracking | passed | python -m trading_core.cli build-and-audit-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26 | 1.120609 |
| 9 | stage_09_workflow_audit | passed | python -m trading_core.cli audit-a-share-daily-research-workflow --as-of-date 2026-06-26 | 0.000000 |
| 10 | stage_10_owner_summary | passed | write owner-facing A-share daily workflow summary | 0.000000 |

## Boundary
- Workflow orchestration only.
- Old run-daily was not called.
- No broker connection was made.
- No real orders were placed.
- No order preview was generated.
- Not live trading ready.
