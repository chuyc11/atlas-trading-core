from __future__ import annotations

from pathlib import Path

from a_share_virtual_portfolio_tracking_test_utils import build_tracking_package, make_tracking_paths, tracking_json


def test_benchmark_comparison_placeholder_when_index_data_missing(tmp_path: Path) -> None:
    paths = make_tracking_paths(tmp_path)
    build_tracking_package(paths)
    snapshot = tracking_json(paths, "benchmark_comparison_snapshot")

    assert snapshot["benchmarks"] == ["CSI300", "CSI500", "CSI1000", "CASH", "EQUAL_WEIGHT_PORTFOLIO"]
    assert snapshot["benchmark_data_available"] is False
    csi_rows = [row for row in snapshot["records"] if row["benchmark"] in {"CSI300", "CSI500", "CSI1000"}]
    assert csi_rows
    assert all(row["benchmark_return"] is None for row in csi_rows)
    assert all(row["benchmark_data_available"] is False for row in csi_rows)
    assert all(row["benchmark_gap_reason"] for row in csi_rows)
    cash_rows = [row for row in snapshot["records"] if row["benchmark"] == "CASH"]
    assert all(row["benchmark_return"] == 0.0 for row in cash_rows)
    assert all(row["portfolio_return"] == 0.0 for row in snapshot["records"])
