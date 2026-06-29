# A 股 build_from_existing_data 重复性验证报告

## 1. Repeatability 总览

- 日期: 2026-06-26
- workflow mode: build_from_existing_data
- overall_passed: True
- blocking_reasons: []

## 2. 重复 build 执行结果

- command_executed: True
- exit_code: 0
- status: passed
- workflow_audit_overall_passed: True

## 3. Build-vs-Build 对比

- comparison_completed: True
- first_artifact_count: 298
- second_artifact_count: 298
- missing_required_artifact_count: 0

## 4. Drift 分类

- timestamp_only_drift_count: 41
- metadata_hash_drift_count: 23
- business_output_drift_count: 0
- drift_categories_found: ['metadata_hash_drift', 'timestamp_only_drift']

## 5. 受保护路径检查

- preexisting_protected_paths: ['data/orders', 'data/trades']
- protected_path_modifications_detected: False
- protected_files_modified: []
- protected_files_created: []
- protected_files_deleted: []

## 6. Warning 对比

- first_warning_count: 10
- second_warning_count: 10
- new_warnings: []

## 7. Source Trace 稳定性

- source_trace_complete: True
- forbidden_generated_sources: []

## 8. Boundary 稳定性

- old_run_daily_called: False
- broker_connected: False
- real_orders_placed: False
- order_preview_generated: False
- buy_sell_signals_generated: False

## 9. 下一步建议

- recommended_next_version: v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh

## 10. 免责声明

本报告只用于研究流程重复性验证和差异稳定性检查。
本阶段不是实盘，不连接券商，不读取真实账户，不下单，不生成订单预览，不把重复性验证解释为交易动作。
本报告不构成投资建议，不声称保证盈利，不声称 live trading ready。
