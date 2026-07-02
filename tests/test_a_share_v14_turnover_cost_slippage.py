from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_turnover_cost_slippage_models_are_simulated(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    turnover = v14_json(paths, "v14_turnover_cost_slippage_result")

    assert result["turnover_cost_slippage_result_generated"] is True
    assert turnover["simulated_turnover_analyzer_generated"] is True
    assert turnover["transaction_cost_model_registry"]["commission_assumption"]
    assert turnover["slippage_model_registry"]["base_slippage_bps"] == 5
    assert len(turnover["cost_sensitivity_grid"]) == 2
    assert turnover["real_fee_claimed"] is False
    assert turnover["real_slippage_claimed"] is False
