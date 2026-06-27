# A-Share Candidate Generation System

`v0.7.5-a-share-candidate-generation-system` consumes the v0.7.4 strict-universe score artifacts and builds research candidate pools for long, mid, and short horizons.

The stage answers one question: which strict-tradable A-share symbols deserve further research review for each horizon?

It does not answer which stocks to buy, sell, allocate to a portfolio, or place orders for.

## Commands

```powershell
python -m trading_core.cli generate-a-share-candidates --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-candidates --as-of-date 2026-06-26
python -m trading_core.cli generate-and-audit-a-share-candidates --as-of-date 2026-06-26
```

The default `as_of_date` is `2026-06-26`. The generator requires an exact score directory by default. Use `--allow-latest-score-date` only for explicit historical catch-up runs.

Optional counts:

```powershell
python -m trading_core.cli generate-a-share-candidates --as-of-date 2026-06-26 --long-count 30 --mid-count 30 --short-count 30 --extended-count 100
```

## Selection Method

- Long candidates use `LongRank` / `LongPercentile` with risk, liquidity, and fundamental confidence gates.
- Mid candidates use `MidRank` / `MidPercentile` with risk, liquidity, and industry gates.
- Short candidates use `ShortRank` / `ShortPercentile` with liquidity, risk, and overheat gates.
- Multi-horizon candidates require two horizon percentiles at or above 85, or `CompositePercentile` at or above 95.
- Risk-downgraded candidates capture high-scoring names that fail risk, liquidity, or confidence gates.

All percentiles use the 0-100 convention. Fixed score thresholds such as `LongScore >= 75` are not used as the sole selection rule.

## Artifacts

Machine-readable artifacts:

- `data/equity_selection/daily/YYYY-MM-DD/candidate_generation_config.json`
- `data/equity_selection/daily/YYYY-MM-DD/long_candidates.json`
- `data/equity_selection/daily/YYYY-MM-DD/long_candidates.parquet`
- `data/equity_selection/daily/YYYY-MM-DD/mid_candidates.json`
- `data/equity_selection/daily/YYYY-MM-DD/mid_candidates.parquet`
- `data/equity_selection/daily/YYYY-MM-DD/short_candidates.json`
- `data/equity_selection/daily/YYYY-MM-DD/short_candidates.parquet`
- `data/equity_selection/daily/YYYY-MM-DD/extended_watch_pool.json`
- `data/equity_selection/daily/YYYY-MM-DD/extended_watch_pool.parquet`
- `data/equity_selection/daily/YYYY-MM-DD/multi_horizon_candidates.json`
- `data/equity_selection/daily/YYYY-MM-DD/risk_downgraded_candidates.json`
- `data/equity_selection/daily/YYYY-MM-DD/candidate_reason_breakdown.json`
- `data/equity_selection/daily/YYYY-MM-DD/candidate_generation_summary.json`
- `data/equity_selection/daily/YYYY-MM-DD/candidate_manifest.json`

Human-readable reports:

- `outputs/equity_selection/daily/YYYY-MM-DD/LONG_CANDIDATES.md`
- `outputs/equity_selection/daily/YYYY-MM-DD/MID_CANDIDATES.md`
- `outputs/equity_selection/daily/YYYY-MM-DD/SHORT_CANDIDATES.md`
- `outputs/equity_selection/daily/YYYY-MM-DD/MULTI_HORIZON_CANDIDATES.md`
- `outputs/equity_selection/daily/YYYY-MM-DD/RISK_DOWNGRADED_CANDIDATES.md`
- `outputs/equity_selection/daily/YYYY-MM-DD/CANDIDATE_GENERATION_SUMMARY.md`

Audit artifacts:

- `data/equity_data_quality/a_share_candidate_generation_audit.json`
- `outputs/audit/A_SHARE_CANDIDATE_GENERATION_AUDIT.md`

## Release Evidence

The release run for `as_of_date=2026-06-26` passed:

```text
strict_tradable_count = 3676
scored_symbols = 3676
long_candidates = 30
mid_candidates = 30
short_candidates = 30
extended_watch_pool = 300
multi_horizon_candidates = 50
risk_downgraded_candidates = 294
overall_passed = true
blocking_reasons = []
warnings = []
recommended_next_version = v0.7.6-a-share-virtual-portfolio-construction
```

## Boundary

v0.7.5 is a candidate generation stage.

Candidates are not investment advice. Candidates are not buy/sell signals. Candidates are not order instructions. Candidates are not virtual portfolios. Candidates are not profit guarantees.

These remain forbidden:

- virtual portfolio generation
- portfolio weights
- position sizing
- buy/sell signal generation
- order preview generation
- broker connection
- real orders
- `run-daily`
- official forward dry-run day2 execution
- live-trading readiness claims

Virtual portfolios are deferred to v0.7.6. Daily AI stock selection briefing is deferred to v0.7.7.
