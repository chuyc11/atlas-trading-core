from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths, v22_json
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_model_and_factor_ensembles_are_research_scores_only(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    model = v22_json(paths, "v22_model_ensemble_result")
    factor = v22_json(paths, "v22_factor_ensemble_result")

    assert result["model_ensemble_result_generated"] is True
    assert result["factor_ensemble_result_generated"] is True
    assert model["model_ensemble_score_is_buy_sell_signal"] is False
    assert factor["factor_ensemble_generates_investment_advice"] is False
    assert factor["factor_ensemble_generates_buy_sell_signal"] is False
    assert result["ensemble_results_fabricated"] is False
