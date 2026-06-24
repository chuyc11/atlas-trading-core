# Trading Core System Dashboard

## 1. Version Status
- current VERSION: v0.3.0-ml-shadow-pipeline-audited
- latest known tag: v0.4.0-strategy-experiment-system-audited
- release stages: {'v0.1': 'completed', 'v0.2': 'historical-real-data validated', 'v0.3': 'ml-shadow-pipeline audited', 'v0.4': 'strategy-experiment-system audited', 'v0.5': 'in_progress'}

## 2. Completed Milestones
- v0.1 core hardened
- v0.2 historical real-data validated
- v0.2.1 price-only historical replay validated
- v0.3 ML shadow pipeline audited
- v0.4 strategy experiment system audited

## 3. Artifact Inventory
| artifact | exists | notes |
|---|---|---|
| real_data_validation | true | present |
| historical_replay | false | missing |
| ml_shadow_report | true | present |
| experiment_system_audit | true | present |
| weekly_report | true | present |
| monthly_report | true | present |

## 4. Current Research Status
- trading core: file-backed virtual trading research
- ML shadow: shadow only, not active
- experiments: research artifacts only
- reports: v0.5 in progress
- validations: historical and audit evidence only

## 5. Known Limitations
- forward 30d dry-run not completed
- full global-briefing replay not completed
- no real broker
- no live trading
- strategy effectiveness not proven

## 6. Safety Boundary
- no broker
- no live trading
- no RL active trading
- no LLM trading decision
- no active promotion
