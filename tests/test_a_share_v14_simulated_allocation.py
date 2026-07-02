from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_simulated_allocation_layer_and_blockers(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    allocation = v14_json(paths, "v14_simulated_allocation_result")

    assert result["simulated_allocation_result_generated"] is True
    assert result["allocation_is_simulated"] is True
    assert allocation["strategy_allocation_registry"]["quality_template"] == 0.08
    assert allocation["risk_budget_registry"]["max_strategy_weight"] == 0.1
    assert allocation["allocation_eligibility_check_passed"] is False
    assert "capacity_blocker" in allocation["allocation_blocker_register"]
    assert allocation["allocation_points_to_real_account"] is False
