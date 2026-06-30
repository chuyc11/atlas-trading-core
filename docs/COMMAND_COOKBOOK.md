# Command Cookbook

This cookbook is for resuming the research-only workbench. It does not authorize live trading.

## Resume project

```bash
git status
git tag --points-at HEAD
python -m pytest
```

## Find reports

```bash
python -m trading_core.cli quick-status
python -m trading_core.cli report-index
python -m trading_core.cli latest-artifact --type all
python -m trading_core.cli latest-artifact --type handoff
python -m trading_core.cli artifact-browser
```

## Check safety

```bash
python -m trading_core.cli boundary-regression-audit
python -m trading_core.cli system-integrity-audit
python -m trading_core.cli forward-dry-run-readiness
python -m trading_core.cli audit-global-briefing-replay
python -m trading_core.cli audit-isolated-replay-adapter
python -m trading_core.cli audit-global-briefing-real-package-integration
python -m trading_core.cli audit-global-briefing-evidence-quality
python -m trading_core.cli audit-historical-data-acquisition
python -m trading_core.cli audit-historical-data-gap-closure
python -m trading_core.cli audit-day0-readiness
python -m trading_core.cli audit-forward-dry-run-day1-owner-report-pack
python -m trading_core.cli audit-a-share-candidates --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-virtual-portfolios --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-ops-history-baseline --as-of-date 2026-06-26
```

## Run v0.8.6 A-share ops history baseline

```bash
python -m trading_core.cli validate-a-share-ops-history-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-ops-history-baseline --as-of-date 2026-06-26 --mode build_trend_baselines
python -m trading_core.cli audit-a-share-ops-history-baseline --as-of-date 2026-06-26
```

Combined:

```bash
python -m trading_core.cli build-and-audit-a-share-ops-history-baseline --as-of-date 2026-06-26 --mode build_trend_baselines
```

This path appends real ops run history and builds operational baselines only. It does not synthesize history, generate orders, connect a broker, call old run-daily, execute official day2, or treat trends as trade instructions.

## Run v0.8.7 A-share gated build_from_existing_data dry-run

```bash
python -m trading_core.cli validate-a-share-gated-build-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-gated-build-from-existing-data --as-of-date 2026-06-26 --mode run_gated_build_from_existing_data
python -m trading_core.cli audit-a-share-gated-build-from-existing-data --as-of-date 2026-06-26
```

Combined:

```bash
python -m trading_core.cli build-and-audit-a-share-gated-build-from-existing-data --as-of-date 2026-06-26 --mode run_gated_build_from_existing_data
```

This path requires the preflight gate, uses `build_from_existing_data`, does not refresh public network data, does not run `full_research_run`, does not call old `run-daily`, does not connect a broker, and does not generate orders or buy/sell signals.

## Run v0.8.8 A-share build_from_existing_data repeatability

```bash
python -m trading_core.cli validate-a-share-build-repeatability-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-build-repeatability --as-of-date 2026-06-26 --mode run_repeat_build_from_existing_data
python -m trading_core.cli audit-a-share-build-repeatability --as-of-date 2026-06-26
```

Combined:

```bash
python -m trading_core.cli build-and-audit-a-share-build-repeatability --as-of-date 2026-06-26 --mode run_repeat_build_from_existing_data
```

This path repeats the gated `build_from_existing_data` workflow, compares first-build and second-build artifacts, and snapshots protected order/trade/account paths before and after the repeat run. Pre-existing `data/orders` or `data/trades` directories are allowed if unchanged; new, modified, or deleted protected files are blocking. It does not refresh public network data, run `full_research_run`, call old `run-daily`, connect broker, generate buy/sell signals, generate order previews, place orders, or treat repeatability as a trade instruction.

## Run v0.8.9 A-share build-output owner dashboard

```bash
python -m trading_core.cli validate-a-share-build-output-owner-dashboard-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-build-output-owner-dashboard --as-of-date 2026-06-26 --mode build_owner_dashboard_from_build_output
python -m trading_core.cli audit-a-share-build-output-owner-dashboard --as-of-date 2026-06-26
```

Combined:

```bash
python -m trading_core.cli build-and-audit-a-share-build-output-owner-dashboard --as-of-date 2026-06-26 --mode build_owner_dashboard_from_build_output
```

This path refreshes owner-facing dashboard artifacts from stable `build_from_existing_data` outputs. It prefers build output over validate-source artifacts, requires repeatability audit success, requires `business_output_drift_count=0`, and carries protected path status forward. It does not rerun `build_from_existing_data`, refresh public network data, run `full_research_run`, call old `run-daily`, connect broker, create order previews, place orders, or treat dashboard output as a trade instruction.

## Run v0.8.10 A-share build-output ops refresh

```bash
python -m trading_core.cli validate-a-share-build-output-ops-refresh-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-build-output-ops-refresh --as-of-date 2026-06-26 --mode build_build_output_monitoring_remediation_ops_refresh
python -m trading_core.cli audit-a-share-build-output-ops-refresh --as-of-date 2026-06-26
```

Combined:

