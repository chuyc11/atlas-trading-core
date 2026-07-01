# A-Share Tradable Universe Report

- target_version: v0.7.2-a-share-tradable-universe-filter
- as_of_date: 2026-06-22
- strict_tradable_count: 0
- caution_count: 0
- excluded_count: 1647
- unknown_status_count: 4221
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
- avg_amount_20d_below_threshold: 1031
- insufficient_250d_history: 490
- insufficient_120d_history: 432
- possible_suspension: 426
- insufficient_60d_trading_observations: 413
- insufficient_60d_history: 398
- insufficient_20d_trading_observations: 382
- missing_price_on_as_of_date: 368
- close_price_missing: 368
- limit_status_unknown: 368
- insufficient_20d_history: 362
- inactive: 355
- amount_missing: 354
- st_stock: 333

strict_tradable_universe is the default input for future scoring. caution_universe is observation-only unless a future command explicitly allows it.
