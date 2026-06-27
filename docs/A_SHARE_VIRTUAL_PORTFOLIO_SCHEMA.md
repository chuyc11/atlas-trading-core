# A-Share Virtual Portfolio Schema

This document describes the v0.7.6 virtual portfolio artifacts.

## Conventions

- `target_weight` uses decimal convention and sums to approximately 1.0 per portfolio.
- all portfolios are long-only.
- no leverage, margin, options, futures, or derivatives are represented.
- input candidates come from v0.7.5 candidate pools and multi-horizon candidates.
- risk-downgraded candidates are excluded from main virtual portfolios.

## Portfolio Records

Each portfolio record includes:

- `as_of_date`
- `portfolio_id`
- `portfolio_horizon`
- `symbol`
- `name`
- `exchange`
- `board`
- `industry_level_1`
- `industry_level_2`
- `industry`
- `target_weight`
- `weight_rank`
- `candidate_source`
- `candidate_rank`
- `LongScore`
- `MidScore`
- `ShortScore`
- `RiskScore`
- `LiquidityScore`
- `IndustryScore`
- `FundamentalScore`
- `CompositeOpportunityScore`
- `weight_reason`
- `risk_notes`
- `confidence_notes`
- `source_candidate_manifest`
- `source_score_manifest`
- `created_at`

Required disclaimer fields:

- `virtual_only=true`
- `research_only=true`
- `not_investment_advice=true`
- `not_buy_signal=true`
- `not_sell_signal=true`
- `not_order_instruction=true`
- `not_profit_guarantee=true`
- `not_live_trading_ready=true`

Short portfolio records also include:

- `overheat_risk_notes`
- `liquidity_risk_notes`
- `short_horizon_validity_notes`

## Manifest

`portfolio_manifest.json` records:

- target version
- input candidate manifest path
- input score manifest path
- portfolio holdings
- weight sums
- max single-stock weights
- max industry weights
- `virtual_portfolio_generated=true`
- `real_portfolio_generated=false`
- `buy_sell_signals_generated=false`
- `order_preview_generated=false`
- `broker_connected=false`
- `real_orders_placed=false`
- `model_profit_guaranteed=false`

## Forbidden Fields

Virtual portfolio schemas must not include:

- `buy_signal`
- `sell_signal`
- `order_preview`
- `broker_order`
- `real_order`
- `trade_instruction`
- `order_instruction`
- `rebalance_instruction`

## Boundary

Virtual portfolio schemas describe research target weights only. They are not real portfolios, not buy/sell signals, not broker order previews, not real orders, and not profit guarantees.
