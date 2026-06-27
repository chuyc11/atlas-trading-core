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
```

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
