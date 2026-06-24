# Global Briefing Signal Contract

## Scope
This contract defines historical macro signal packages accepted by trading-core.

## Required Fields
- as_of_date
- generated_at
- region
- signals
- source
- version

## Point-in-Time Rules
- Only signals generated at or before the replay decision timestamp may be used.
- Future macro signals must be rejected.

## What This Is Not
- not a live global-briefing integration
- not live trading
- not forward dry-run
- not strategy effectiveness proof

## Boundary
- contract only
- no network access
- no main ledger writes
- run-daily not called
