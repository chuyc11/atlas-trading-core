# Runbook

All commands are local, file-backed, and virtual/research-only.

## Tests

```powershell
python -m pytest
```

## Historical data validation

```powershell
python -m trading_core.cli validate-data-package --input data/raw/prices/etf_daily
python -m trading_core.cli real-data-validation-report --artifact-dir outputs/validation
```

## Feature / label

```powershell
python -m trading_core.cli build-features --start-date START --end-date END --data data/raw/prices/etf_daily
python -m trading_core.cli build-labels --start-date START --end-date END --data data/raw/prices/etf_daily
python -m trading_core.cli build-ml-dataset --features data/features/features.jsonl --labels data/labels/labels.jsonl --start-date START --end-date END --train-days 252 --validation-days 63 --test-days 21 --step-days 21 --label-column forward_return_5d
```

## ML shadow

```powershell
python -m trading_core.cli train-ml-shadow --dataset data/ml/walk_forward_dataset.json --rows data/ml/walk_forward_rows.jsonl --model-type mock --label-column forward_return_5d
python -m trading_core.cli predict-ml-shadow --model data/ml/ml_shadow_model.json --rows data/ml/walk_forward_rows.jsonl
python -m trading_core.cli generate-ml-shadow-signals --predictions data/ml/ml_shadow_predictions.jsonl --top-k 3 --target-weight 0.05
python -m trading_core.cli ml-shadow-leaderboard --predictions data/ml/ml_shadow_predictions.jsonl --signals data/shadow/ml_shadow_signals.jsonl
python -m trading_core.cli ml-shadow-report --dataset data/ml/walk_forward_dataset.json --model data/ml/ml_shadow_model.json --predictions data/ml/ml_shadow_predictions.jsonl --signals data/shadow/ml_shadow_signals.jsonl --leaderboard data/shadow/ml_shadow_leaderboard.json
```

## Experiment system

```powershell
python -m trading_core.cli register-experiment --config config/experiments/momentum_sweep.yaml
python -m trading_core.cli run-parameter-sweep --config config/experiments/momentum_sweep.yaml
python -m trading_core.cli compare-strategies --inputs data/experiments/parameter_sweep-EXP-sweep-momentum-20260624.json data/shadow/ml_shadow_leaderboard-2024-01-01-2026-06-23-MLSHADOW-20240101-20260623-mock.json
python -m trading_core.cli simulate-promotion --comparison data/experiments/strategy_comparison-20260624-134823-738476.json
python -m trading_core.cli update-mistake-patterns --inputs data/experiments/parameter_sweep-EXP-sweep-momentum-20260624.json data/experiments/strategy_comparison-20260624-134823-738476.json data/experiments/promotion_simulation-20260624-134834-576436.json data/shadow/ml_shadow_leaderboard-2024-01-01-2026-06-23-MLSHADOW-20240101-20260623-mock.json
python -m trading_core.cli experiment-dashboard
```

## Reporting system

```powershell
python -m trading_core.cli weekly-research-report --start-date START --end-date END --include-experiments --include-ml-shadow --include-mistakes
python -m trading_core.cli monthly-research-report --start-date START --end-date END --include-weekly --include-experiments --include-ml-shadow
python -m trading_core.cli system-dashboard --include-artifact-inventory --include-release-status
python -m trading_core.cli project-status-report --include-next-steps --include-risk-register
python -m trading_core.cli run-research-pipeline --start-date START --end-date END
```

## Audit commands

```powershell
python -m trading_core.cli audit-experiment-system
python -m trading_core.cli audit-reporting-system
python -m trading_core.cli cli-inventory
python -m trading_core.cli artifact-inventory
python -m trading_core.cli system-smoke-test --include-reports --include-inventory
python -m trading_core.cli boundary-regression-audit
python -m trading_core.cli system-integrity-audit
python -m trading_core.cli audit-global-briefing-real-package-integration
python -m trading_core.cli audit-global-briefing-evidence-quality
python -m trading_core.cli audit-historical-data-acquisition
```

## Global briefing historical replay harness

This workflow builds an isolated historical replay harness for global-briefing macro signal packages. It is not forward dry-run validation, not live trading readiness, and not strategy effectiveness proof.

```powershell
python -m trading_core.cli global-briefing-contract
python -m trading_core.cli validate-global-briefing-signals --input tests/fixtures/global_briefing/signals_valid.jsonl --start-date 2024-01-02 --end-date 2024-01-08
python -m trading_core.cli build-global-briefing-replay-bundle --signals tests/fixtures/global_briefing/signals_valid.jsonl --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --allow-carry-forward
python -m trading_core.cli replay-global-briefing-history --bundle data/replays/global_briefing/replay_bundle-2024-01-02-2024-01-08.json --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --execution-mode isolated --initial-cash 1000000
python -m trading_core.cli global-briefing-replay-report --replay data/replays/global_briefing/global_briefing_replay-2024-01-02-2024-01-08.json
python -m trading_core.cli audit-isolated-replay-adapter
```

Boundary:

- isolated replay only
- no-trade fallback replaced for the fixture E2E path
- isolated replay ledger written only under `data/replays/global_briefing/`
- no broker
- no live trading
- no forward dry-run started or validated
- no main orders/trades/portfolio/accounts writes
- no labels, ML shadow, experiments, or promotion in the replay decision path

## Real global-briefing package integration

This workflow ingests a local historical global-briefing package, normalizes it to the v1 signal contract, checks coverage and point-in-time safety, runs the isolated replay adapter, builds an integration report, and audits release readiness. It is local-file-only and does not use network access.

