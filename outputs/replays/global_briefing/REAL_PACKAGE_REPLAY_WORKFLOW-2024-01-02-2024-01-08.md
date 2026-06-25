# Real Global Briefing Package Replay Workflow

## Scope
This workflow runs local historical global-briefing package replay in isolated mode.

## Steps
- normalize package
- validate normalized signals
- audit package coverage
- build replay bundle
- run isolated replay
- generate replay evaluation

## Outputs
- normalized_signals: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\normalized\GB-REAL-FIXTURE.normalized.jsonl
- validation: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\system\global_briefing_signal_validation.json
- coverage_audit: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\system\global_briefing_package_coverage_audit.json
- bundle: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\replay_bundle-2024-01-02-2024-01-08.json
- replay: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\global_briefing_replay-2024-01-02-2024-01-08.json
- evaluation: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\global_briefing_replay_evaluation-2024-01-02-2024-01-08.json

## Warnings
- row 1 signal comment kept as string
- row 2 signal comment kept as string
- row 3 signal comment kept as string
- row 4 signal comment kept as string
- duplicate as_of_date rows available for point-in-time selection: ['2024-01-05']
- missing signal dates: ['2024-01-04', '2024-01-06', '2024-01-07', '2024-01-08']
- duplicate signal days: ['2024-01-05']
- 2024-01-02: unknown signal fields ignored: ['comment']
- 2024-01-02: missing price for 512880.SH; no order generated
- 2024-01-03: unknown signal fields ignored: ['comment']
- 2024-01-03: missing price for 512880.SH; no order generated
- 2024-01-03: missing price for 588000.SH; no order generated
- 2024-01-04: unknown signal fields ignored: ['comment']
- 2024-01-04: target delta below lot size for 510300.SH
- 2024-01-04: missing price for 512880.SH; no order generated
- 2024-01-04: missing price for 588000.SH; no order generated
- 2024-01-05: unknown signal fields ignored: ['comment']
- 2024-01-05: missing price for 512880.SH; no order generated
- 2024-01-05: missing price for 588000.SH; no order generated
- 2024-01-08: unknown signal fields ignored: ['comment']
- 2024-01-08: target delta below lot size for 510300.SH
- 2024-01-08: missing price for 512880.SH; no order generated
- 2024-01-08: missing price for 588000.SH; no order generated
- 2024-01-02: unknown signal fields ignored: ['comment']
- 2024-01-02: missing price for 512880.SH; no order generated
- 2024-01-03: unknown signal fields ignored: ['comment']
- 2024-01-03: missing price for 512880.SH; no order generated
- 2024-01-03: missing price for 588000.SH; no order generated
- 2024-01-04: unknown signal fields ignored: ['comment']
- 2024-01-04: target delta below lot size for 510300.SH
- 2024-01-04: missing price for 512880.SH; no order generated
- 2024-01-04: missing price for 588000.SH; no order generated
- 2024-01-05: unknown signal fields ignored: ['comment']
- 2024-01-05: missing price for 512880.SH; no order generated
- 2024-01-05: missing price for 588000.SH; no order generated
- 2024-01-08: unknown signal fields ignored: ['comment']
- 2024-01-08: target delta below lot size for 510300.SH
- 2024-01-08: missing price for 512880.SH; no order generated
- 2024-01-08: missing price for 588000.SH; no order generated

## Boundary
- local package only
- no network access
- isolated replay only
- main ledger not written
- run-daily not called
- not forward dry-run validation
- not live trading readiness
- not strategy effectiveness proof
