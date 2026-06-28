from __future__ import annotations

from pathlib import Path

from a_share_performance_test_utils import build_performance_package, make_performance_paths
from trading_core.equity_performance.performance_source_trace import forbidden_source_path_hits


def test_performance_source_trace_complete(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    result = build_performance_package(paths)
    trace = result["performance_source_trace"]
    assert trace["source_trace_complete"] is True
    assert trace["forbidden_source_path_hits"] == []


def test_performance_source_trace_blocks_forbidden_paths() -> None:
    hits = forbidden_source_path_hits([{"path": "tests/fixtures/day_002/orders.json"}])
    assert hits
