from trading_core.equity_current_day_builds.gated_build_report import render_dry_run_report


def test_gated_build_report_contains_disclaimer():
    text = render_dry_run_report(as_of_date="2026-06-26", preflight_gate={"overall_passed": True}, execution_record={"status": "passed", "command": "cmd"}, workflow_result={"workflow_audit_overall_passed": True}, comparison={"comparison_completed": True}, drift_summary={"overall_status": "clean"}, boundary={"overall_passed": True}, summary={})
    assert "不授权任何交易" in text

