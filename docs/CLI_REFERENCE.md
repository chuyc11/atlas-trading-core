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
| Backtest / replay | `global-briefing-contract` | Generate accepted historical macro signal package contract | data/system, outputs/system | orders/trades/portfolio/accounts | contract only; no network |
| Backtest / replay | `global-briefing-package-manifest` | Scan local historical global-briefing package files | data/system, outputs/system | orders/trades/portfolio/accounts | local files only; no network |
| Backtest / replay | `normalize-global-briefing-package` | Normalize a local real package to the v1 global-briefing signal contract | data/global_briefing/normalized, data/system, outputs/system | orders/trades/portfolio/accounts | normalization only; replay not started |
| Backtest / replay | `audit-global-briefing-package-coverage` | Audit normalized package coverage and point-in-time safety | data/system, outputs/audit | orders/trades/portfolio/accounts | coverage audit only; replay not started |
| Backtest / replay | `run-global-briefing-real-package-replay` | Run the local real package normalization, validation, coverage audit, isolated replay, and evaluation workflow | data/global_briefing/normalized, data/system, data/replays/global_briefing, outputs/replays/global_briefing | main daily ledger | isolated replay only; no network; not forward dry-run |
| Backtest / replay | `global-briefing-real-package-report` | Summarize the real package integration workflow and limitations | data/system, outputs/replays/global_briefing | orders/trades/portfolio/accounts | report only; not strategy proof |
| Backtest / replay | `global-briefing-warning-triage` | Classify warnings from v0.5.6 real-package-style artifacts | data/system, outputs/system | orders/trades/portfolio/accounts | triage only; not production acceptance |
| Backtest / replay | `global-briefing-evidence-quality-report` | Explain evidence levels and production-readiness limitations | data/system, outputs/system | orders/trades/portfolio/accounts | report only; production readiness remains false |
| Backtest / replay | `global-briefing-production-acceptance-criteria` | Write future production package acceptance criteria | data/system, outputs/system, docs | orders/trades/portfolio/accounts | criteria only; does not accept a package |
| Backtest / replay | `historical-data-source-resolution` | Resolve source priority for authorized historical packages A-I | data/system, outputs/system | orders/trades/portfolio/accounts | resolution only; no download |
| Backtest / replay | `download-historical-data-packages` | Download or load authorized historical packages A-I with package-level status, checksum, provenance, and fail-soft behavior | data/market/historical/authorized, data/global_briefing/authorized, data/system, outputs/system | orders/trades/portfolio/accounts | historical data authorization is not trading authorization |
| Backtest / replay | `normalize-historical-data-packages` | Normalize downloaded packages and build `GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1` | data/global_briefing/authorized/packages, data/global_briefing/normalized, data/system, outputs/system | orders/trades/portfolio/accounts | proxy signals are not internal global-briefing signals |
| Backtest / replay | `audit-historical-data-quality` | Audit coverage, checksum, provenance, PIT safety, proxy contract, secret leakage, and protected paths for packages A-J | data/system, outputs/audit | orders/trades/portfolio/accounts | quality audit only |
| Backtest / replay | `run-full-historical-proxy-replay` | Run isolated historical replay using the unified proxy signal package | data/replays/global_briefing, outputs/replays/global_briefing | main daily ledger | isolated historical replay only; not forward dry-run validation |
| Backtest / replay | `historical-data-acquisition-report` | Summarize A-J package status, production GB package status, proxy status, quality audit, replay, and boundaries | data/system, outputs/system | orders/trades/portfolio/accounts | report only; not strategy proof |
| Backtest / replay | `historical-warning-inventory` | Group and classify historical data quality and proxy replay warnings while preserving raw warning counts | data/system, outputs/system | orders/trades/portfolio/accounts | inventory only; not production acceptance |
| Backtest / replay | `close-historical-data-gaps` | Repair or proxy EPU/OECD gaps, rebuild proxy packages, run quality audit, grouped replay, acquisition report/audit, and warning inventory | data/global_briefing/authorized, data/global_briefing/normalized, data/replays/global_briefing, data/system, outputs/system, outputs/audit, outputs/replays/global_briefing | main daily ledger | historical gap closure only; no run-daily, no labels, no ML shadow, no experiments, no promotion |
| Backtest / replay | `historical-data-gap-closure-report` | Summarize v0.5.7 baseline to v0.5.7.1 EPU/OECD repair, warning reduction, coverage, and boundaries | data/system, outputs/system | orders/trades/portfolio/accounts | report only; historical data authorization is not trading authorization |
| Backtest / replay | `day0-data-freeze` | Freeze accepted day-0 research inputs for a future forward dry-run | data/system, outputs/system | orders/trades/portfolio/accounts | data freeze only; does not start forward dry-run |
| Backtest / replay | `day0-warning-register` | Classify accepted, unresolved, and blocking warnings before future day 1 | data/system, outputs/system | orders/trades/portfolio/accounts | warning register only |
| Backtest / replay | `day0-blocking-conditions` | Define fail-closed day-0 start gate conditions | data/system, outputs/system | orders/trades/portfolio/accounts | conditions only; manual confirmation still required |
| Backtest / replay | `day0-run-daily-preflight` | Generate a run-daily preflight checklist and preview-only command | data/system, outputs/system | orders/trades/portfolio/accounts | does not execute run-daily |
| Backtest / replay | `day0-manual-confirmation-packet` | Generate manual confirmation packet with all fields default false | data/system, outputs/system | orders/trades/portfolio/accounts | no auto-confirmation |
| Backtest / replay | `forward-dry-run-operating-calendar` | Generate a 30 trading-day operating calendar and daily log template | data/system, outputs/system | orders/trades/portfolio/accounts | calendar/template only; forward dry-run not started |
| Backtest / replay | `day0-readiness-report` | Summarize day-0 readiness pack and manual confirmation status | data/system, outputs/system | orders/trades/portfolio/accounts | report only |
| Planning | `plan-checklist` | Extract R001-R024 MVP requirements into a machine-readable checklist | data/system, outputs/system | orders/trades/portfolio/accounts | checklist only; does not authorize day 1 |
| Planning | `mvp-requirement-map` | Map MVP requirements to candidate repo evidence | data/system, outputs/system | orders/trades/portfolio/accounts | evidence map only |
| Planning | `artifact-coverage-scanner` | Scan modules, tests, artifacts, audits, reports, and docs as metadata-only evidence candidates | data/system, outputs/system | orders/trades/portfolio/accounts | scanner only |
| Planning | `classify-mvp-gaps` | Classify each MVP requirement as passed, partial, missing, deferred, or not applicable | data/system, outputs/system | orders/trades/portfolio/accounts | classification only |
| Planning | `classify-day1-blockers` | Extract day-1 blockers and manual-acceptance items from MVP gap classification | data/system, outputs/system | orders/trades/portfolio/accounts | classifier only; day 1 remains disallowed by default |
| Planning | `next-work-register` | Recommend the next work package from gap and blocker classifications | data/system, outputs/system | orders/trades/portfolio/accounts | register only |
| Execution | `ashare-execution-gap-plan` | Build v0.5.9 execution blocker hardening plan from v0.5.8.1 artifacts | data/system, outputs/system | orders/trades/portfolio/accounts | planning only |
| Execution | `ashare-trading-calendar-audit` | Generate and audit SSE/SZSE/HKEX trading calendar contract | data/system, outputs/system, outputs/audit | orders/trades/portfolio/accounts | calendar audit only |
| Execution | `execution-timeline-contract` | Generate T-day close signal and T+1 execution timeline contract | data/system, outputs/system | orders/trades/portfolio/accounts | contract only |
| Execution | `ashare-price-status-contract` | Generate fail-closed tradability contract for suspension, missing price, limit up/down, ST, and new listing status | data/system, outputs/system | orders/trades/portfolio/accounts | contract only |
| Execution | `ashare-lot-and-position-contract` | Generate board lot, odd lot, cash, position, and available-share contract | data/system, outputs/system | orders/trades/portfolio/accounts | contract only |
| Execution | `ashare-execution-cost-contract` | Generate fee, tax, slippage, and fill price contract | data/system, outputs/system | orders/trades/portfolio/accounts | contract only |
| Execution | `virtual-execution-contract` | Generate integrated virtual execution contract | data/system, outputs/system | orders/trades/portfolio/accounts | contract only |
| Execution | `audit-isolated-ledger-invariants` | Audit isolated virtual execution ledger invariants | data/system, data/replays/global_briefing, outputs/audit | main ledger | isolated audit only |
| Execution | `execution-aware-replay-smoke` | Run isolated execution-aware replay smoke with accepted and rejected order scenarios | data/system, data/replays/global_briefing, outputs/system, outputs/audit | main ledger | isolated smoke only; not forward validation |
| Execution | `reclassify-day1-blockers-after-execution-hardening` | Reclassify v0.5.8.1 day-1 blockers after v0.5.9 execution artifacts | data/system, outputs/system | orders/trades/portfolio/accounts | reclassification only; day 1 still not started |
| Backtest / replay | `validate-global-briefing-signals` | Validate historical global-briefing signal package | data/system, outputs/system | orders/trades/portfolio/accounts | validation only; replay not started |
| Backtest / replay | `build-global-briefing-replay-bundle` | Align historical macro signals to price replay dates | data/replays/global_briefing, outputs/replays/global_briefing | orders/trades/portfolio/accounts | macro input only; not a trading signal |
| Backtest / replay | `replay-global-briefing-history` | Run isolated historical global-briefing replay harness with `--execution-mode isolated` by default | data/replays/global_briefing, outputs/replays/global_briefing | main daily ledger | isolated replay only; not forward dry-run |
| Backtest / replay | `global-briefing-replay-report` | Evaluate replay completeness and boundaries | data/replays/global_briefing, outputs/replays/global_briefing | orders/trades/portfolio/accounts | research review only; not strategy proof |
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
| Audits | `audit-global-briefing-replay` | Audit full global-briefing historical replay harness | data/system, outputs/audit | orders/trades/portfolio/accounts | historical replay harness only; no promotion |
| Audits | `audit-isolated-replay-adapter` | Audit isolated replay execution adapter and ledger paths | data/system, outputs/audit | orders/trades/portfolio/accounts | adapter audit only; not forward validation |
| Audits | `audit-global-briefing-real-package-integration` | Audit local real package integration readiness for the v0.5.6 release tag | data/system, outputs/audit | orders/trades/portfolio/accounts | release audit only; not live readiness |
| Audits | `audit-global-briefing-evidence-quality` | Audit warning triage, evidence quality report, and production acceptance criteria | data/system, outputs/audit | orders/trades/portfolio/accounts | evidence-quality audit only |
| Audits | `audit-historical-data-acquisition` | Audit v0.5.7 source resolution, downloads, normalization, quality, proxy replay, report, protected paths, secrets, and wording | data/system, outputs/audit | orders/trades/portfolio/accounts | release audit only; no run-daily, no labels, no ML shadow, no experiments, no promotion |
| Audits | `audit-historical-data-gap-closure` | Audit v0.5.7.1 gap closure workflow, EPU/OECD repair, proxy rebuild, warning inventory, grouped replay warnings, acquisition audit, protected paths, secrets, and wording | data/system, outputs/audit | orders/trades/portfolio/accounts | release audit only; not forward dry-run validation, not live readiness, not strategy proof |
| Audits | `audit-day0-readiness` | Audit v0.5.8 day-0 readiness pack, manual confirmation defaults, preflight preview-only status, protected paths, and wording | data/system, outputs/audit | orders/trades/portfolio/accounts | release audit only; does not start forward dry-run |
| Audits | `audit-plan-alignment` | Audit v0.5.8.1 plan checklist, MVP map, artifact scan, gap classification, day-1 blockers, and next work register | data/system, outputs/audit | orders/trades/portfolio/accounts | plan alignment audit only; not day 1 authorization |
| Audits | `audit-ashare-execution-rules` | Audit v0.5.9 A-share execution hardening, isolated ledger invariants, replay smoke, blocker reclassification, boundaries, and wording | data/system, outputs/audit | orders/trades/portfolio/accounts | release audit only; not forward dry-run validation |
| Audits | `admission` | Run admission gate research check | stdout | broker | not automatic promotion |
| Evolution | `score-signals` | Planned signal scoring | research artifacts | broker | not live |
| Evolution | `classify-mistakes` | Planned mistake classification | research artifacts | broker | diagnostic only |
| Evolution | `score-strategies` | Planned strategy scoring | research artifacts | strategy state | not promotion |
| Evolution | `update-rule-memory` | Planned rule memory update | research artifacts | strategy state | research only |
| Evolution | `update-experiment-queue` | Planned queue update | research artifacts | strategy state | research only |
| Evolution | `run-evolution` | Planned evolution run | research artifacts | strategy state | no auto promotion |
