from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths, v19_json
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk


def test_v19_research_portfolio_and_strategy_integration_are_not_real_trading(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    portfolio = v19_json(paths, "v19_research_portfolio_model_integration_result")
    integration = v19_json(paths, "v19_candidate_strategy_model_integration_result")

    assert result["research_portfolio_model_integration_result_generated"] is True
    assert portfolio["research_portfolio_is_real_portfolio"] is False
    assert portfolio["research_portfolio_generates_real_allocation"] is False
    assert portfolio["research_portfolio_generates_buy_sell_signal"] is False
    assert portfolio["research_portfolio_simulation_only"] is True
    assert integration["candidate_strategy_model_integration_result_generated"] is True
    assert integration["model_integration_generates_real_trade"] is False
    assert integration["model_auto_replaces_existing_strategy"] is False
    assert integration["candidate_watchlist_is_buy_list"] is False
