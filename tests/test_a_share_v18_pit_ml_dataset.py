from __future__ import annotations

from pathlib import Path

from a_share_v18_test_utils import make_v18_paths, v18_json
from trading_core.equity_v18_research_db_feature_ml_lab.builder import run_a_share_v18_research_db_feature_ml_lab


def test_v18_pit_ml_dataset_blocks_future_features_and_labels(tmp_path: Path) -> None:
    paths = make_v18_paths(tmp_path)
    result = run_a_share_v18_research_db_feature_ml_lab(paths=paths, simulation_only=True)
    dataset = v18_json(paths, "v18_pit_ml_dataset_result")

    assert result["pit_ml_dataset_result_generated"] is True
    assert dataset["pit_aware_ml_dataset_builder_generated"] is True
    assert dataset["pit_cutoff_validation"] == "passed"
    assert dataset["no_future_feature_validation"] == "passed"
    assert dataset["no_future_label_validation"] == "passed"
    assert dataset["train_validation_test_split_generated"] is True
    assert dataset["oos_split_generated"] is True
    assert dataset["walk_forward_split_generated"] is True
    assert dataset["future_data_usage_detected"] is False
    assert dataset["dataset_fabricated"] is False
