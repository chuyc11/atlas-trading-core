# A-share Filter Reason Taxonomy

This taxonomy is the machine-readable reason vocabulary for `v0.7.2-a-share-tradable-universe-filter`.

## Universe Eligibility

- `not_in_master`
- `unsupported_exchange`
- `inactive`
- `delisted`
- `not_yet_listed`
- `missing_list_date`

## ST And Risk Warning

- `st_stock`
- `risk_warning_stock`
- `delisting_board`
- `name_contains_st`
- `st_status_unknown`

`st_status_unknown` may enter `caution_universe`, but not `strict_tradable_universe`.

## Listing Age

- `new_listing_lt_120_trading_days`
- `listing_age_unknown`

Listing age is measured using the trading calendar, not natural days.

## Suspension And Missing Price

- `missing_price_on_as_of_date`
- `insufficient_20d_trading_observations`
- `insufficient_60d_trading_observations`
- `possible_suspension`

## Liquidity

- `avg_amount_20d_below_threshold`
- `avg_amount_60d_below_threshold`
- `amount_missing`
- `liquidity_unknown`

When `amount` is missing but `volume * close` is usable, the symbol records `estimated_amount=true`.

## Market Cap

- `total_mv_below_threshold`
- `circ_mv_below_threshold`
- `market_cap_missing`
- `market_cap_unit_unknown`

Provider units must be normalized to CNY when known. The v0.7.2 run uses `daily_basic_panel` as an as-of market-cap fallback because historical daily basic market-cap fields are unavailable.

## Price

- `close_price_below_threshold`
- `close_price_missing`

## Price Sanity

- `invalid_price_record`
- `invalid_high_low`
- `invalid_volume`
- `invalid_amount`

## Limit Status

- `one_word_limit_up_risk`
- `one_word_limit_down_risk`
- `limit_status_unknown`

One-word limit up/down risks are excluded from `strict_tradable_universe`. `limit_status_unknown` may enter caution, but not strict.

## Data Coverage

- `insufficient_20d_history`
- `insufficient_60d_history`
- `insufficient_120d_history`
- `insufficient_250d_history`

## Bucket Rules

- Any hard exclusion reason sends the symbol to `excluded_universe`.
- Missing critical data sends the symbol to `unknown_status_universe` unless a hard exclusion also applies.
- Non-fatal uncertainty sends the symbol to `caution_universe`.
- Only symbols with no filter reasons enter `strict_tradable_universe`.

The strict bucket is the default input for future feature engineering and scoring. The caution bucket is observation-only unless explicitly allowed by a future command.

