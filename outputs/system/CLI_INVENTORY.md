# CLI Inventory

| command | category | purpose | writes_to | safety |
|---|---|---|---|---|
| acceptance-report | reports | Write acceptance report materials | outputs | documentation_only |
| admission | audits | Run admission research check | stdout | not_auto_promotion |
| artifact-inventory | audits | Generate artifact inventory | data/system, outputs/system | inventory_only, not_run_daily |
| attribution | core / daily | Planned attribution generation | data/attribution | research_only |
| audit-dry-run | backtest / replay | Audit dry-run range | outputs/audit | audit_only |
| audit-experiment-system | audits | Audit experiment system | data/experiments, outputs/audit | audit_only |
| audit-reporting-system | audits | Audit reporting system | data/system, outputs/audit | audit_only |
| backtest | backtest / replay | Run historical backtest | data/backtests, outputs/backtests | historical_only |
| benchmark | core / daily | Planned benchmark generation | data/benchmarks | research_only |
| boundary-regression-audit | audits | Audit boundary regressions | data/system, outputs/audit | audit_only, not_run_daily |
| build-features | feature / label | Build feature matrix | data/features, outputs/features | research_only |
| build-labels | feature / label | Build label matrix | data/labels, outputs/labels | not_run_daily_input |
| build-ml-dataset | feature / label | Build ML walk-forward dataset | data/ml, outputs/ml | research_only |
| check-consistency | health / consistency | Check daily consistency | outputs/consistency | audit_only |
| check-consistency-range | health / consistency | Check range consistency | outputs/consistency | audit_only |
| classify-mistakes | evolution | Planned mistake classification | data/evolution | diagnostic_only |
| cli-inventory | audits | Generate CLI inventory | data/system, outputs/system | inventory_only, not_run_daily |
| compare-strategies | experiments | Compare strategies | data/experiments, outputs/experiments | comparison_only |
| dry-run-validation-report | backtest / replay | Build dry-run validation report | outputs/validation | not_forward_proof |
| execute | core / daily | Planned virtual execution | data/trades | virtual_only, no_broker |
| experiment-dashboard | experiments | Build experiment dashboard | data/experiments, outputs/experiments | read_only_summary |
| export-summary | reports | Export virtual trading summary | data/exports | virtual_summary |
| fetch-prices | data acquisition / validation | Fetch price data | configured output | data_only |
| generate-ml-shadow-signals | ml shadow | Generate shadow signals | data/shadow, outputs/shadow | shadow_output_is_not_order |
| generate-orders | core / daily | Planned virtual order generation | data/orders | virtual_only, no_broker |
| generate-signals | core / daily | Planned virtual signal generation | data/signals | virtual_only |
| health | health / consistency | Load or generate runtime health | data/runtime | virtual_only |
| import-prices | data acquisition / validation | Import historical prices | data/raw | data_only |
| init | core / daily | Initialize project directories | data, outputs | setup_only |
| leaderboard | reports | Build strategy leaderboard | outputs/strategy-leaderboard | research_only |
| list-experiments | experiments | List experiments | stdout | read_only |
| load-macro | core / daily | Load macro signals | stdout | read_only |
| mark | core / daily | Planned mark-to-market | data/portfolios | virtual_only |
| merge-price-data | data acquisition / validation | Merge price datasets | configured output | data_only |
| ml-shadow-leaderboard | ml shadow | Build shadow leaderboard | data/shadow, outputs/shadow | not_promotion |
| ml-shadow-report | ml shadow | Build shadow report | outputs/shadow | report_only |
| monthly-research-report | reports | Generate monthly research report | data/reports, outputs/reports | research_only, not_an_admission_gate |
| predict-ml-shadow | ml shadow | Generate shadow predictions | data/ml | shadow_only |
| project-status-report | reports | Generate project status report | data/system, outputs/system | governance_only |
| real-data-validation-report | data acquisition / validation | Build real data validation report | outputs/validation | report_only |
| register-experiment | experiments | Register experiment | data/experiments | registry_only |
| replay-dry-run | backtest / replay | Replay historical dry-run | data/replays, outputs/replays | historical_only |
| replay-last-trading-days | backtest / replay | Replay last trading days | data/replays, outputs/replays | historical_only |
| report | core / daily | Planned daily report | outputs/daily | report_only |
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
| validate-data-package | data acquisition / validation | Validate data package | outputs/validation | validation_only |
| walk-forward | backtest / replay | Run walk-forward summary | stdout | research_only |
| weekly-research-report | reports | Generate weekly research report | data/reports, outputs/reports | research_only, not_an_admission_gate |

## Safety Boundary
- inventory only
- run-daily not called
- no orders/trades/portfolio/accounts written
