# Public Data Provider Strategy

v0.7.1 provider strategy is conservative: public and local providers may feed the local data foundation, but no provider response is allowed to become a score, candidate, portfolio, broker instruction, or real order.

## Priority

Provider priority:

```text
1. qstock-style public data adapter
2. AkShare
3. Tushare if package and token are available
4. BaoStock
5. local CSV/Parquet import
6. future iFinD / QuantAPI adapter slots
```

The selected provider and all failed providers are written to:

```text
data/equity_data_quality/a_share_data_source_manifest.json
outputs/equity_data_quality/A_SHARE_DATA_SOURCE_MANIFEST.md
```

## qstock-style Adapter

`qstock_reference_public_http` is a trading-core adapter. It can use qstock-style public data design ideas, but it must not import `external_research/qstock` or merge third-party code into the main flow.

The adapter records:

- provider name.
- rows available.
- provider reason.
- partial-fetch warnings.
- whether an external public data endpoint was called.

`external_api_called=true` means only public historical/delayed data download. It does not mean real-time market data, broker access, account access, order submission, or live trading readiness.

## Fallback Rules

If a provider is unavailable:

- record `source_unavailable` or provider-specific reason.
- try the next provider when implemented and configured.
- keep unavailable providers in `providers_failed`.
- write the source manifest even when only a partial provider succeeds.
- fail closed when equity master, trading calendar, or daily price coverage is insufficient for a data-foundation release.

If only partial secondary data is available:

- adjusted prices can fall back to raw prices with `adjustment_type=raw`.
- daily basic fields can be nullable.
- industry can use board-level fallback.
- financial numeric fields can be nullable placeholders.
- every fallback must be visible in coverage audit warnings.

## Future Provider Work

Future versions should improve provider depth without weakening safety:

- v0.7.2 can add tradable-universe filters on top of audited local artifacts.
- provider-specific calendars should replace weekday fallback when a reliable source is available.
- forward/backward adjusted data should replace raw adjusted fallback when coverage is sufficient.
- industry taxonomy and financials should prefer stable historical sources with point-in-time dates.
- scoring modules must not call provider APIs directly.

## Forbidden Uses

Provider adapters must not:

- connect a broker.
- access trading accounts.
- submit orders.
- write main order/trade/portfolio/account ledgers.
- execute official forward dry-run day2.
- call `run-daily`.
- generate recommendations, scores, candidates, or virtual portfolios.
- claim profit, live readiness, or investment advice.
