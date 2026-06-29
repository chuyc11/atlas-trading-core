# A股 Safe Action Checklist

- [ ] 检查 audit 是否通过 (verify_audit)
- [ ] 检查 warning 是否为已知非阻塞 (document_known_warning)
- [ ] 检查 source trace 是否完整 (inspect_artifact)
- [ ] 检查 boundary 是否干净 (verify_audit)
- [ ] 检查是否需要安全重跑数据验证 (rerun_safe_data_validation) command=`python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date 2026-06-26 --mode validate_existing_data`
- [ ] 检查是否需要安全重跑 current-day validation (rerun_safe_current_day_research_validation) command=`python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts`
- [ ] 检查是否需要安全重跑 dashboard / monitoring (rerun_safe_dashboard_build) command=`python -m trading_core.cli build-and-audit-a-share-owner-dashboard --as-of-date 2026-06-26 --mode build_dashboard_from_existing_run`
- [ ] 检查是否需要等待更多历史数据 (wait_for_more_history)

- 所有 item 默认 allowed_to_execute_automatically=false。
- checklist 是非交易动作，不是买卖建议。
