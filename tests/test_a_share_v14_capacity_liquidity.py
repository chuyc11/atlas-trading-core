from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_capacity_liquidity_is_simulated_with_disclaimer(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    capacity = v14_json(paths, "v14_capacity_liquidity_result")

    assert result["capacity_liquidity_result_generated"] is True
    assert result["capacity_estimate_is_simulated"] is True
    assert result["liquidity_estimate_is_simulated"] is True
    assert capacity["liquidity_scorecard_generated"] is True
    assert capacity["missing_liquidity_data_warning"] is True
    assert capacity["capacity_blocker"] is True
    assert "simulation estimates only" in capacity["disclaimer"]
    assert capacity["real_tradable_capacity_claimed"] is False