```bash
python -m trading_core.cli build-and-audit-a-share-build-output-ops-refresh --as-of-date 2026-06-26 --mode build_build_output_monitoring_remediation_ops_refresh
```

This path refreshes monitoring, remediation, ops center, and ops history artifacts from the v0.8.9 build-output dashboard. It uses `build_from_existing_data` as source workflow mode, requires zero business output drift, and keeps automatic action count at zero. It does not rerun `build_from_existing_data`, refresh public network data, run `full_research_run`, execute remediation actions, send external notifications, generate buy/sell signals, generate order previews, place orders, connect broker, call old run-daily, execute official forward dry-run day2, or treat ops refresh as a trade instruction.

## Run v0.8.11 A-share owner daily pack

```bash
python -m trading_core.cli validate-a-share-owner-daily-pack-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-owner-daily-pack --as-of-date 2026-06-26 --mode build_owner_operations_decision_pack
python -m trading_core.cli audit-a-share-owner-daily-pack --as-of-date 2026-06-26
```

Combined:

```bash
python -m trading_core.cli build-and-audit-a-share-owner-daily-pack --as-of-date 2026-06-26 --mode build_owner_operations_decision_pack
```

This path creates an owner-facing daily runbook and owner operations decision pack from the v0.8.10 build-output ops refresh. It uses `build_from_existing_data` only as recorded source mode. It does not rerun `build_from_existing_data`, refresh public network data, run `full_research_run`, execute remediation actions, send external notifications, generate buy/sell signals, generate order previews, place orders, connect broker, call old run-daily, execute official forward dry-run day2, treat the daily pack as a trade instruction, or claim profit/live readiness.

## Run v0.7 external project intake

```bash
python scripts/download_external_research_repos.py
python -m trading_core.cli external-project-intake
```

This v0.7.0 path downloads ignored external research clones and generates intake/planning artifacts only. It does not merge third-party trading code, does not call run-daily, does not connect a broker, does not place real orders, and does not use LLM output as a trading decision.

## Run v0.7.1 A-share data foundation

