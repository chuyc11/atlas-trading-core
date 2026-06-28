from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_factor_exposure_weighted_averages(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "factor_exposure_snapshot")
    for row in payload["portfolios"].values():
        assert row["CompositeOpportunityScore"] is not None
        assert row["RiskScore"] is not None
