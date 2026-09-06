from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_benchmark_relative_attribution_handles_unavailable_and_equal_weight(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "benchmark_relative_attribution_snapshot")
    csi = [row for row in payload["records"] if row["benchmark_id"] == "CSI300"]
    equal_weight = [row for row in payload["records"] if row["benchmark_id"] == "EQUAL_WEIGHT_CANDIDATE_POOL"]
    assert csi
    assert all(row["benchmark_constituent_exposure_status"] == "unavailable" for row in csi)
    assert equal_weight
    assert all(row["benchmark_constituent_exposure_status"] == "available" for row in equal_weight)
