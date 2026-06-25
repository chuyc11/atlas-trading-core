# Historical Warning Inventory

## Scope
This report groups warnings from v0.5.7 historical data quality and proxy replay artifacts.
Historical data authorization is not trading authorization.

## Raw Warning Count
- 346

## Grouped Warning Count
- 10

## Categories
- coverage_gap: 1
- lot_size_constraint: 1
- missing_optional_package: 1
- missing_price: 1
- missing_signal_component: 2
- source_download_failed: 4

## Top Warning Groups
- source_download_failed severity=medium raw_count=5 pattern=FRED source unavailable or timed out
- source_download_failed severity=medium raw_count=4 pattern=FRED source unavailable or timed out
- missing_optional_package severity=medium raw_count=2 pattern=optional package status explained
- missing_signal_component severity=medium raw_count=2 pattern=policy uncertainty / EPU component unavailable or proxied
- source_download_failed severity=medium raw_count=2 pattern=FRED source unavailable or timed out
- missing_signal_component severity=medium raw_count=1 pattern=OECD CLI / macro-cycle component unavailable or proxied
- source_download_failed severity=medium raw_count=1 pattern=FRED source unavailable or timed out
- lot_size_constraint severity=medium raw_count=172 pattern=target delta below lot size
- missing_price severity=high raw_count=156 pattern=missing replay price for symbol
- coverage_gap severity=medium raw_count=123 pattern=coverage gap in replay calendar or price-aligned dates

## Fix Plan
- source_download_failed: use configured authorized/local source or documented fallback
- source_download_failed: use configured authorized/local source or documented fallback
- missing_optional_package: configure optional source if production validation is required
- missing_signal_component: review EPU source configuration or accept proxy limitation
- source_download_failed: use configured authorized/local source or documented fallback
- missing_signal_component: review OECD source configuration or accept macro-cycle proxy
- source_download_failed: use configured authorized/local source or documented fallback
- lot_size_constraint: review lot size and target-weight settings
- missing_price: fill historical price gap or reduce replay universe
- coverage_gap: review calendar and expected trading-day basis

## Boundary
- inventory only
- no run-daily call
- no main ledger write
- not forward dry-run
- not strategy effectiveness proof
