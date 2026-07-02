from __future__ import annotations

from pathlib import Path

from a_share_v18_test_utils import make_v18_paths, v18_json
from trading_core.equity_v18_research_db_feature_ml_lab.builder import run_a_share_v18_research_db_feature_ml_lab


def test_v18_feature_store_pit_validation_and_leakage_flag(tmp_path: Path) -> None:
    paths = make_v18_paths(tmp_path)
    result = run_a_share_v18_research_db_feature_ml_lab(paths=paths, simulation_only=True)
    feature = v18_json(paths, "v18_feature_store_result")

    assert result["feature_store_result_generated"] is True
    assert feature["feature_definition_registry_generated"] is True
    assert feature["feature_group_registry_generated"] is True
    assert feature["feature_store_pit_validated"] is True
    assert feature["feature_leakage_risk_flag"] is False
    assert feature["feature_matrix_fabricated"] is False
    assert feature["feature_usage_count"] == 3
