# A-Share Benchmark Audit

`audit-a-share-benchmark-comparison` validates the v0.7.10 benchmark package.

## Checks

- all required benchmark artifacts exist
- all benchmark ids are present
- CSI300, CSI500, and CSI1000 are available unless placeholders were explicitly allowed
- CASH, strict-tradable equal-weight, and candidate-pool equal-weight are available
- no future dates are used
- source trace has no forbidden source paths
- first-day limited history is correctly flagged
- portfolio performance is not fabricated
- boundary fields remain clean
- forbidden artifacts and positive wording are absent

## Output

- `data/equity_data_quality/a_share_benchmark_comparison_audit.json`
- `outputs/audit/A_SHARE_BENCHMARK_COMPARISON_AUDIT.md`

Passing this audit confirms benchmark comparison artifact integrity only. It is not investment advice, not live readiness, and not a trading authorization.
