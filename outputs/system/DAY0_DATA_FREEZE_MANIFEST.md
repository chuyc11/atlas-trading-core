# Day-0 Data Freeze Manifest

## Scope
This freezes day-0 research data inputs for a future 30 trading-day forward dry-run.
Day-0 readiness does not start forward dry-run.
Historical data authorization is not trading authorization.

## Frozen Packages
- HIST-ETF-OHLCV-CN-HK-V1: status=downloaded accepted_for_day0=true path=data/market/historical/authorized/HIST-ETF-OHLCV-CN-HK-V1.csv
- HIST-BENCHMARK-INDEX-CN-HK-V1: status=downloaded accepted_for_day0=true path=data/market/historical/authorized/HIST-BENCHMARK-INDEX-CN-HK-V1.csv
- HIST-FX-USDCNY-V1: status=downloaded accepted_for_day0=true path=data/global_briefing/authorized/packages/HIST-FX-USDCNY-V1.csv
- HIST-GLOBAL-RISK-VIX-V1: status=downloaded accepted_for_day0=true path=data/global_briefing/authorized/packages/HIST-GLOBAL-RISK-VIX-V1.csv
- HIST-RATES-LIQUIDITY-V1: status=downloaded accepted_for_day0=true path=data/global_briefing/authorized/packages/HIST-RATES-LIQUIDITY-V1.csv
- HIST-COMMODITY-INFLATION-RISK-V1: status=downloaded accepted_for_day0=true path=data/global_briefing/authorized/packages/HIST-COMMODITY-INFLATION-RISK-V1.csv
- HIST-POLICY-UNCERTAINTY-EPU-V1: status=partial_downloaded accepted_for_day0=true path=data/global_briefing/authorized/packages/HIST-POLICY-UNCERTAINTY-EPU-V1.csv
- HIST-OECD-CLI-MACRO-CYCLE-V1: status=downloaded accepted_for_day0=true path=data/global_briefing/authorized/packages/HIST-OECD-CLI-MACRO-CYCLE-V1.csv
- HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1: status=not_configured accepted_for_day0=true path=data/global_briefing/authorized/packages/HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1.raw

## Accepted Limitations
- HIST-POLICY-UNCERTAINTY-EPU-V1: missing us_epu/europe_epu
- HIST-POLICY-UNCERTAINTY-EPU-V1: policy uncertainty proxy only
- HIST-OECD-CLI-MACRO-CYCLE-V1: not official OECD CLI
- HIST-OECD-CLI-MACRO-CYCLE-V1: authorized macro-cycle proxy

## Explicit Non-Claims
- This does not validate forward dry-run.
- This does not prove strategy effectiveness.
- This is not live trading readiness.
- Historical data authorization is not trading authorization.

## Boundary
- data freeze only
- run-daily not called
- main ledger not written
- forward dry-run not started
