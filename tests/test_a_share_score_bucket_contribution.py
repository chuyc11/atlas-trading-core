from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_score_bucket_contribution_aggregation(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "score_bucket_contribution_snapshot")
    assert "CompositeOpportunityScore" in payload["score_types"]
    assert all(len(rows) == 5 for rows in payload["portfolios"].values())
