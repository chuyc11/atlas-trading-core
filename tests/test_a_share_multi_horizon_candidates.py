from __future__ import annotations

from pathlib import Path

from a_share_candidate_test_utils import build_candidate_package, candidate_json, make_candidate_paths, relaxed_candidate_config


def test_multi_horizon_candidate_overlap_detection(tmp_path: Path) -> None:
    paths = make_candidate_paths(tmp_path)
    build_candidate_package(paths, relaxed_candidate_config())
    rows = candidate_json(paths, "multi_horizon_candidates")

    assert rows
    assert {"symbol", "horizon_overlap_type", "best_horizon", "primary_strengths", "risk_notes"}.issubset(rows[0])
    assert rows[0]["candidate_not_investment_advice"] is True
