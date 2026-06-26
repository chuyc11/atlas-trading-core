from __future__ import annotations

from pathlib import Path
import json

import pytest

from forward_dry_run_day1_owner_report_test_utils import make_day1_owner_report_paths
from trading_core.forward_dry_run.day1_virtual_order_fill_report import build_day1_virtual_order_fill_report


def test_day1_virtual_order_fill_report_summarizes_virtual_execution(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    result = build_day1_virtual_order_fill_report(paths=paths)
    preview = json.loads((paths.data_dir / "forward_dry_run" / "day_001" / "day1_virtual_order_preview.json").read_text(encoding="utf-8"))
    execution = json.loads((paths.data_dir / "forward_dry_run" / "day_001" / "day1_virtual_execution_result.json").read_text(encoding="utf-8"))
    assert result["orders_total"] == len(preview["orders"])
    assert result["fills_total"] == len(execution["fills"])
    assert result["rejects_total"] == 0
    assert result["real_orders_placed"] is False
    assert result["broker_orders_placed"] is False
    assert result["main_orders_written"] is False
    assert result["boundary"]["virtual_orders_only"] is True


def test_day1_virtual_order_fill_report_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_owner_report_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-virtual-order-fill-report"]) == 0