```bash
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

Equivalent one-command path:

```bash
python -m trading_core.cli build-a-share-data-foundation
```

This v0.7.1 path writes A-share master, calendar, market, industry, fundamental, source-manifest, coverage-audit, and schema-audit artifacts only. Public/free provider data may be delayed, partial, or unavailable; those limitations are recorded in the source manifest and audits. It does not generate LongScore/MidScore/ShortScore, candidates, watchlists, virtual portfolios, broker calls, real orders, `run-daily`, or official forward dry-run day2 artifacts.

## Run v0.7.1.1 A-share historical panel backfill

```bash
python -m trading_core.cli a-share-historical-backfill-plan
python -m trading_core.cli backfill-a-share-historical-panels --target-start-date 2021-01-01 --minimum-start-date 2023-01-01 --end-date 2026-06-26
python -m trading_core.cli audit-a-share-historical-panel-coverage
python -m trading_core.cli audit-a-share-feature-readiness
```

This v0.7.1.1 path expands single-day A-share data into historical panels for future filters and multi-horizon features. It must fail closed when public historical provider coverage is insufficient. It does not generate scores, candidates, watchlists, virtual portfolios, broker calls, real orders, `run-daily`, or official forward dry-run day2 artifacts.

## Run v0.7.1.2 A-share historical provider expansion

```bash
python -m trading_core.cli diagnose-a-share-historical-backfill-coverage
python -m trading_core.cli build-a-share-historical-backfill-symbol-queue
python -m trading_core.cli backfill-a-share-historical-panels-full-market --target-start-date 2021-01-01 --minimum-start-date 2023-01-01 --end-date 2026-06-26 --batch-size 100 --max-symbols 0 --resume --retry 2
python -m trading_core.cli audit-a-share-historical-panel-coverage
python -m trading_core.cli audit-a-share-feature-readiness
```

This v0.7.1.2 path resolves the v0.7.1.1 10-symbol coverage blocker by using a full-market queue from `equity_master.parquet`, provider fallback tracking, checkpoint/resume, batch manifests, and per-symbol manifests. It remains data preparation only: no scores, candidates, watchlists, virtual portfolios, broker calls, real orders, `run-daily`, or official forward dry-run day2 artifacts.

## Run v0.7.2 A-share tradable universe filter

```bash
python -m trading_core.cli build-a-share-tradable-universe --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-tradable-universe --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli build-and-audit-a-share-tradable-universe --as-of-date 2026-06-26
```

This v0.7.2 path filters the A-share full-market history into `strict_tradable_universe`, `caution_universe`, `excluded_universe`, and `unknown_status_universe`. It is not selection or scoring: it does not generate LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, candidates, watchlists, virtual portfolios, broker calls, real orders, `run-daily`, or official forward dry-run day2 artifacts.

## Run v0.7.3 A-share multi-horizon feature engineering

```bash
python -m trading_core.cli build-a-share-multi-horizon-features --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-multi-horizon-features --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli build-and-audit-a-share-multi-horizon-features --as-of-date 2026-06-26
```

This v0.7.3 path consumes `strict_tradable_universe` and writes feature-only parquet tables plus manifest, coverage, summary, and audit artifacts. It is not scoring or selection: it does not generate LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, candidates, watchlists, virtual portfolios, broker calls, real orders, `run-daily`, profit claims, live readiness, or official forward dry-run day2 artifacts.

## Run v0.7.4 A-share long/mid/short scoring

```bash
python -m trading_core.cli build-a-share-scores --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-scores --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli build-and-audit-a-share-scores --as-of-date 2026-06-26
```

This v0.7.4 path consumes v0.7.3 strict-universe features and writes scores, ranks, percentiles, component breakdowns, distributions, reports, and scoring audit artifacts only. It is not candidate generation or trading: it does not generate candidates, watchlists, virtual portfolios, buy/sell signals, broker calls, real orders, `run-daily`, profit claims, live readiness, or official forward dry-run day2 artifacts.

## Run v0.7.5 A-share candidate generation

```bash
python -m trading_core.cli generate-a-share-candidates --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-candidates --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli generate-and-audit-a-share-candidates --as-of-date 2026-06-26
```

This v0.7.5 path consumes v0.7.4 score artifacts and writes long, mid, and short candidate pools, an extended watch pool, multi-horizon candidates, risk-downgraded candidates, reason breakdown, manifest, reports, summary, and candidate audit artifacts. It is candidate generation only: candidates are not investment advice, not buy/sell signals, not order instructions, not virtual portfolios, not broker calls, not real orders, not `run-daily`, not profit claims, not live readiness, and not official forward dry-run day2 artifacts. Virtual portfolios are handled by v0.7.6 and daily briefing is handled by v0.7.7.

## Run v0.7.6 A-share virtual portfolio construction

```bash
python -m trading_core.cli build-a-share-virtual-portfolios --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-virtual-portfolios --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli build-and-audit-a-share-virtual-portfolios --as-of-date 2026-06-26
```

This v0.7.6 path consumes v0.7.5 candidate artifacts and writes long, mid, and short virtual portfolios, virtual target weights, industry exposure, risk/liquidity summary, manifest, reports, summary, and virtual portfolio audit artifacts. It is virtual portfolio construction only: virtual portfolios are not real portfolios, target weights are not order instructions, no buy/sell signals are generated, no broker order preview is generated, no broker is connected, no real orders are placed, `run-daily` is not called, and no profit or live readiness claim is made. Daily briefing is handled by v0.7.7.

## Run v0.7.7 A-share daily stock selection briefing

```bash
python -m trading_core.cli build-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli build-and-audit-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26
```

This v0.7.7 path consumes existing feature, score, candidate, virtual portfolio, exposure, risk/liquidity, and audit artifacts. It writes daily Chinese briefing, source trace, manifest, boundary check, and briefing audit artifacts only. It does not regenerate scores, candidates, or virtual portfolios; it does not generate buy/sell signals, order previews, broker artifacts, real orders, `run-daily`, profit claims, live readiness, or official forward dry-run day2 artifacts. Virtual portfolio tracking and paper ledger work is implemented in v0.7.8.

## Run forward dry-run day1 owner report pack

```bash
python -m trading_core.cli forward-dry-run-day1-owner-report-scope-plan
python -m trading_core.cli forward-dry-run-day1-owner-summary-report
python -m trading_core.cli forward-dry-run-day1-strategy-signal-explanation
python -m trading_core.cli forward-dry-run-day1-virtual-order-fill-report
python -m trading_core.cli forward-dry-run-day1-isolated-ledger-report
python -m trading_core.cli forward-dry-run-day1-data-reproducibility-appendix
python -m trading_core.cli forward-dry-run-day1-continuation-blocker-note
python -m trading_core.cli forward-dry-run-day1-owner-report-pack-summary
python -m trading_core.cli audit-forward-dry-run-day1-owner-report-pack
```

This v0.6.3.2 path is report-only. It does not execute day2, does not call run-daily, does not download real-time market data, does not call external market APIs, does not write main orders/trades/portfolio/accounts, does not connect a broker, and does not place real orders. Day2 is blocked by local data horizon insufficiency; the next step is `v0.6.3.3-forward-dry-run-data-horizon-extension`.

## Run reporting pipeline

```bash
python -m trading_core.cli run-research-pipeline --start-date START --end-date END
```

## Run global-briefing historical replay harness

```bash
python -m trading_core.cli global-briefing-contract
python -m trading_core.cli validate-global-briefing-signals --input tests/fixtures/global_briefing/signals_valid.jsonl --start-date 2024-01-02 --end-date 2024-01-08
python -m trading_core.cli build-global-briefing-replay-bundle --signals tests/fixtures/global_briefing/signals_valid.jsonl --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --allow-carry-forward
python -m trading_core.cli replay-global-briefing-history --bundle data/replays/global_briefing/replay_bundle-2024-01-02-2024-01-08.json --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --execution-mode isolated --initial-cash 1000000
python -m trading_core.cli global-briefing-replay-report --replay data/replays/global_briefing/global_briefing_replay-2024-01-02-2024-01-08.json
python -m trading_core.cli audit-isolated-replay-adapter
```

The global-briefing replay harness is isolated historical replay only. v0.5.5 replaces the fixture E2E no-trade fallback with isolated execution artifacts under `data/replays/global_briefing/` only. It is not forward dry-run validation, not live trading readiness, and not strategy effectiveness proof.

## Run real global-briefing package integration

```bash
python -m trading_core.cli global-briefing-package-manifest --root tests/fixtures/global_briefing_real
python -m trading_core.cli normalize-global-briefing-package --input tests/fixtures/global_briefing_real/real_package_aliases.csv --package-id GB-REAL-FIXTURE --region CN --source global_briefing --version v1
python -m trading_core.cli audit-global-briefing-package-coverage --signals data/global_briefing/normalized/GB-REAL-FIXTURE.normalized.jsonl --prices tests/fixtures/global_briefing_real/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --min-coverage 0.60
python -m trading_core.cli run-global-briefing-real-package-replay --input tests/fixtures/global_briefing_real/real_package_aliases.csv --prices tests/fixtures/global_briefing_real/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --package-id GB-REAL-FIXTURE --region CN --source global_briefing --version v1 --allow-carry-forward --min-coverage 0.60 --execution-mode isolated
python -m trading_core.cli global-briefing-real-package-report
python -m trading_core.cli audit-global-briefing-real-package-integration
```

The real package integration path is local-file-only. It normalizes historical global-briefing packages, audits coverage and point-in-time safety, and runs isolated replay under `data/replays/global_briefing/`; it is not forward dry-run validation, not live trading readiness, and not strategy effectiveness proof.

## Run global-briefing evidence quality reports

```bash
python -m trading_core.cli global-briefing-warning-triage
python -m trading_core.cli global-briefing-evidence-quality-report
python -m trading_core.cli global-briefing-production-acceptance-criteria
python -m trading_core.cli audit-global-briefing-evidence-quality
```

The evidence-quality reports clarify warning categories, fixture-only evidence, production acceptance thresholds, and production readiness=false. They do not start replay, call run-daily, validate forward dry-run, certify live trading readiness, or prove strategy effectiveness.

## Run authorized historical data acquisition

```bash
python -m trading_core.cli download-historical-data-packages --start-date 2018-01-01 --end-date latest --continue-on-error
python -m trading_core.cli normalize-historical-data-packages
python -m trading_core.cli audit-historical-data-quality
python -m trading_core.cli run-full-historical-proxy-replay --start-date 2024-01-02 --end-date 2024-12-31 --execution-mode isolated --min-coverage 0.80
python -m trading_core.cli historical-data-acquisition-report
python -m trading_core.cli audit-historical-data-acquisition
```

This workflow acquires historical research data packages and builds the unified proxy package. Historical data authorization is not trading authorization. The proxy signals are not internal global-briefing signals, the production global-briefing package remains separately reported, and the historical replay is not forward dry-run validation, not live trading readiness, and not strategy effectiveness proof.

## Run historical data gap closure

```bash
python -m trading_core.cli close-historical-data-gaps --start-date 2018-01-01 --end-date latest --replay-start-date 2024-01-02 --replay-end-date 2024-12-31 --min-coverage 0.80 --continue-on-error
python -m trading_core.cli historical-warning-inventory
python -m trading_core.cli historical-data-gap-closure-report
python -m trading_core.cli audit-historical-data-gap-closure
```

This v0.5.7.1 path repairs or proxies EPU, repairs OECD CLI or builds an authorized macro-cycle proxy explicitly marked as not official OECD CLI, rebuilds the proxy package, preserves raw warning counts, and displays grouped warnings. It is not forward dry-run validation, not live trading readiness, not strategy effectiveness proof, and not trading authorization.

## Run day-0 operational readiness pack

```bash
python -m trading_core.cli day0-data-freeze
python -m trading_core.cli day0-warning-register
python -m trading_core.cli day0-blocking-conditions
python -m trading_core.cli day0-run-daily-preflight
python -m trading_core.cli day0-manual-confirmation-packet
python -m trading_core.cli forward-dry-run-operating-calendar
python -m trading_core.cli day0-readiness-report
python -m trading_core.cli audit-day0-readiness
```

This v0.5.8 path prepares manual confirmation for a future day 1. It does not start forward dry-run, does not call run-daily, does not complete manual confirmation, does not prove strategy effectiveness, and does not certify live trading readiness.

## Run plan alignment and MVP gap audit

```bash
python -m trading_core.cli plan-checklist
python -m trading_core.cli mvp-requirement-map
python -m trading_core.cli artifact-coverage-scanner
python -m trading_core.cli classify-mvp-gaps
python -m trading_core.cli classify-day1-blockers
python -m trading_core.cli next-work-register
python -m trading_core.cli audit-plan-alignment
```

This v0.5.8.1 path audits the MVP plan against current implementation evidence. It does not start forward dry-run, does not call run-daily, does not write the main ledger, and does not use labels, ML shadow, LLM, RL, experiments, or promotion outputs as day-1 authorization.

## Run A-share execution rules hardening

```bash
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

