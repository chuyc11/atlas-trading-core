from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import make_authorization_paths
from trading_core.forward_dry_run.start_prerequisite_inventory import build_forward_dry_run_start_prerequisite_inventory


def test_start_prerequisite_inventory(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    result = build_forward_dry_run_start_prerequisite_inventory(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    statuses = {item["prerequisite_id"]: item["status"] for item in result["prerequisites"]}
    for required in ["plan_alignment", "ashare_execution_rules", "baseline_strategy_pack", "daily_workflow_binding", "data_quality", "protected_path_residue", "manual_confirmation", "owner_authorization", "run_daily_preview", "day1_prompt_eligibility"]:
        assert required in statuses
    for technical in ["plan_alignment", "ashare_execution_rules", "baseline_strategy_pack", "daily_workflow_binding", "data_quality", "protected_path_residue"]:
        assert statuses[technical] == "passed"
    assert statuses["manual_confirmation"] == "pending"
    assert statuses["owner_authorization"] == "pending"
    assert statuses["day1_prompt_eligibility"] == "not_eligible"
    assert result["overall_day1_allowed"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_start_prerequisite_inventory_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-start-prerequisite-inventory"]) == 0

