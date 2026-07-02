from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_pit_sample_split_no_future_data(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    split = v17_json(paths, "v17_pit_sample_split_result")

    assert result["pit_sample_split_result_generated"] is True
    assert split["train_period"]["end"] < split["validation_period"]["start"]
    assert split["validation_period"]["end"] < split["test_period"]["start"]
    assert split["test_period"]["end"] < split["out_of_sample_period"]["start"]
    assert split["no_future_data_split_check"] is True
    assert split["future_data_usage_detected"] is False
    assert split["split_reproducibility_hash"]
