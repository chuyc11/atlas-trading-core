from __future__ import annotations

from trading_core.equity_data_quality.common import HISTORICAL_BOUNDARY
from trading_core.equity_data_quality.feature_readiness_audit import FORBIDDEN_WORDING


def test_a_share_historical_backfill_boundaries_forbid_trading_claims() -> None:
    assert HISTORICAL_BOUNDARY["scores_generated"] is False
    assert HISTORICAL_BOUNDARY["candidates_generated"] is False
    assert HISTORICAL_BOUNDARY["virtual_portfolio_generated"] is False
    assert HISTORICAL_BOUNDARY["day2_executed"] is False
    assert HISTORICAL_BOUNDARY["run_daily_called"] is False
    assert HISTORICAL_BOUNDARY["broker_connected"] is False
    assert HISTORICAL_BOUNDARY["real_orders_placed"] is False
    assert HISTORICAL_BOUNDARY["model_profit_guaranteed"] is False
    assert HISTORICAL_BOUNDARY["live_trading_ready"] is False
    assert "保证盈利" in FORBIDDEN_WORDING
    assert "live trading ready" in FORBIDDEN_WORDING
