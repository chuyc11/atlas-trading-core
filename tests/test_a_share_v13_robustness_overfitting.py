from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v13_research_quality_lab.builder import run_a_share_v13_research_quality_lab


def test_v13_robustness_and_overfit_reviews(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)
    result = run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)

    robustness = v13_json(paths, "v13_robustness_sensitivity_stress_result")
    overfit = v13_json(paths, "v13_overfitting_false_discovery_result")

    assert result["robustness_score_generated"] is True
    assert robustness["robustness_score"] == 61
    assert overfit["overfitting_risk_classified"] is True
    assert overfit["false_discovery_warning_recorded"] is True
    assert "reject_if_oos_fails" in overfit["rejection_or_demotion_rules"]