This v0.5.9 path hardens virtual execution rules for future forward dry-run preparation. It does not start forward dry-run, does not call run-daily, does not write the main ledger, and does not prove strategy effectiveness or certify live trading readiness.

## Run baseline strategy pack

```bash
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

This v0.6.0 path builds deterministic baseline strategies, PIT-safe signals, preview-only order proposals, isolated strategy replay, benchmark comparison, reports, summary, audit, and v060 blocker reclassification. It does not start forward dry-run, does not call run-daily, does not write the main ledger, does not use labels, ML shadow, LLM, RL, experiments, or promotion outputs as authorization, and does not prove strategy effectiveness or certify live trading readiness.

## Run daily workflow binding

```bash
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

This v0.6.1 path uses local authorized historical daily data snapshots and does not download real-time market data. It freezes inputs, generates daily baseline signals, order previews, isolated execution previews, report packets, residue scan, audit, and v061 reclassification. It does not call run-daily, does not start forward dry-run, does not write the main ledger, does not use labels, ML shadow, LLM, RL, experiments, or promotion outputs as authorization, and does not certify live trading readiness.

## Run forward dry-run start authorization pack

```bash
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

This v0.6.2 path creates a start authorization pack only. Technical prerequisites are present, manual confirmation defaults false, owner authorization defaults false, `day1_start_allowed=false`, `day1_prompt_eligible=false`, and `day1_prompt_generated=false`. The run-daily command preview is metadata only. It does not call run-daily, does not start forward dry-run, does not write the main ledger, does not use labels, ML shadow, LLM, RL, experiments, or promotion outputs as authorization, and does not certify live trading readiness.

## Run owner manual confirmation materialization

```bash
python -m trading_core.cli forward-dry-run-owner-manual-confirmation-record
python -m trading_core.cli complete-forward-dry-run-manual-confirmation-checklist-v2
python -m trading_core.cli update-forward-dry-run-owner-authorization-packet
python -m trading_core.cli revalidate-forward-dry-run-start-gate-v0621
python -m trading_core.cli revalidate-forward-dry-run-day1-prompt-eligibility
python -m trading_core.cli audit-forward-dry-run-authorization-materialization
python -m trading_core.cli reclassify-day1-blockers-after-authorization-materialization
```

This v0.6.2.1 path materializes owner manual confirmation and authorizes day1 prompt generation only. It sets `manual_confirmation_complete=true`, `forward_dry_run_start_authorized=true`, and `day1_prompt_eligible=true`, while keeping `day1_prompt_generated=false` and `day1_start_allowed=false`. It does not call run-daily, does not start forward dry-run, does not write the main ledger, and remains not forward dry-run validation, not strategy effectiveness proof, and not live trading readiness.

## Run virtual forward dry-run day 1

```bash
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

