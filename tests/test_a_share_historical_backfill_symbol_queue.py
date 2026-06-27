from __future__ import annotations

from pathlib import Path

from a_share_historical_test_utils import make_history_paths
from trading_core.equity_data.full_market_symbol_queue import build_a_share_historical_backfill_symbol_queue


def test_symbol_queue_loads_from_equity_master_not_sample_universe(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    result = build_a_share_historical_backfill_symbol_queue(paths=paths)

    assert result["uses_equity_master_as_source"] is True
    assert result["uses_etf_universe"] is False
    assert result["uses_fixture_universe"] is False
    assert result["queue_total_symbols"] == 6
    assert result["eligible_price_backfill_symbols"] == 4
    assert result["symbols"][0]["symbol"].endswith((".SH", ".SZ"))
