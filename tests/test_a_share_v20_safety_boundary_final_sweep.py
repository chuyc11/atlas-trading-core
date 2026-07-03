from __future__ import annotations

from pathlib import Path

from a_share_v20_test_utils import make_v20_paths, v20_json
from trading_core.equity_v20_platform_closeout.builder import run_a_share_v20_platform_closeout


def test_v20_safety_boundary_final_sweep_forbidden_fields(tmp_path: Path) -> None:
    paths = make_v20_paths(tmp_path)
    result = run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    safety = v20_json(paths, "v20_safety_boundary_final_sweep")

    assert result["safety_boundary_final_sweep_generated"] is True
    assert result["safety_boundary_sweep_passed"] is True
    assert safety["safety_boundary_sweep_passed"] is True
    assert result["broker_connected"] is False
    assert result["real_account_data_read"] is False
    assert result["real_orders_placed"] is False
    assert result["real_order_preview_generated"] is False
    assert result["buy_sell_signals_generated"] is False
    assert result["live_trading_ready"] is False
