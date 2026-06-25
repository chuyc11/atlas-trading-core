from __future__ import annotations

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, write_text
from trading_core.global_briefing.downloaders.epu_downloader import build_epu_rows
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages


def _fail_http(_url: str, _timeout: int) -> bytes:
    raise TimeoutError("network disabled in test")


def test_local_epu_csv_loaded_with_checksum_provenance_and_report(tmp_path) -> None:
    paths = make_paths(tmp_path)
    write_text(
        paths.data_dir / "global_briefing" / "authorized" / "input" / "epu" / "epu.csv",
        "date,series_id,value,frequency,source,downloaded_at,generated_at\n"
        "2024-01-02,global_epu,120,daily,local,2026-06-25T00:00:00Z,2024-01-02T23:59:00Z\n",
    )
    result = download_historical_data_packages(
        packages=["HIST-POLICY-UNCERTAINTY-EPU-V1"],
        start_date="2024-01-02",
        end_date="2024-01-08",
        paths=paths,
        http_get=_fail_http,
    )
    item = result["packages"][0]
    assert item["status"] == "loaded_from_local"
    assert item["sha256"]
    assert item["provenance_path"]
    assert "Historical data authorization is not trading authorization" in open(paths.outputs_dir / "system" / "HIST_POLICY_UNCERTAINTY_EPU_PACKAGE_REPORT.md", encoding="utf-8").read()
    assert_no_protected_paths(paths)


def test_authorized_api_success_and_generated_at(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    paths = make_paths(tmp_path)
    monkeypatch.setenv("EPU_AUTH_BASE_URL", "https://epu.example.test")
    monkeypatch.setenv("EPU_AUTH_EXPORT_ENDPOINT", "/export")

    def http_get(url: str, timeout: int) -> bytes:
        assert timeout == 8
        assert "epu.example.test" in url
        return (
            b"date,global_epu,china_epu,us_epu,europe_epu\n"
            b"2024-01-02,120,130,110,105\n"
        )

    rows, source, status, warnings, metadata = build_epu_rows(paths=paths, start_date="2024-01-02", end_date="2024-01-08", timeout=8, retries=1, http_get=http_get)
    assert source == "epu_authorized_api"
    assert status == "downloaded"
    assert not warnings
    assert metadata["official_epu"] is True
    assert {row["series_id"] for row in rows} == {"global_epu", "china_epu", "us_epu", "europe_epu"}
    assert all(row["generated_at"].startswith(row["date"]) for row in rows)


def test_fred_success_partial_and_failed_soft(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    paths = make_paths(tmp_path)
    monkeypatch.delenv("EPU_AUTH_BASE_URL", raising=False)
    monkeypatch.delenv("EPU_AUTH_EXPORT_ENDPOINT", raising=False)
    monkeypatch.setenv("FRED_EPU_SERIES_IDS", "global_epu:GLOBALID,china_epu:CHINAID")

    def http_get(url: str, _timeout: int) -> bytes:
        series = "GLOBALID" if "GLOBALID" in url else "CHINAID"
        return f"observation_date,{series}\n2024-01-02,123\n".encode()

    rows, source, status, _warnings, metadata = build_epu_rows(paths=paths, start_date="2024-01-02", end_date="2024-01-08", timeout=8, retries=1, http_get=http_get)
    assert source == "fred"
    assert status == "partial_downloaded"
    assert metadata["missing_series"] == ["us_epu", "europe_epu"]
    assert {row["series_id"] for row in rows} == {"global_epu", "china_epu"}

    monkeypatch.setenv("FRED_EPU_SERIES_IDS", "us_epu:USID")
    rows, _source, status, warnings, _metadata = build_epu_rows(paths=paths, start_date="2024-01-02", end_date="2024-01-08", timeout=8, retries=1, http_get=lambda _url, _timeout: b"observation_date,USID\n2024-01-02,100\n")
    assert rows
    assert status == "failed_soft"
    assert any("lacks Global or China" in warning for warning in warnings)

    empty_paths = make_paths(tmp_path / "empty")
    rows, _source, status, warnings, metadata = build_epu_rows(paths=empty_paths, start_date="2024-01-02", end_date="2024-01-08", timeout=1, retries=1, http_get=_fail_http)
    assert rows == []
    assert status == "failed_soft"
    assert metadata["policy_uncertainty_proxy"] is False
    assert warnings