This v0.6.3 path executes virtual isolated forward dry-run day 1 only. It uses local authorized historical data as of 2026-06-25, writes the isolated forward dry-run ledger, records `forward_dry_run_days_completed=1`, and sets `next_day_index=2`. It does not call run-daily, does not connect a broker, does not place real orders, does not write the main ledger, and remains not full forward dry-run validation, not strategy effectiveness proof, and not live trading readiness.

## Run day1 continuation artifact materialization

```bash
python -m trading_core.cli forward-dry-run-day1-continuation-gap-analysis
python -m trading_core.cli forward-dry-run-day1-artifact-manifest
python -m trading_core.cli forward-dry-run-day1-reproducibility-manifest
python -m trading_core.cli forward-dry-run-day2-readiness-packet
python -m trading_core.cli forward-dry-run-day2-continuation-gate-preview
python -m trading_core.cli audit-forward-dry-run-day1-continuation-artifacts
python -m trading_core.cli reclassify-day1-continuation-artifacts-v0631
```

This v0.6.3.1 path resolves the continuation artifact gap exposed by the v0.6.4 preflight. It keeps `day2_executed=false`, `day3_executed=false`, and `run_daily_called=false`. It does not write day_002 artifacts, does not write the main ledger, and does not certify strategy effectiveness, full forward dry-run validation, or live trading readiness.

## Run A-share virtual portfolio tracking

```bash
python -m trading_core.cli build-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli build-and-audit-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26
```

This v0.7.8 path creates research-only virtual paper ledgers, virtual holdings snapshots, NAV, first-day performance/drawdown, exposure, benchmark comparison placeholders, manifest, source trace, reports, and audit. The paper ledger is not a real-money ledger. Virtual holdings are not real holdings. Virtual returns are not actual returns. It does not call run-daily, does not execute day2, does not connect a broker, does not place real orders, and does not generate buy/sell signals or order previews.

## Run A-share daily workflow orchestration

```bash
python -m trading_core.cli preflight-a-share-daily-workflow --as-of-date 2026-06-26
python -m trading_core.cli run-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode validate_existing_artifacts
python -m trading_core.cli audit-a-share-daily-research-workflow --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli run-and-audit-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode validate_existing_artifacts
```

