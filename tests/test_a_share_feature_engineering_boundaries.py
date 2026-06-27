from __future__ import annotations

import json
from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE, build_feature_package, feature_frame, make_feature_paths
from trading_core.equity_features.feature_audit import FORBIDDEN_POSITIVE_WORDING, audit_a_share_multi_horizon_features
from trading_core.equity_features.feature_config import FEATURE_BOUNDARY


def test_feature_engineering_boundaries_block_scores_candidates_portfolios_and_live_claims(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    result = build_feature_package(paths)

    assert result["boundary"] == FEATURE_BOUNDARY
    for group in ["short_horizon", "mid_horizon", "long_horizon", "risk", "liquidity", "fundamental"]:
        frame = feature_frame(paths, group)
        assert not any("score" in column.lower() or "rank" in column.lower() or "signal" in column.lower() for column in frame.columns)
    assert '"live_trading_ready": true' in FORBIDDEN_POSITIVE_WORDING

    manifest_path = paths.data_dir / "equity_features" / "daily" / AS_OF_DATE / "feature_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["boundary"]["live_trading_ready"] = True
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    audit = audit_a_share_multi_horizon_features(paths=paths, as_of_date=AS_OF_DATE, minimum_strict_count=1)
    assert audit["overall_passed"] is False
    assert "boundary_live_trading_ready_false=false" in audit["blocking_reasons"]
    assert audit["forbidden_wording_hits"]
