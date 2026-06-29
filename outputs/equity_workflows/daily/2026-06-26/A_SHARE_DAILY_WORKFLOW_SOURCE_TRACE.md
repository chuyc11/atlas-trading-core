# A-Share Daily Workflow Source Trace

- trace_id: A-SHARE-DAILY-WORKFLOW-SOURCE-TRACE
- as_of_date: 2026-06-26
- mode: validate_existing_artifacts
- source_trace_complete: true
- forbidden_path_hits: []

| path | exists | sha256 |
|---|---:|---|
| data/equity_market/history | true |  |
| data/equity_selection/daily/2026-06-26/tradable_universe.json | true | 3a28e0d6b5a53260d1e61535d99230fff50e9b4262355e4ce6e0e0046d7b91eb |
| data/equity_selection/daily/2026-06-26/tradable_universe_manifest.json | true | 0a5a8d426dee93bd90343e008a5e662afc0c5803293cf00a08eaf599a9038c45 |
| data/equity_features/daily/2026-06-26/feature_manifest.json | true | c00f9d61c5c5ece4b2403665d4c8c7fb10ba219154cf519574ef6620d47afff4 |
| data/equity_scores/daily/2026-06-26/score_manifest.json | true | cfd5a577232117d1771aa509d60c9d5d2ad28205deac9c09c6d193b1c5ac9810 |
| data/equity_selection/daily/2026-06-26/candidate_manifest.json | true | 9a4bd4c13f2feeffd15ce8296e35fea659f9cb66fa7e971fdbc98fb8ec692ce7 |
| data/equity_portfolios/daily/2026-06-26/portfolio_manifest.json | true | bf757c2fa15b274a65a890e331b676a8990fe19602b335d5993a4a0b2475cbda |
| data/equity_briefings/daily/2026-06-26/briefing_manifest.json | true | 73ef565ec9068df786fd5bf7a197f750ee62b21cfad1a0f941b3e735c3116a0a |
| data/equity_portfolio_tracking/daily/2026-06-26/tracking_manifest.json | true | c2f3727a76f998dccffbf745b4af4ba758ac60fc2de97c97204766430a046f74 |
| data/equity_data_quality/a_share_tradable_universe_audit.json | true | c52ffce712fd97943e633141b78b98831e6678cda35156fde2509bebe78cadda |
| data/equity_data_quality/a_share_multi_horizon_feature_audit.json | true | 3aa6477294afc46f7f9d7a18bdf66a2c3091ea8d6bef6eafd6c7350c2a255d0a |
| data/equity_data_quality/a_share_scoring_audit.json | true | 18259c6c330257acbf190c1fe207e4f1382a35f09d9a5c865ba8319ea06a9127 |
| data/equity_data_quality/a_share_candidate_generation_audit.json | true | 28cc99eb857a9dadd7884bcc7a51d95119a50bb70432d1a0867d8fbc51b6704b |
| data/equity_data_quality/a_share_virtual_portfolio_construction_audit.json | true | a4df8be6e16fc6d05a51bd0747fc8394a4fe6b3343327302b7c1ea582d8b76e5 |
| data/equity_data_quality/a_share_daily_stock_selection_briefing_audit.json | true | c7f210cfb8eddbde09d482aa78697d25b88186b9c61c5a5275ee6a3f85255b19 |
| data/equity_data_quality/a_share_virtual_portfolio_tracking_audit.json | true | d49e5df8ca380c617b5768f2df001151093ffdd72a1decf268756d0558884dd3 |
| data/equity_workflows/daily/2026-06-26/workflow_config.json | true | a1e99479932228abbfa3e4b91b1c8381da2216b34841a0cbf8e308155744c987 |
| data/equity_workflows/daily/2026-06-26/workflow_preflight.json | true | db11ba4fa8bc1d708fe9f400e02ff299139098bbd4cd0e6e97ae151e978b4eeb |
| data/equity_workflows/daily/2026-06-26/workflow_stage_manifest.json | true | b0d4eae9ad950ba5174384abe0a1bf34fbf0390b3f7814bb53c3a5fbdcb8eaca |
| data/equity_workflows/daily/2026-06-26/workflow_run_manifest.json | true | bcd1de537423d52f705f974b4cc029e3c7c9a8d2a8c9d0e100f3dde400094c5e |
| data/equity_workflows/daily/2026-06-26/workflow_boundary_check.json | true | 4ae6e39cec0beae5bca70bacecef37ea79d43d9f83d9bed3e42c6475d733d463 |

## Stage Commands

| stage | status | command |
|---|---|---|
| stage_00_preflight | passed | python -m trading_core.cli preflight-a-share-daily-workflow --as-of-date 2026-06-26 |
| stage_01_data_readiness | passed | verify required A-share research artifacts |
| stage_02_tradable_universe | passed | verify existing artifacts for tradable_universe |
| stage_03_feature_engineering | passed | verify existing artifacts for feature_engineering |
| stage_04_scoring | passed | verify existing artifacts for scoring |
| stage_05_candidate_generation | passed | verify existing artifacts for candidate_generation |
| stage_06_virtual_portfolio_construction | passed | verify existing artifacts for virtual_portfolio_construction |
| stage_07_daily_briefing | passed | verify existing artifacts for daily_briefing |
| stage_08_virtual_portfolio_tracking | passed | verify existing artifacts for virtual_portfolio_tracking |
| stage_09_workflow_audit | passed | python -m trading_core.cli audit-a-share-daily-research-workflow --as-of-date 2026-06-26 |
| stage_10_owner_summary | passed | write owner-facing A-share daily workflow summary |
