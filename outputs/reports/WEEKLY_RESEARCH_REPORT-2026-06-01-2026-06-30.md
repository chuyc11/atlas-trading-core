# Weekly Trading Research Report

## 1. Scope
- start_date: 2026-06-01
- end_date: 2026-06-30
- period_type: weekly

## 2. Executive Summary
- overall_status: watch
- critical_errors: 0
- warnings: []

## 3. Trading Activity
- run_days: 8
- orders: 8
- trades: 0
- rejected_orders: 0
- portfolio continuity notes: []

## 4. Risk and Account Review
- risk events: 0
- drawdown notes: []
- position notes: []

## 5. ML Shadow Review
- model_id: MLSHADOW-20260101-20260131-mock
- prediction_count: 30
- signal_count: 10
- recommendation: promising
- boundary: shadow only

## 6. Experiment Review
- parameter sweep count: 2
- strategy comparison count: 1
- promotion simulation count: 1
- mistake pattern count: 4

## 7. Mistake Patterns
- unstable_rank_ic | severity=high | evidence=242 | action=keep_shadow
- benchmark_underperformance | severity=high | evidence=48 | action=compare_benchmark
- cost_drag | severity=high | evidence=24 | action=reduce_turnover
- overfit_parameter | severity=high | evidence=24 | action=require_more_data

## 8. Limitations
- not an admission gate
- not live trading
- not forward 30d dry-run
- not active promotion

## 9. Safety Boundary
- research_only=true
- no orders/trades/portfolio/accounts written
- no strategy state changed
- no promotion triggered
- This does not validate forward 30d dry-run.
