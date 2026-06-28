from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_attribution_data_availability_limited_history(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "attribution_data_availability")
    assert payload["limited_history"] is True
    assert payload["structural_diagnostics_available"] is True
    assert payload["realized_performance_attribution_available"] is False
    assert payload["insufficient_history"] is True
