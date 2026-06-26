from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_owner_report_test_utils import make_day1_owner_report_paths
from trading_core.forward_dry_run.day1_data_reproducibility_appendix import build_day1_data_reproducibility_appendix


def test_day1_data_reproducibility_appendix_records_sources_and_no_downloads(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    result = build_day1_data_reproducibility_appendix(paths=paths)
    assert result["day1_as_of_date"] == "2026-06-25"
    assert result["market_data_source"]
    assert result["benchmark_source"]
    assert result["risk_proxy_source"]
    assert result["external_api_called"] is False
    assert result["real_time_market_data_downloaded"] is False
    assert result["ledger_hash"]


def test_day1_data_reproducibility_appendix_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_owner_report_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-data-reproducibility-appendix"]) == 0
