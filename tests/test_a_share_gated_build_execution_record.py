from trading_core.equity_current_day_builds.execution_record import execute_gated_build_and_record


def test_gated_build_execution_record_skips_when_preflight_failed(tmp_path):
    record = execute_gated_build_and_record(paths=None, as_of_date="2026-06-26", preflight_gate={"overall_passed": False}, execution_plan={"workflow_command": "x"})
    assert record["command_executed"] is False
    assert record["old_run_daily_called"] is False

