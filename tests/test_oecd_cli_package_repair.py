from __future__ import annotations

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, write_text
from trading_core.global_briefing.downloaders.oecd_cli_downloader import build_oecd_cli_rows
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.macro_cycle_proxy_builder import REGIONS


def _fail_http(_url: str, _timeout: int) -> bytes:
    raise TimeoutError("network disabled in test")


def _all_region_csv(source: str = "oecd_authorized_api") -> bytes:
    rows = ["date,region,cli_value,source,official_oecd_cli,macro_cycle_proxy"]
    rows.extend(f"2024-01-02,{region},100.1,{source},true,false" for region in REGIONS)
    return ("\n".join(rows) + "\n").encode()


def test_local_oecd_csv_loaded_with_checksum_provenance_and_report(tmp_path) -> None:
    paths = make_paths(tmp_path)
    write_text(
        paths.data_dir / "global_briefing" / "authorized" / "input" / "oecd_cli" / "oecd.csv",
        _all_region_csv("local").decode(),
    )
    result = download_historical_data_packages(
        packages=["HIST-OECD-CLI-MACRO-CYCLE-V1"],
        start_date="2024-01-02",
        end_date="2024-01-08",
        paths=paths,
        http_get=_fail_http,
    )
    item = result["packages"][0]
    assert item["status"] == "loaded_from_local"
    assert item["sha256"]
    assert item["provenance_path"]
    assert "Historical data authorization is not trading authorization" in open(paths.outputs_dir / "system" / "HIST_OECD_CLI_MACRO_CYCLE_PACKAGE_REPORT.md", encoding="utf-8").read()
    assert_no_protected_paths(paths)


def test_authorized_api_and_public_api_success(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    paths = make_paths(tmp_path)
    monkeypatch.setenv("OECD_AUTH_BASE_URL", "https://oecd-auth.example.test")
    monkeypatch.setenv("OECD_AUTH_EXPORT_ENDPOINT", "/cli")
    rows, source, status, _warnings, metadata = build_oecd_cli_rows(paths=paths, start_date="2024-01-02", end_date="2024-01-08", timeout=8, retries=1, http_get=lambda _url, _timeout: _all_region_csv())
    assert source == "oecd_authorized_api"
    assert status == "downloaded"
    assert metadata["official_oecd_cli"] is True
    assert {row["region"] for row in rows} == set(REGIONS)

    monkeypatch.delenv("OECD_AUTH_BASE_URL", raising=False)
    monkeypatch.delenv("OECD_AUTH_EXPORT_ENDPOINT", raising=False)
    monkeypatch.setenv("OECD_PUBLIC_CLI_URL", "https://oecd-public.example.test/cli")
    rows, source, status, _warnings, metadata = build_oecd_cli_rows(paths=paths, start_date="2024-01-02", end_date="2024-01-08", timeout=8, retries=1, http_get=lambda _url, _timeout: _all_region_csv("oecd_public_api"))
    assert source == "oecd_public_api"
    assert status == "downloaded"
    assert metadata["official_oecd_cli"] is True


def test_macro_cycle_proxy_when_official_unavailable(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    paths = make_paths(tmp_path)
    monkeypatch.delenv("OECD_AUTH_BASE_URL", raising=False)
    monkeypatch.delenv("OECD_AUTH_EXPORT_ENDPOINT", raising=False)
    monkeypatch.delenv("OECD_PUBLIC_CLI_URL", raising=False)
    download_historical_data_packages(
        packages=[
            "HIST-BENCHMARK-INDEX-CN-HK-V1",
            "HIST-FX-USDCNY-V1",
            "HIST-GLOBAL-RISK-VIX-V1",
            "HIST-RATES-LIQUIDITY-V1",
            "HIST-COMMODITY-INFLATION-RISK-V1",
        ],
        start_date="2024-01-02",
        end_date="2024-01-08",
        source_mode="fixture",
        paths=paths,
    )
    result = download_historical_data_packages(
        packages=["HIST-OECD-CLI-MACRO-CYCLE-V1"],
        start_date="2024-01-02",
        end_date="2024-01-08",
        paths=paths,
        http_get=_fail_http,
    )
    item = result["packages"][0]
    assert item["status"] == "downloaded"
    assert item["source"] == "authorized_macro_cycle_proxy"
    assert item["official_oecd_cli"] is False
    assert item["macro_cycle_proxy"] is True
    assert item["not_official_oecd_cli"] is True
    assert item["sha256"] and item["provenance_path"]

    empty_paths = make_paths(tmp_path / "empty")
    rows, _source, status, warnings, metadata = build_oecd_cli_rows(paths=empty_paths, start_date="2024-01-02", end_date="2024-01-08", timeout=1, retries=1, http_get=_fail_http)
    assert rows == []
    assert status == "failed_soft"
    assert metadata["macro_cycle_proxy"] is True
    assert warnings