This v0.7.9 path orchestrates the existing v0.7.2-v0.7.8 A-share research chain only. `validate_existing_artifacts` verifies existing artifacts without rebuilding upstream stages. `build_from_existing_data` may rebuild the A-share research chain from existing historical panels. `full_research_run` keeps public data refresh disabled unless `--allow-public-data-refresh` is explicitly passed. The workflow does not rewrite upstream business modules, does not call old `run-daily`, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, does not generate buy/sell signals, does not generate order previews, does not claim model profitability, and is not live-trading ready.

## Run A-share benchmark comparison

```bash
python -m trading_core.cli build-a-share-benchmark-comparison --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-benchmark-comparison --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli build-and-audit-a-share-benchmark-comparison --as-of-date 2026-06-26
```

This v0.7.10 path builds research-only benchmark data and portfolio comparison artifacts for CSI300, CSI500, CSI1000, CASH, strict-tradable equal weight, and candidate-pool equal weight. It resolves the prior index placeholder warning when real benchmark history is available. It does not call old `run-daily`, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, and does not generate buy/sell signals or order previews. First-day portfolio history remains explicitly limited.

## Run A-share multi-day performance tracking

```bash
python -m trading_core.cli build-a-share-multi-day-performance --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-multi-day-performance --as-of-date 2026-06-26
```

Equivalent one-command path:

```bash
python -m trading_core.cli build-and-audit-a-share-multi-day-performance --as-of-date 2026-06-26
```

This v0.7.11 path builds research-only virtual portfolio NAV, return, drawdown, benchmark-relative, holding mark-to-market, source trace, limitation, boundary, summary, and audit artifacts. The default `current_snapshot` mode uses only the current tracking date. If only one tracking day exists, it records `sufficient_history=false`, `first_day_initialization=true`, and `performance_not_yet_observed=true`. It does not fabricate portfolio history, does not call old `run-daily`, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, and does not generate buy/sell signals or order previews.

## What not to do

* do not run live trading
* do not treat shadow as active
* do not use historical replay as forward dry-run
* do not use reports as admission gate
* do not treat global-briefing replay artifacts as broker or promotion output
* do not treat real package integration as live readiness or forward validation
* do not treat evidence-quality reports as production package acceptance
* do not treat authorized historical data acquisition as trading authorization
* do not treat historical gap closure as trading authorization or production global-briefing validation
* do not treat day-0 readiness as forward dry-run validation or live trading readiness
* do not treat plan alignment as day 1 authorization
* do not treat historical performance as strategy effectiveness proof
* do not use ML shadow, LLM, RL, or promotion outputs as day-1 authorization
* do not treat execution hardening as strategy effectiveness proof or live trading readiness
* do not treat isolated execution-aware smoke as forward validation
* do not treat proxy signals as internal global-briefing signals
* do not treat baseline strategy historical replay as forward validation
* do not treat baseline strategy reports as promotion authorization
* do not treat daily workflow previews as forward validation
* do not treat protected path residue scans as cleanup authorization
* do not treat the v0.6.2 start authorization pack as owner approval
* do not generate day1 execution instructions before explicit owner confirmation
* do not treat v0.6.2.1 prompt eligibility as day1 execution approval
* do not treat v0.6.3 day1 execution as completion of the full 30-day forward dry-run
* do not treat v0.6.3.1 day2 readiness packet as day2 execution authorization
* do not treat v0.7.1 data ingestion as stock recommendation, scoring, portfolio generation, or trading readiness
* do not call provider APIs directly from future scoring modules without the v0.7.1 local schema and audit layer
* do not treat v0.7.1.1 historical backfill as scoring, candidate generation, portfolio generation, or trading readiness
* do not treat v0.7.1.2 historical provider expansion as scoring, candidate generation, portfolio generation, or trading readiness
* do not treat v0.7.2 tradable universe filtering as scoring, candidate generation, watchlist generation, portfolio generation, or trading readiness
* do not treat v0.7.5 candidates or watch pools as investment advice, buy/sell signals, portfolio weights, order instructions, broker readiness, profit guarantees, or live trading readiness
* do not treat v0.7.6 virtual portfolios or target weights as real portfolios, buy/sell signals, broker order previews, real-account rebalance instructions, profit guarantees, or live trading readiness
* do not treat v0.7.7 daily briefings as trading advice, score regeneration, candidate regeneration, portfolio regeneration, buy/sell signals, order previews, broker readiness, profit guarantees, or live trading readiness
* do not treat v0.7.8 paper ledgers as real-money ledgers, virtual holdings as real holdings, or virtual returns as actual returns
* do not treat v0.7.10 benchmark comparison as investment advice, order instruction, realized multi-day portfolio evidence, profit guarantee, broker readiness, or live trading readiness
* do not treat v0.7.11 first-day performance tracking as observed strategy performance, investment advice, order instruction, realized multi-day evidence, profit guarantee, broker readiness, or live trading readiness
* do not treat v0.8.2 owner dashboard content as a trading instruction, order plan, broker status, real-account state, profit guarantee, or live trading readiness
* do not treat v0.8.3 owner alerts as trading instructions, order plans, broker status, real-account actions, profit guarantees, or live trading readiness

## Boundary

