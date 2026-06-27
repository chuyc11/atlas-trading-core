# Trading Core

## What this project is

- file-backed virtual trading research system
- A-share full-market AI stock selection planning and virtual portfolio tracking research
- paper / virtual trading only
- research workflow for ETF strategies, ML shadow, experiments, and reports

## What this project is not

- not a broker integration
- not live trading
- not investment advice
- not an auto-trading system
- not an RL trading agent
- not an LLM trading decision system

## Current release

v0.7.2-a-share-tradable-universe-filter

## Completed milestones

- v0.1 core hardened
- v0.2 historical real-data validation
- v0.2.1 price-only historical replay
- v0.3 ML shadow audited
- v0.4 strategy experiment audited
- v0.5 reporting control plane audited
- v0.5.1 system integrity and documentation
- v0.5.2 usability polish
- v0.5.3 forward dry-run readiness audited
- v0.5.4 global-briefing historical replay harness audited
- v0.5.5 isolated replay execution adapter audited
- v0.5.6 real global-briefing signal integration audited
- v0.5.6.1 warning triage and evidence quality audited
- v0.5.7 authorized full historical data acquisition audited
- v0.5.7.1 historical data gap closure audited
- v0.5.8 day-0 operational readiness audited
- v0.5.8.1 plan alignment and MVP gap audited
- v0.5.9 A-share execution rules hardened
- v0.6.0 baseline strategy pack audited
- v0.6.1 daily workflow binding audited
- v0.6.2 forward dry-run start authorization pack audited
- v0.6.2.1 owner manual confirmation materialized
- v0.6.3 forward dry-run day 1 executed and audited
- v0.6.3.1 forward dry-run day1 continuation artifacts
- v0.6.3.2 forward dry-run day1 owner report pack
- v0.7.0 external project intake and A-share full-market selection plan
- v0.7.1 A-share full-market data ingestion foundation
- v0.7.1.2 A-share historical data provider expansion
- v0.7.2 A-share tradable universe filter

## Known limitations

- forward dry-run has started with virtual isolated day 1 complete; full 30d dry-run not completed
- authorized historical data access is available, but historical data authorization is not trading authorization
- authorized production global-briefing historical signal package is separately reported and may be `not_configured`
- unified proxy signals are research proxy signals, not internal global-briefing signals
- EPU may be repaired from authorized/local/API/FRED-compatible sources or represented by a policy-uncertainty proxy when official source access is unavailable
- OECD CLI may be repaired from authorized/local/API sources or represented by an authorized macro-cycle proxy explicitly marked as not official OECD CLI
- historical replay is not forward dry-run validation
- plan alignment is an audit, not day 1 authorization
- v0.5.9 hardens virtual execution rules but does not start forward dry-run
- v0.6.0 adds a research-only baseline strategy pack and does not start forward dry-run
- v0.6.1 binds daily research workflow previews using local authorized historical daily snapshots
- v0.6.2 creates a start authorization pack only and does not start forward dry-run
- v0.6.2 keeps manual confirmation false, owner authorization false, day1_start_allowed=false, day1_prompt_eligible=false, and day1_prompt_generated=false by default
- v0.6.2.1 materializes owner manual confirmation: manual_confirmation_complete=true, forward_dry_run_start_authorized=true, day1_prompt_eligible=true, day1_prompt_generated=false, and day1_start_allowed=false
- v0.6.3 executes virtual isolated forward dry-run day 1 only; it writes the forward dry-run ledger, not the main ledger
- v0.6.3.1 only fills day1 continuation artifact gaps; it does not execute day2
- v0.6.3.2 generates an owner-facing day1 report pack only; it does not execute day2, does not call run-daily, does not download real-time data, and does not call external APIs
- v0.7.0 downloads and scans external research repositories for design intake only; it does not merge third-party trading code into the main flow
- v0.7.0 starts the A-share full-market selection planning line; it does not ingest A-share market data yet, does not score stocks yet, and does not create real orders
- v0.7.1 builds the A-share data foundation only; it does not score stocks, generate candidates, generate virtual portfolios, connect a broker, place real orders, call run-daily, or execute official forward dry-run day2
- v0.7.1 may call public historical/delayed data endpoints; this is data ingestion only, not real-time trading data and not broker access
- v0.7.1 records free-source limitations in coverage/schema audits; adjusted prices, industry classification, and financial fields may be partial or fallback-labeled
- v0.7.1.1 historical panel backfill workflow is implemented and fail-closed in the current environment; public historical providers did not satisfy the release gate of 3000 price-history symbols
- v0.7.1.1 is not released as a success tag; no scores, candidates, virtual portfolios, broker calls, real orders, run-daily, or day2 artifacts were generated
- v0.7.1.2 expands historical data provider coverage and passes the minimum historical coverage gate for v0.7.2 preparation, but it still does not score stocks, generate candidates, generate watchlists, generate virtual portfolios, connect a broker, place real orders, call run-daily, or execute official forward dry-run day2
- v0.7.2 builds the A-share strict/caution/excluded/unknown tradable universe buckets only; it does not generate LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, candidates, watchlists, virtual portfolios, broker calls, real orders, run-daily output, or official forward dry-run day2 artifacts
- day2 is blocked by local data horizon insufficiency; the latest common local market/benchmark/risk-proxy date is 2026-06-25, which day1 already used
- strategy effectiveness not proven
- no live trading

