from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import make_authorization_paths
from trading_core.forward_dry_run.manual_confirmation_checklist_v2 import CONFIRMATION_ITEMS, build_forward_dry_run_manual_confirmation_checklist_v2


def test_manual_confirmation_checklist_v2_defaults_false(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    result = build_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert [item["item"] for item in result["confirmation_items"]] == CONFIRMATION_ITEMS
    assert all(item["confirmed"] is False for item in result["confirmation_items"])
    assert result["manual_confirmation_complete"] is False
    assert result["does_not_auto_complete"] is True
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False


def test_manual_confirmation_checklist_v2_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-manual-confirmation-checklist-v2"]) == 0

