from __future__ import annotations

from pathlib import Path

from a_share_benchmark_test_utils import benchmark_json, build_benchmark_package, make_benchmark_paths


def test_benchmark_manifest_generated(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    build_benchmark_package(paths)
    manifest = benchmark_json(paths, "benchmark_manifest")
    assert manifest["manifest_id"] == "A-SHARE-BENCHMARK-COMPARISON-MANIFEST"
    assert manifest["first_day_initialization"] is True
    assert manifest["recommended_next_version"] == "v0.7.11-a-share-multi-day-portfolio-performance-tracking"
