from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths, v19_json
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk


def test_v19_model_explainability_does_not_fabricate_attribution(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    explainability = v19_json(paths, "v19_model_explainability_result")

    assert result["model_explainability_result_generated"] is True
    assert explainability["feature_importance_registry_generated"] is True
    assert explainability["actual_feature_importance_generated"] is False
    assert explainability["feature_importance_unavailable_warning"]
    assert explainability["feature_attribution_fabricated"] is False
    assert explainability["model_explanation_fabricated"] is False
    assert explainability["explanation_becomes_trade_reason"] is False
    assert explainability["explanation_generates_buy_sell_advice"] is False
    assert explainability["owner_report_displays_limitation"] is True
