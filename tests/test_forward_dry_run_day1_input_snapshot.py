from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_test_utils import DAY1_AS_OF, make_day1_paths
from trading_core.forward_dry_run.day1_input_snapshot import build_day1_input_snapshot


def test_day1_input_snapshot_uses_latest_local_authorized_date(tmp_path: Path) -> None:
    paths = make_day1_paths(tmp_path)
    result = build_day1_input_snapshot(paths=paths)
    assert result["overall_passed"] is True
    assert result["as_of_date"] == DAY1_AS_OF
    assert result["universe_complete"] is True
    assert result["benchmark_complete"] is True
    assert result["risk_proxy_complete"] is True
    assert result["real_time_market_data_downloaded"] is False
    assert result["external_api_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert result["source_hashes"]["market_data"]["sha256"]


def test_day1_input_snapshot_blocks_missing_coverage(tmp_path: Path) -> None:
    paths = make_day1_paths(tmp_path)
    market = paths.project_root / "data" / "market" / "historical" / "authorized" / "HIST-ETF-OHLCV-CN-HK-V1.csv"
    market.write_text("\n".join(market.read_text(encoding="utf-8").splitlines()[:-1]) + "\n", encoding="utf-8")
    result = build_day1_input_snapshot(paths=paths)
    assert result["overall_passed"] is False
    assert result["missing_symbols"]


def test_day1_input_snapshot_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-input-snapshot"]) == 0
