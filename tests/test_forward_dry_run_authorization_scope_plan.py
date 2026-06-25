from pathlib import Path

import pytest

from forward_dry_run_authorization_test_utils import make_authorization_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.forward_dry_run.start_authorization_scope_plan import build_forward_dry_run_authorization_scope_plan


def test_authorization_scope_plan(tmp_path: Path) -> None:
    paths = make_authorization_paths(tmp_path)
    result = build_forward_dry_run_authorization_scope_plan(paths=paths)
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert result["target_version"] == "v0.6.2-forward-dry-run-start-authorization-pack-audited"
    assert result["daily_workflow_audit_passed"] is True
    assert result["known_day1_blockers_closed"] is True
    assert result["forward_dry_run_day1_allowed"] is False
    assert result["boundary"]["manual_confirmation_complete"] is False
    assert result["boundary"]["forward_dry_run_start_authorized"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert_no_protected_paths(paths)


def test_authorization_scope_plan_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_authorization_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-authorization-scope-plan"]) == 0