```powershell
python -m trading_core.cli global-briefing-package-manifest --root tests/fixtures/global_briefing_real
python -m trading_core.cli normalize-global-briefing-package --input tests/fixtures/global_briefing_real/real_package_aliases.csv --package-id GB-REAL-FIXTURE --region CN --source global_briefing --version v1
python -m trading_core.cli audit-global-briefing-package-coverage --signals data/global_briefing/normalized/GB-REAL-FIXTURE.normalized.jsonl --prices tests/fixtures/global_briefing_real/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --min-coverage 0.60
python -m trading_core.cli run-global-briefing-real-package-replay --input tests/fixtures/global_briefing_real/real_package_aliases.csv --prices tests/fixtures/global_briefing_real/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --package-id GB-REAL-FIXTURE --region CN --source global_briefing --version v1 --allow-carry-forward --min-coverage 0.60 --execution-mode isolated
python -m trading_core.cli global-briefing-real-package-report
python -m trading_core.cli audit-global-briefing-real-package-integration
```

Boundary:

- local historical package integration only
- no network access
- isolated replay only
- no main orders/trades/portfolio/accounts writes
- run-daily not called
- labels, ML shadow, experiments, promotion, RL, and LLM trading decisions not used
- forward dry-run not started or validated
- not live trading readiness
- not strategy effectiveness proof

## Global briefing evidence quality

This workflow explains the quality and limits of the v0.5.6 real-package-style evidence. It is evidence-quality only and does not accept a production package by itself.

```powershell
python -m trading_core.cli global-briefing-warning-triage
python -m trading_core.cli global-briefing-evidence-quality-report
python -m trading_core.cli global-briefing-production-acceptance-criteria
python -m trading_core.cli audit-global-briefing-evidence-quality
```

Boundary:

- evidence-quality only
- production readiness remains false
- no replay started
- no main orders/trades/portfolio/accounts writes
- run-daily not called
- no network access
- not strategy effectiveness proof
- not forward dry-run validation
- not live trading readiness

## Authorized historical data acquisition

This workflow downloads or loads the authorized historical packages required for research replay and global-briefing proxy construction. Historical data authorization is not trading authorization. The unified proxy package is not an internal global-briefing signal package, and production global-briefing package status must be reported separately.

```powershell
python -m trading_core.cli download-historical-data-packages --start-date 2018-01-01 --end-date latest --continue-on-error
python -m trading_core.cli normalize-historical-data-packages
python -m trading_core.cli audit-historical-data-quality
python -m trading_core.cli run-full-historical-proxy-replay --start-date 2024-01-02 --end-date 2024-12-31 --execution-mode isolated --min-coverage 0.80
python -m trading_core.cli historical-data-acquisition-report
python -m trading_core.cli audit-historical-data-acquisition
```

Boundary:

- historical data acquisition only
- no broker/account/order/trade/position/margin data
- no real orders
- no main orders/trades/portfolio/accounts writes
- isolated replay ledger written only under `data/replays/global_briefing/`
- run-daily not called
- labels, ML shadow, experiments, promotion, RL, and LLM trading decisions not used
- forward dry-run not started or validated
- historical replay is not strategy effectiveness proof
- not live trading readiness

## Historical data gap closure and warning reduction

This workflow is the v0.5.7.1 patch path. It repairs or substitutes EPU and OECD CLI historical research inputs, rebuilds the unified proxy package and normalized proxy package, groups warnings, reruns isolated replay, regenerates acquisition evidence, and audits the gap closure.

```powershell
python -m trading_core.cli close-historical-data-gaps --start-date 2018-01-01 --end-date latest --replay-start-date 2024-01-02 --replay-end-date 2024-12-31 --min-coverage 0.80 --continue-on-error
python -m trading_core.cli historical-warning-inventory
python -m trading_core.cli historical-data-gap-closure-report
python -m trading_core.cli audit-historical-data-gap-closure
```

Boundary:

- historical data authorization is not trading authorization
- EPU repair may use authorized/local/API/FRED-compatible data or a policy-uncertainty proxy
- OECD CLI repair may use authorized/local/API data or an authorized macro-cycle proxy marked as not official OECD CLI
- no broker/account/order/trade/position/margin data
- no main orders/trades/portfolio/accounts writes
- isolated replay ledger written only under `data/replays/global_briefing/`
- run-daily not called
- labels, ML shadow, experiments, promotion, RL, and LLM trading decisions not used
- forward dry-run not started or validated
- historical replay is not strategy effectiveness proof
- not live trading readiness

## Day-0 operational readiness pack

This v0.5.8 workflow prepares the day-0 packet for a future 30 trading-day forward dry-run. Day-0 readiness does not start forward dry-run.

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

Boundary:

- day-0 readiness does not start forward dry-run
- run-daily not called
- manual confirmation remains incomplete by default
- EPU partial limitation accepted
- OECD macro-cycle proxy limitation accepted and not official OECD CLI
- internal global-briefing historical package remains not_configured
- proxy package is not an internal global-briefing signal
- historical data authorization is not trading authorization
- not strategy effectiveness proof
- not live trading readiness
- main ledger not written

## Plan alignment and MVP gap audit

This v0.5.8.1 workflow audits the project plan against current MVP evidence. Plan alignment is an audit, not day 1 authorization.

```powershell
python -m trading_core.cli plan-checklist
python -m trading_core.cli mvp-requirement-map
python -m trading_core.cli artifact-coverage-scanner
python -m trading_core.cli classify-mvp-gaps
python -m trading_core.cli classify-day1-blockers
python -m trading_core.cli next-work-register
python -m trading_core.cli audit-plan-alignment
```

Boundary:

- plan alignment audit only
- forward dry-run not started
- run-daily not called
- main ledger not written
- historical replay is not forward validation
- historical performance is not strategy effectiveness proof
- ML shadow not used as day-1 authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- recommended next version is generated by `next-work-register`
