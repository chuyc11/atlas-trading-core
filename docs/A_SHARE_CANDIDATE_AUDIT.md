# A-Share Candidate Audit

`audit-a-share-candidates` validates v0.7.5 candidate generation artifacts.

```powershell
python -m trading_core.cli audit-a-share-candidates --as-of-date 2026-06-26
```

## Checks

The audit verifies:

- candidate config exists
- candidate manifest exists
- long, mid, and short candidate files exist
- extended watch pool exists
- multi-horizon candidates exist
- risk-downgraded candidates exist
- reason breakdown exists
- candidate reports exist
- input score manifest exists
- candidates are a subset of the strict tradable universe
- candidates exist in score tables
- candidate counts match config
- extended watch pool meets config
- manifest counts match files
- long candidates are sorted by `LongRank`
- mid candidates are sorted by `MidRank`
- short candidates are sorted by `ShortRank`
- candidate records contain explanations
- candidate records contain risk notes
- candidate records contain disclaimer flags
- no virtual portfolio artifacts were generated
- no buy/sell signal artifacts were generated
- no order preview was generated
- no buy/sell/order/position columns exist
- no profit-guarantee wording is present
- boundary flags are consistent across config, manifest, and summary

## Outputs

- `data/equity_data_quality/a_share_candidate_generation_audit.json`
- `outputs/audit/A_SHARE_CANDIDATE_GENERATION_AUDIT.md`

## Passing Release Evidence

For `as_of_date=2026-06-26`:

```text
overall_passed = true
blocking_reasons = []
warnings = []
strict_tradable_count = 3676
scored_symbols = 3676
long_candidates = 30
mid_candidates = 30
short_candidates = 30
extended_watch_pool = 300
multi_horizon_candidates = 50
risk_downgraded_candidates = 294
recommended_next_version = v0.7.6-a-share-virtual-portfolio-construction
```

## Boundary

Passing audit does not approve stock recommendations, virtual portfolios, order previews, broker access, real orders, profit claims, or live-trading readiness.

The audit must fail closed if virtual portfolio, buy/sell signal, order preview, broker, real-order, profit-guarantee, or live-readiness artifacts appear in the v0.7.5 candidate generation stage.
