# Global Briefing Historical Replay

## Scope
This is isolated historical replay.
It is not forward dry-run.
It is not live trading validation.
It does not prove strategy effectiveness.

## Inputs
- bundle=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\replay_bundle-2024-01-02-2024-01-08.json
- prices=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\tests\fixtures\global_briefing\prices_valid.csv

## Replay Summary
- replay_days=5
- days_processed=5
- orders=0
- trades=0
- ending_equity=1000000.0
- warnings=['core execution adapter not isolated; no-trade replay summary generated']

## Data Quality
- missing_price_days=[]
- missing_signal_days=[]

## Isolated Output Paths
- orders: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\orders\orders-GB-HIST-REPLAY-20240102-20240108.jsonl
- trades: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\trades\trades-GB-HIST-REPLAY-20240102-20240108.jsonl
- portfolio: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\portfolio\portfolio-GB-HIST-REPLAY-20240102-20240108.jsonl
- account: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\accounts\account-GB-HIST-REPLAY-20240102-20240108.json

## Boundary
- isolated replay only
- main ledger not written
- run-daily CLI not called
- no broker
- no live trading
- no labels
- no ML shadow
- no promotion
