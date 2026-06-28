from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_report, build_attribution_package, make_attribution_paths


def test_attribution_report_generated(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    report = attribution_report(paths, "attribution_summary_report")
    assert "总体结论" in report
    assert "recommended next version" in report
