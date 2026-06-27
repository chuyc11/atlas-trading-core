# A-Share Long Mid Short Scoring System

`v0.7.4-a-share-long-mid-short-scoring-system` builds score artifacts for the strict A-share tradable universe.

The stage answers one question: what are the relative long, mid, and short horizon scores for each strict tradable symbol?

It does not answer which stocks to buy, sell, recommend, place in a watchlist, or allocate to a portfolio.

## Commands

```powershell
python -m trading_core.cli build-a-share-scores --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-scores --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-scores --as-of-date 2026-06-26
```

The default `as_of_date` is `2026-06-26`. The builder requires an exact feature directory by default. Use `--allow-latest-feature-date` only for explicit historical catch-up runs.

## Score Components

- `RiskScore`: higher means lower measured risk.
- `LiquidityScore`: higher means better tradability and lower friction.
- `IndustryScore`: higher means stronger industry-relative context.
- `FundamentalScore`: higher means better quality, growth, valuation, balance-sheet, and freshness mix, with confidence reduced for partial data.
- `LongScore`: 6-24 month relative opportunity score.
- `MidScore`: 1-6 month relative opportunity score.
- `ShortScore`: 5-20 trading-day relative opportunity score.
- `CompositeOpportunityScore`: blended ranking aid consumed by the v0.7.5 candidate generator.

All scores use a 0-100 convention. Percentiles use 0-100. Confidence values use 0-1.

## Artifacts

Machine-readable artifacts:

- `data/equity_scores/daily/YYYY-MM-DD/score_config.json`
- `data/equity_scores/daily/YYYY-MM-DD/risk_liquidity_industry_fundamental_scores.parquet`
- `data/equity_scores/daily/YYYY-MM-DD/horizon_scores.parquet`
- `data/equity_scores/daily/YYYY-MM-DD/composite_scores.parquet`
- `data/equity_scores/daily/YYYY-MM-DD/score_component_breakdown.parquet`
- `data/equity_scores/daily/YYYY-MM-DD/score_distribution.json`
- `data/equity_scores/daily/YYYY-MM-DD/score_manifest.json`
- `data/equity_scores/daily/YYYY-MM-DD/scoring_summary.json`

Human-readable reports:

- `outputs/equity_scores/daily/YYYY-MM-DD/SCORE_DISTRIBUTION_REPORT.md`
- `outputs/equity_scores/daily/YYYY-MM-DD/SCORING_SUMMARY.md`
- `outputs/audit/A_SHARE_SCORING_AUDIT.md`

Audit JSON:

- `data/equity_data_quality/a_share_scoring_audit.json`

## Release Evidence

The release run for `as_of_date=2026-06-26` passed:

```text
strict_tradable_count = 3676
scored_symbols = 3676
long_score_symbols = 3676
mid_score_symbols = 3676
short_score_symbols = 3676
composite_score_symbols = 3676
overall_passed = true
blocking_reasons = []
recommended_next_version = v0.7.5-a-share-candidate-generation-system
```

The audit records one warning: fundamental score confidence is partial.

## Boundary

v0.7.4 is a scoring stage.

Scores are not recommendations. Scores are not buy/sell signals. Scores are not profit guarantees. Scores are inputs consumed by the v0.7.5 candidate-generation system.

These remain forbidden:

- candidate generation
- watchlist generation
- virtual portfolio generation
- buy/sell signal generation
- broker connection
- real orders
- `run-daily`
- official forward dry-run day2 execution
- live-trading readiness claims

Candidate generation is handled by v0.7.5. Virtual portfolios are deferred to v0.7.6.
