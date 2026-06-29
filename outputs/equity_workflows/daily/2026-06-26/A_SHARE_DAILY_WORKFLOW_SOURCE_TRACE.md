# A-Share Daily Workflow Source Trace

- trace_id: A-SHARE-DAILY-WORKFLOW-SOURCE-TRACE
- as_of_date: 2026-06-26
- mode: build_from_existing_data
- source_trace_complete: true
- forbidden_path_hits: []

| path | exists | sha256 |
|---|---:|---|
| data/equity_market/history | true |  |
| data/equity_selection/daily/2026-06-26/tradable_universe.json | true | f680cae08302fd5d45147ef3cf4a5ee18fe9f07d6a5217dd289b3b4406be407f |
| data/equity_selection/daily/2026-06-26/tradable_universe_manifest.json | true | 7f9439bbe7f234aba9fc71e3a540547c6639040b246b16618d649c4c8f1e1a2d |
| data/equity_features/daily/2026-06-26/feature_manifest.json | true | df11e3c9ac0bed0a3f10151daafc59ee866e40b5b855e0ee6f0382fdcd6cf8c2 |
| data/equity_scores/daily/2026-06-26/score_manifest.json | true | cdf143c5a86302051894a81e486e30ee8631e4f706a2e5ea6fa843749b3f9d07 |
| data/equity_selection/daily/2026-06-26/candidate_manifest.json | true | 0d55632badcf3214198cc2a1c273b1ba24e5b68b3032d3017c1c2b7635f27101 |
| data/equity_portfolios/daily/2026-06-26/portfolio_manifest.json | true | 9f031f287ea0e863d80b3261a73b80f7a168a60f4e9f3dc89cda58f6b6aa3d90 |
| data/equity_briefings/daily/2026-06-26/briefing_manifest.json | true | f75faac6002feb2bce6236d180e5f4c091f14d8b524e5e038325b26451667c2a |
| data/equity_portfolio_tracking/daily/2026-06-26/tracking_manifest.json | true | 522d5b7a5a2b050827afaf0e69dccb3632423fe26eae1c4ed9ea3f12f1a646d5 |
| data/equity_data_quality/a_share_tradable_universe_audit.json | true | c52ffce712fd97943e633141b78b98831e6678cda35156fde2509bebe78cadda |
| data/equity_data_quality/a_share_multi_horizon_feature_audit.json | true | 3aa6477294afc46f7f9d7a18bdf66a2c3091ea8d6bef6eafd6c7350c2a255d0a |
| data/equity_data_quality/a_share_scoring_audit.json | true | 37196a6aef1d6cca52931f2a3e304ec50af2e351c73221ed3ed3214d77a2c593 |
| data/equity_data_quality/a_share_candidate_generation_audit.json | true | 40ae2f38386148386eb1b5af5a01a2f2e2fd9e6bc611245492c4ffe766186d9a |
| data/equity_data_quality/a_share_virtual_portfolio_construction_audit.json | true | a4df8be6e16fc6d05a51bd0747fc8394a4fe6b3343327302b7c1ea582d8b76e5 |
| data/equity_data_quality/a_share_daily_stock_selection_briefing_audit.json | true | c7f210cfb8eddbde09d482aa78697d25b88186b9c61c5a5275ee6a3f85255b19 |
| data/equity_data_quality/a_share_virtual_portfolio_tracking_audit.json | true | d49e5df8ca380c617b5768f2df001151093ffdd72a1decf268756d0558884dd3 |
| data/equity_workflows/daily/2026-06-26/workflow_config.json | true | 5de510a2b17c7db3354d919013095b3796510484a70ee4a402e622e42d1d151e |
| data/equity_workflows/daily/2026-06-26/workflow_preflight.json | true | 412e6e6870fd70aad81e9cd1c00fb0b448ce05b61eed58280af912f4392d0e25 |
| data/equity_workflows/daily/2026-06-26/workflow_stage_manifest.json | true | 006b642ff1c4bf287c5e7433b593eeadb6ae24779b3f45c10f8ec422452aee65 |
| data/equity_workflows/daily/2026-06-26/workflow_run_manifest.json | true | b1a3ef4eb087f422888708678307da064ed3894b0198a3d83668054fdccdb71a |
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
