# Historical Data Quality Audit

## Overall Verdict
- overall_passed=true
- blocking_reasons=[]

## Coverage
- start_date: 2018-01-01
- end_date: 2026-06-25
- required_packages: 9
- available_packages: 8
- critical_packages_available: True

## Packages
- HIST-ETF-OHLCV-CN-HK-V1: passed=true status=downloaded coverage_ratio=0.999677
- HIST-BENCHMARK-INDEX-CN-HK-V1: passed=true status=downloaded coverage_ratio=1.0
- HIST-FX-USDCNY-V1: passed=true status=downloaded coverage_ratio=1.0
- HIST-GLOBAL-RISK-VIX-V1: passed=true status=downloaded coverage_ratio=0.999354
- HIST-RATES-LIQUIDITY-V1: passed=true status=downloaded coverage_ratio=0.999354
- HIST-COMMODITY-INFLATION-RISK-V1: passed=true status=downloaded coverage_ratio=0.999677
- HIST-POLICY-UNCERTAINTY-EPU-V1: passed=true status=partial_downloaded coverage_ratio=1.0
- HIST-OECD-CLI-MACRO-CYCLE-V1: passed=true status=downloaded coverage_ratio=0.623951
- HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1: passed=true status=not_configured coverage_ratio=0.0

## Boundary
- Historical data authorization is not trading authorization.
- quality audit only
- no main ledger write
- no run-daily call
- not forward dry-run validation
- not strategy effectiveness proof
