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

## What not to do

* do not run live trading
* do not treat shadow as active
* do not use historical replay as forward dry-run
* do not use reports as admission gate
* do not treat global-briefing replay artifacts as broker or promotion output
* do not treat real package integration as live readiness or forward validation
* do not treat evidence-quality reports as production package acceptance

## Boundary

* This project remains research-only.
* This system is not live-ready.
* Forward 30d dry-run is not completed.
* Global-briefing historical replay and real package integration are isolated and write no main ledger.
