# Forward Dry-Run Operating Calendar

## Scope
This is a calendar/template for a future 30 trading-day forward dry-run.
It does not start the forward dry-run.
Historical data authorization is not trading authorization.

## Day Template
- status=not_started
- expected checks: data refresh, command preview, artifacts, protected paths, warning log, manual note

## Weekly Review
- day 5
- day 10
- day 15
- day 20
- day 25
- day 30

## Fail-Closed Rules
- missing data
- consistency failure
- unexpected protected path mutation
- run-daily import boundary breach
- manual stop

## Boundary
- calendar only
- forward dry-run not started
- run-daily not called
