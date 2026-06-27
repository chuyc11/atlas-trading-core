from __future__ import annotations

from pathlib import Path

from a_share_virtual_portfolio_test_utils import build_portfolio_package, make_portfolio_paths, portfolio_frame, relaxed_portfolio_config


def test_short_virtual_portfolio_count_weights_and_notes(tmp_path: Path) -> None:
    paths = make_portfolio_paths(tmp_path)
    build_portfolio_package(paths, relaxed_portfolio_config())
    frame = portfolio_frame(paths, "short_virtual_portfolio_parquet")

    assert len(frame) == 2
    assert round(float(frame["target_weight"].sum()), 6) == 1.0
    assert "overheat_risk_notes" in frame.columns
    assert "liquidity_risk_notes" in frame.columns
    assert "short_horizon_validity_notes" in frame.columns

