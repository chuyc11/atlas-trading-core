from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths


def test_attribution_manifest_generated(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "attribution_manifest")
    assert payload["manifest_id"] == "A-SHARE-PERFORMANCE-ATTRIBUTION-MANIFEST"
    assert payload["recommended_next_version"].startswith("v0.8.0")
