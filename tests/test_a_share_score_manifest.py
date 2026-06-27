from __future__ import annotations

from pathlib import Path

from a_share_score_test_utils import build_score_package, make_score_paths, score_json
from trading_core.equity_scoring.score_config import RECOMMENDED_NEXT_VERSION, SCORE_BOUNDARY, SCORE_COLUMNS, TARGET_VERSION


def test_score_manifest_tracks_artifacts_ranges_and_boundary(tmp_path: Path) -> None:
    paths = make_score_paths(tmp_path)
    build_score_package(paths)

    manifest = score_json(paths, "score_manifest")
    assert manifest["target_version"] == TARGET_VERSION
    assert manifest["strict_tradable_count"] == 3
    assert manifest["no_future_leakage"] is True
    assert manifest["boundary"] == SCORE_BOUNDARY
    assert manifest["recommended_next_version"] == RECOMMENDED_NEXT_VERSION
    assert set(SCORE_COLUMNS).issubset(manifest["score_ranges"])
    assert all(record["exists"] for record in manifest["score_artifacts"].values())
