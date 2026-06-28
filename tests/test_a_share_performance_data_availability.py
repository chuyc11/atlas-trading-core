from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths


def test_performance_data_availability_flags_single_observation(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    result = build_performance_package(paths)
    availability = result["performance_data_availability"]
    assert availability["portfolio_observation_count"] == 1
    assert availability["common_observation_count"] == 1
    assert availability["sufficient_history"] is False
    assert availability["insufficient_history"] is True
