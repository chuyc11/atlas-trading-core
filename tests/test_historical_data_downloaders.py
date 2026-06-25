from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_data_packages import REQUIRED_PACKAGE_IDS


def test_download_all_packages_fixture_success(tmp_path: Path) -> None:
    result = download_historical_data_packages(start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=make_paths(tmp_path))
    assert {item["package_id"] for item in result["packages"]} == set(REQUIRED_PACKAGE_IDS)
    assert all(item["status"] in {"loaded_from_local", "downloaded"} for item in result["packages"])


def test_individual_failure_does_not_stop_all_when_continue_on_error(tmp_path: Path) -> None:
    def fail(_url: str, _timeout: int) -> bytes:
        raise TimeoutError("timeout")

    result = download_historical_data_packages(packages=["HIST-FX-USDCNY-V1", "HIST-GLOBAL-RISK-VIX-V1"], continue_on_error=True, paths=make_paths(tmp_path), http_get=fail)
    assert len(result["packages"]) == 2
    assert all(item["status"] == "failed" for item in result["packages"])


def test_checksum_source_dates_written_and_no_secret(tmp_path: Path) -> None:
    result = download_historical_data_packages(packages=["HIST-GLOBAL-RISK-VIX-V1"], start_date="2024-01-02", end_date="2024-01-08", source_mode="fixture", paths=make_paths(tmp_path))
    item = result["packages"][0]
    assert item["sha256"]
    assert item["source"] == "fixture"
    assert item["date_min"] == "2024-01-02"
    assert item["date_max"] == "2024-01-08"
    assert "secret" not in Path(result["json_path"]).read_text(encoding="utf-8").lower()


def test_download_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = download_historical_data_packages(packages=["HIST-GLOBAL-RISK-VIX-V1"], source_mode="fixture", paths=paths)
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert_no_protected_paths(paths)


def test_download_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["download-historical-data-packages", "--start-date", "2024-01-02", "--end-date", "2024-01-08", "--source-mode", "fixture", "--continue-on-error"]) == 0
