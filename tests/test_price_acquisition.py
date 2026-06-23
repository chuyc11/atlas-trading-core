from __future__ import annotations

import builtins
import csv
from pathlib import Path
from typing import Any

import pytest

from trading_core.data.price_acquisition import AKSHARE_REQUIRED_MESSAGE, AkSharePriceSource, fetch_prices
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json


class MockPriceSource:
    source_name = "mock-akshare"

    def __init__(self, fail_symbols: set[str] | None = None) -> None:
        self.fail_symbols = fail_symbols or set()
        self.calls: list[tuple[str, str, str, str]] = []

    def fetch_daily(self, symbol: str, market: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        self.calls.append((symbol, market, start_date, end_date))
        if symbol in self.fail_symbols:
            raise RuntimeError("source failed")
        return [
            {"日期": "2026-01-01", "开盘": 4.0, "最高": 4.1, "最低": 3.9, "收盘": 4.05, "成交量": 1000},
            {"日期": "2026-01-02", "开盘": 4.05, "最高": 4.2, "最低": 4.0, "收盘": 4.1, "成交量": 1200},
        ]


def _universe() -> dict[str, Any]:
    return {
        "symbols": [
            {"symbol": "510300.SH", "market": "A_SHARE", "asset_type": "ETF"},
            {"symbol": "2800.HK", "market": "HK", "asset_type": "ETF"},
        ]
    }


def _fast_config() -> dict[str, Any]:
    return {
        "retry": {"max_attempts": 1, "initial_sleep_seconds": 0, "backoff_multiplier": 1, "jitter_seconds": 0},
        "throttle": {"sleep_between_symbols_seconds": 0},
        "failure_policy": {
            "allow_partial_success": True,
            "never_generate_synthetic_prices": True,
            "never_forward_fill_missing_prices": True,
        },
    }


def _no_sleep(seconds: float) -> None:
    return None


def test_fetch_prices_writes_csv_manifest_and_validation(tmp_path: Path) -> None:
    output = tmp_path / "etf_daily"
    source = MockPriceSource()

    result = fetch_prices(
        "2026-01-01",
        "2026-01-02",
        output,
        project_paths(tmp_path),
        source,
        _universe(),
        config=_fast_config(),
        sleep_func=_no_sleep,
    )

    manifest = read_json(output / "manifest.json")
    assert manifest["symbols_requested"] == ["510300.SH", "2800.HK"]
    assert manifest["symbols_success"] == ["510300.SH", "2800.HK"]
    assert manifest["symbols_failed"] == []
    assert manifest["source"] == "mock-akshare"
    assert manifest["attempts_by_symbol"]["510300.SH"][0]["status"] == "success"
    assert result["validation"]["passed"] is True
    assert Path(result["validation"]["json_path"]).exists()
    assert source.calls == [
        ("510300.SH", "A_SHARE", "2026-01-01", "2026-01-02"),
        ("2800.HK", "HK", "2026-01-01", "2026-01-02"),
    ]

    with (output / "510300.SH.csv").open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == ["date", "symbol", "open", "high", "low", "close", "volume", "source", "quality"]
        rows = list(reader)
    assert rows[0] == {
        "date": "2026-01-01",
        "symbol": "510300.SH",
        "open": "4.0",
        "high": "4.1",
        "low": "3.9",
        "close": "4.05",
        "volume": "1000.0",
        "source": "mock-akshare",
        "quality": "fresh",
    }


def test_fetch_prices_records_single_symbol_failure_without_synthetic_csv(tmp_path: Path) -> None:
    output = tmp_path / "etf_daily"
    source = MockPriceSource(fail_symbols={"2800.HK"})

    result = fetch_prices(
        "2026-01-01",
        "2026-01-02",
        output,
        project_paths(tmp_path),
        source,
        _universe(),
        config=_fast_config(),
        sleep_func=_no_sleep,
    )

    manifest = result["manifest"]
    assert manifest["symbols_success"] == ["510300.SH"]
    assert manifest["symbols_failed"] == ["2800.HK"]
    assert "2800.HK: mock-akshare attempt 1: source failed" in manifest["warnings"]
    assert (output / "510300.SH.csv").exists()
    assert not (output / "2800.HK.csv").exists()
    assert "2800.HK" not in manifest["output_files"]
    assert result["validation"]["symbols"] == ["510300.SH"]


def test_akshare_missing_error_is_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "akshare":
            raise ImportError("no akshare")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError, match=AKSHARE_REQUIRED_MESSAGE):
        AkSharePriceSource()


def test_fetch_prices_does_not_forward_fill_missing_rows(tmp_path: Path) -> None:
    class SparseSource(MockPriceSource):
        def fetch_daily(self, symbol: str, market: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
            return [{"date": "2026-01-01", "open": 4.0, "high": 4.1, "low": 3.9, "close": 4.05, "volume": 1000}]

    output = tmp_path / "etf_daily"
    result = fetch_prices(
        "2026-01-01",
        "2026-01-05",
        output,
        project_paths(tmp_path),
        SparseSource(),
        _universe(),
        config=_fast_config(),
        sleep_func=_no_sleep,
    )

    with (output / "510300.SH.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert result["manifest"]["symbols_success"] == ["510300.SH", "2800.HK"]
    assert result["validation"]["total_rows"] == 2
