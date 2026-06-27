from __future__ import annotations

from pathlib import Path

from a_share_score_test_utils import build_score_package, make_score_paths, score_frame


def test_mid_score_range_rank_and_confidence(tmp_path: Path) -> None:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)

    frame = score_frame(paths, "horizon_scores")
    assert frame["MidScore"].between(0, 100).all()
    assert sorted(frame["MidRank"].tolist()) == [1, 2, 3]
    assert frame["MidPercentile"].between(0, 100).all()
    assert frame["MidConfidence"].between(0, 1).all()
