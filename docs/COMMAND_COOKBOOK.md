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
```

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
