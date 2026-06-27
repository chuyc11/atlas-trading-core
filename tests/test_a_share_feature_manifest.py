from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE, build_feature_package, feature_json, make_feature_paths
from trading_core.equity_features.feature_config import FEATURE_BOUNDARY, TARGET_VERSION


def test_feature_manifest_records_artifacts_and_boundaries(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    manifest = feature_json(paths, "feature_manifest.json")

    assert manifest["target_version"] == TARGET_VERSION
    assert manifest["as_of_date"] == AS_OF_DATE
    assert manifest["strict_tradable_count"] == 3
    assert set(manifest["feature_groups"]) == {"short_horizon", "mid_horizon", "long_horizon", "risk", "liquidity", "industry", "fundamental"}
    assert manifest["boundary"] == FEATURE_BOUNDARY
    assert manifest["scores_generated"] is False
