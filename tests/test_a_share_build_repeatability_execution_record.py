from unittest.mock import patch

from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_build_repeatability.execution_plan import build_repeat_build_execution_plan
from trading_core.equity_build_repeatability.execution_record import execute_repeat_build_and_record
import pytest

pytestmark = pytest.mark.smoke


def test_repeatability_execution_record_skips_on_preflight_failure(tmp_path):
    paths = make_paths(tmp_path)
    record = execute_repeat_build_and_record(
        paths=paths,
        as_of_date=AS_OF_DATE,
        input_availability={"overall_passed": False},
        date_alignment={"overall_passed": True},
        execution_plan={"workflow_command": "echo no", "command_allowed": True},
    )
    assert record["command_executed"] is False
    assert record["old_run_daily_called"] is False


def test_repeatability_execution_record_rejects_tampered_plan(tmp_path):
    paths = make_paths(tmp_path)
    plan = build_repeat_build_execution_plan(as_of_date=AS_OF_DATE)
    plan["workflow_command"] = "unexpected"
    with patch("trading_core.equity_build_repeatability.execution_record.subprocess.run") as run:
        record = execute_repeat_build_and_record(
            paths=paths,
            as_of_date=AS_OF_DATE,
            input_availability={"overall_passed": True},
            date_alignment={"overall_passed": True},
            execution_plan=plan,
        )
    run.assert_not_called()
    assert record["blocking_reasons"] == ["execution_plan_command_mismatch"]
