from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths, v19_json
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk


def test_v19_model_risk_taxonomy_and_tier_are_research_only(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    risk = v19_json(paths, "v19_model_risk_review_result")

    assert result["model_risk_review_result_generated"] is True
    assert risk["model_risk_taxonomy_generated"] is True
    assert risk["model_risk_tier"] == "high_research_risk"
    assert "real_trading_active" not in risk["allowed_risk_tiers"]
    assert risk["risk_tier_is_live_permission"] is False
    assert risk["model_risk_report_simulation_only"] is True
    assert risk["model_risk_results_fabricated"] is False
