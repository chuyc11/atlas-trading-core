from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths


def test_holding_mark_to_market_math_and_forbidden_fields(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    result = build_performance_package(paths)
    series = result["holding_mark_to_market_series"]
    assert series["forbidden_fields_present"] == []
    first = series["records"][0]
    assert abs(first["virtual_shares"] * first["mark_price"] - first["position_value"]) < 1e-4
    assert "order_id" not in first
    assert "buy_signal" not in first
