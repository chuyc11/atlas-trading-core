from __future__ import annotations

from pathlib import Path

from a_share_data_refresh_test_utils import build_data_refresh_package, data_refresh_json, make_data_refresh_paths


def test_data_refresh_manifest_generated(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    build_data_refresh_package(paths)
    payload = data_refresh_json(paths, "data_refresh_manifest")
    assert payload["manifest_id"] == "A-SHARE-DAILY-DATA-REFRESH-MANIFEST"
    assert payload["recommended_next_version"].startswith("v0.8.1")
