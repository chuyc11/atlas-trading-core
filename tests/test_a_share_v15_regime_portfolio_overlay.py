from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v15_market_regime_lab.builder import run_a_share_v15_market_regime_lab


def test_v15_regime_portfolio_overlay_is_simulated_only(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    overlay = v15_json(paths, "v15_regime_portfolio_overlay_result")

    assert result["regime_portfolio_overlay_generated"] is True
    assert overlay["simulated_risk_off_overlay"] is True
    assert overlay["regime_aware_rebalance_blocker"] is True
    assert overlay["regime_overlay_generates_real_allocation"] is False
    assert overlay["regime_overlay_generates_real_rebalance"] is False
    assert overlay["regime_overlay_generates_order_preview"] is False
    assert overlay["regime_overlay_generates_buy_sell_signal"] is False
    assert result["regime_overlay_generates_buy_sell_signal"] is False
