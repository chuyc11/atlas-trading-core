from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_package_normalizer import normalize_historical_data_packages


def _download(paths):
    return download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)


def test_normalize_etf_benchmark_vix_fx_and_build_proxy(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _download(paths)
    result = normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    assert result["packages"]["HIST-ETF-OHLCV-CN-HK-V1"]["status"] == "normalized"
    assert result["packages"]["HIST-BENCHMARK-INDEX-CN-HK-V1"]["status"] == "normalized"
    assert result["packages"]["HIST-GLOBAL-RISK-VIX-V1"]["status"] == "normalized"
    assert result["packages"]["HIST-FX-USDCNY-V1"]["status"] == "normalized"
    assert Path(result["proxy_package"]["normalized_path"]).exists()
    assert result["proxy_package"]["validated"] is True


def test_proxy_monthly_carry_forward_no_future_and_boundary(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    _download(paths)
    result = normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    text = Path(result["proxy_package"]["normalized_path"]).read_text(encoding="utf-8")
    assert "2024-01-31" not in text
    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)


def test_missing_optional_package_warning(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    download_historical_data_packages(packages=["HIST-ETF-OHLCV-CN-HK-V1", "HIST-BENCHMARK-INDEX-CN-HK-V1", "HIST-FX-USDCNY-V1", "HIST-GLOBAL-RISK-VIX-V1"], start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=paths)
    result = normalize_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", paths=paths)
    assert any("missing optional" in item for item in result["warnings"])


def test_normalizer_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _download(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["normalize-historical-data-packages", "--start-date", "2024-01-02", "--end-date", "2024-01-08"]) == 0
