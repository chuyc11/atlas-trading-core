# Baseline Strategy Contract

Baseline strategy pack is research-only and does not start forward dry-run.

## Strategies
- equal_weight_etf_rotation: equal_weight_etf_rotation_v1
  - deterministic rule-based
  - after T close signal, T+1 execution
  - isolated replay only
  - not strategy effectiveness proof
  - not forward dry-run validation
  - not live trading readiness
- momentum_risk_adjusted_rotation: momentum_risk_adjusted_rotation_v1
  - deterministic rule-based
  - after T close signal, T+1 execution
  - isolated replay only
  - not strategy effectiveness proof
  - not forward dry-run validation
  - not live trading readiness
- defensive_cash_rotation: defensive_cash_rotation_v1
  - deterministic rule-based
  - after T close signal, T+1 execution
  - isolated replay only
  - not strategy effectiveness proof
  - not forward dry-run validation
  - not live trading readiness

## Boundary
- contract only
- run-daily not called
- forward dry-run not started
- main ledger not written
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
