# Artifact Inventory

| artifact | path | exists | category | machine_readable | human_readable | main chain |
|---|---|---|---|---|---|---|
| data/raw | data/raw | true | raw | true | false | false |
| data/features | data/features | true | features | true | false | false |
| data/labels | data/labels | true | labels | true | false | false |
| data/ml | data/ml | true | ml | true | false | false |
| data/shadow | data/shadow | true | shadow | true | false | false |
| data/experiments | data/experiments | true | experiments | true | false | false |
| data/reports | data/reports | true | reports | true | false | false |
| data/system | data/system | true | system | true | false | false |
| outputs/backtests | outputs/backtests | true | backtests | false | true | false |
| outputs/replays | outputs/replays | true | replays | false | true | false |
| outputs/shadow | outputs/shadow | true | shadow | false | true | false |
| outputs/experiments | outputs/experiments | true | experiments | false | true | false |
| outputs/reports | outputs/reports | true | reports | false | true | false |
| outputs/system | outputs/system | true | system | false | true | false |
| outputs/audit | outputs/audit | true | audit | false | true | false |
| mistake_pattern_library.json | data/experiments/mistake_pattern_library.json | true | experiments | true | false | false |
| experiment_dashboard.json | data/experiments/experiment_dashboard.json | true | experiments | true | false | false |
| weekly_research_summary-2026-06-17-2026-06-23.json | data/reports/weekly_research_summary-2026-06-17-2026-06-23.json | true | reports | true | false | false |
| cli_inventory.json | data/system/cli_inventory.json | true | system | true | false | false |
| artifact_inventory.json | data/system/artifact_inventory.json | true | system | true | false | false |
| system_smoke_test.json | data/system/system_smoke_test.json | true | system | true | false | false |
| boundary_regression_audit.json | data/system/boundary_regression_audit.json | true | system | true | false | false |
| system_integrity_audit.json | data/system/system_integrity_audit.json | false | system | true | false | false |
| SYSTEM_INTEGRITY_AUDIT.md | outputs/audit/SYSTEM_INTEGRITY_AUDIT.md | false | audit | false | true | false |

## Safety Boundary
- inventory only
- no orders/trades/portfolio/accounts written
- artifacts are not live trading instructions