## Quickstart

Install and verify:

```powershell
python -m trading_core.cli --help
python -m pytest
```

Run v0.7 external intake:

```powershell
python scripts/download_external_research_repos.py
python -m trading_core.cli external-project-intake
```

Run v0.7.1 A-share data foundation:

```powershell
python -m trading_core.cli equity-data-source-manifest
python -m trading_core.cli build-a-share-equity-master
python -m trading_core.cli build-a-share-trading-calendar
python -m trading_core.cli ingest-a-share-daily-prices
python -m trading_core.cli ingest-a-share-adjusted-prices
python -m trading_core.cli ingest-a-share-daily-basic
python -m trading_core.cli ingest-a-share-industry-classification
python -m trading_core.cli ingest-a-share-basic-financials
python -m trading_core.cli audit-a-share-data-coverage
python -m trading_core.cli audit-a-share-data-schema
```

Or run the same foundation chain in one command:

```powershell
python -m trading_core.cli build-a-share-data-foundation
```

Run v0.7.2 A-share tradable universe filter:

```powershell
python -m trading_core.cli build-a-share-tradable-universe --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-tradable-universe --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli build-and-audit-a-share-tradable-universe --as-of-date 2026-06-26
```

The default downstream input is `strict_tradable_universe`. `caution_universe` is observation-only unless a future command explicitly allows it.

The v0.7.1 foundation writes local data artifacts under `data/equity_universe/`, `data/equity_market/`, `data/equity_industry/`, `data/equity_fundamental/`, and `data/equity_data_quality/`. It does not write scores, candidates, virtual portfolios, broker artifacts, real orders, main ledgers, or official forward dry-run day2 artifacts.

Run v0.7.1.2 historical provider expansion and readiness checks:

```powershell
python -m trading_core.cli a-share-historical-backfill-plan
python -m trading_core.cli diagnose-a-share-historical-backfill-coverage
python -m trading_core.cli build-a-share-historical-backfill-symbol-queue
python -m trading_core.cli backfill-a-share-historical-panels-full-market --target-start-date 2021-01-01 --minimum-start-date 2023-01-01 --end-date 2026-06-26 --batch-size 100 --max-symbols 0 --resume --retry 2
python -m trading_core.cli audit-a-share-historical-panel-coverage
python -m trading_core.cli audit-a-share-feature-readiness
```

