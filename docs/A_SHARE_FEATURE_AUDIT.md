# A-Share Feature Audit

This document summarizes the v0.7.3 feature audit that gates v0.7.4 scoring.

## Command

```powershell
python -m trading_core.cli audit-a-share-multi-horizon-features --as-of-date 2026-06-26
```

## Release Result

For `as_of_date=2026-06-26`:

```text
strict_tradable_count = 3676
all feature group symbol coverage = 1.0
short mandatory field coverage = 1.0
mid mandatory field coverage = 1.0
long mandatory field coverage = 0.98669
risk mandatory field coverage = 1.0
liquidity mandatory field coverage = 1.0
industry mandatory field coverage = 1.0
fundamental mandatory field coverage = 0.708806
no_future_leakage = true
blocking_reasons = []
recommended_next_version = v0.7.4-a-share-long-mid-short-scoring-system
```

## Boundary

The feature audit does not approve candidate generation, watchlist generation, virtual portfolios, broker integration, real orders, `run-daily`, or official forward dry-run day2.

It only confirms that feature artifacts are complete enough and point-in-time safe enough for the v0.7.4 scoring stage.
