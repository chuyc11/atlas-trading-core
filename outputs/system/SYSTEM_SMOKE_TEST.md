# System Smoke Test

- passed: true
- blocking_reasons: []
- warnings: []

| check | passed | severity | details |
|---|---|---|---|
| version_exists | true | required |  |
| readme_exists | true | required |  |
| doc_exists:docs/ARCHITECTURE.md | true | required |  |
| doc_exists:docs/SAFETY_BOUNDARY.md | true | required |  |
| doc_exists:docs/RELEASE_MATRIX.md | true | required |  |
| doc_exists:docs/CLI_REFERENCE.md | true | required |  |
| doc_exists:docs/ARTIFACT_MAP.md | true | required |  |
| doc_exists:docs/RUNBOOK.md | true | required |  |
| doc_exists:docs/FORWARD_DRY_RUN_RUNBOOK.md | true | required |  |
| module_importable:trading_core.cli | true | required |  |
| module_importable:trading_core.daily_run | true | required |  |
| module_importable:trading_core.features.feature_store | true | required |  |
| module_importable:trading_core.labels.label_store | true | required |  |
| module_importable:trading_core.ml.shadow_leaderboard | true | required |  |
| module_importable:trading_core.experiments.experiment_dashboard | true | required |  |
| module_importable:trading_core.reports.research_pipeline | true | required |  |
| key_cli_inventory_available | true | required |  |
| artifact_inventory_available | true | required |  |
| artifact_present:data/experiments/experiment_registry.json | true | optional |  |
| artifact_present:data/experiments/mistake_pattern_library.json | true | optional |  |
| artifact_present:data/shadow/ml_shadow_leaderboard-2024-01-01-2026-06-23-MLSHADOW-20240101-20260623-mock.json | true | optional |  |
| artifact_present:data/reports/monthly_research_summary-2026-06-01-2026-06-30.json | true | optional |  |
| report_dir_present:outputs/reports | true | optional |  |
| report_dir_present:outputs/system | true | optional |  |
| reporting_pipeline_commands_available | true | required | registered |
| experiment_artifacts_present | true | optional |  |
| ml_shadow_artifacts_present | true | optional |  |
| no_protected_ledger_write | true | required |  |

## Safety Boundary
- smoke only
- run-daily not called
- no orders/trades/portfolio/accounts written
