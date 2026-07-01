# A-Share Tradable Universe Report

- target_version: v0.7.2-a-share-tradable-universe-filter
- as_of_date: 2026-06-24
- strict_tradable_count: 0
- caution_count: 0
- excluded_count: 1648
- unknown_status_count: 4220
- include_caution: false
- stock scores generated: false
- candidates generated: false
- watchlist generated: false
- virtual portfolios generated: false
- broker connected: false
- real orders placed: false
- live trading ready: false

## Thresholds
- min_listing_trading_days: 120
- min_effective_trading_days_20d: 17
- min_effective_trading_days_60d: 50
- min_avg_amount_20d: 50000000
- min_avg_amount_60d: 30000000
- min_total_mv: 3000000000
- min_circ_mv: 2000000000
- min_close_price: 2.0
- require_20d_history: True
- require_60d_history: True
- require_120d_history: True
- require_250d_history: True

## Top Exclusion Reasons
- market_cap_missing: 5868
- avg_amount_20d_below_threshold: 1041
- insufficient_250d_history: 489
- insufficient_120d_history: 431
- possible_suspension: 420
- insufficient_60d_trading_observations: 411
- insufficient_60d_history: 396
- insufficient_20d_trading_observations: 380
- insufficient_20d_history: 360
- missing_price_on_as_of_date: 359
- close_price_missing: 359
- limit_status_unknown: 359
- inactive: 355
- amount_missing: 353
- st_stock: 333

strict_tradable_universe is the default input for future scoring. caution_universe is observation-only unless a future command explicitly allows it.
