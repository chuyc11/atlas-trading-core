import pytest

from trading_core.equity_build_repeatability.execution_plan import build_repeat_build_execution_plan


def test_repeatability_execution_plan_uses_build_from_existing_data():
    plan = build_repeat_build_execution_plan(as_of_date="2026-06-26")
    assert plan["workflow_mode"] == "build_from_existing_data"
    assert "--workflow-mode build_from_existing_data" in plan["command"]
    assert plan["workflow_argv"][0] == "python"
    assert plan["command_allowed"] is True


def test_repeatability_execution_plan_has_no_old_run_daily():
    plan = build_repeat_build_execution_plan(as_of_date="2026-06-26")
    assert "run-daily" not in plan["command"]


def test_repeatability_execution_plan_rejects_command_metacharacters():
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        build_repeat_build_execution_plan(as_of_date="2026-06-26; whoami")
