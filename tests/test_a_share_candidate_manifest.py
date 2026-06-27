from __future__ import annotations

from pathlib import Path

from a_share_candidate_test_utils import build_candidate_package, candidate_json, make_candidate_paths, relaxed_candidate_config
from trading_core.equity_selection.candidate_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def test_candidate_manifest_tracks_counts_and_boundary(tmp_path: Path) -> None:
    paths = make_candidate_paths(tmp_path)
    build_candidate_package(paths, relaxed_candidate_config())
    manifest = candidate_json(paths, "candidate_manifest")

    assert manifest["target_version"] == TARGET_VERSION
    assert manifest["candidate_counts"]["long_candidates"] == 2
    assert manifest["candidate_generation_only"] is True
    assert manifest["virtual_portfolio_generated"] is False
    assert manifest["recommended_next_version"] == RECOMMENDED_NEXT_VERSION
