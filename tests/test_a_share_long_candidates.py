from __future__ import annotations

from pathlib import Path

from a_share_candidate_test_utils import build_candidate_package, candidate_frame, make_candidate_paths, relaxed_candidate_config


def test_long_candidate_count_sorting_and_flags(tmp_path: Path) -> None:
    paths = make_candidate_paths(tmp_path)
    build_candidate_package(paths, relaxed_candidate_config(long_count=2))
    frame = candidate_frame(paths, "long_candidates_parquet")

    assert len(frame) == 2
    assert frame["LongRank"].tolist() == sorted(frame["LongRank"].tolist())
    assert frame["candidate_horizon"].tolist() == ["Long", "Long"]
    assert frame["candidate_not_investment_advice"].all()
    assert frame["not_buy_signal"].all()
