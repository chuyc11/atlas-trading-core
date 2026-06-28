from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_liquidity_bucket_contribution_aggregation(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "liquidity_bucket_contribution_snapshot")
    assert all("weighted_average_liquidity_score" in row for row in payload["liquidity_diagnostics"].values())
