from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths, v19_json
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk


def test_v19_model_monitoring_records_drift_limitations_without_fabrication(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    monitoring = v19_json(paths, "v19_model_monitoring_drift_result")

    assert result["model_monitoring_drift_result_generated"] is True
    assert monitoring["feature_drift_monitoring"] == "not_available_without_feature_history"
    assert monitoring["prediction_drift_monitoring"] == "not_available_without_prediction_history"
    assert monitoring["model_staleness_monitoring"] == "passed_for_as_of_date"
    assert monitoring["insufficient_data_warning"] is True
    assert monitoring["drift_detection_fabricated"] is False
    assert monitoring["model_monitoring_results_fabricated"] is False
    assert monitoring["external_notification_sent"] is False
