from __future__ import annotations

from pathlib import Path

from a_share_data_refresh_test_utils import build_data_refresh_package, data_refresh_json, make_data_refresh_paths
from trading_core.equity_data_refresh.data_refresh_source_trace import forbidden_source_path_hits


def test_data_refresh_source_trace_complete_and_blocks_forbidden_paths(tmp_path: Path) -> None:
    paths = make_data_refresh_paths(tmp_path)
    build_data_refresh_package(paths)
    payload = data_refresh_json(paths, "data_refresh_source_trace")
    assert payload["source_trace_complete"] is True
    assert forbidden_source_path_hits([{"path": "data/orders/example.json"}])
