from __future__ import annotations

from pathlib import Path

from a_share_v18_test_utils import make_v18_paths, v18_json
from trading_core.equity_v18_research_db_feature_ml_lab.builder import run_a_share_v18_research_db_feature_ml_lab


def test_v18_model_lab_uses_deterministic_fallback_without_trade_signals(tmp_path: Path) -> None:
    paths = make_v18_paths(tmp_path)
    result = run_a_share_v18_research_db_feature_ml_lab(paths=paths, simulation_only=True)
    lab = v18_json(paths, "v18_model_lab_result")
    training = v18_json(paths, "v18_model_training_evaluation_result")

    assert result["model_lab_result_generated"] is True
    assert lab["deterministic_baseline_model_generated"] is True
    assert lab["deterministic_simple_model_fallback_used"] is True
    assert lab["model_generates_buy_sell_signal"] is False
    assert training["model_training_evaluation_result_generated"] is True
    assert training["model_results_fabricated"] is False
    assert training["oos_results_fabricated"] is False
