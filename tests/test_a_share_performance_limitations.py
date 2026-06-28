from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths


def test_performance_limitations_state_first_day_is_not_performance(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    result = build_performance_package(paths)
    limitations = result["performance_limitations"]
    assert limitations["first_day_initialization"] is True
    assert limitations["performance_not_yet_observed"] is True
    assert any("First-day initialization" in item for item in limitations["limitations"])
