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
```
