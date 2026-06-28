from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_industry_diagnostics_flags(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "industry_diagnostics_snapshot")
    assert all("unclassified_industry_high" in row["diagnostic_flags"] for row in payload["portfolios"].values())
