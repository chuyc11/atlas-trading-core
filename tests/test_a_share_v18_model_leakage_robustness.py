from __future__ import annotations

from pathlib import Path

from a_share_v18_test_utils import make_v18_paths, v18_json
from trading_core.equity_v18_research_db_feature_ml_lab.builder import run_a_share_v18_research_db_feature_ml_lab


def test_v18_model_leakage_and_robustness_guards(tmp_path: Path) -> None:
    paths = make_v18_paths(tmp_path)
    result = run_a_share_v18_research_db_feature_ml_lab(paths=paths, simulation_only=True)
    leakage = v18_json(paths, "v18_model_leakage_robustness_result")

    assert result["model_leakage_robustness_result_generated"] is True
    assert leakage["model_leakage_guard_passed"] is True
    assert leakage["feature_timestamp_guard_for_model"] == "passed"
    assert leakage["label_timestamp_guard_for_model"] == "passed"
    assert leakage["training_test_contamination_check"] == "passed"
    assert leakage["duplicate_row_leakage_check"] == "passed"
    assert leakage["look_ahead_leakage_blocker"] is False
    assert leakage["future_data_usage_detected"] is False
