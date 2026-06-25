# Forward Dry-Run Run-Daily Command Preview

v0.6.2 creates an authorization pack only and does not start forward dry-run

## Preview
- command: `python -m trading_core.cli run-daily --mode forward-dry-run --day-index 1`
- preview_only: true
- executed: false
- run_daily_called: false
- metadata only; not instructions to execute day1

## Boundary
- v0.6.2 creates an authorization pack only and does not start forward dry-run
- run-daily not called
- forward dry-run not started
- forward dry-run not validated
- main ledger not written
- manual confirmation defaults false
- owner authorization defaults false
- not forward dry-run validation
- not strategy effectiveness proof
- not live trading readiness
- no broker connected
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
