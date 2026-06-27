# A-Share Scoring Interpretation

v0.7.4 scores are relative research scores for the strict tradable universe.

They are inputs for future candidate generation. They are not recommendations, not buy/sell signals, not portfolio weights, and not a profit guarantee.

## How To Read Scores

- Higher `RiskScore` means lower measured risk.
- Higher `LiquidityScore` means better liquidity and lower estimated trading friction.
- Higher `IndustryScore` means better industry-relative context.
- Higher `FundamentalScore` means better fundamental quality/valuation/growth mix, subject to confidence.
- Higher `LongScore`, `MidScore`, and `ShortScore` means stronger relative score for that horizon.
- Higher `CompositeOpportunityScore` means stronger blended score, not an instruction to act.

## Confidence

Confidence is a data coverage and component-coverage measure. It is not probability of profit.

Partial fundamental coverage is allowed, but the score confidence must fall rather than giving missing data a free high score.

## What Scores Do Not Mean

Scores do not mean:

- a buy recommendation
- a sell recommendation
- candidate stock
- watchlist membership
- portfolio allocation
- expected profit
- live-trading readiness

## Next Stages

- v0.7.5 will own candidate generation.
- v0.7.6 will own virtual portfolios.
- Later validation stages must test stability and outcomes before any stronger claims are allowed.
