from __future__ import annotations

from pathlib import Path

from a_share_data_refresh_test_utils import build_data_refresh_package, data_refresh_json, make_data_refresh_paths


def test_dataset_refresh_result_passes(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    build_data_refresh_package(paths)
    payload = data_refresh_json(paths, "dataset_refresh_result")
    assert {row["status"] for row in payload["datasets"]} == {"passed"}
