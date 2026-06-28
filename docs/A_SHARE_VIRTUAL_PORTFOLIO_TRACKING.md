# A-Share Virtual Portfolio Tracking

`v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger` adds research-only tracking for the v0.7.6 long/mid/short virtual portfolios.

## Scope

The stage reads existing artifacts only:

- v0.7.6 virtual portfolio construction artifacts
- v0.7.7 daily stock selection briefing artifacts
- v0.7.4 score snapshots
- historical daily and adjusted price panels
- trading calendar

It writes virtual tracking artifacts under:

- `data/equity_portfolio_tracking/daily/YYYY-MM-DD/`
- `outputs/equity_portfolio_tracking/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_virtual_portfolio_tracking_audit.json`
- `outputs/audit/A_SHARE_VIRTUAL_PORTFOLIO_TRACKING_AUDIT.md`

## Commands

```powershell
python -m trading_core.cli build-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26
```

## Outputs

- `tracking_config.json`
- `long_paper_ledger.json`
- `mid_paper_ledger.json`
- `short_paper_ledger.json`
- `long_holdings_snapshot.json`
- `mid_holdings_snapshot.json`
- `short_holdings_snapshot.json`
- `portfolio_nav_snapshot.json`
- `portfolio_performance_snapshot.json`
- `portfolio_drawdown_snapshot.json`
- `portfolio_exposure_snapshot.json`
- `benchmark_comparison_snapshot.json`
- `tracking_manifest.json`
- `tracking_source_trace.json`
- `tracking_summary.json`
- Markdown tracking reports

## Boundary

- Paper ledger is virtual-only and research-only.
- Paper ledger is not a real-money ledger.
- Virtual holdings are not real holdings.
- Virtual returns are not actual returns.
- Virtual portfolio tracking does not connect a broker.
- Virtual portfolio tracking does not place real orders.
- Virtual portfolio tracking does not generate buy/sell signals.
- Virtual portfolio tracking does not generate order previews.
- v0.7.9 implements daily workflow orchestration around this tracking package.
- v0.7.10 is reserved for benchmark data and relative performance comparison.
