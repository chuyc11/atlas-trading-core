from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE, build_feature_package, make_feature_paths
from trading_core.equity_features.feature_audit import audit_a_share_multi_horizon_features


def test_multi_horizon_feature_audit_passes_and_fails_closed_for_missing_manifest(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    result = audit_a_share_multi_horizon_features(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)

    assert result["overall_passed"] is True
    assert result["counts"]["strict_tradable_count"] == 3
    assert result["recommended_next_version"] == "v0.7.4-a-share-long-mid-short-scoring-system"

    (paths.data_dir / "equity_features" / "daily" / AS_OF_DATE / "feature_manifest.json").unlink()
    failed = audit_a_share_multi_horizon_features(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert failed["overall_passed"] is False
    assert "feature_manifest_exists=false" in failed["blocking_reasons"]
