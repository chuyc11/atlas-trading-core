# A Share Owner Dashboard

- As of date: 2026-06-26
- Resolved as of date: 2026-06-26
- Overall status: passed_with_warnings
- Warning count: 65
- Blocking count: 0
- Scope: owner-facing research monitoring only; not order instruction; no broker connection; no real orders.

## 1. Executive Status
- Status: 通过但有提示 / passed_with_warnings
- Briefing: available
- Tracking: available
- Benchmark: available
- Performance: limited_history
- Attribution: structural_diagnostics_available

## 2. Data Freshness
- Data refresh audit passed: True
- Freshness status: None
- Coverage status: None
- Gap count: None

## 3. Provider Health
- Providers: 7 total, 2 enabled
- Enabled providers: local_file_provider, cached_panel_provider
- Disabled providers: eastmoney_public_provider, akshare_provider, qstock_provider, baostock_provider, tushare_provider
- Network providers disabled: True

## 4. Workflow Status
- Current-day audit passed: True
- Workflow audit passed: True
- Workflow mode: validate_existing_artifacts
- Old run-daily called: False
- Day2 executed: False

## 5. Research Outputs
- None: available (outputs/equity_briefings/daily/2026-06-26/DAILY_STOCK_SELECTION_BRIEFING.md)
- None: available (outputs/equity_portfolio_tracking/daily/2026-06-26/VIRTUAL_PORTFOLIO_TRACKING_SUMMARY.md)
- None: available (outputs/equity_benchmarks/daily/2026-06-26/A_SHARE_BENCHMARK_SUMMARY.md)
- None: available (outputs/equity_performance/daily/2026-06-26/A_SHARE_MULTI_DAY_PERFORMANCE_SUMMARY.md)
- None: available (outputs/equity_attribution/daily/2026-06-26/A_SHARE_ATTRIBUTION_SUMMARY.md)
- None: available (outputs/equity_current_day_runs/daily/2026-06-26/A_SHARE_CURRENT_DAY_RUN_SUMMARY.md)

## 6. Candidate Summary
- Long candidates: 30
- Mid candidates: 30
- Short candidates: 30
- Extended watch pool: 300
- Risk downgraded: 294
- Top long symbols: 688002.SH, 603259.SH, 688127.SH, 600999.SH, 603268.SH, 601066.SH, 600909.SH, 300308.SZ, 600160.SH, 601939.SH

## 7. Portfolio Summary
- Portfolio count: 3
- Performance observed: False
- Included risk-downgraded symbols: None

## 8. Benchmark Summary
- Status: available
- First-day initialization: True
- Available benchmarks: None

## 9. Performance Summary
- Status: limited_history
- Observation count: None / 20
- Sufficient history: False

## 10. Attribution Summary
- Status: structural_diagnostics_available
- Structural diagnostics available: True
- Realized attribution available: False

## 11. Warning And Blocker Summary
- Blocking count: 0
- Warning count: 65
- Warning: daily_basic:required_field_all_null
- Warning: fundamental score confidence is partial
- Warning: index benchmark data unavailable for CSI300/CSI500/CSI1000 placeholders
- Warning: long_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- Warning: market cap used daily_basic_panel fallback because historical daily_basic market cap is unavailable
- Warning: mid_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- Warning: raw industry_level_1 contains Unclassified; briefing disclosed fallback industry bucket usage
- Warning: short_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- Warning: trading_calendar:exchange_level_calendar_collapsed_to_trade_date
- Warning: daily_basic:required_field_all_null
- Warning: fundamental score confidence is partial
- Warning: index benchmark data unavailable for CSI300/CSI500/CSI1000 placeholders
- Warning: long_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- Warning: market cap used daily_basic_panel fallback because historical daily_basic market cap is unavailable
- Warning: mid_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- Warning: raw industry_level_1 contains Unclassified; briefing disclosed fallback industry bucket usage
- Warning: short_virtual_portfolio: raw industry_level_1 contains Unclassified; audit uses industry fallback buckets for caps
- Warning: trading_calendar:exchange_level_calendar_collapsed_to_trade_date
- Warning: daily_basic:required_field_all_null
- Warning: fundamental score confidence is partial

## 12. Artifact Navigation
- Artifact count: 10
- data_refresh_summary: data/equity_data_refresh/daily/2026-06-26/data_refresh_summary.json (exists=True)
- current_day_run_summary: outputs/equity_current_day_runs/daily/2026-06-26/A_SHARE_CURRENT_DAY_RUN_SUMMARY.md (exists=True)
- daily_briefing: outputs/equity_briefings/daily/2026-06-26/DAILY_STOCK_SELECTION_BRIEFING.md (exists=True)
- tracking_summary: outputs/equity_portfolio_tracking/daily/2026-06-26/VIRTUAL_PORTFOLIO_TRACKING_SUMMARY.md (exists=True)
- benchmark_summary: outputs/equity_benchmarks/daily/2026-06-26/A_SHARE_BENCHMARK_SUMMARY.md (exists=True)
- performance_summary: outputs/equity_performance/daily/2026-06-26/A_SHARE_MULTI_DAY_PERFORMANCE_SUMMARY.md (exists=True)
- attribution_summary: outputs/equity_attribution/daily/2026-06-26/A_SHARE_ATTRIBUTION_SUMMARY.md (exists=True)
- current_day_audit: data/equity_data_quality/a_share_current_day_research_run_audit.json (exists=True)
- data_refresh_audit: data/equity_data_quality/a_share_daily_data_refresh_audit.json (exists=True)
- workflow_audit: data/equity_data_quality/a_share_daily_workflow_audit.json (exists=True)

## 13. Source Trace And Boundary
- Source trace complete: True
- Boundary passed: True
- Forbidden artifacts: None
- Boundary statement: research-only, virtual-only, no order preview, no broker, no real account data, no live execution.
