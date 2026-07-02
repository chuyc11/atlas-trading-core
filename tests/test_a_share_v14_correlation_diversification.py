from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_correlation_diversification_does_not_fabricate_history(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    correlation = v14_json(paths, "v14_correlation_diversification_result")

    assert result["correlation_diversification_result_generated"] is True
    assert correlation["simulated_strategy_return_series_registry_generated"] is True
    assert correlation["strategy_correlation_matrix"]["quality_template"]["quality_template"] == 1.0
    assert correlation["strategy_correlation_matrix"]["quality_template"]["risk_template"] is None
    assert correlation["insufficient_correlation_history_warning"] is True
    assert correlation["no_fabricated_correlation"] is True
    assert correlation["no_fabricated_covariance"] is True
    assert correlation["diversification_score"] == 58
