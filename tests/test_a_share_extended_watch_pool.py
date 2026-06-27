from __future__ import annotations

from pathlib import Path

from a_share_candidate_test_utils import build_candidate_package, candidate_frame, make_candidate_paths, relaxed_candidate_config


def test_extended_watch_pool_generation(tmp_path: Path) -> None:
    paths = make_candidate_paths(tmp_path)
    build_candidate_package(paths, relaxed_candidate_config(extended_count=2))
    frame = candidate_frame(paths, "extended_watch_pool_parquet")

    assert len(frame) == 6
    assert set(frame["candidate_horizon"]) == {"ExtendedLong", "ExtendedMid", "ExtendedShort"}
    assert frame["not_order_instruction"].all()
