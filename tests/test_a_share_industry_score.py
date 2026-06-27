from __future__ import annotations

from pathlib import Path

from a_share_score_test_utils import build_score_package, make_score_paths, score_frame


def test_industry_score_range_and_confidence(tmp_path: Path) -> None:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)

    frame = score_frame(paths, "risk_liquidity_industry_fundamental_scores")
    assert frame["IndustryScore"].between(0, 100).all()
    assert frame["industry_percentile"].between(0, 100).all()
    assert frame["industry_confidence"].between(0, 1).all()
    assert set(frame["industry_level_1"]) == {"Finance", "Industrial"}
