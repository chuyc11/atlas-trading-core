# Historical Data Download Manifest

## Scope
Historical data authorization is not trading authorization.
This workflow downloads or loads historical research packages only.

## Summary
- required_packages: 9
- downloaded: 7
- partial_downloaded: 1
- loaded_from_local: 0
- not_configured: 1
- failed: 0
- failed_soft: 0
- skipped_optional: 0
- normalized: 0
- audit_passed: 0
- audit_failed: 0

## Packages
- HIST-ETF-OHLCV-CN-HK-V1: status=downloaded source=yahoo_query_or_equivalent_authorized_market_data_source rows=14791 path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\market\historical\authorized\HIST-ETF-OHLCV-CN-HK-V1.csv
- HIST-BENCHMARK-INDEX-CN-HK-V1: status=downloaded source=yahoo_query_or_equivalent_authorized_market_data_source rows=7892 path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\market\historical\authorized\HIST-BENCHMARK-INDEX-CN-HK-V1.csv
- HIST-FX-USDCNY-V1: status=downloaded source=yahoo_query_or_equivalent_authorized_market_data_source rows=2207 path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-FX-USDCNY-V1.csv
- HIST-GLOBAL-RISK-VIX-V1: status=downloaded source=cboe_vix rows=2161 path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-GLOBAL-RISK-VIX-V1.csv
- HIST-RATES-LIQUIDITY-V1: status=downloaded source=yahoo_query_or_equivalent_authorized_market_data_source rows=6384 path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-RATES-LIQUIDITY-V1.csv
- HIST-COMMODITY-INFLATION-RISK-V1: status=downloaded source=yahoo_query_or_equivalent_authorized_market_data_source rows=8532 path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-COMMODITY-INFLATION-RISK-V1.csv
- HIST-POLICY-UNCERTAINTY-EPU-V1: status=partial_downloaded source=authorized_policy_uncertainty_proxy rows=4916 path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-POLICY-UNCERTAINTY-EPU-V1.csv
- HIST-OECD-CLI-MACRO-CYCLE-V1: status=downloaded source=authorized_macro_cycle_proxy rows=7674 path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-OECD-CLI-MACRO-CYCLE-V1.csv
- HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1: status=not_configured source=gb_authorized_api rows=0 path=C:\Users\26084\Documents\Codex\2026-06-12\new-chat\work\trading-core\data\global_briefing\authorized\packages\HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1.raw

## Boundary
- historical data download only
- no broker/account/order/trade/position/margin data
- no main ledger write
- no run-daily call
- no forward dry-run started