The v0.7.1.2 evidence resolves the v0.7.1.1 coverage blocker with 5516 price-history symbols, 1326 trading days, and passing coverage/readiness audits. This remains historical data preparation only; it is not scoring, candidate generation, portfolio generation, broker integration, or live trading readiness.

Run plan alignment and MVP gap audit:

```powershell
python -m trading_core.cli plan-checklist
python -m trading_core.cli mvp-requirement-map
python -m trading_core.cli artifact-coverage-scanner
python -m trading_core.cli classify-mvp-gaps
python -m trading_core.cli classify-day1-blockers
python -m trading_core.cli next-work-register
python -m trading_core.cli audit-plan-alignment
```

Run A-share execution rules hardening audit:

```powershell
python -m trading_core.cli ashare-execution-gap-plan
python -m trading_core.cli ashare-trading-calendar-audit
python -m trading_core.cli execution-timeline-contract
python -m trading_core.cli ashare-price-status-contract
python -m trading_core.cli ashare-lot-and-position-contract
python -m trading_core.cli ashare-execution-cost-contract
python -m trading_core.cli virtual-execution-contract
python -m trading_core.cli audit-isolated-ledger-invariants
python -m trading_core.cli execution-aware-replay-smoke
python -m trading_core.cli reclassify-day1-blockers-after-execution-hardening
python -m trading_core.cli audit-ashare-execution-rules
```

Run v0.6.0 baseline strategy pack:

```powershell
python -m trading_core.cli baseline-strategy-scope-plan
python -m trading_core.cli baseline-strategy-contract
python -m trading_core.cli baseline-strategy-registry
python -m trading_core.cli generate-baseline-strategy-signals --strategy all --start-date 2024-01-02 --end-date 2024-12-31
python -m trading_core.cli build-baseline-order-preview --strategy all --execution-mode isolated
python -m trading_core.cli replay-baseline-strategy --strategy all --start-date 2024-01-02 --end-date 2024-12-31 --execution-mode isolated
python -m trading_core.cli compare-baseline-strategy-benchmarks --strategy all --start-date 2024-01-02 --end-date 2024-12-31
python -m trading_core.cli baseline-strategy-report --strategy all --start-date 2024-01-02 --end-date 2024-12-31
python -m trading_core.cli baseline-strategy-pack-summary
python -m trading_core.cli audit-baseline-strategy-pack
python -m trading_core.cli reclassify-day1-blockers-after-baseline-strategies
```

Run v0.6.1 daily workflow binding:

```powershell
python -m trading_core.cli daily-workflow-scope-plan
python -m trading_core.cli daily-market-data-snapshot --as-of-date 2024-12-31
python -m trading_core.cli audit-daily-data-quality --snapshot data/daily_workflow/snapshots/daily_market_data_snapshot-2024-12-31.json
python -m trading_core.cli daily-input-freeze-manifest --as-of-date 2024-12-31
python -m trading_core.cli daily-baseline-signals --as-of-date 2024-12-31 --strategy all
python -m trading_core.cli daily-order-preview --as-of-date 2024-12-31 --strategy all --execution-mode isolated
python -m trading_core.cli daily-isolated-execution-preview --as-of-date 2024-12-31 --execution-mode isolated
python -m trading_core.cli daily-report-packet --as-of-date 2024-12-31
python -m trading_core.cli protected-path-residue-scan
python -m trading_core.cli audit-daily-workflow --as-of-date 2024-12-31
python -m trading_core.cli reclassify-day1-blockers-after-daily-workflow
```

Run v0.6.2 forward dry-run start authorization pack:

```powershell
python -m trading_core.cli forward-dry-run-authorization-scope-plan
python -m trading_core.cli forward-dry-run-start-prerequisite-inventory
python -m trading_core.cli current-daily-workflow-readiness-snapshot
python -m trading_core.cli forward-dry-run-manual-confirmation-checklist-v2
python -m trading_core.cli forward-dry-run-owner-authorization-packet
python -m trading_core.cli validate-forward-dry-run-start-gate-v062
python -m trading_core.cli forward-dry-run-run-daily-command-preview
python -m trading_core.cli forward-dry-run-day1-prompt-eligibility
python -m trading_core.cli audit-forward-dry-run-start-authorization
python -m trading_core.cli reclassify-day1-blockers-after-start-authorization
```

