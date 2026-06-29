from trading_core.equity_current_day_builds.execution_plan import build_gated_build_execution_plan


def test_gated_build_execution_plan_uses_build_from_existing_data():
    plan = build_gated_build_execution_plan(as_of_date="2026-06-26", preflight_gate={"overall_passed": True})
    assert "--workflow-mode build_from_existing_data" in plan["workflow_command"]
    assert "run-daily" in plan["commands_forbidden"]

