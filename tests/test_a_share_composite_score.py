from __future__ import annotations

from pathlib import Path

from a_share_score_test_utils import build_score_package, make_score_paths, score_frame


def test_composite_score_range_rank_and_inputs(tmp_path: Path) -> None:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)

    frame = score_frame(paths, "composite_scores")
    assert frame["CompositeOpportunityScore"].between(0, 100).all()
    assert sorted(frame["CompositeRank"].tolist()) == [1, 2, 3]
    assert frame["CompositePercentile"].between(0, 100).all()
    assert frame["CompositeConfidence"].between(0, 1).all()
    for column in ["LongScore", "MidScore", "ShortScore", "RiskScore", "LiquidityScore", "IndustryScore", "FundamentalScore"]:
        assert column in frame.columns
