from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths, v19_json
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk


def test_v19_prediction_quality_is_not_order_signal_or_advice(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    prediction = v19_json(paths, "v19_prediction_quality_validation_result")

    assert result["prediction_quality_validation_result_generated"] is True
    assert prediction["prediction_visible_as_of_check"] == "passed"
    assert prediction["prediction_pit_consistency_check"] == "passed"
    assert prediction["prediction_confidence_unavailable_warning"] is True
    assert prediction["predictions_are_trade_signals"] is False
    assert prediction["prediction_enters_orders_path"] is False
    assert prediction["prediction_not_order"] is True
    assert prediction["prediction_not_investment_advice"] is True
    assert prediction["prediction_quality_results_fabricated"] is False
