from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.data.price_acquisition import fetch_prices, should_return_failure
from trading_core.storage.file_paths import project_paths


class FlakySource:
    source_name = "akshare"

    def __init__(self, failures_before_success: dict[str, int]) -> None:
        self.failures_before_success = dict(failures_before_success)
        self.calls: dict[str, int] = {}

    def fetch_daily(self, symbol: str, market: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        self.calls[symbol] = self.calls.get(symbol, 0) + 1
        if self.calls[symbol] <= self.failures_before_success.get(symbol, 0):
            raise RuntimeError(f"temporary failure {self.calls[symbol]}")
        return [{"date": "2026-01-01", "open": 4.0, "high": 4.1, "low": 3.9, "close": 4.05, "volume": 1000}]


def _universe() -> dict[str, Any]:
    return {
        "symbols": [
            {"symbol": "510300.SH", "market": "A_SHARE", "asset_type": "ETF"},
            {"symbol": "159915.SZ", "market": "A_SHARE", "asset_type": "ETF"},
        ]
    }


def _config(max_attempts: int = 3) -> dict[str, Any]:
    return {
        "retry": {"max_attempts": max_attempts, "initial_sleep_seconds": 1, "backoff_multiplier": 2, "jitter_seconds": 0},
        "throttle": {"sleep_between_symbols_seconds": 0.5},
        "failure_policy": {
            "allow_partial_success": True,
            "never_generate_synthetic_prices": True,
            "never_forward_fill_missing_prices": True,
        },
    }


def test_retry_succeeds_on_second_attempt_and_records_manifest(tmp_path: Path) -> None:
    slept: list[float] = []
    source = FlakySource({"510300.SH": 1})

    result = fetch_prices(
        "2026-01-01",
        "2026-01-02",
        tmp_path / "out",
        project_paths(tmp_path),
        source=source,
        universe=_universe(),
        config=_config(),
        sleep_func=slept.append,
        random_func=lambda: 0.0,
    )

    attempts = result["manifest"]["attempts_by_symbol"]["510300.SH"]
    assert [row["status"] for row in attempts] == ["failed", "success"]
    assert attempts[0]["sleep_seconds"] == 1.0
    assert result["manifest"]["symbols_success"] == ["510300.SH", "159915.SZ"]
    assert result["manifest"]["retry_policy"]["max_attempts"] == 3
    assert result["manifest"]["throttle_policy"]["sleep_between_symbols_seconds"] == 0.5
    assert slept == [1.0, 0.5]


def test_all_retries_failed_writes_manifest_and_no_synthetic_csv(tmp_path: Path) -> None:
    result = fetch_prices(
        "2026-01-01",
        "2026-01-02",
        tmp_path / "out",
        project_paths(tmp_path),
        source=FlakySource({"510300.SH": 9, "159915.SZ": 9}),
        universe=_universe(),
        config=_config(max_attempts=2),
        sleep_func=lambda _seconds: None,
        random_func=lambda: 0.0,
    )

    assert result["manifest"]["symbols_success"] == []
    assert result["manifest"]["symbols_failed"] == ["510300.SH", "159915.SZ"]
    assert should_return_failure(result) is True
    assert not (tmp_path / "out" / "510300.SH.csv").exists()
    assert result["validation"]["passed"] is False


def test_single_symbol_failure_does_not_block_other_symbol(tmp_path: Path) -> None:
    result = fetch_prices(
        "2026-01-01",
        "2026-01-02",
        tmp_path / "out",
        project_paths(tmp_path),
        source=FlakySource({"159915.SZ": 9}),
        universe=_universe(),
        config=_config(max_attempts=2),
        sleep_func=lambda _seconds: None,
        random_func=lambda: 0.0,
    )

    assert result["manifest"]["symbols_success"] == ["510300.SH"]
    assert result["manifest"]["symbols_failed"] == ["159915.SZ"]
    assert (tmp_path / "out" / "510300.SH.csv").exists()
    assert not (tmp_path / "out" / "159915.SZ.csv").exists()
    assert "akshare attempt 2" in result["manifest"]["errors_by_symbol"]["159915.SZ"][-1]
