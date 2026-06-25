# Trading Core

## What this project is

- file-backed virtual trading research system
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

v0.5.6-real-global-briefing-signal-integration-audited

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

## Known limitations

- forward 30d dry-run not completed
- global-briefing real package integration is complete for local fixture E2E, but fixture smoke data is not broad historical coverage
- strategy effectiveness not proven
- no live trading

## Quickstart

Install and verify:

```powershell
python -m trading_core.cli --help
python -m pytest
```

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

## Safety boundary

- no broker
- no live trading
- no real orders
- no auto promotion
- local global-briefing package integration uses local files only and no network access
- no forward dry-run started by the historical replay harness
- no forward dry-run started by the real package integration workflow
- no labels, ML shadow, experiments, RL, or LLM trading decisions in the global-briefing replay decision path
- isolated replay ledger is written only under `data/replays/global_briefing/`
