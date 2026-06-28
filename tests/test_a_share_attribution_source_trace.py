from __future__ import annotations

from pathlib import Path

from a_share_attribution_test_utils import attribution_json, build_attribution_package, make_attribution_paths
from trading_core.equity_attribution.attribution_source_trace import forbidden_source_path_hits


def test_attribution_source_trace_complete_and_blocks_forbidden_paths(tmp_path: Path) -> None:
    paths = make_attribution_paths(tmp_path)
    build_attribution_package(paths)
    payload = attribution_json(paths, "attribution_source_trace")
    assert payload["source_trace_complete"] is True
    assert forbidden_source_path_hits([{"path": "tests/fixtures/mock.json"}])
