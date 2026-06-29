from trading_core.equity_ops_history.ops_history_report import render_audit, render_run_history


def test_ops_history_reports_render_core_fields():
    payload = {"ops_history_summary": {"as_of_date": "2026-06-26", "source_version": "v0.8.5", "run_history_observation_count": 1, "trend_analysis_available": False, "baseline_status": "insufficient_history"}, "ops_history_append_result": {"append_completed": True, "idempotent_append": False}, "ops_trend_sufficiency": {"minimum_required_observations": 5}}
    assert "insufficient_history" in render_run_history(payload)
    audit = {"audit_id": "audit", "overall_passed": True, "blocking_reasons": [], "trend_sufficiency": {"run_history_observation_count": 1, "trend_analysis_available": False, "baseline_status": "insufficient_history"}, "recommended_next_version": "next"}
    assert "overall_passed: true" in render_audit(audit)

