from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths, v16_json
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules


def test_v16_point_in_time_registry_and_versions(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    pit = v16_json(paths, "v16_point_in_time_data_registry")
    versions = v16_json(paths, "v16_dataset_feature_label_version_registry")

    assert result["point_in_time_data_registry_generated"] is True
    assert pit["point_in_time_visibility_fabricated"] is False
    assert pit["future_visibility_blocked"] is True
    assert versions["dataset_feature_label_version_registry_generated"] is True
    assert versions["label_visibility_guard"] is True
