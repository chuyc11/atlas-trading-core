from __future__ import annotations

from pathlib import Path
import json

import pytest

from forward_dry_run_day1_owner_report_test_utils import make_day1_owner_report_paths
from trading_core.forward_dry_run.day1_owner_summary_report import build_day1_owner_summary_report


def test_day1_owner_summary_report_key_numbers_and_boundaries(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    result = build_day1_owner_summary_report(paths=paths)
    assert result["report_id"] == "FORWARD-DRY-RUN-DAY1-OWNER-SUMMARY-REPORT"
    assert result["as_of_date"] == "2026-06-25"
    assert result["key_numbers"]["strategies_total"] == 3
    assert result["key_numbers"]["strategies_generated"] == 3
    preview = json.loads((paths.data_dir / "forward_dry_run" / "day_001" / "day1_virtual_order_preview.json").read_text(encoding="utf-8"))
    execution = json.loads((paths.data_dir / "forward_dry_run" / "day_001" / "day1_virtual_execution_result.json").read_text(encoding="utf-8"))
    assert result["key_numbers"]["virtual_orders_total"] == len(preview["orders"])
    assert result["key_numbers"]["virtual_fills"] == len(execution["fills"])
    assert result["key_numbers"]["virtual_rejects"] == 0
    assert result["boundary"]["live_trading_ready"] is False


def test_day1_owner_summary_report_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_owner_report_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-owner-summary-report"]) == 0
