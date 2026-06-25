# Global Briefing Signal Validation

## Overall Verdict
- overall_passed=true
- blocking_reasons=[]

## Coverage
- expected_trading_days=7
- observed_signal_days=3
- coverage_ratio=0.42857142857142855
- missing_dates=['2024-01-04', '2024-01-06', '2024-01-07', '2024-01-08']

## Point-in-Time Safety
- passed=true
- future_signal_rows=0

## Warnings
- duplicate as_of_date rows available for point-in-time selection: ['2024-01-05']
- missing signal dates: ['2024-01-04', '2024-01-06', '2024-01-07', '2024-01-08']

## Boundary
- validation only
- replay not started
- no orders/trades/portfolio/accounts written
- run-daily not called
