# A 股 Build Output Owner Dashboard

## 1. 今日 Build Output 总览

- 日期: 2026-06-26
- source_workflow_mode: build_from_existing_data
- overall_status: passed
- build_output_available: True

## 2. 数据刷新状态

- data_refresh_audit_passed: True

## 3. Build-from-existing-data Workflow 状态

- repeat_build_status: passed
- repeat_build_audit_passed: True

## 4. Repeatability 状态

- repeatability_audit_passed: True
- business_output_drift_count: 0
- timestamp_only_drift_count: 41
- metadata_hash_drift_count: 23

## 5. Protected Path 状态

- preexisting_protected_paths: ['data/orders', 'data/trades']
- protected_path_modifications_detected: False

## 6. 研究产物导航

- repeatability_summary: data/equity_build_repeatability/daily/2026-06-26/repeatability_summary.json exists=True
- repeatability_audit: data/equity_data_quality/a_share_build_repeatability_audit.json exists=True
- gated_build_summary: data/equity_current_day_builds/daily/2026-06-26/gated_build_summary.json exists=True
- build_artifact_index: data/equity_current_day_builds/daily/2026-06-26/build_artifact_index.json exists=True
- current_day_summary: data/equity_current_day_runs/daily/2026-06-26/current_day_summary.json exists=True
- candidate_summary: data/equity_selection/daily/2026-06-26/candidate_generation_summary.json exists=True
- portfolio_manifest: data/equity_portfolios/daily/2026-06-26/portfolio_manifest.json exists=True
- briefing: data/equity_briefings/daily/2026-06-26/daily_stock_selection_briefing.json exists=True
- tracking_summary: data/equity_portfolio_tracking/daily/2026-06-26/tracking_summary.json exists=True
- build_output_dashboard_report: outputs/equity_build_output_dashboard/daily/2026-06-26/A_SHARE_BUILD_OUTPUT_OWNER_DASHBOARD.md exists=True

## 7. 候选 / 虚拟组合 / Benchmark / Performance / Attribution 摘要

- candidate_available: True
- portfolio_available: True
- benchmark_available: True
- performance_available: True
- attribution_available: True

## 8. Warning / Blocking

- blocking_count: 0
- warning_count: 2
- blocking_reasons: []

## 9. Validate Dashboard vs Build Dashboard 对比

- comparison_completed: True
- expected_source_mode_difference: {'validate_dashboard_source_workflow_mode': 'validate_existing_artifacts', 'build_dashboard_source_workflow_mode': 'build_from_existing_data', 'expected_different': True}

## 10. 安全边界

- research-only / virtual-only
- no broker connection
- no real account read
- no real orders
- no order preview
- no public network refresh
- no full_research_run
- no old run-daily
- dashboard output is not a trade instruction

## 11. 下一步建议

- recommended_next_version: v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh

## 12. 免责声明

本 dashboard 只用于研究流程可视化和边界检查，不构成投资建议，不授权任何交易动作，不承诺收益，也不代表 live trading ready。
