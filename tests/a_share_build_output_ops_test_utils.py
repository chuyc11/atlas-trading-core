from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths, seed_build_output_dashboard_outputs
from tests.a_share_owner_dashboard_test_utils import write_json, write_text


def seed_build_output_ops_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_build_output_dashboard_outputs(paths, as_of_date)
    from trading_core.equity_build_output_dashboard.build_output_dashboard_audit import audit_a_share_build_output_owner_dashboard

    audit_a_share_build_output_owner_dashboard(as_of_date=as_of_date, paths=paths)
    mon = paths.data_dir / "equity_owner_monitoring" / "daily" / as_of_date
    write_json(mon / "monitoring_status_card.json", {"target_version": "v0.8.3-a-share-owner-alerting-and-run-history-monitoring", "as_of_date": as_of_date, "overall_monitoring_status": "passed_with_warnings", "critical_alert_count": 0, "warning_alert_count": 0, "known_non_blocking_alert_count": 0, "blocking_count": 0, "warning_count": 1, "external_notifications_sent": False})
    write_json(mon / "owner_alert_summary_card.json", {"target_version": "v0.8.3-a-share-owner-alerting-and-run-history-monitoring", "as_of_date": as_of_date, "critical_alerts": [], "warning_alerts": [], "known_non_blocking_alerts": [], "informational_alerts": []})
    write_json(mon / "alert_evaluation_result.json", {"target_version": "v0.8.3-a-share-owner-alerting-and-run-history-monitoring", "as_of_date": as_of_date, "overall_passed": True})
    write_json(mon / "alert_event_log.json", {"target_version": "v0.8.3-a-share-owner-alerting-and-run-history-monitoring", "as_of_date": as_of_date, "events": []})
    write_json(mon / "monitoring_boundary_check.json", {"target_version": "v0.8.3-a-share-owner-alerting-and-run-history-monitoring", "as_of_date": as_of_date, "overall_passed": True, "external_notifications_sent": False, "broker_connected": False, "real_orders_placed": False})
    write_json(mon / "monitoring_manifest.json", {"target_version": "v0.8.3-a-share-owner-alerting-and-run-history-monitoring", "as_of_date": as_of_date, "overall_passed": True})
    write_json(paths.data_dir / "equity_data_quality" / "a_share_owner_monitoring_audit.json", {"target_version": "v0.8.3-a-share-owner-alerting-and-run-history-monitoring", "as_of_date": as_of_date, "overall_passed": True, "blocking_reasons": [], "warnings": [], "monitoring_checks": {"external_notifications_sent": False}})

    rem = paths.data_dir / "equity_owner_remediation" / "daily" / as_of_date
    write_json(rem / "remediation_priority_summary.json", {"target_version": "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist", "as_of_date": as_of_date, "status": "manual_review_required", "priority_buckets": {"P0_blocking": [], "P1_high_warning": ["known_warning"]}})
    write_json(rem / "safe_owner_action_checklist.json", {"target_version": "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist", "as_of_date": as_of_date, "items": [{"item_id": "VERIFY-AUDITS", "safe_action_type": "verify_audit", "allowed_to_execute_automatically": False, "command_if_any": None}]})
    write_json(rem / "non_actionable_issue_list.json", {"target_version": "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist", "as_of_date": as_of_date, "items": []})
    write_json(rem / "dry_run_remediation_plan.json", {"target_version": "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist", "as_of_date": as_of_date, "execute_remediation_actions": False})
    write_json(rem / "remediation_boundary_check.json", {"target_version": "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist", "as_of_date": as_of_date, "overall_passed": True, "execute_remediation_actions": False, "external_notifications_sent": False})
    write_json(rem / "remediation_manifest.json", {"target_version": "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist", "as_of_date": as_of_date, "overall_passed": True})
    write_json(paths.data_dir / "equity_data_quality" / "a_share_owner_remediation_audit.json", {"target_version": "v0.8.4-a-share-owner-remediation-runbook-and-action-checklist", "as_of_date": as_of_date, "overall_passed": True, "blocking_reasons": [], "warnings": [], "remediation_checks": {"automatic_action_count": 0, "execute_remediation_actions": False, "external_notifications_sent": False}})

    ops = paths.data_dir / "equity_ops_center" / "daily" / as_of_date
    write_json(ops / "ops_health_score_card.json", {"target_version": "v0.8.5-a-share-daily-ops-command-center", "as_of_date": as_of_date, "score": 65, "grade": "C", "overall_status": "passed_with_warnings"})
    write_json(ops / "ops_module_status_matrix.json", {"target_version": "v0.8.5-a-share-daily-ops-command-center", "as_of_date": as_of_date, "rows": [{"module_id": "owner_monitoring", "audit_passed": True, "status": "passed"}]})
    write_json(ops / "ops_issue_summary.json", {"target_version": "v0.8.5-a-share-daily-ops-command-center", "as_of_date": as_of_date, "blocking_issues": [], "warning_issues": [{"issue_id": "known_warning"}], "known_non_blocking_issues": []})
    write_json(ops / "ops_action_summary.json", {"target_version": "v0.8.5-a-share-daily-ops-command-center", "as_of_date": as_of_date, "safe_action_count": 1, "automatic_action_count": 0, "manual_review_count": 1, "top_owner_actions": ["检查 audit 是否通过"], "forbidden_action_hits": []})
    write_json(ops / "ops_owner_next_steps.json", {"target_version": "v0.8.5-a-share-daily-ops-command-center", "as_of_date": as_of_date, "do_now": [], "review_today": ["检查 audit 是否通过"], "wait_for_more_history": ["等待更多 monitoring/run-history 样本后再解释趋势。"], "developer_follow_up": [], "no_action_required": ["当前无需自动操作；继续观察并按 checklist 人工复核。"]})
    write_json(ops / "ops_boundary_check.json", {"target_version": "v0.8.5-a-share-daily-ops-command-center", "as_of_date": as_of_date, "overall_passed": True, "broker_connected": False, "real_orders_placed": False, "old_run_daily_called": False})
    write_json(ops / "ops_manifest.json", {"target_version": "v0.8.5-a-share-daily-ops-command-center", "as_of_date": as_of_date, "overall_passed": True})
    write_json(paths.data_dir / "equity_data_quality" / "a_share_daily_ops_center_audit.json", {"target_version": "v0.8.5-a-share-daily-ops-command-center", "as_of_date": as_of_date, "overall_passed": True, "blocking_reasons": [], "warnings": [], "ops_checks": {"automatic_action_count": 0, "aggregate_existing_artifacts_only": True, "external_notifications_sent": False}})
    write_json(paths.data_dir / "equity_data_quality" / "a_share_ops_history_baseline_audit.json", {"target_version": "v0.8.6-a-share-ops-run-history-deepening-and-trend-baselines", "as_of_date": as_of_date, "overall_passed": True, "blocking_reasons": []})


def seed_build_output_ops_outputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_build_output_ops_inputs(paths, as_of_date)
    from trading_core.equity_build_output_ops_refresh.build_output_ops_builder import build_a_share_build_output_ops_refresh

    build_a_share_build_output_ops_refresh(as_of_date=as_of_date, paths=paths)

