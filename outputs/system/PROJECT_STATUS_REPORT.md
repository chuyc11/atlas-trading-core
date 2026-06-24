# Project Status Report

## 1. Current Stage
- v0.5 research reporting control plane

## 2. Completed Versions
- v0.1.0-core-hardened
- v0.2.0-historical-real-data-validated
- v0.2.1-price-only-historical-replay-validated
- v0.3.0-ml-shadow-pipeline-audited
- v0.4.0-strategy-experiment-system-audited

## 3. Completed Capabilities
- core_trading: file-backed virtual trading, risk, valuation
- real_data_validation: historical validation, price-only replay
- ml_shadow: features, labels, leaderboard
- experiment_system: registry, sweep, comparison, simulation, mistake patterns
- reporting: v0.5 reporting in progress

## 4. Open Items
- forward 30d dry-run
- full global-briefing historical replay
- strategy effectiveness proof
- v0.5 release audit

## 5. Risk Register
- Shadow results may be misread as live trading readiness | severity=high | mitigation=Keep reports explicitly marked as research-only

## 6. Next Steps
- Complete v0.5 release audit
- Do not start RL before reporting layer is audited

## 7. Boundary
- project is research-only
- no live trading
- no broker
- no active promotion
