# CLI Reference

Each command is virtual, file-backed, or research-only. Commands must not be treated as a broker interface.

| Category | Command | Purpose | Writes to | Does not write to | Safety notes |
|---|---|---|---|---|---|
| Core / daily | `init` | Create project directories | data directories, outputs directories | broker, live orders | setup only |
| Core / daily | `load-macro` | Load macro signal rows | stdout | orders/trades/portfolio/accounts | read-only |
| Core / daily | `run-daily` | Run virtual daily workflow | data signals/orders/trades/portfolios, outputs/daily | broker, live orders | virtual only |
| Core / daily | `generate-signals` | Planned daily signal step | virtual artifacts | broker | not live |
| Core / daily | `generate-orders` | Planned virtual order step | virtual artifacts | broker | not live |
| Core / daily | `execute` | Planned virtual execution step | virtual artifacts | broker | not live |
| Core / daily | `mark` | Planned mark-to-market step | virtual artifacts | broker | not live |
| Core / daily | `benchmark` | Planned benchmark step | data/benchmarks | broker | research only |
| Core / daily | `attribution` | Planned attribution step | data/attribution | broker | research only |
| Core / daily | `report` | Planned daily report step | outputs/daily | broker | report only |
| Health / consistency | `health` | Load or generate runtime health | data/runtime when daily fallback occurs | broker | may call run-daily only if health missing |
| Health / consistency | `summarize-health` | Summarize health over a range | stdout | orders/trades/portfolio/accounts | read-only |
| Health / consistency | `check-consistency` | Check daily accounting consistency | outputs/consistency | broker | audit only |
| Health / consistency | `check-consistency-range` | Check consistency over range | outputs/consistency | broker | audit only |
| Data acquisition / validation | `import-prices` | Import historical CSV prices | data/raw | orders/trades/portfolio/accounts | data only |
| Data acquisition / validation | `fetch-prices` | Fetch configured prices | configured output path | orders/trades/portfolio/accounts | data only |
| Data acquisition / validation | `merge-price-data` | Merge price files | configured output path | orders/trades/portfolio/accounts | data only |
| Data acquisition / validation | `validate-data-package` | Validate a data package | validation outputs | orders/trades/portfolio/accounts | validation only |
| Data acquisition / validation | `real-data-validation-report` | Build validation report | outputs/validation | orders/trades/portfolio/accounts | report only |
| Backtest / replay | `backtest` | Run historical backtest | data/backtests, outputs/backtests | main daily ledger | historical only |
| Backtest / replay | `walk-forward` | Run walk-forward summaries | stdout | main daily ledger | research only |
| Backtest / replay | `run-backtest-batch` | Run batch backtests | data/backtests, outputs/backtests | main daily ledger | historical only |
| Backtest / replay | `replay-dry-run` | Replay historical dry-run | data/replays, outputs/replays | main daily ledger by default | not forward dry-run |
| Backtest / replay | `replay-last-trading-days` | Replay last N trading days | data/replays, outputs/replays | main daily ledger by default | not forward dry-run |
| Backtest / replay | `audit-dry-run` | Audit dry-run range | outputs/audit or outputs/validation | orders/trades/portfolio/accounts | audit only |
| Backtest / replay | `dry-run-validation-report` | Build dry-run validation report | outputs/validation | orders/trades/portfolio/accounts | not proof of future performance |
| Feature / label | `build-features` | Build feature matrix | data/features, outputs/features | orders/trades/portfolio/accounts | research only |
| Feature / label | `build-labels` | Build label matrix | data/labels, outputs/labels | run-daily | labels are not used in daily trading |
| Feature / label | `build-ml-dataset` | Build walk-forward ML dataset | data/ml, outputs/ml | run-daily | research only |
| ML shadow | `train-ml-shadow` | Train shadow model scaffold | data/ml, outputs/ml | strategy state | shadow only |
| ML shadow | `predict-ml-shadow` | Generate shadow predictions | data/ml | orders/trades/portfolio/accounts | shadow only |
| ML shadow | `generate-ml-shadow-signals` | Generate shadow signals | data/shadow, outputs/shadow | main daily ledger | shadow output is not an order |
| ML shadow | `ml-shadow-leaderboard` | Build shadow leaderboard | data/shadow, outputs/shadow | strategy state | not promotion |
| ML shadow | `ml-shadow-report` | Build shadow report | outputs/shadow | orders/trades/portfolio/accounts | report only |
| Experiments | `register-experiment` | Register experiment config | data/experiments | strategy state | registry only |
| Experiments | `list-experiments` | List experiments | stdout | orders/trades/portfolio/accounts | read-only |
| Experiments | `show-experiment` | Show one experiment | stdout | orders/trades/portfolio/accounts | read-only |
| Experiments | `run-parameter-sweep` | Run parameter sweep | data/experiments, outputs/experiments | strategy state | shadow experiment only |
| Experiments | `compare-strategies` | Compare strategy artifacts | data/experiments, outputs/experiments | promotion | comparison only |
| Experiments | `simulate-promotion` | Simulate promotion status | data/experiments, outputs/experiments | strategy state | simulation is not promotion |
| Experiments | `update-mistake-patterns` | Build diagnostic pattern library | data/experiments, outputs/experiments | strategy parameters | diagnostic only |
| Experiments | `experiment-dashboard` | Build experiment dashboard | data/experiments, outputs/experiments | promotion | read-only summary |
| Reports | `weekly-research-report` | Generate weekly research report | data/reports, outputs/reports | orders/trades/portfolio/accounts | not admission gate |
| Reports | `monthly-research-report` | Generate monthly research report | data/reports, outputs/reports | orders/trades/portfolio/accounts | not admission gate |
| Reports | `system-dashboard` | Generate system dashboard | data/system, outputs/system | orders/trades/portfolio/accounts | status only |
| Reports | `project-status-report` | Generate project status report | data/system, outputs/system | orders/trades/portfolio/accounts | governance only |
| Reports | `run-research-pipeline` | Run reporting pipeline | data/reports, data/system, outputs/reports, outputs/system | run-daily | reporting only |
| Reports | `leaderboard` | Build strategy leaderboard | outputs/strategy-leaderboard | broker | research only |
| Reports | `export-summary` | Export trading summary | data/exports | broker | virtual summary |
| Reports | `acceptance-report` | Write acceptance materials | outputs | broker | documentation only |
| Reports | `final-handoff-review` | Generate final human handoff review | data/system, outputs/system | orders/trades/portfolio/accounts | handoff only |
| Reports | `report-index` | Generate report index page | data/system, outputs/system | orders/trades/portfolio/accounts | index only |
| Reports | `latest-artifact` | Locate latest artifact by type | data/system, outputs/system | orders/trades/portfolio/accounts | locator only, does not open files |
| Reports | `artifact-browser` | Generate human artifact browser | data/system, outputs/system | orders/trades/portfolio/accounts | browser only |
| Reports | `quick-status` | Generate quick project status | data/system, outputs/system | orders/trades/portfolio/accounts | status only |
| Audits | `audit-experiment-system` | Audit experiment system | data/experiments, outputs/audit | strategy state | audit only |
| Audits | `audit-reporting-system` | Audit reporting system | data/system, outputs/audit | orders/trades/portfolio/accounts | audit only |
| Audits | `cli-inventory` | Generate CLI inventory | data/system, outputs/system | orders/trades/portfolio/accounts | inventory only |
| Audits | `artifact-inventory` | Generate artifact inventory | data/system, outputs/system | orders/trades/portfolio/accounts | inventory only |
| Audits | `system-smoke-test` | Run non-trading smoke checks | data/system, outputs/system | orders/trades/portfolio/accounts | smoke only |
| Audits | `boundary-regression-audit` | Audit safety boundary regression | data/system, outputs/audit | orders/trades/portfolio/accounts | static audit only |
| Audits | `system-integrity-audit` | Audit v0.5.1 system integrity | data/system, outputs/audit | orders/trades/portfolio/accounts | release audit only |
| Audits | `usability-audit` | Audit v0.5.2 usability polish | data/system, outputs/audit | orders/trades/portfolio/accounts | usability audit only |
| Audits | `forward-dry-run-readiness` | Audit readiness to prepare a 30 trading-day forward dry-run | data/system, outputs/system, outputs/audit | orders/trades/portfolio/accounts | readiness only; does not start forward dry-run |
| Audits | `admission` | Run admission gate research check | stdout | broker | not automatic promotion |
| Evolution | `score-signals` | Planned signal scoring | research artifacts | broker | not live |
| Evolution | `classify-mistakes` | Planned mistake classification | research artifacts | broker | diagnostic only |
| Evolution | `score-strategies` | Planned strategy scoring | research artifacts | strategy state | not promotion |
| Evolution | `update-rule-memory` | Planned rule memory update | research artifacts | strategy state | research only |
| Evolution | `update-experiment-queue` | Planned queue update | research artifacts | strategy state | research only |
| Evolution | `run-evolution` | Planned evolution run | research artifacts | strategy state | no auto promotion |
