# A-Share Portfolio Interpretation

v0.7.6 virtual portfolios are research-only target-weight portfolios for the strict tradable A-share universe.

They are generated from v0.7.5 candidate pools. They are inputs for future virtual tracking and daily owner briefing. They are not real portfolios, not investment advice, not buy/sell signals, not order previews, not broker instructions, and not profit guarantees.

## How To Read Virtual Portfolios

- Long virtual portfolio is a 6-24 month research tracking portfolio.
- Mid virtual portfolio is a 1-6 month research tracking portfolio.
- Short virtual portfolio is a 5-20 trading-day research tracking portfolio.
- `target_weight` is a virtual research target, not a real account instruction.
- `weight_reason` explains deterministic construction logic.
- `risk_notes` and liquidity summaries identify review points.
- industry exposure reports show concentration under the configured cap logic.

## What Target Weights Do Not Mean

Target weights do not mean:

- buy recommendation
- sell recommendation
- broker order preview
- real-account rebalance instruction
- required position size
- expected profit
- live-trading readiness

## Next Stage

v0.7.7 owns daily AI stock selection briefing from existing candidate, score, and virtual portfolio artifacts.

Later validation stages must evaluate virtual tracking behavior before any stronger claim is allowed.
