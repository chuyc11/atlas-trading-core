# Baseline Strategy Pack

v0.6.0 adds three deterministic rule-based baseline strategies:

- `equal_weight_etf_rotation`
- `momentum_risk_adjusted_rotation`
- `defensive_cash_rotation`

Baseline strategy pack is research-only and does not start forward dry-run.

## Coverage

- strategy contract
- parameter versioning
- input declarations
- PIT-safe signal generation
- after T close signal timing
- T+1 earliest execution semantics
- preview-only order proposals
- isolated replay only
- v0.5.9 virtual execution rules
- benchmark comparison
- strategy reports
- baseline strategy pack audit
- day1 blocker reclassification v060

## Commands

```powershell
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

## Boundary

- run-daily not called
- forward dry-run not started
- forward dry-run not validated
- main ledger not written
- order previews use `preview_only=true`
- order previews use `executed=false`
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- experiments and promotion outputs not used as authorization
- promotion not triggered
- historical performance is not strategy effectiveness proof
- not forward dry-run validation
- not live trading readiness
- no broker connected
- recommended next version is `v0.6.1-daily-workflow-binding`

