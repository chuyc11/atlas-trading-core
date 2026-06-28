from __future__ import annotations

from pathlib import Path

from a_share_data_refresh_test_utils import build_data_refresh_package, data_refresh_report, make_data_refresh_paths


def test_data_refresh_report_generated(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    build_data_refresh_package(paths)
    report = data_refresh_report(paths, "data_refresh_summary_report")
    assert "总体结论" in report
    assert "recommended next version" in report
