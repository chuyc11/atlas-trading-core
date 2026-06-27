from __future__ import annotations

import json
from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE, build_feature_package, make_feature_paths
from trading_core.equity_features.feature_audit import audit_a_share_multi_horizon_features


def test_feature_audit_blocks_future_source_dates(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    manifest_path = paths.data_dir / "equity_features" / "daily" / AS_OF_DATE / "feature_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_dates"]["max_price_date_used"] = "2026-06-29"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = audit_a_share_multi_horizon_features(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)

    assert result["overall_passed"] is False
    assert "no_future_leakage=false" in result["blocking_reasons"]
    assert result["no_future_leakage"]["future_dates"]["max_price_date_used"] == "2026-06-29"
