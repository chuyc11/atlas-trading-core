# Forward Dry-Run Day-0 Checklist

## 1. Baseline
- Current git commit recorded
- Current tag recorded
- python -m pytest passed
- boundary-regression-audit passed
- system-integrity-audit passed
- usability-audit passed

## 2. Universe Freeze
- ETF universe frozen
- Benchmark set frozen
- Strategy configuration frozen
- Risk configuration frozen

## 3. Data Readiness
- Price source path confirmed
- Macro signal source confirmed
- No future data available to run-daily
- Calendar source confirmed

## 4. Boundary Confirmation
- No broker
- No live trading
- No real orders
- No ML shadow in run-daily
- No labels in run-daily
- No experiment promotion

## 5. Output Paths
- Forward dry-run output path confirmed
- Historical replay output path separated
- ML shadow output path separated
- Experiment output path separated

## 6. Daily Procedure
- run-daily command documented
- health command documented
- export-summary command documented
- check-consistency command documented

## 7. Stop Conditions
- data missing
- consistency failure
- unexpected main ledger mutation
- run-daily imports labels / ML / experiments
- strategy state modified unexpectedly
