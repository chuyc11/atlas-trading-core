# A-Share Scoring Audit

`audit-a-share-scores` validates v0.7.4 scoring artifacts.

```powershell
python -m trading_core.cli audit-a-share-scores --as-of-date 2026-06-26
```

## Checks

The audit verifies:

- score config exists
- score manifest exists
- all score files exist
- input feature manifest exists
- scored symbols are a subset of strict tradable universe
- excluded symbols are absent
- scored symbol count equals strict tradable count
- score ranges are within 0-100
- rank columns are complete and unique
- percentile columns are within 0-100
- confidence columns are within 0-1
- component breakdown exists for all score names
- no candidate artifacts were generated
- no watchlist artifacts were generated
- no virtual portfolio artifacts were generated
- no buy/sell signal columns exist
- no profit or live-trading wording is present
- scoring boundary flags are consistent across config, manifest, and summary
- no future leakage is inherited from the feature manifest

## Outputs

- `data/equity_data_quality/a_share_scoring_audit.json`
- `outputs/audit/A_SHARE_SCORING_AUDIT.md`

## Passing Release Evidence

For `as_of_date=2026-06-26`:

```text
overall_passed = true
blocking_reasons = []
strict_tradable_count = 3676
scored_symbols = 3676
candidate_artifacts_present = []
watchlist_artifacts_present = []
virtual_portfolio_artifacts_present = []
recommended_next_version = v0.7.5-a-share-candidate-generation-system
```

## Boundary

Passing audit does not mean stock recommendations are approved. It only means score artifacts are complete and boundary-safe for downstream v0.7.5 candidate generation.

The audit must fail closed if candidate, watchlist, virtual portfolio, buy/sell signal, broker, real-order, profit-guarantee, or live-readiness artifacts appear in the v0.7.4 scoring stage.