* This project remains research-only.
* This system is not live-ready.
* Forward 30d dry-run is not completed.
* Global-briefing historical replay and real package integration are isolated and write no main ledger.
* v0.5.7 authorized historical data acquisition writes no main ledger and does not call run-daily.
* v0.5.7.1 historical data gap closure writes no main ledger and does not call run-daily.
* v0.5.8 day-0 readiness writes no main ledger and does not call run-daily.
* v0.5.8.1 plan alignment writes no main ledger, does not call run-daily, and does not authorize day 1.
* v0.5.9 A-share execution hardening writes no main ledger, does not call run-daily, and does not start forward dry-run.
* v0.6.0 baseline strategy pack writes no main ledger, does not call run-daily, and does not start forward dry-run.
* v0.6.1 daily workflow binding writes no main ledger, does not call run-daily, does not download real-time market data, and does not start forward dry-run.
* v0.6.2 start authorization pack writes no main ledger, does not call run-daily, does not start forward dry-run, and keeps authorization pending.
* v0.6.2.1 owner manual confirmation materialization writes no main ledger, does not call run-daily, does not start forward dry-run, and does not generate a day1 execution prompt.
* v0.6.3 forward dry-run day 1 writes only isolated forward dry-run artifacts, does not call run-daily, does not connect a broker, does not place real orders, and does not write the main ledger.
* v0.6.3.1 day1 continuation artifacts write no day_002 artifacts, do not call run-daily, do not connect a broker, do not place real orders, and do not write the main ledger.
* v0.7.1 A-share data foundation writes equity data and quality artifacts only, does not call run-daily, does not execute day2, does not connect a broker, does not place real orders, and does not generate scores, candidates, or virtual portfolios.
* v0.7.1.1 A-share historical backfill writes history and audit artifacts only, does not call run-daily, does not execute day2, does not connect a broker, does not place real orders, and does not generate scores, candidates, or virtual portfolios.
* v0.7.1.2 A-share historical provider expansion writes history, queue, checkpoint, batch, manifest, and audit artifacts only, does not call run-daily, does not execute day2, does not connect a broker, does not place real orders, and does not generate scores, candidates, or virtual portfolios.
* v0.7.2 A-share tradable universe filtering writes filter buckets and audits only, does not call run-daily, does not execute day2, does not connect a broker, does not place real orders, and does not generate scores, candidates, watchlists, or virtual portfolios.
* v0.7.5 A-share candidate generation writes candidate and watch-pool artifacts only, does not call run-daily, does not execute day2, does not connect a broker, does not place real orders, and does not generate virtual portfolios, buy/sell signals, or order previews.
* v0.7.6 A-share virtual portfolio construction writes virtual portfolio artifacts only, does not call run-daily, does not execute day2, does not connect a broker, does not place real orders, and does not generate real portfolios, buy/sell signals, or broker order previews.
* v0.7.7 A-share daily stock selection briefing writes briefing artifacts only, reads existing artifacts only, does not call run-daily, does not execute day2, does not connect a broker, does not place real orders, and does not regenerate scores, candidates, virtual portfolios, buy/sell signals, or order previews.
* v0.7.8 A-share virtual portfolio tracking writes virtual tracking and paper ledger artifacts only, reads existing artifacts only, does not call run-daily, does not execute day2, does not connect a broker, does not place real orders, and does not generate real portfolios, buy/sell signals, or order previews.
* v0.7.9 A-share daily workflow orchestration writes workflow artifacts only, does not rewrite upstream modules, does not call old run-daily, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, and does not generate buy/sell signals or order previews.
* v0.7.10 A-share benchmark comparison writes benchmark artifacts only, reads existing workflow/tracking/selection/portfolio/price artifacts, does not call old run-daily, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, and does not generate buy/sell signals or order previews.
* v0.7.11 A-share multi-day performance tracking writes virtual performance artifacts only, reads existing workflow/tracking/benchmark/price artifacts, does not call old run-daily, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, does not generate buy/sell signals or order previews, and does not fabricate portfolio history.
* v0.7.12 A-share performance attribution writes attribution and risk diagnostics artifacts only, reads existing performance/benchmark/tracking/portfolio/candidate/score artifacts, does not call old run-daily, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, does not generate buy/sell signals or order previews, and does not fabricate realized attribution.
* v0.8.0 A-share daily data refresh writes provider and dataset validation artifacts only, does not call old run-daily, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, does not generate buy/sell signals or order previews, and does not trigger the full research workflow by default.
* v0.8.1 A-share current-day research runner requires the data refresh audit to pass, then runs the new A-share research workflow CLI; it does not call old run-daily, does not execute official forward dry-run day2, does not connect a broker, does not read real account data, does not place real orders, does not generate buy/sell signals or order previews, and does not treat research output as trade instruction.
* v0.8.2 A-share owner dashboard reads existing run artifacts only, does not refresh data, does not rerun workflow, does not call old run-daily, does not execute official forward dry-run day2, does not connect a broker, does not read real account data, does not place real orders, does not generate buy/sell signals or order previews, and does not treat dashboard content as trade instruction.
* v0.8.3 A-share owner monitoring reads existing dashboard/current-day/data-refresh artifacts only, writes local alert and run-history artifacts, does not send external notifications by default, does not refresh data, does not rerun workflow, does not call old run-daily, does not execute official forward dry-run day2, does not connect a broker, does not read real account data, does not place real orders, does not generate buy/sell signals or order previews, and does not treat alerts as trade instructions.

