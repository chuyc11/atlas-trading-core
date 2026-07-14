import subprocess
from unittest.mock import patch

from trading_core.equity_current_day_builds.execution_plan import build_gated_build_execution_plan
from trading_core.equity_current_day_builds.execution_record import execute_gated_build_and_record
from trading_core.storage.file_paths import ProjectPaths


def test_gated_build_execution_record_skips_when_preflight_failed(tmp_path):
    record = execute_gated_build_and_record(paths=None, as_of_date="2026-06-26", preflight_gate={"overall_passed": False}, execution_plan={"workflow_command": "x"})
    assert record["command_executed"] is False
    assert record["old_run_daily_called"] is False


def test_gated_build_execution_record_uses_allowlisted_argv_without_shell(tmp_path):
    paths = ProjectPaths(tmp_path)
    paths.project_root.mkdir(parents=True)
    plan = build_gated_build_execution_plan(as_of_date="2026-06-26", preflight_gate={"overall_passed": True})
    with patch(
        "trading_core.equity_current_day_builds.execution_record.subprocess.run",
        return_value=subprocess.CompletedProcess([], 0, "", ""),
    ) as run:
        record = execute_gated_build_and_record(
            paths=paths,
            as_of_date="2026-06-26",
            preflight_gate={"overall_passed": True},
            execution_plan=plan,
        )
    argv = run.call_args.args[0]
    assert isinstance(argv, list)
    assert argv[1:4] == ["-m", "trading_core.cli", "run-and-audit-a-share-current-day-research"]
    assert run.call_args.kwargs["shell"] is False
    assert record["command_executed"] is True


def test_gated_build_execution_record_rejects_tampered_plan(tmp_path):
    paths = ProjectPaths(tmp_path)
    plan = build_gated_build_execution_plan(as_of_date="2026-06-26", preflight_gate={"overall_passed": True})
    plan["workflow_argv"].append("unexpected")
    with patch("trading_core.equity_current_day_builds.execution_record.subprocess.run") as run:
        record = execute_gated_build_and_record(
            paths=paths,
            as_of_date="2026-06-26",
            preflight_gate={"overall_passed": True},
            execution_plan=plan,
        )
    run.assert_not_called()
    assert record["blocking_reasons"] == ["execution_plan_command_mismatch"]
