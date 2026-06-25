from pathlib import Path

import pytest

from daily_workflow_test_utils import AS_OF, make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.daily_workflow.daily_market_data_snapshot import build_daily_market_data_snapshot


def test_daily_market_data_snapshot(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    result = build_daily_market_data_snapshot(as_of_date=AS_OF, paths=paths)
    assert result["as_of_date"] == AS_OF
    assert result["latest_available_trading_date"] == AS_OF
    assert len([item for item in result["symbols"].values() if item["available"]]) == 8
    assert result["risk_proxy_available"] is True
    assert result["source_records"]["benchmark_data"]["exists"] is True
    assert result["boundary"]["real_time_download"] is False
    assert result["boundary"]["external_api_called"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_daily_market_data_snapshot_auto_latest_and_missing_symbol(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    result = build_daily_market_data_snapshot(paths=paths)
    assert result["as_of_date"] == AS_OF
    market = paths.project_root / "data" / "market" / "historical" / "authorized" / "HIST-ETF-OHLCV-CN-HK-V1.csv"
    text = "\n".join(line for line in market.read_text(encoding="utf-8").splitlines() if "3033.HK" not in line)
    market.write_text(text + "\n", encoding="utf-8")
    missing = build_daily_market_data_snapshot(as_of_date=AS_OF, paths=paths)
    assert missing["symbols"]["3033.HK"]["available"] is False


def test_daily_market_data_snapshot_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["daily-market-data-snapshot", "--as-of-date", AS_OF]) == 0

