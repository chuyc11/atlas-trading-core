from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_test_utils import build_day1_authorized_stack, make_day1_paths
from trading_core.forward_dry_run.day1_input_snapshot import build_day1_input_snapshot
from trading_core.forward_dry_run.day1_ledger_snapshot import build_day1_ledger_snapshot
from trading_core.forward_dry_run.day1_pre_execution_gate import build_day1_pre_execution_gate
from trading_core.forward_dry_run.day1_strategy_signals import build_day1_strategy_signals
from trading_core.forward_dry_run.day1_virtual_execution_result import build_day1_virtual_execution_result
from trading_core.forward_dry_run.day1_virtual_order_preview import build_day1_virtual_order_preview


def _build_execution_prereqs(paths) -> None:
    build_day1_authorized_stack(paths)
    build_day1_pre_execution_gate(paths=paths, git_status_clean_override=True)
    build_day1_input_snapshot(paths=paths)
    build_day1_strategy_signals(paths=paths)
    build_day1_virtual_order_preview(paths=paths)


def test_day1_virtual_execution_writes_isolated_ledger_only(tmp_path: Path) -> None:
    paths = make_day1_paths(tmp_path)
    _build_execution_prereqs(paths)
    result = build_day1_virtual_execution_result(paths=paths)
    assert result["execution_mode"] == "forward_dry_run_virtual"
    assert result["virtual_execution"] is True
    assert result["real_execution"] is False
    assert result["broker_execution"] is False
    assert len(result["fills"]) > 0
    assert result["ledger_writes"]["forward_dry_run_ledger_written"] is True
    assert result["ledger_writes"]["main_orders_written"] is False
    assert (paths.data_dir / "forward_dry_run" / "ledger" / "day1_ledger.json").exists()
    assert not (paths.data_dir / "orders").exists()
    assert not (paths.data_dir / "trades").exists()


def test_day1_ledger_snapshot_sets_day2_continuation_state(tmp_path: Path) -> None:
    paths = make_day1_paths(tmp_path)
    _build_execution_prereqs(paths)
    build_day1_virtual_execution_result(paths=paths)
    result = build_day1_ledger_snapshot(paths=paths)
    assert result["forward_dry_run_started"] is True
    assert result["forward_dry_run_days_completed"] == 1
    assert result["next_day_index"] == 2
    assert result["boundary"]["main_ledger_written"] is False


def test_day1_virtual_execution_cli_chain(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_paths(tmp_path)
    _build_execution_prereqs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-virtual-execution"]) == 0
    assert cli.main(["forward-dry-run-day1-ledger-snapshot"]) == 0
