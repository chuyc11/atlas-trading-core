# A-Share Benchmark Comparison

`v0.7.10-a-share-benchmark-data-and-performance-comparison` adds benchmark data and portfolio-relative comparison for the A-share research system.

## Scope

The stage reads v0.7.9 workflow artifacts, v0.7.8 tracking artifacts, v0.7.2-v0.7.6 selection/candidate/portfolio artifacts, local price panels, and index benchmark history.

It writes:

- `data/equity_benchmarks/daily/YYYY-MM-DD/`
- `outputs/equity_benchmarks/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_benchmark_comparison_audit.json`
- `outputs/audit/A_SHARE_BENCHMARK_COMPARISON_AUDIT.md`

## Commands

```powershell
python -m trading_core.cli build-a-share-benchmark-comparison --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-benchmark-comparison --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-benchmark-comparison --as-of-date 2026-06-26
```

## Benchmarks

- `CSI300`
- `CSI500`
- `CSI1000`
- `CASH`
- `EQUAL_WEIGHT_STRICT_TRADABLE`
- `EQUAL_WEIGHT_CANDIDATE_POOL`

Index benchmarks must be available by default. Placeholder index benchmarks are allowed only for explicit non-release local runs.

## Boundary

This stage does not create buy/sell signals, does not generate order previews, does not connect a broker, does not place orders, does not call old `run-daily`, and does not execute official forward dry-run day2.

## v0.7.11 Next Stage

v0.7.11 consumes the benchmark NAV/return artifacts and the v0.7.8 virtual tracking artifacts to build portfolio NAV, return, drawdown, benchmark-relative, and holding mark-to-market series. It does not use benchmark history to fabricate portfolio history. Limited portfolio observations remain explicitly flagged until enough virtual tracking days exist.
