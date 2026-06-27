from __future__ import annotations

from pathlib import Path

from a_share_historical_test_utils import fake_price_provider_result, make_history_paths
from trading_core.equity_data.full_market_symbol_queue import build_a_share_historical_backfill_symbol_queue
from trading_core.equity_data.historical_backfill_scheduler import build_a_share_historical_backfill_symbol_manifest
from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history


def test_symbol_manifest_records_per_symbol_status(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    queue = build_a_share_historical_backfill_symbol_queue(paths=paths)
    backfill_a_share_daily_price_history(
        start_date="2023-01-01",
        end_date="2026-06-26",
        paths=paths,
        provider_result=fake_price_provider_result(symbols=["600000.SH"], periods=260),
    )

    result = build_a_share_historical_backfill_symbol_manifest(paths=paths, queue_rows=queue["symbols"])
    row = next(item for item in result["symbols"] if item["symbol"] == "600000.SH")

    assert row["status"] == "success"
    assert row["has_250d_history"] is True
    assert result["summary"]["symbols_succeeded"] == 1
