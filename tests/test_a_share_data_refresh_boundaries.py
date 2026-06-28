from __future__ import annotations

from pathlib import Path

from a_share_data_refresh_test_utils import build_data_refresh_package, data_refresh_json, make_data_refresh_paths
from trading_core.equity_data_refresh.data_refresh_config import FORBIDDEN_POSITIVE_WORDING


def test_data_refresh_boundaries_clean(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    build_data_refresh_package(paths)
    boundary = data_refresh_json(paths, "data_refresh_boundary_check")
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["model_profit_guaranteed"] is False
    assert boundary["live_trading_ready"] is False
    assert boundary["forbidden_wording_positive_hits"] == []
    assert "买入信号" in FORBIDDEN_POSITIVE_WORDING
