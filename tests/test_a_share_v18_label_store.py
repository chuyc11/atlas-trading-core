from __future__ import annotations

from pathlib import Path

from a_share_v18_test_utils import make_v18_paths, v18_json
from trading_core.equity_v18_research_db_feature_ml_lab.builder import run_a_share_v18_research_db_feature_ml_lab


def test_v18_label_store_horizon_and_leakage_guard(tmp_path: Path) -> None:
    paths = make_v18_paths(tmp_path)
    result = run_a_share_v18_research_db_feature_ml_lab(paths=paths, simulation_only=True)
    label = v18_json(paths, "v18_label_store_result")

    assert result["label_store_result_generated"] is True
    assert label["label_definition_registry_generated"] is True
    assert label["label_horizon_registry_generated"] is True
    assert label["label_leakage_guard"] == "passed"
    assert label["label_store_leakage_checked"] is True
    assert label["label_horizon_mismatch_blocker"] is False
    assert label["future_label_used_for_current_model"] is False
    assert label["label_matrix_fabricated"] is False
