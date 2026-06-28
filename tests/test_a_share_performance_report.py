from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths, performance_report


def test_performance_reports_generated(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    build_performance_package(paths)
    report = performance_report(paths, "performance_summary_report")
    assert "A Share Multi-Day Performance Summary" in report
    assert "first_day_initialization: true" in report
    assert "Recommended next version" in report
