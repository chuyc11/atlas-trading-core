from __future__ import annotations

from pathlib import Path

from a_share_candidate_test_utils import build_candidate_package, candidate_frame, make_candidate_paths, relaxed_candidate_config


def test_mid_candidate_count_sorting_and_explanations(tmp_path: Path) -> None:
    paths = make_candidate_paths(tmp_path)
    build_candidate_package(paths, relaxed_candidate_config(mid_count=2))
    frame = candidate_frame(paths, "mid_candidates_parquet")

    assert len(frame) == 2
    assert frame["MidRank"].tolist() == sorted(frame["MidRank"].tolist())
    assert frame["primary_inclusion_reasons"].astype(str).str.contains("high_mid_percentile").all()
    assert frame["main_risk_reasons"].astype(str).str.len().min() > 0
