from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths, v16_json
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules


def test_v16_transaction_cost_slippage_not_fabricated(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    costs = v16_json(paths, "v16_transaction_cost_slippage_result")

    assert result["transaction_cost_slippage_result_generated"] is True
    assert result["transaction_cost_fabricated"] is False
    assert costs["cost_sensitivity_grid_generated"] is True
    assert costs["real_cost_claimed"] is False
