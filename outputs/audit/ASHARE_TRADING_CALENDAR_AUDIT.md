# A-Share Trading Calendar Audit

## Overall Verdict
- overall_passed=true

## Checks
- sse_weekday_trading_day: true
- szse_weekday_trading_day: true
- hkex_weekday_trading_day: true
- weekend_non_trading: true
- explicit_holiday_non_trading: true
- next_trading_day_skips_weekend: true
- next_trading_day_skips_holiday: true
- previous_trading_day: true
- hkex_and_ashare_differ: true
- weekday_assumption_forbidden: true

## Boundary
- calendar audit only
- run-daily not called
- forward dry-run not started
- main ledger not written
