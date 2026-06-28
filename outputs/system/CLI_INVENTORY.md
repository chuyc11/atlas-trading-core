# CLI Inventory

| command | category | purpose | writes_to | safety |
|---|---|---|---|---|
| a-share-historical-backfill-plan | a-share history | Write v0.7.1.1 historical panel backfill plan | data/equity_data_quality, outputs/equity_data_quality | plan_only, not_run_daily, no_scores, no_orders |
| acceptance-report | reports | Write acceptance report materials | outputs | documentation_only |
| admission | audits | Run admission research check | stdout | not_auto_promotion |
| artifact-browser | reports | Generate human artifact browser | data/system, outputs/system | browser_only, not_run_daily |
| artifact-inventory | audits | Generate artifact inventory | data/system, outputs/system | inventory_only, not_run_daily |
| attribution | core / daily | Planned attribution generation | data/attribution | research_only |
| audit-a-share-candidates | a-share candidates | Audit v0.7.5 candidate counts, explanations, forbidden artifacts, and boundaries | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, fail_closed, no_virtual_portfolio, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| audit-a-share-daily-research-workflow | a-share workflow | Audit v0.7.9 workflow manifests, source trace, stage status, upstream audits, and boundaries | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, fail_closed, no_day2, no_broker, no_real_orders, no_buy_sell_signals, no_order_preview |
| audit-a-share-daily-stock-selection-briefing | a-share briefings | Audit v0.7.7 briefing sections, source trace, wording, and boundaries | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, fail_closed, no_score_regeneration, no_candidate_regeneration, no_virtual_portfolio_regeneration, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| audit-a-share-data-coverage | a-share data | Audit A-share data artifact coverage and safety boundary | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, no_scores, no_orders |
| audit-a-share-data-schema | a-share data | Audit A-share data artifact schemas and sanity constraints | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, no_scores, no_orders |
| audit-a-share-feature-readiness | a-share history | Audit readiness for tradable universe and multi-horizon features | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, no_scores, no_candidates |
| audit-a-share-historical-panel-coverage | a-share history | Audit historical panel coverage against v0.7.1.1 release gates | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, fail_closed |
| audit-a-share-multi-horizon-features | a-share features | Audit v0.7.3 multi-horizon feature coverage, leakage, and boundaries | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, fail_closed, no_scores, no_candidates, no_watchlist, no_virtual_portfolio |
| audit-a-share-scores | a-share scoring | Audit v0.7.4 score ranges, ranks, forbidden artifacts, and boundaries | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, fail_closed, scores_allowed, no_candidates, no_watchlist, no_virtual_portfolio, no_broker, no_real_orders |
| audit-a-share-tradable-universe | a-share selection | Audit v0.7.2 tradable universe artifacts and boundaries | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, fail_closed, no_scores, no_candidates, no_virtual_portfolio |
| audit-a-share-virtual-portfolio-tracking | a-share tracking | Audit v0.7.8 virtual tracking ledgers, NAV, exposure, benchmark placeholders, wording, and boundaries | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, fail_closed, no_real_portfolio, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| audit-a-share-virtual-portfolios | a-share portfolios | Audit v0.7.6 virtual portfolio weights, caps, forbidden artifacts, and boundaries | data/equity_data_quality, outputs/audit | audit_only, not_run_daily, fail_closed, no_real_portfolio, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| audit-dry-run | backtest / replay | Audit dry-run range | outputs/audit | audit_only |
| audit-experiment-system | audits | Audit experiment system | data/experiments, outputs/audit | audit_only |
| audit-reporting-system | audits | Audit reporting system | data/system, outputs/audit | audit_only |
| backfill-a-share-adjusted-price-history | a-share history | Build adjusted price history panel with raw fallback labeling | data/equity_market/history | historical_backfill_only, not_run_daily, raw_fallback_recorded |
| backfill-a-share-daily-basic-history | a-share history | Build daily basic history panel with field coverage tracking | data/equity_market/history | historical_backfill_only, not_run_daily, partial_fields_allowed_with_audit |
| backfill-a-share-daily-price-history | a-share history | Backfill public A-share daily price history panel | data/equity_market/history | historical_backfill_only, not_run_daily, no_scores, no_orders |
| backfill-a-share-financial-history | a-share history | Backfill quarterly basic financial history panel | data/equity_fundamental/history | historical_backfill_only, not_run_daily, no_scores, no_orders |
| backfill-a-share-historical-panels | a-share history | Run plan, history backfill, coverage audit, and feature readiness audit | data/equity_market/history, data/equity_fundamental/history, data/equity_data_quality, outputs/equity_data_quality, outputs/audit | historical_backfill_only, not_run_daily, no_broker, no_real_orders, no_scores, no_candidates |
| backfill-a-share-historical-panels-full-market | a-share history | Run v0.7.1.2 full-market queued historical backfill with checkpoint/resume | data/equity_market/history, data/equity_fundamental/history, data/equity_data_quality, data/equity_data_quality/backfill_batches, outputs/equity_data_quality, outputs/audit | historical_backfill_only, not_run_daily, no_broker, no_real_orders, no_scores, no_candidates, fail_closed |
| backtest | backtest / replay | Run historical backtest | data/backtests, outputs/backtests | historical_only |
| benchmark | core / daily | Planned benchmark generation | data/benchmarks | research_only |
| boundary-regression-audit | audits | Audit boundary regressions | data/system, outputs/audit | audit_only, not_run_daily |
| build-a-share-daily-stock-selection-briefing | a-share briefings | Build v0.7.7 Chinese daily A-share stock selection research briefing from existing artifacts | data/equity_briefings/daily/YYYY-MM-DD, outputs/equity_briefings/daily/YYYY-MM-DD | briefing_only, read_existing_artifacts_only, not_run_daily, fail_closed, no_score_regeneration, no_candidate_regeneration, no_virtual_portfolio_regeneration, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| build-a-share-data-foundation | a-share data | Run the v0.7.1 A-share data foundation chain | data/equity_universe, data/equity_market, data/equity_industry, data/equity_fundamental, data/equity_data_quality, outputs/equity_universe, outputs/equity_data_quality, outputs/audit | data_ingestion_only, not_run_daily, no_broker, no_real_orders, no_selection, no_scores |
| build-a-share-equity-master | a-share data | Build normalized A-share equity master | data/equity_universe, outputs/equity_universe | data_ingestion_only, not_run_daily, no_selection, no_scores |
| build-a-share-historical-backfill-symbol-queue | a-share history | Build full-market A-share historical backfill queue from equity_master | data/equity_data_quality, outputs/equity_data_quality | queue_only, not_run_daily, no_scores, no_orders |
| build-a-share-multi-horizon-features | a-share features | Build v0.7.3 strict-universe multi-horizon feature artifacts | data/equity_features/daily/YYYY-MM-DD, outputs/equity_features/daily/YYYY-MM-DD | feature_engineering_only, not_run_daily, fail_closed, no_scores, no_candidates, no_watchlist, no_virtual_portfolio |
| build-a-share-scores | a-share scoring | Build v0.7.4 strict-universe long/mid/short score artifacts | data/equity_scores/daily/YYYY-MM-DD, outputs/equity_scores/daily/YYYY-MM-DD | scoring_only, scores_allowed, not_run_daily, fail_closed, no_candidates, no_watchlist, no_virtual_portfolio, no_broker, no_real_orders |
| build-a-share-tradable-universe | a-share selection | Build v0.7.2 strict/caution/excluded/unknown tradable universe buckets | data/equity_selection/daily/YYYY-MM-DD, outputs/equity_selection/daily/YYYY-MM-DD | filter_only, not_run_daily, no_broker, no_real_orders, no_scores, no_candidates, no_watchlist, no_virtual_portfolio |
| build-a-share-trading-calendar | a-share data | Build SSE/SZSE/BSE trading calendar foundation | data/equity_universe, outputs/equity_universe | data_ingestion_only, not_run_daily, no_orders |
| build-a-share-virtual-portfolio-tracking | a-share tracking | Build v0.7.8 research-only virtual portfolio tracking and paper ledgers from existing v0.7.6/v0.7.7 artifacts | data/equity_portfolio_tracking/daily/YYYY-MM-DD, outputs/equity_portfolio_tracking/daily/YYYY-MM-DD | virtual_only, research_only, read_existing_artifacts_only, not_run_daily, fail_closed, no_real_portfolio, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| build-a-share-virtual-portfolios | a-share portfolios | Build v0.7.6 long/mid/short research-only virtual portfolios and target weights | data/equity_portfolios/daily/YYYY-MM-DD, outputs/equity_portfolios/daily/YYYY-MM-DD | virtual_only, research_only, not_run_daily, fail_closed, no_real_portfolio, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| build-and-audit-a-share-daily-stock-selection-briefing | a-share briefings | Build and audit the v0.7.7 daily A-share briefing package | data/equity_briefings/daily/YYYY-MM-DD, data/equity_data_quality, outputs/equity_briefings/daily/YYYY-MM-DD, outputs/audit | briefing_only, read_existing_artifacts_only, not_run_daily, fail_closed, no_score_regeneration, no_candidate_regeneration, no_virtual_portfolio_regeneration, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| build-and-audit-a-share-multi-horizon-features | a-share features | Build and audit the v0.7.3 A-share multi-horizon feature package | data/equity_features/daily/YYYY-MM-DD, data/equity_data_quality, outputs/equity_features/daily/YYYY-MM-DD, outputs/audit | feature_engineering_only, not_run_daily, fail_closed, no_broker, no_real_orders, no_scores, no_candidates, no_watchlist, no_virtual_portfolio |
| build-and-audit-a-share-scores | a-share scoring | Build and audit the v0.7.4 A-share long/mid/short scoring package | data/equity_scores/daily/YYYY-MM-DD, data/equity_data_quality, outputs/equity_scores/daily/YYYY-MM-DD, outputs/audit | scoring_only, scores_allowed, not_run_daily, fail_closed, no_candidates, no_watchlist, no_virtual_portfolio, no_broker, no_real_orders |
| build-and-audit-a-share-tradable-universe | a-share selection | Build and audit the v0.7.2 A-share tradable universe | data/equity_selection/daily/YYYY-MM-DD, data/equity_data_quality, outputs/equity_selection/daily/YYYY-MM-DD, outputs/audit | filter_only, not_run_daily, no_broker, no_real_orders, no_scores, no_candidates, no_watchlist, no_virtual_portfolio |
| build-and-audit-a-share-virtual-portfolio-tracking | a-share tracking | Build and audit the v0.7.8 A-share virtual portfolio tracking package | data/equity_portfolio_tracking/daily/YYYY-MM-DD, data/equity_data_quality, outputs/equity_portfolio_tracking/daily/YYYY-MM-DD, outputs/audit | virtual_only, research_only, read_existing_artifacts_only, not_run_daily, fail_closed, no_real_portfolio, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| build-and-audit-a-share-virtual-portfolios | a-share portfolios | Build and audit the v0.7.6 A-share virtual portfolio package | data/equity_portfolios/daily/YYYY-MM-DD, data/equity_data_quality, outputs/equity_portfolios/daily/YYYY-MM-DD, outputs/audit | virtual_only, research_only, not_run_daily, fail_closed, no_real_portfolio, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| build-features | feature / label | Build feature matrix | data/features, outputs/features | research_only |
| build-labels | feature / label | Build label matrix | data/labels, outputs/labels | not_run_daily_input |
| build-ml-dataset | feature / label | Build ML walk-forward dataset | data/ml, outputs/ml | research_only |
| check-consistency | health / consistency | Check daily consistency | outputs/consistency | audit_only |
| check-consistency-range | health / consistency | Check range consistency | outputs/consistency | audit_only |
| classify-mistakes | evolution | Planned mistake classification | data/evolution | diagnostic_only |
| cli-inventory | audits | Generate CLI inventory | data/system, outputs/system | inventory_only, not_run_daily |
| compare-strategies | experiments | Compare strategies | data/experiments, outputs/experiments | comparison_only |
| diagnose-a-share-historical-backfill-coverage | a-share history | Diagnose v0.7.1.1 historical backfill coverage blockers | data/equity_data_quality, outputs/audit | diagnostic_only, not_run_daily, fail_closed |
| dry-run-validation-report | backtest / replay | Build dry-run validation report | outputs/validation | not_forward_proof |
| equity-data-source-manifest | a-share data | Probe public A-share data provider availability and write source manifest | data/equity_data_quality, outputs/equity_data_quality | data_ingestion_only, not_run_daily, no_broker, no_real_orders |
| execute | core / daily | Planned virtual execution | data/trades | virtual_only, no_broker |
| experiment-dashboard | experiments | Build experiment dashboard | data/experiments, outputs/experiments | read_only_summary |
| export-summary | reports | Export virtual trading summary | data/exports | virtual_summary |
| external-project-intake | planning | Scan external research repos and write v0.7 A-share selection planning artifacts | data/system, outputs/system, docs | intake_only, not_run_daily, no_broker, no_real_orders, no_third_party_code_merge |
| fetch-prices | data acquisition / validation | Fetch price data | configured output | data_only |
| final-handoff-review | reports | Generate final human handoff review | data/system, outputs/system | handoff_only, not_run_daily |
| forward-dry-run-readiness | audits | Audit readiness to prepare 30 trading-day forward dry-run | data/system, outputs/system, outputs/audit | readiness_only, not_run_daily, does_not_start_forward_dry_run |
| generate-a-share-candidates | a-share candidates | Generate v0.7.5 strict-universe long/mid/short research candidate pools | data/equity_selection/daily/YYYY-MM-DD, outputs/equity_selection/daily/YYYY-MM-DD | candidate_generation_only, not_run_daily, fail_closed, no_virtual_portfolio, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| generate-and-audit-a-share-candidates | a-share candidates | Generate and audit the v0.7.5 A-share research candidate package | data/equity_selection/daily/YYYY-MM-DD, data/equity_data_quality, outputs/equity_selection/daily/YYYY-MM-DD, outputs/audit | candidate_generation_only, not_run_daily, fail_closed, no_virtual_portfolio, no_buy_sell_signals, no_order_preview, no_broker, no_real_orders |
| generate-ml-shadow-signals | ml shadow | Generate shadow signals | data/shadow, outputs/shadow | shadow_output_is_not_order |
| generate-orders | core / daily | Planned virtual order generation | data/orders | virtual_only, no_broker |
| generate-signals | core / daily | Planned virtual signal generation | data/signals | virtual_only |
| health | health / consistency | Load or generate runtime health | data/runtime | virtual_only |
| import-prices | data acquisition / validation | Import historical prices | data/raw | data_only |
| ingest-a-share-adjusted-prices | a-share data | Build adjusted price panel with fallback coverage notes | data/equity_market | data_ingestion_only, not_run_daily, raw_fallback_recorded |
| ingest-a-share-basic-financials | a-share data | Build basic financials panel with nullable field coverage | data/equity_fundamental | data_ingestion_only, not_run_daily, partial_fields_allowed_with_audit |
| ingest-a-share-daily-basic | a-share data | Ingest A-share daily basic market indicators | data/equity_market | data_ingestion_only, not_run_daily, partial_fields_allowed_with_audit |
| ingest-a-share-daily-prices | a-share data | Ingest A-share daily OHLCV price panel | data/equity_market | data_ingestion_only, not_run_daily, no_selection, no_broker |
| ingest-a-share-industry-classification | a-share data | Build A-share industry classification panel | data/equity_industry | data_ingestion_only, not_run_daily, fallback_recorded |
| init | core / daily | Initialize project directories | data, outputs | setup_only |
| latest-artifact | reports | Locate latest artifact by type | data/system, outputs/system | locator_only, not_run_daily |
| leaderboard | reports | Build strategy leaderboard | outputs/strategy-leaderboard | research_only |
| list-experiments | experiments | List experiments | stdout | read_only |
| load-macro | core / daily | Load macro signals | stdout | read_only |
| mark | core / daily | Planned mark-to-market | data/portfolios | virtual_only |
| merge-price-data | data acquisition / validation | Merge price datasets | configured output | data_only |
| ml-shadow-leaderboard | ml shadow | Build shadow leaderboard | data/shadow, outputs/shadow | not_promotion |
| ml-shadow-report | ml shadow | Build shadow report | outputs/shadow | report_only |
| monthly-research-report | reports | Generate monthly research report | data/reports, outputs/reports | research_only, not_an_admission_gate |
| predict-ml-shadow | ml shadow | Generate shadow predictions | data/ml | shadow_only |
| preflight-a-share-daily-workflow | a-share workflow | Check v0.7.9 daily workflow readiness, versions, artifacts, CLI availability, and boundaries | data/equity_workflows/daily/YYYY-MM-DD | orchestration_only, not_run_daily, fail_closed, no_day2, no_broker, no_real_orders, no_buy_sell_signals, no_order_preview |
| project-status-report | reports | Generate project status report | data/system, outputs/system | governance_only |
| quick-status | reports | Generate quick project status | data/system, outputs/system | status_only, not_run_daily |
| real-data-validation-report | data acquisition / validation | Build real data validation report | outputs/validation | report_only |
| register-experiment | experiments | Register experiment | data/experiments | registry_only |
| replay-dry-run | backtest / replay | Replay historical dry-run | data/replays, outputs/replays | historical_only |
| replay-last-trading-days | backtest / replay | Replay last trading days | data/replays, outputs/replays | historical_only |
| report | core / daily | Planned daily report | outputs/daily | report_only |
| report-index | reports | Generate human report index | data/system, outputs/system | index_only, not_run_daily |
| run-a-share-daily-research-workflow | a-share workflow | Run the v0.7.9 A-share daily research workflow orchestration modes | data/equity_workflows/daily/YYYY-MM-DD, outputs/equity_workflows/daily/YYYY-MM-DD | orchestration_only, not_run_daily, fail_closed, no_day2, no_broker, no_real_orders, no_buy_sell_signals, no_order_preview |
| run-and-audit-a-share-daily-research-workflow | a-share workflow | Run and audit the v0.7.9 A-share daily research workflow in one command | data/equity_workflows/daily/YYYY-MM-DD, data/equity_data_quality, outputs/equity_workflows/daily/YYYY-MM-DD, outputs/audit | orchestration_only, not_run_daily, fail_closed, no_day2, no_broker, no_real_orders, no_buy_sell_signals, no_order_preview |
| run-backtest-batch | backtest / replay | Run batch backtests | data/backtests, outputs/backtests | historical_only |
| run-daily | core / daily | Run virtual daily workflow | data/signals, data/orders, data/trades, data/portfolios, outputs/daily | virtual_only, no_broker, not_live |
| run-evolution | evolution | Planned evolution workflow | data/evolution | no_auto_promotion |
| run-parameter-sweep | experiments | Run parameter sweep | data/experiments, outputs/experiments | shadow_only |
| run-research-pipeline | reports | Run research reporting pipeline | data/reports, data/system, outputs/reports, outputs/system | research_only, not_run_daily |
| score-signals | evolution | Planned signal scoring | data/evolution | research_only |
| score-strategies | evolution | Planned strategy scoring | data/evolution | not_promotion |
| show-experiment | experiments | Show experiment | stdout | read_only |
| simulate-promotion | experiments | Simulate promotion | data/experiments, outputs/experiments | simulation_is_not_promotion |
| summarize-health | health / consistency | Summarize runtime health | stdout | read_only |
| system-dashboard | reports | Generate system dashboard | data/system, outputs/system | status_only |
| system-integrity-audit | audits | Audit system integrity release candidate | data/system, outputs/audit | release_audit_only, not_run_daily |
| system-smoke-test | audits | Run non-trading system smoke test | data/system, outputs/system | smoke_only, not_run_daily |
| train-ml-shadow | ml shadow | Train shadow model | data/ml, outputs/ml | shadow_only |
| update-experiment-queue | evolution | Planned experiment queue update | data/evolution | research_only |
| update-mistake-patterns | experiments | Update mistake pattern library | data/experiments, outputs/experiments | diagnostic_only |
| update-rule-memory | evolution | Planned rule memory update | data/evolution | research_only |
| usability-audit | audits | Audit usability polish release candidate | data/system, outputs/audit | audit_only, not_run_daily |
| validate-data-package | data acquisition / validation | Validate data package | outputs/validation | validation_only |
| walk-forward | backtest / replay | Run walk-forward summary | stdout | research_only |
| weekly-research-report | reports | Generate weekly research report | data/reports, outputs/reports | research_only, not_an_admission_gate |

## Safety Boundary
- inventory only
- run-daily not called
- no orders/trades/portfolio/accounts written
