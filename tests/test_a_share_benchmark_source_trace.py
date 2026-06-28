from __future__ import annotations

from pathlib import Path

from a_share_benchmark_test_utils import benchmark_json, build_benchmark_package, make_benchmark_paths
from trading_core.equity_benchmarks.benchmark_source_trace import forbidden_source_path_hits


def test_benchmark_source_trace_complete_and_blocks_forbidden_paths(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    build_benchmark_package(paths)
    trace = benchmark_json(paths, "benchmark_source_trace")
    assert trace["source_trace_complete"] is True
    assert trace["forbidden_source_path_hits"] == []
    assert forbidden_source_path_hits([{"path": "tests/fixtures/foo.json"}])
