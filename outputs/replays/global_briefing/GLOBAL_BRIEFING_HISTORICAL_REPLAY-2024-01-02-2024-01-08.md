# Global Briefing Historical Replay

## Scope
This is isolated historical replay.
It is not forward dry-run.
It is not live trading validation.
It does not prove strategy effectiveness.

## Inputs
- bundle=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\replay_bundle-2024-01-02-2024-01-08.json
- prices=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\tests\fixtures\global_briefing_real\prices_valid.csv

## Replay Summary
- replay_days=5
- days_processed=5
- signals=14
- orders=3
- trades=3
- valuations=5
- ending_cash=865074.2725
- ending_equity=1000344.2725
- warnings=["2024-01-02: unknown signal fields ignored: ['comment']", '2024-01-02: missing price for 512880.SH; no order generated', "2024-01-03: unknown signal fields ignored: ['comment']", '2024-01-03: missing price for 512880.SH; no order generated', '2024-01-03: missing price for 588000.SH; no order generated', "2024-01-04: unknown signal fields ignored: ['comment']", '2024-01-04: target delta below lot size for 510300.SH', '2024-01-04: missing price for 512880.SH; no order generated', '2024-01-04: missing price for 588000.SH; no order generated', "2024-01-05: unknown signal fields ignored: ['comment']", '2024-01-05: missing price for 512880.SH; no order generated', '2024-01-05: missing price for 588000.SH; no order generated', "2024-01-08: unknown signal fields ignored: ['comment']", '2024-01-08: target delta below lot size for 510300.SH', '2024-01-08: missing price for 512880.SH; no order generated', '2024-01-08: missing price for 588000.SH; no order generated']

## Execution Mode
- isolated
- no_trade_fallback=false
- adapter=global_briefing_isolated_replay_adapter_v1

## Data Quality
- missing_price_days=[]
- missing_signal_days=[]

## Isolated Replay Ledger
- account path: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\accounts\account-GB-HIST-REPLAY-20240102-20240108.json
- signals path: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\signals\signals-GB-HIST-REPLAY-20240102-20240108.jsonl
- orders path: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\orders\orders-GB-HIST-REPLAY-20240102-20240108.jsonl
- trades path: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\trades\trades-GB-HIST-REPLAY-20240102-20240108.jsonl
- portfolio path: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\portfolio\portfolio-GB-HIST-REPLAY-20240102-20240108.jsonl
- valuations path: C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\replays\global_briefing\valuations\valuations-GB-HIST-REPLAY-20240102-20240108.jsonl

## Boundary
- isolated replay ledger only
- main ledger not written
- run-daily CLI not called
- not forward dry-run
- not live trading
- not strategy effectiveness proof
- no broker
- no labels
- no ML shadow
- no promotion
