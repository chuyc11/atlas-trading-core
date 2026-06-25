# Day-0 Manual Confirmation Packet

## Scope
This packet must be reviewed manually before any future forward dry-run starts.
This file does not authorize automatically.
Day-0 readiness does not start forward dry-run.
Historical data authorization is not trading authorization.

## Accepted Limitations
- EPU partial: missing us_epu/europe_epu; policy uncertainty proxy only.
- OECD macro-cycle proxy is not official OECD CLI.
- Internal global-briefing historical signal package remains not_configured.
- Proxy package is not an internal global-briefing signal.

## Explicit Non-Claims
- not strategy effectiveness proof
- not forward dry-run validation
- not live trading readiness
- not trading authorization

## Manual Confirmation Fields
All confirmation fields default to false.
- owner_confirmed_data_freeze: false
- owner_confirmed_warning_acceptance: false
- owner_confirmed_no_blocking_conditions: false
- owner_confirmed_run_daily_preview: false
- owner_confirmed_forward_dry_run_can_start: false

## Boundary
- manual confirmation packet only
- no auto-confirmation
- forward dry-run not started
- run-daily not called
