# Full Historical Proxy Workflow

## Scope
Proxy signals are not internal global-briefing signals.
Historical data authorization is not trading authorization.
This workflow is historical replay only.

## Overall Status
- overall_status=research_review_ready
- blocking_reasons=[]

## Outputs
- windowed_signals: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\full_historical_proxy_signals-2024-01-02-2024-12-31.jsonl
- validation: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\system\global_briefing_signal_validation.json
- coverage_audit: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\system\global_briefing_package_coverage_audit.json
- bundle: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\replay_bundle-2024-01-02-2024-12-31.json
- replay: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\global_briefing_replay-2024-01-02-2024-12-31.json
- evaluation: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\global_briefing_replay_evaluation-2024-01-02-2024-12-31.json

## Boundary
- historical replay only
- proxy signals are not internal global-briefing signals
- not forward dry-run validation
- not strategy effectiveness proof
- not live trading readiness
- main ledger not written
- run-daily not called