The v0.6.2 pack is fail-closed. Technical prerequisites are present, authorization remains pending, and the next required action is owner manual confirmation. The run-daily command preview is metadata only; run-daily is not called, forward dry-run is not started, the main ledger is not written, no broker is connected, ML/LLM/RL trading decisions are not added, and promotion is not triggered.

Run v0.6.2.1 owner manual confirmation materialization:

```powershell
python -m trading_core.cli forward-dry-run-owner-manual-confirmation-record
python -m trading_core.cli complete-forward-dry-run-manual-confirmation-checklist-v2
python -m trading_core.cli update-forward-dry-run-owner-authorization-packet
python -m trading_core.cli revalidate-forward-dry-run-start-gate-v0621
python -m trading_core.cli revalidate-forward-dry-run-day1-prompt-eligibility
python -m trading_core.cli audit-forward-dry-run-authorization-materialization
python -m trading_core.cli reclassify-day1-blockers-after-authorization-materialization
```

The v0.6.2.1 pack materializes owner manual confirmation but does not start forward dry-run day 1. The next required action is owner requests day1 prompt. It does not call run-daily, does not write the main ledger, does not validate forward dry-run, does not prove strategy effectiveness, and does not certify live trading readiness.

Run v0.6.3 virtual isolated forward dry-run day 1:

```powershell
python -m trading_core.cli forward-dry-run-day1-pre-execution-gate
python -m trading_core.cli forward-dry-run-day1-input-snapshot
python -m trading_core.cli forward-dry-run-day1-strategy-signals
python -m trading_core.cli forward-dry-run-day1-virtual-order-preview
python -m trading_core.cli forward-dry-run-day1-virtual-execution
python -m trading_core.cli forward-dry-run-day1-ledger-snapshot
python -m trading_core.cli forward-dry-run-day1-risk-boundary-report
python -m trading_core.cli forward-dry-run-day1-operator-report
python -m trading_core.cli audit-forward-dry-run-day1
python -m trading_core.cli forward-dry-run-status
python -m trading_core.cli reclassify-day1-blockers-after-forward-dry-run-day1
```

The v0.6.3 workflow executes day 1 in `forward_dry_run_virtual` mode using local authorized historical data as of 2026-06-25. It writes only isolated forward dry-run day 1 and ledger artifacts under `data/forward_dry_run/` and `outputs/forward_dry_run/`, plus status/audit summaries. It does not call run-daily, does not connect a broker, does not place real orders, does not write the main ledger, does not validate the full 30-day forward dry-run, does not prove strategy effectiveness, and does not certify live trading readiness.

Run v0.6.3.1 day1 continuation artifact materialization:

```powershell
python -m trading_core.cli forward-dry-run-day1-continuation-gap-analysis
python -m trading_core.cli forward-dry-run-day1-artifact-manifest
python -m trading_core.cli forward-dry-run-day1-reproducibility-manifest
python -m trading_core.cli forward-dry-run-day2-readiness-packet
python -m trading_core.cli forward-dry-run-day2-continuation-gate-preview
python -m trading_core.cli audit-forward-dry-run-day1-continuation-artifacts
python -m trading_core.cli reclassify-day1-continuation-artifacts-v0631
```

The v0.6.3.1 workflow absorbs the v0.6.4 blocking preflight and fills the missing day1 continuation artifacts required before a future day2 attempt. It does not execute day2 or day3, does not call run-daily, does not write the main ledger, and remains not strategy effectiveness proof, not full forward dry-run validation, and not live trading readiness.

Build features and labels:

