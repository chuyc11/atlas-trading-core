from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_liquidity_diagnostics_flags(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "liquidity_diagnostics_snapshot")
    assert all(row["top_illiquidity_contributors"] for row in payload["portfolios"].values())
