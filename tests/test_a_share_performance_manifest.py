from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths


def test_performance_manifest_generated(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    result = build_performance_package(paths)
    manifest = result["performance_manifest"]
    assert manifest["manifest_id"] == "A-SHARE-MULTI-DAY-PERFORMANCE-MANIFEST"
    assert manifest["sufficient_history"] is False
    assert manifest["recommended_next_version"] == "v0.7.12-a-share-performance-attribution-and-risk-diagnostics"