```powershell
python -m trading_core.cli build-features --start-date 2024-01-01 --end-date 2026-06-23 --data data/raw/prices/etf_daily
python -m trading_core.cli build-labels --start-date 2024-01-01 --end-date 2026-06-23 --data data/raw/prices/etf_daily
```

Run ML shadow pipeline:

```powershell
python -m trading_core.cli build-ml-dataset --features data/features/features.jsonl --labels data/labels/labels.jsonl --start-date 2024-01-01 --end-date 2026-06-23 --train-days 252 --validation-days 63 --test-days 21 --step-days 21 --label-column forward_return_5d
python -m trading_core.cli train-ml-shadow --dataset data/ml/walk_forward_dataset.json --rows data/ml/walk_forward_rows.jsonl --model-type mock --label-column forward_return_5d
python -m trading_core.cli predict-ml-shadow --model data/ml/ml_shadow_model.json --rows data/ml/walk_forward_rows.jsonl
python -m trading_core.cli generate-ml-shadow-signals --predictions data/ml/ml_shadow_predictions.jsonl --top-k 3 --target-weight 0.05
python -m trading_core.cli ml-shadow-leaderboard --predictions data/ml/ml_shadow_predictions.jsonl --signals data/shadow/ml_shadow_signals.jsonl
```

Run experiment pipeline:

```powershell
python -m trading_core.cli register-experiment --config config/experiments/momentum_sweep.yaml
python -m trading_core.cli run-parameter-sweep --config config/experiments/momentum_sweep.yaml
python -m trading_core.cli compare-strategies --inputs data/experiments/parameter_sweep-EXP-sweep-momentum-20260624.json data/shadow/ml_shadow_leaderboard-2024-01-01-2026-06-23-MLSHADOW-20240101-20260623-mock.json
python -m trading_core.cli experiment-dashboard
```

Run reporting pipeline:

```powershell
python -m trading_core.cli weekly-research-report --start-date 2026-06-17 --end-date 2026-06-23 --include-experiments --include-ml-shadow --include-mistakes
python -m trading_core.cli monthly-research-report --start-date 2026-06-01 --end-date 2026-06-30 --include-weekly --include-experiments --include-ml-shadow
python -m trading_core.cli run-research-pipeline --start-date 2026-06-01 --end-date 2026-06-30
```

Run audits and system checks:

```powershell
python -m trading_core.cli cli-inventory
python -m trading_core.cli artifact-inventory
python -m trading_core.cli system-smoke-test --include-reports --include-inventory
python -m trading_core.cli boundary-regression-audit
python -m trading_core.cli system-integrity-audit
python -m trading_core.cli audit-global-briefing-replay
python -m trading_core.cli audit-isolated-replay-adapter
python -m trading_core.cli audit-global-briefing-real-package-integration
```

Run the global-briefing historical replay harness smoke:

```powershell
python -m trading_core.cli global-briefing-contract
python -m trading_core.cli validate-global-briefing-signals --input tests/fixtures/global_briefing/signals_valid.jsonl --start-date 2024-01-02 --end-date 2024-01-08
python -m trading_core.cli build-global-briefing-replay-bundle --signals tests/fixtures/global_briefing/signals_valid.jsonl --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --allow-carry-forward
python -m trading_core.cli replay-global-briefing-history --bundle data/replays/global_briefing/replay_bundle-2024-01-02-2024-01-08.json --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --execution-mode isolated --initial-cash 1000000
python -m trading_core.cli global-briefing-replay-report --replay data/replays/global_briefing/global_briefing_replay-2024-01-02-2024-01-08.json
python -m trading_core.cli audit-isolated-replay-adapter
```

Run the real global-briefing package integration smoke:

