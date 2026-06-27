from __future__ import annotations

from pathlib import Path

from a_share_candidate_test_utils import build_candidate_package, candidate_frame, make_candidate_paths, relaxed_candidate_config


def test_short_candidate_count_sorting_and_component_highlights(tmp_path: Path) -> None:
    paths = make_candidate_paths(tmp_path)
    build_candidate_package(paths, relaxed_candidate_config(short_count=2))
    frame = candidate_frame(paths, "short_candidates_parquet")

    assert len(frame) == 2
    assert frame["ShortRank"].tolist() == sorted(frame["ShortRank"].tolist())
    assert frame["primary_inclusion_reasons"].astype(str).str.contains("high_short_percentile").all()
    assert frame["component_highlights"].astype(str).str.len().min() > 0
