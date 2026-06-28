from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths
from trading_core.equity_attribution.attribution_config import FORBIDDEN_POSITIVE_WORDING


def test_attribution_boundaries_clean(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths, mode="multi_day_performance_attribution")
    boundary = attribution_json(paths, "attribution_boundary_check")
    assert boundary["run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["future_data_used"] is False
    assert boundary["historical_performance_fabricated"] is False
    assert boundary["attribution_used_as_trade_signal"] is False
    assert boundary["forbidden_wording_positive_hits"] == []
    assert "买入信号" in FORBIDDEN_POSITIVE_WORDING
