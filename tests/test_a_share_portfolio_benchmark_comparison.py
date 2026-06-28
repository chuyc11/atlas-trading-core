from __future__ import annotations

from pathlib import Path

from a_share_benchmark_test_utils import benchmark_json, build_benchmark_package, make_benchmark_paths


def test_portfolio_benchmark_comparison_flags_limited_history(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    build_benchmark_package(paths)
    comparison = benchmark_json(paths, "portfolio_benchmark_comparison")
    assert comparison["limited_history_correctly_flagged"] is True
    assert comparison["performance_not_fabricated"] is True
    assert len(comparison["comparisons"]) == 18
    assert all(row["comparison_status"] == "limited_history" for row in comparison["comparisons"])
