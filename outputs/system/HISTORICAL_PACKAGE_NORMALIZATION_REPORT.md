# Historical Package Normalization Report

## Scope
Historical data authorization is not trading authorization.
This report normalizes historical research data and builds a proxy signal package.

## Packages
- HIST-ETF-OHLCV-CN-HK-V1: status=normalized path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\market\historical\authorized\HIST-ETF-OHLCV-CN-HK-V1.csv
- HIST-BENCHMARK-INDEX-CN-HK-V1: status=normalized path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\market\historical\authorized\HIST-BENCHMARK-INDEX-CN-HK-V1.csv
- HIST-FX-USDCNY-V1: status=normalized path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-FX-USDCNY-V1.csv
- HIST-GLOBAL-RISK-VIX-V1: status=normalized path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-GLOBAL-RISK-VIX-V1.csv
- HIST-RATES-LIQUIDITY-V1: status=normalized path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-RATES-LIQUIDITY-V1.csv
- HIST-COMMODITY-INFLATION-RISK-V1: status=normalized path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-COMMODITY-INFLATION-RISK-V1.csv
- HIST-POLICY-UNCERTAINTY-EPU-V1: status=normalized path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-POLICY-UNCERTAINTY-EPU-V1.csv
- HIST-OECD-CLI-MACRO-CYCLE-V1: status=normalized path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-OECD-CLI-MACRO-CYCLE-V1.csv
- HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1: status=not_configured path=None
- GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1: status=normalized path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\normalized\GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl

## Proxy Package
- package_path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.jsonl
- normalized_path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\normalized\GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl
- validated=true

## Boundary
- normalization only
- proxy package is not internal global-briefing signal
- no main ledger write
- no run-daily call
- not forward dry-run validation
