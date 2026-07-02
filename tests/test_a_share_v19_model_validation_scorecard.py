from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths, v19_json
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk


def test_v19_model_validation_scorecard_uses_v18_dependencies(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    scorecard = v19_json(paths, "v19_model_validation_scorecard")

    assert result["model_validation_scorecard_generated"] is True
    assert scorecard["source_v18_model_registry_dependency_check"] is True
    assert scorecard["source_v18_model_card_dependency_check"] is True
    assert scorecard["source_v18_prediction_registry_dependency_check"] is True
    assert scorecard["model_validation_used_pit_dataset"] is True
    assert scorecard["model_validation_used_feature_store"] is True
    assert scorecard["model_validation_used_label_store"] is True
    assert scorecard["model_validation_results_fabricated"] is False
    assert scorecard["decision_is_owner_readiness_gate_decision"] is False
