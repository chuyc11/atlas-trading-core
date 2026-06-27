from __future__ import annotations

from pathlib import Path

from a_share_score_test_utils import build_score_package, make_score_paths, score_frame


def test_liquidity_score_range_and_confidence(tmp_path: Path) -> None:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)

    frame = score_frame(paths, "risk_liquidity_industry_fundamental_scores")
    assert frame["LiquidityScore"].between(0, 100).all()
    assert frame["liquidity_percentile"].between(0, 100).all()
    assert frame["liquidity_confidence"].between(0, 1).all()
    assert "liquidity_component_breakdown" in frame.columns
