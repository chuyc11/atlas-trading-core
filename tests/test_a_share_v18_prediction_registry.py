from __future__ import annotations

from pathlib import Path

from a_share_v18_test_utils import make_v18_paths, v18_json
from trading_core.equity_v18_research_db_feature_ml_lab.builder import run_a_share_v18_research_db_feature_ml_lab


def test_v18_prediction_registry_is_not_order_or_signal(tmp_path: Path) -> None:
    paths = make_v18_paths(tmp_path)
    result = run_a_share_v18_research_db_feature_ml_lab(paths=paths, simulation_only=True)
    predictions = v18_json(paths, "v18_prediction_registry")

    assert result["prediction_registry_generated"] is True
    assert predictions["prediction_not_trade_signal"] is True
    assert predictions["prediction_not_investment_advice"] is True
    assert predictions["prediction_not_order"] is True
    assert predictions["predictions_are_trade_signals"] is False
    assert predictions["prediction_enters_orders_path"] is False
    assert predictions["prediction_results_fabricated"] is False
