# v0.5.1 Validation Gap Remediation

## Remediated Gaps
- timezone
- max_daily_turnover enforcement
- mistake pattern boundary metadata

## Deferred Gaps
- market-rule-aware execution deferred to v0.6
- generalized Point-in-Time schema deferred to v0.7

## Safety Boundary
- remediation only
- no strategy state changed
- no strategy parameter changed
- no promotion triggered
- no orders/trades/portfolio/accounts written
- run-daily not called

## Details
- GAP-002: project_timezone changed to Asia/Shanghai
- GAP-003: max_daily_turnover is enforced by risk engine
- GAP-004: mistake_pattern_library JSON now includes explicit diagnostic boundary metadata

## Deferred Details
- GAP-001: market-rule-aware execution requires larger simulation realism release
- GAP-005: generalized Point-in-Time schema requires separate data architecture release
