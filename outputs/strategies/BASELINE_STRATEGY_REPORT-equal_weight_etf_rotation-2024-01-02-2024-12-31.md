# Baseline Strategy Report - equal_weight_etf_rotation

Baseline strategy pack is research-only and does not start forward dry-run.

## Strategy
- strategy_id: equal_weight_etf_rotation
- strategy_version: equal_weight_etf_rotation_v1
- objective: Maintain an equal-weight ETF baseline across tradable universe members.

## PIT Constraints
- uses signal_date or earlier price data
- uses signal_date or earlier risk proxy data
- generated after T close
- execution earliest date is T+1 or later

## Replay Summary
- orders: 9
- trades: 8
- rejected_orders: 1
- no_trade_fallback: False

## Benchmark Comparison
- cumulative_return: -0.04386981
- max_drawdown: -0.04734279

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
