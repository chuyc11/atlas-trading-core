from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths, v19_json
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk


def test_v19_model_robustness_and_overfitting_review(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    robustness = v19_json(paths, "v19_model_robustness_validation_result")
    overfit = v19_json(paths, "v19_model_overfitting_false_discovery_result")

    assert result["model_robustness_validation_result_generated"] is True
    assert robustness["deterministic_fallback_robustness_check"] == "passed"
    assert robustness["robustness_pass_fabricated"] is False
    assert robustness["unsupported_robustness_limitations_recorded"] is True
    assert overfit["model_overfitting_false_discovery_result_generated"] is True
    assert overfit["multiple_testing_warning"] is True
    assert overfit["data_snooping_warning"] is True
    assert overfit["statistical_significance_fabricated"] is False
    assert overfit["placeholder_used_as_real_conclusion"] is False
