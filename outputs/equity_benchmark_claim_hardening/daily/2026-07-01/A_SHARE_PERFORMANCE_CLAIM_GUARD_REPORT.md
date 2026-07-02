# A股绩效声明 Guard 报告

## Allowed
- simulation status statement
- data quality statement
- internal research metric
- simulated benchmark-relative metric only when benchmark coverage and alignment pass

## Blocked
- real performance claim
- unverified benchmark-relative claim
- live trading ready claim
- investment advice claim

## Current Decision
- benchmark_relative_claim_allowed: False
- simulated_performance_claim_allowed_with_disclaimer: True
- real_performance_claim_allowed: False
