# A-Share Daily Workflow Source Trace

- trace_id: A-SHARE-DAILY-WORKFLOW-SOURCE-TRACE
- as_of_date: 2026-06-26
- mode: build_from_existing_data
- source_trace_complete: true
- forbidden_path_hits: []

| path | exists | sha256 |
|---|---:|---|
| data/equity_market/history | true |  |
| data/equity_selection/daily/2026-06-26/tradable_universe.json | true | ff8b4ebae6f7918a2d4a6f2f50118ce02e5b51ea05cf62cb4c67ebfb7f1c259a |
| data/equity_selection/daily/2026-06-26/tradable_universe_manifest.json | true | b11dee928585d223754da4dff60d7580ce7df6a557f5fc81a20d9f002a3f29c7 |
| data/equity_features/daily/2026-06-26/feature_manifest.json | true | debef12dc2361e696cbcc93c900020028da97fbae68cbf5c71a39b308b452589 |
| data/equity_scores/daily/2026-06-26/score_manifest.json | true | 7415cefd63a7841e7448835b8ef220d3552ac4b3c64fdb79cb171404d872fd83 |
| data/equity_selection/daily/2026-06-26/candidate_manifest.json | true | 35a89c7bd98a28d816df50cd4450791e99d320355e0c06257d75fdf013d2c2bc |
| data/equity_portfolios/daily/2026-06-26/portfolio_manifest.json | true | 62610caa98885be73e7d16ce62d190927dabb8895b306fe28a91677b44a6735b |
| data/equity_briefings/daily/2026-06-26/briefing_manifest.json | true | 8bbad188fd65afccca118c6b48f029cfa8f99611ff6b78f24c29c974cacd3421 |
| data/equity_portfolio_tracking/daily/2026-06-26/tracking_manifest.json | true | 4aee40da0f618adcacd82302e89a47480c14717d99b85b4090a8ca1f4a884f5f |
| data/equity_data_quality/a_share_tradable_universe_audit.json | true | c52ffce712fd97943e633141b78b98831e6678cda35156fde2509bebe78cadda |
| data/equity_data_quality/a_share_multi_horizon_feature_audit.json | true | 3aa6477294afc46f7f9d7a18bdf66a2c3091ea8d6bef6eafd6c7350c2a255d0a |
| data/equity_data_quality/a_share_scoring_audit.json | true | 37196a6aef1d6cca52931f2a3e304ec50af2e351c73221ed3ed3214d77a2c593 |
| data/equity_data_quality/a_share_candidate_generation_audit.json | true | 40ae2f38386148386eb1b5af5a01a2f2e2fd9e6bc611245492c4ffe766186d9a |
| data/equity_data_quality/a_share_virtual_portfolio_construction_audit.json | true | a4df8be6e16fc6d05a51bd0747fc8394a4fe6b3343327302b7c1ea582d8b76e5 |
| data/equity_data_quality/a_share_daily_stock_selection_briefing_audit.json | true | c7f210cfb8eddbde09d482aa78697d25b88186b9c61c5a5275ee6a3f85255b19 |
| data/equity_data_quality/a_share_virtual_portfolio_tracking_audit.json | true | d49e5df8ca380c617b5768f2df001151093ffdd72a1decf268756d0558884dd3 |
| data/equity_workflows/daily/2026-06-26/workflow_config.json | true | 5de510a2b17c7db3354d919013095b3796510484a70ee4a402e622e42d1d151e |
| data/equity_workflows/daily/2026-06-26/workflow_preflight.json | true | fd4c0a3550fbee9e3790b7b01d7147761b1e87ca579f57840007e0999061ffb7 |
| data/equity_workflows/daily/2026-06-26/workflow_stage_manifest.json | true | 8a4a3ee4df43093ee510cb853e8508b13dbcb67d477638ef518552b9a6cb9b17 |
| data/equity_workflows/daily/2026-06-26/workflow_run_manifest.json | true | fad9142c2f15dc55c21fe3bc068538b835c229bfd9eb7b2a6a54a747da165905 |
| data/equity_workflows/daily/2026-06-26/workflow_boundary_check.json | true | 2c6b3b7ec5b4442b9541c99e0dbe811bb76ebf87c3a81552c5503acefab55dbe |

## Stage Commands

| stage | status | command |
|---|---|---|
| stage_00_preflight | passed | python -m trading_core.cli preflight-a-share-daily-workflow --as-of-date 2026-06-26 |
| stage_01_data_readiness | passed | verify historical A-share data panels |
| stage_02_tradable_universe | passed | python -m trading_core.cli build-and-audit-a-share-tradable-universe --as-of-date 2026-06-26 |
| stage_03_feature_engineering | passed | python -m trading_core.cli build-and-audit-a-share-multi-horizon-features --as-of-date 2026-06-26 |
| stage_04_scoring | passed | python -m trading_core.cli build-and-audit-a-share-scores --as-of-date 2026-06-26 |
| stage_05_candidate_generation | passed | python -m trading_core.cli generate-and-audit-a-share-candidates --as-of-date 2026-06-26 |
| stage_06_virtual_portfolio_construction | passed | python -m trading_core.cli build-and-audit-a-share-virtual-portfolios --as-of-date 2026-06-26 |
| stage_07_daily_briefing | passed | python -m trading_core.cli build-and-audit-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26 |
| stage_08_virtual_portfolio_tracking | passed | python -m trading_core.cli build-and-audit-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26 |
| stage_09_workflow_audit | passed | python -m trading_core.cli audit-a-share-daily-research-workflow --as-of-date 2026-06-26 |
| stage_10_owner_summary | passed | write owner-facing A-share daily workflow summary |