```powershell
python -m trading_core.cli global-briefing-package-manifest --root tests/fixtures/global_briefing_real
python -m trading_core.cli normalize-global-briefing-package --input tests/fixtures/global_briefing_real/real_package_aliases.csv --package-id GB-REAL-FIXTURE --region CN --source global_briefing --version v1
python -m trading_core.cli audit-global-briefing-package-coverage --signals data/global_briefing/normalized/GB-REAL-FIXTURE.normalized.jsonl --prices tests/fixtures/global_briefing_real/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --min-coverage 0.60
python -m trading_core.cli run-global-briefing-real-package-replay --input tests/fixtures/global_briefing_real/real_package_aliases.csv --prices tests/fixtures/global_briefing_real/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --package-id GB-REAL-FIXTURE --region CN --source global_briefing --version v1 --allow-carry-forward --min-coverage 0.60 --execution-mode isolated
python -m trading_core.cli global-briefing-real-package-report
python -m trading_core.cli audit-global-briefing-real-package-integration
```

Run the global-briefing evidence quality reports:

```powershell
python -m trading_core.cli global-briefing-warning-triage
python -m trading_core.cli global-briefing-evidence-quality-report
python -m trading_core.cli global-briefing-production-acceptance-criteria
python -m trading_core.cli audit-global-briefing-evidence-quality
```

Run authorized full historical data acquisition and proxy replay:

```powershell
python -m trading_core.cli download-historical-data-packages --start-date 2018-01-01 --end-date latest --continue-on-error
python -m trading_core.cli normalize-historical-data-packages
python -m trading_core.cli audit-historical-data-quality
python -m trading_core.cli run-full-historical-proxy-replay --start-date 2024-01-02 --end-date 2024-12-31 --execution-mode isolated --min-coverage 0.80
python -m trading_core.cli historical-data-acquisition-report
python -m trading_core.cli audit-historical-data-acquisition
```

Run v0.5.7.1 historical data gap closure and warning reduction:

```powershell
python -m trading_core.cli close-historical-data-gaps --start-date 2018-01-01 --end-date latest --replay-start-date 2024-01-02 --replay-end-date 2024-12-31 --min-coverage 0.80 --continue-on-error
python -m trading_core.cli historical-data-gap-closure-report
python -m trading_core.cli audit-historical-data-gap-closure
```

Run v0.5.8 day-0 operational readiness pack:

```powershell
python -m trading_core.cli day0-data-freeze
python -m trading_core.cli day0-warning-register
python -m trading_core.cli day0-blocking-conditions
python -m trading_core.cli day0-run-daily-preflight
python -m trading_core.cli day0-manual-confirmation-packet
python -m trading_core.cli forward-dry-run-operating-calendar
python -m trading_core.cli day0-readiness-report
python -m trading_core.cli audit-day0-readiness
```

## Safety boundary

- no broker
- no live trading
- no real orders
- no auto promotion
- historical data authorization is not trading authorization
- authorized historical data acquisition does not connect to a broker and does not download account/order/trade/position/margin data
- local global-briefing package integration uses local files only and no network access
- v0.5.7 historical package acquisition may use approved public data endpoints and authorized local/API configuration for historical research data only
- v0.5.7.1 historical gap closure only repairs or proxies historical research packages and groups warnings
- v0.5.8 day-0 readiness does not start forward dry-run and does not call run-daily
- no forward dry-run started by the historical replay harness
- no forward dry-run started by the real package integration workflow
- no forward dry-run started by authorized historical data acquisition
- no labels, ML shadow, experiments, RL, or LLM trading decisions in the global-briefing replay decision path
- isolated replay ledger is written only under `data/replays/global_briefing/`
- v0.6.0 baseline strategy pack is research-only and does not start forward dry-run
- v0.6.0 isolated strategy replay ledgers are written only under `data/replays/strategies/`
- v0.6.1 daily workflow binding uses local authorized historical daily data snapshots and does not download real-time market data
- v0.6.1 writes preview artifacts only under `data/daily_workflow/` and `outputs/daily_workflow/`
- v0.7.1 writes A-share data foundation artifacts only under equity data/data-quality paths and does not call `run-daily`
