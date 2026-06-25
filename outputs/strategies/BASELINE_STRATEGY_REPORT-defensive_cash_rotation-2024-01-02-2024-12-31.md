# Baseline Strategy Report - defensive_cash_rotation

Baseline strategy pack is research-only and does not start forward dry-run.

## Strategy
- strategy_id: defensive_cash_rotation
- strategy_version: defensive_cash_rotation_v1
- objective: Shift between ETF exposure and cash based on a global risk proxy.

## PIT Constraints
- uses signal_date or earlier price data
- uses signal_date or earlier risk proxy data
- generated after T close
- execution earliest date is T+1 or later

## Replay Summary
- orders: 5
- trades: 4
- rejected_orders: 1
- no_trade_fallback: False

## Benchmark Comparison
- cumulative_return: -0.03851471
- max_drawdown: -0.03851471

## Execution Summary
- execution_mode: isolated
- uses_v059_virtual_execution_contract: True
- isolated_outputs_only: True

## Explicit Non-Claims
- This is not strategy effectiveness proof.
- This is not forward dry-run validation.
- This is not live trading readiness.
- This does not trigger promotion.
- This does not use ML/LLM/RL for trading decisions.

## Boundary
- strategy report only
- run-daily not called
- forward dry-run not started
- main ledger not written
