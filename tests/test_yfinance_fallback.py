from __future__ import annotations

import builtins
import csv
from pathlib import Path
from typing import Any

import pytest

from trading_core.data.price_acquisition import (
    YFINANCE_LIMITATION,
    YFINANCE_REQUIRED_MESSAGE,
    YFinancePriceSource,
    fetch_prices,
)
from trading_core.storage.file_paths import project_paths


class Source:
    def __init__(self, source_name: str, *, fail: bool = False) -> None:
        self.source_name = source_name
        self.fail = fail
        self.calls: list[str] = []

    def fetch_daily(self, symbol: str, market: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        self.calls.append(symbol)
        if self.fail:
            raise RuntimeError(f"{self.source_name} failed")
        return [{"date": "2026-01-01", "open": 4.0, "high": 4.1, "low": 3.9, "close": 4.05, "volume": 1000}]


class MockYF:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def download(self, symbol: str, **kwargs: Any) -> list[dict[str, Any]]:
        self.calls.append({"symbol": symbol, **kwargs})
        return [{"Date": "2026-01-01", "Open": 4.0, "High": 4.1, "Low": 3.9, "Close": 4.05, "Volume": 1000}]


class BadYF(MockYF):
    def download(self, symbol: str, **kwargs: Any) -> list[dict[str, Any]]:
        self.calls.append({"symbol": symbol, **kwargs})
        return [{"Open": 4.0, "High": 4.1, "Low": 3.9, "Close": 4.05, "Volume": 1000}]


class TupleKeyYF(MockYF):
    def download(self, symbol: str, **kwargs: Any) -> list[dict[str, Any]]:
        self.calls.append({"symbol": symbol, **kwargs})
        return [
            {
                ("Date", ""): "2026-01-01",
                ("Open", symbol): 4.0,
                ("High", symbol): 4.1,
                ("Low", symbol): 3.9,
                ("Close", symbol): 4.05,
                ("Volume", symbol): 1000,
            }
        ]


def _universe() -> dict[str, Any]:
    return {"symbols": [{"symbol": "510300.SH", "market": "A_SHARE", "asset_type": "ETF"}]}


def _mapping() -> dict[str, Any]:
    return {"510300.SH": {"akshare": "510300", "yfinance": "510300.SS"}}


def _config() -> dict[str, Any]:
    return {
        "retry": {"max_attempts": 1, "initial_sleep_seconds": 0, "backoff_multiplier": 1, "jitter_seconds": 0},
        "throttle": {"sleep_between_symbols_seconds": 0},
        "failure_policy": {
            "allow_partial_success": True,
            "never_generate_synthetic_prices": True,
            "never_forward_fill_missing_prices": True,
        },
    }


def test_yfinance_missing_error_is_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "yfinance":
            raise ImportError("no yfinance")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError, match=YFINANCE_REQUIRED_MESSAGE):
        YFinancePriceSource()


def test_yfinance_source_writes_csv_and_limitation(tmp_path: Path) -> None:
    mock_yf = MockYF()
    source = YFinancePriceSource(yf_module=mock_yf, symbol_mapping=_mapping())

    result = fetch_prices(
        "2026-01-01",
        "2026-01-01",
        tmp_path / "out",
        project_paths(tmp_path),
        source_mode="yfinance",
        sources={"yfinance": source},
        universe=_universe(),
        config=_config(),
        symbol_mapping=_mapping(),
        sleep_func=lambda _seconds: None,
    )

    assert result["manifest"]["source_by_symbol"] == {"510300.SH": "yfinance"}
    assert YFINANCE_LIMITATION in result["manifest"]["warnings"]
    assert mock_yf.calls[0]["symbol"] == "510300.SS"
    with (tmp_path / "out" / "510300.SH.csv").open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == ["date", "symbol", "open", "high", "low", "close", "volume", "source", "quality"]
        assert list(reader)[0]["source"] == "yfinance"


def test_auto_does_not_call_yfinance_when_akshare_succeeds(tmp_path: Path) -> None:
    akshare = Source("akshare")
    yfinance = Source("yfinance")

    result = fetch_prices(
        "2026-01-01",
        "2026-01-01",
        tmp_path / "out",
        project_paths(tmp_path),
        source_mode="auto",
        sources={"akshare": akshare, "yfinance": yfinance},
        universe=_universe(),
        config=_config(),
        symbol_mapping=_mapping(),
        sleep_func=lambda _seconds: None,
    )

    assert akshare.calls == ["510300.SH"]
    assert yfinance.calls == []
    assert result["manifest"]["fallback_source"] == {}
    assert result["manifest"]["source_by_symbol"] == {"510300.SH": "akshare"}


def test_auto_falls_back_to_yfinance_after_akshare_failure(tmp_path: Path) -> None:
    akshare = Source("akshare", fail=True)
    yfinance = Source("yfinance")

    result = fetch_prices(
        "2026-01-01",
        "2026-01-01",
        tmp_path / "out",
        project_paths(tmp_path),
        source_mode="auto",
        sources={"akshare": akshare, "yfinance": yfinance},
        universe=_universe(),
        config=_config(),
        symbol_mapping=_mapping(),
        sleep_func=lambda _seconds: None,
    )

    assert akshare.calls == ["510300.SH"]
    assert yfinance.calls == ["510300.SH"]
    assert result["manifest"]["source_by_symbol"] == {"510300.SH": "yfinance"}
    assert result["manifest"]["fallback_source"] == {"510300.SH": "yfinance"}
    assert "akshare attempt 1" in result["manifest"]["errors_by_symbol"]["510300.SH"][0]


def test_yfinance_bad_rows_are_recorded_without_csv(tmp_path: Path) -> None:
    source = YFinancePriceSource(yf_module=BadYF(), symbol_mapping=_mapping())

    result = fetch_prices(
        "2026-01-01",
        "2026-01-01",
        tmp_path / "out",
        project_paths(tmp_path),
        source_mode="yfinance",
        sources={"yfinance": source},
        universe=_universe(),
        config=_config(),
        symbol_mapping=_mapping(),
        sleep_func=lambda _seconds: None,
    )

    assert result["manifest"]["symbols_success"] == []
    assert result["manifest"]["symbols_failed"] == ["510300.SH"]
    assert "yfinance normalize" in result["manifest"]["errors_by_symbol"]["510300.SH"][-1]
    assert not (tmp_path / "out" / "510300.SH.csv").exists()
    assert result["validation"]["passed"] is False


def test_yfinance_tuple_columns_are_normalized(tmp_path: Path) -> None:
    source = YFinancePriceSource(yf_module=TupleKeyYF(), symbol_mapping=_mapping())

    result = fetch_prices(
        "2026-01-01",
        "2026-01-01",
        tmp_path / "out",
        project_paths(tmp_path),
        source_mode="yfinance",
        sources={"yfinance": source},
        universe=_universe(),
        config=_config(),
        symbol_mapping=_mapping(),
        sleep_func=lambda _seconds: None,
    )

    assert result["manifest"]["symbols_success"] == ["510300.SH"]
    with (tmp_path / "out" / "510300.SH.csv").open("r", encoding="utf-8", newline="") as handle:
        assert list(csv.DictReader(handle))[0]["date"] == "2026-01-01"
