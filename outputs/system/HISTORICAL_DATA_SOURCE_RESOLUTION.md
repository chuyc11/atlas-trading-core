# Historical Data Source Resolution

## Scope
Historical data authorization is not trading authorization.
This resolver does not connect to a broker and does not authorize trading.

## Packages
- HIST-ETF-OHLCV-CN-HK-V1: source=yahoo_query_or_equivalent_authorized_market_data_source type=public_api status=configured allowed=true
- HIST-BENCHMARK-INDEX-CN-HK-V1: source=yahoo_query_or_equivalent_authorized_market_data_source type=public_api status=configured allowed=true
- HIST-FX-USDCNY-V1: source=fred type=public_api status=configured allowed=true
- HIST-GLOBAL-RISK-VIX-V1: source=fred type=public_api status=configured allowed=true
- HIST-RATES-LIQUIDITY-V1: source=fred type=public_api status=configured allowed=true
- HIST-COMMODITY-INFLATION-RISK-V1: source=fred type=public_api status=configured allowed=true
- HIST-POLICY-UNCERTAINTY-EPU-V1: source=fred type=public_api status=configured allowed=true
- HIST-OECD-CLI-MACRO-CYCLE-V1: source=authorized_macro_cycle_proxy type=derived_authorized_proxy status=configured allowed=true
- HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1: source=gb_authorized_api type=authorized_api status=not_configured allowed=true

## Boundary
- source resolution only
- no historical download started
- no broker/account/order/trade data
- no main ledger write
- no run-daily call