## v0.7.12 A-Share Attribution Commands

```powershell
python -m trading_core.cli build-a-share-performance-attribution --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-performance-attribution --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-performance-attribution --as-of-date 2026-06-26
```

Modes:

* `current_exposure_diagnostics`
* `single_day_initialization_attribution`
* `multi_day_performance_attribution`

`multi_day_performance_attribution` remains insufficient-history until the configured observation window is met. Current outputs are structural diagnostics, not trading instructions.

## v0.8.0 A-Share Daily Data Refresh Commands

```powershell
python -m trading_core.cli build-a-share-daily-data-refresh --as-of-date 2026-06-26 --mode validate_existing_data
python -m trading_core.cli audit-a-share-daily-data-refresh --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date 2026-06-26 --mode validate_existing_data
```

Modes:

* `validate_existing_data`
* `refresh_from_local_sources`
* `refresh_from_public_providers`
* `refresh_and_validate`

Release E2E uses `validate_existing_data`. Public providers require explicit opt-in. This path validates data freshness and coverage but is not a trading-readiness claim.

## v0.8.1 A-Share Current-Day Research Commands

```powershell
python -m trading_core.cli validate-a-share-current-day-readiness --as-of-date 2026-06-26
python -m trading_core.cli run-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts
python -m trading_core.cli audit-a-share-current-day-research-run --as-of-date 2026-06-26
python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts
```

Release E2E uses `run_research_from_existing_refresh` and `validate_existing_artifacts`. The runner fails closed if the data refresh audit fails.

## v0.8.2 A-Share Owner Dashboard Commands

```powershell
python -m trading_core.cli validate-a-share-owner-dashboard-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-owner-dashboard --as-of-date 2026-06-26 --mode build_dashboard_from_existing_run
python -m trading_core.cli audit-a-share-owner-dashboard --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-owner-dashboard --as-of-date 2026-06-26 --mode build_dashboard_from_existing_run
```

Modes:

* `validate_existing_dashboard_inputs`
* `build_dashboard_from_existing_run`
* `audit_existing_dashboard`

Release E2E uses `build_dashboard_from_existing_run`. The dashboard reads existing artifacts only and should be followed by v0.8.3 alerting/run-history work.

## v0.8.3 A-Share Owner Monitoring Commands

```powershell
python -m trading_core.cli validate-a-share-owner-monitoring-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-owner-monitoring --as-of-date 2026-06-26 --mode build_monitoring_dashboard
python -m trading_core.cli audit-a-share-owner-monitoring --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-owner-monitoring --as-of-date 2026-06-26 --mode build_monitoring_dashboard
```

Modes:

* `validate_monitoring_inputs`
* `build_run_history_from_existing_artifacts`
* `evaluate_owner_alerts`
* `build_monitoring_dashboard`

Release E2E uses `build_monitoring_dashboard` with external notifications disabled. v0.8.4 should add owner remediation runbooks and safe action checklists.
# v0.8.4 A-share owner remediation

Validate inputs:

```bash
python -m trading_core.cli validate-a-share-owner-remediation-inputs --as-of-date 2026-06-26
```

Build runbook and checklist:

```bash
python -m trading_core.cli build-a-share-owner-remediation --as-of-date 2026-06-26 --mode build_remediation_runbook
```

Audit existing remediation artifacts:

```bash
python -m trading_core.cli audit-a-share-owner-remediation --as-of-date 2026-06-26
```

Build and audit:

```bash
python -m trading_core.cli build-and-audit-a-share-owner-remediation --as-of-date 2026-06-26 --mode build_remediation_runbook
```

These commands generate plans and checklists only. They do not execute remediation actions, refresh data, rerun research workflow, generate buy/sell signals, place orders, connect broker, call old run-daily, execute official forward dry-run day2, or treat remediation as trade instruction.
# v0.8.5 A-share daily ops command center

Validate inputs:

```bash
python -m trading_core.cli validate-a-share-daily-ops-inputs --as-of-date 2026-06-26
```

Build the ops command center from existing artifacts:

```bash
python -m trading_core.cli build-a-share-daily-ops-center --as-of-date 2026-06-26 --mode aggregate_existing_ops_artifacts
```

Audit existing ops center artifacts:

```bash
python -m trading_core.cli audit-a-share-daily-ops-center --as-of-date 2026-06-26
```

Build and audit:

```bash
python -m trading_core.cli build-and-audit-a-share-daily-ops-center --as-of-date 2026-06-26 --mode aggregate_existing_ops_artifacts
```

These commands aggregate existing ops artifacts by default. They do not refresh data, rerun current-day research, execute remediation actions, generate buy/sell signals, generate order preview, connect broker, place real orders, call old run-daily, execute official forward dry-run day2, or treat ops output as trade instruction.
