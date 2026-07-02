from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_simulated_rebalance_is_not_real_order_or_signal(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    rebalance = v14_json(paths, "v14_simulated_rebalance_plan")

    assert result["simulated_rebalance_plan_generated"] is True
    assert result["rebalance_plan_is_simulated"] is True
    assert rebalance["simulated_rebalance_intent_generated"] is True
    assert rebalance["rebalance_intent_is_not_real_order"] is True
    assert rebalance["rebalance_does_not_create_order_preview"] is True
    assert rebalance["rebalance_does_not_create_buy_sell_signal"] is True
    assert result["real_rebalance_instruction_generated"] is False
    assert result["real_order_preview_generated"] is False
    assert result["buy_sell_signals_generated"] is False
