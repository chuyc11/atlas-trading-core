from pathlib import Path

import pytest

from daily_workflow_test_utils import AS_OF, make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.daily_workflow.daily_input_freeze_manifest import build_daily_input_freeze_manifest


def test_daily_input_freeze_manifest(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    result = build_daily_input_freeze_manifest(as_of_date=AS_OF, paths=paths)
    assert result["as_of_date"] == AS_OF
    for name in ["market_data", "baseline_strategy_registry", "virtual_execution_contract", "data_quality_audit"]:
        assert result["sources"][name]["sha256"]
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    repeated = build_daily_input_freeze_manifest(as_of_date=AS_OF, paths=paths)
    stripped = {k: v for k, v in result.items() if k not in {"generated_at", "manifest_id"}}
    repeated_stripped = {k: v for k, v in repeated.items() if k not in {"generated_at", "manifest_id"}}
    assert stripped == repeated_stripped
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_daily_input_freeze_manifest_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["daily-input-freeze-manifest", "--as-of-date", AS_OF]) == 0

