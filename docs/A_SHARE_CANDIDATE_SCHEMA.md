# A-Share Candidate Schema

This document describes the v0.7.5 candidate generation artifacts.

## Conventions

- score columns: 0 to 100
- percentile columns: 0 to 100
- confidence columns: 0 to 1
- ranks: 1 is highest score
- input universe: `strict_tradable_universe` only
- input scores: v0.7.4 `horizon_scores.parquet`, `composite_scores.parquet`, and `risk_liquidity_industry_fundamental_scores.parquet`

## Candidate Records

`long_candidates`, `mid_candidates`, `short_candidates`, and `extended_watch_pool` records include:

- `as_of_date`
- `symbol`
- `name`
- `exchange`
- `board`
- `industry_level_1`
- `industry_level_2`
- `candidate_horizon`
- `candidate_rank`
- `candidate_percentile`
- `LongScore`
- `MidScore`
- `ShortScore`
- `RiskScore`
- `LiquidityScore`
- `IndustryScore`
- `FundamentalScore`
- `CompositeOpportunityScore`
- `LongRank`
- `MidRank`
- `ShortRank`
- `CompositeRank`
- `LongConfidence`
- `MidConfidence`
- `ShortConfidence`
- `CompositeConfidence`
- `primary_inclusion_reasons`
- `main_risk_reasons`
- `component_highlights`
- `confidence_notes`
- `source_score_manifest`
- `created_at`

Required disclaimer fields:

- `candidate_not_investment_advice=true`
- `not_buy_signal=true`
- `not_sell_signal=true`
- `not_order_instruction=true`
- `not_profit_guarantee=true`

## Reason Taxonomy

Allowed reason identifiers include:

- `high_long_percentile`
- `high_mid_percentile`
- `high_short_percentile`
- `strong_composite_percentile`
- `strong_industry_score`
- `strong_liquidity_score`
- `acceptable_risk_score`
- `strong_fundamental_score`
- `strong_trend_component`
- `strong_momentum_component`
- `strong_risk_adjusted_return`
- `multi_horizon_overlap`
- `risk_downgraded`
- `low_risk_score`
- `low_liquidity_score`
- `low_confidence`
- `fundamental_coverage_low`
- `overheat_risk`

Each strict candidate must have at least two primary inclusion reasons and at least one risk reason or `no_major_risk_flag_detected`.

## Manifest

`candidate_manifest.json` records:

- target version
- input score manifest path
- strict tradable count
- scored symbol count
- candidate counts
- `candidate_generation_only=true`
- `scores_generated_upstream=true`
- `virtual_portfolio_generated=false`
- `buy_sell_signals_generated=false`
- `order_instructions_generated=false`
- `broker_connected=false`
- `real_orders_placed=false`
- `model_profit_guaranteed=false`

## Forbidden Fields

Candidate schemas must not include:

- `buy_signal`
- `sell_signal`
- `order_preview`
- `portfolio_weight`
- `position_size`
- `rebalance_action`
- `trade_instruction`
- `order_instruction`

## Boundary

Candidate schemas describe research selection artifacts consumed by v0.7.6 virtual portfolio construction. They are not investment advice, not buy/sell signals, not real portfolio allocations, not order instructions, and not profit guarantees.
