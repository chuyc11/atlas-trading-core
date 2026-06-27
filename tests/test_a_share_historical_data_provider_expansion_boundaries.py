from __future__ import annotations

from pathlib import Path

from a_share_historical_test_utils import make_history_paths
from trading_core.equity_data.full_market_symbol_queue import build_a_share_historical_backfill_symbol_queue
from trading_core.equity_data_quality.historical_backfill_root_cause import diagnose_a_share_historical_backfill_coverage


def test_provider_expansion_artifacts_preserve_non_trading_boundary(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    queue = build_a_share_historical_backfill_symbol_queue(paths=paths)
    diagnostic = diagnose_a_share_historical_backfill_coverage(paths=paths)

    for payload in [queue, diagnostic]:
        boundary = payload["boundary"]
        assert boundary["scores_generated"] is False
        assert boundary["candidates_generated"] is False
        assert boundary["virtual_portfolio_generated"] is False
        assert boundary["day2_executed"] is False
        assert boundary["run_daily_called"] is False
        assert boundary["broker_connected"] is False
        assert boundary["real_orders_placed"] is False
        assert boundary["model_profit_guaranteed"] is False
