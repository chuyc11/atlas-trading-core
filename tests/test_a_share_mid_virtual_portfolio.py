from __future__ import annotations

from pathlib import Path

from a_share_virtual_portfolio_test_utils import build_portfolio_package, make_portfolio_paths, portfolio_frame, relaxed_portfolio_config


def test_mid_virtual_portfolio_count_weights_and_sources(tmp_path: Path) -> None:
    paths = make_portfolio_paths(tmp_path)
    build_portfolio_package(paths, relaxed_portfolio_config())
    frame = portfolio_frame(paths, "mid_virtual_portfolio_parquet")

    assert len(frame) == 2
    assert round(float(frame["target_weight"].sum()), 6) == 1.0
    assert set(frame["candidate_source"]) <= {"mid_candidates", "multi_horizon_candidates"}
    assert frame["research_only"].all()

