# A-Share Score Schema

This document describes the v0.7.4 score artifacts.

## Conventions

- score columns: 0 to 100
- percentile columns: 0 to 100
- confidence columns: 0 to 1
- ranks: 1 is highest score
- input universe: `strict_tradable_universe` only

## `score_config.json`

Required fields:

- `score_version`
- `as_of_date`
- `normalization_method`
- `winsorization_limits`
- `missing_value_policy`
- `feature_directions`
- `component_weights`
- `horizon_weights`
- `risk_penalty_policy`
- `liquidity_penalty_policy`
- `fundamental_confidence_policy`
- `created_at`
- `boundary`

## `risk_liquidity_industry_fundamental_scores.parquet`

Contains:

- common symbol metadata
- `RiskScore`, `risk_percentile`, `risk_confidence`
- `LiquidityScore`, `liquidity_percentile`, `liquidity_confidence`
- `IndustryScore`, `industry_percentile`, `industry_confidence`
- `FundamentalScore`, `fundamental_percentile`, `fundamental_confidence`
- component breakdown JSON strings for each component group
- `source`
- `created_at`

## `horizon_scores.parquet`

Required columns:

- `as_of_date`
- `symbol`
- `name`
- `exchange`
- `board`
- `industry_level_1`
- `industry_level_2`
- `LongScore`
- `LongRank`
- `LongPercentile`
- `LongConfidence`
- `MidScore`
- `MidRank`
- `MidPercentile`
- `MidConfidence`
- `ShortScore`
- `ShortRank`
- `ShortPercentile`
- `ShortConfidence`
- `source`
- `created_at`

## `composite_scores.parquet`

Required columns:

- `as_of_date`
- `symbol`
- `CompositeOpportunityScore`
- `CompositeRank`
- `CompositePercentile`
- `CompositeConfidence`
- `LongScore`
- `MidScore`
- `ShortScore`
- `RiskScore`
- `LiquidityScore`
- `IndustryScore`
- `FundamentalScore`
- `source`
- `created_at`

## `score_component_breakdown.parquet`

Required columns:

- `as_of_date`
- `symbol`
- `score_name`
- `component_name`
- `component_value`
- `component_weight`
- `component_contribution`
- `component_confidence`
- `source`
- `created_at`

The sum of `component_contribution` for a symbol and score should approximately equal the score value.

## Boundary

Score schemas do not include buy/sell signal columns. They do not include candidate, watchlist, position, order, trade, or broker fields.
