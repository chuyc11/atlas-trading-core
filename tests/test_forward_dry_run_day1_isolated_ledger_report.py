from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_owner_report_test_utils import make_day1_owner_report_paths
from trading_core.forward_dry_run.day1_isolated_ledger_report import build_day1_isolated_ledger_report


def test_day1_isolated_ledger_report_keeps_main_ledger_separate(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    result = build_day1_isolated_ledger_report(paths=paths)
    assert result["forward_dry_run_ledger_written"] is True
    assert result["ledger_path_root"] == "data/forward_dry_run"
    assert result["invariants"]["cash_non_negative"] is True
    assert result["invariants"]["positions_non_negative"] is True
    assert result["invariants"]["available_shares_valid"] is True
    assert result["boundary"]["main_orders_written"] is False
    assert result["boundary"]["main_accounts_written"] is False


def test_day1_isolated_ledger_report_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_owner_report_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-isolated-ledger-report"]) == 0
