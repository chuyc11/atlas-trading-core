from __future__ import annotations

from pathlib import Path

from a_share_feature_test_utils import build_feature_package, feature_json, make_feature_paths
from trading_core.equity_features.feature_audit import MANDATORY_FIELD_COVERAGE_THRESHOLDS, SYMBOL_COVERAGE_THRESHOLDS


def test_feature_field_coverage_meets_release_thresholds(tmp_path: Path) -> None:
    paths = make_feature_paths(tmp_path)
    build_feature_package(paths)

    coverage = feature_json(paths, "feature_field_coverage.json")

    for group, item in coverage["groups"].items():
        assert item["symbol_coverage"] >= SYMBOL_COVERAGE_THRESHOLDS[group]
        assert item["mandatory_field_coverage"] >= MANDATORY_FIELD_COVERAGE_THRESHOLDS[group]
