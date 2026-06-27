# A-Share Tradable Universe Report

- target_version: v0.7.2-a-share-tradable-universe-filter
- as_of_date: 2026-06-26
- strict_tradable_count: 3676
- caution_count: 0
- excluded_count: 2191
- unknown_status_count: 0
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
- min_effective_trading_days_20d: 18
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
- total_mv_below_threshold: 1231
- avg_amount_20d_below_threshold: 1052
- circ_mv_below_threshold: 870
- insufficient_250d_history: 488
- insufficient_120d_history: 426
- possible_suspension: 417
- insufficient_60d_trading_observations: 408
- insufficient_60d_history: 393
- insufficient_20d_trading_observations: 379
- insufficient_20d_history: 358
- missing_price_on_as_of_date: 354
- close_price_missing: 354
- limit_status_unknown: 354
- inactive: 351
- amount_missing: 351

strict_tradable_universe is the default input for future scoring. caution_universe is observation-only unless a future command explicitly allows it.
