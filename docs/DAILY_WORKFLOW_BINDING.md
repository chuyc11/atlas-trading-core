# Daily Workflow Binding

v0.6.1 adds daily workflow binding for research preview infrastructure. It uses local authorized historical daily data snapshots and does not download real-time market data.

## Workflow

- daily workflow scope plan
- daily market data snapshot
- latest available trading date detection from local data
- daily data freshness/completeness audit relative to pinned `as_of_date`
- daily input freeze manifest with file hashes
- daily baseline signals
- daily order previews
- daily isolated execution previews
- daily report packets
- protected path residue scan
- daily workflow audit
- day1 blocker reclassification v061

## Pinned Fixture

The v0.6.1 release E2E uses `2024-12-31` as a historical daily workflow fixture. It is not current live market data.

## Boundary

- run-daily not called
- forward dry-run not started
- forward dry-run not validated
- main ledger not written
- no broker connected
- no real-time market data downloaded
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not strategy effectiveness proof
- not live trading readiness
- recommended next version is `v0.6.2-forward-dry-run-start-authorization-pack`

