from __future__ import annotations

from pathlib import Path

from a_share_benchmark_test_utils import benchmark_report, build_benchmark_package, make_benchmark_paths


def test_benchmark_reports_generated_without_forbidden_positive_wording(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    build_benchmark_package(paths)
    summary = benchmark_report(paths, "benchmark_summary_report")
    comparison = benchmark_report(paths, "portfolio_benchmark_comparison_report")
    assert "Benchmark Availability" in summary
    assert "limited_history" in comparison
    for phrase in ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪"]:
        assert phrase not in summary
