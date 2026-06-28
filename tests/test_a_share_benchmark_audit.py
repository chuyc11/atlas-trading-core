from __future__ import annotations

import json
from pathlib import Path

from a_share_benchmark_test_utils import audit_benchmark_package, benchmark_json, build_benchmark_package, make_benchmark_paths


def test_benchmark_audit_passes_after_build(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    build_benchmark_package(paths)
    audit = audit_benchmark_package(paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["benchmark_availability_checks"]["CSI300"] == "available"


def test_benchmark_audit_fails_for_forbidden_boundary_flag(tmp_path: Path) -> None:
    paths = make_benchmark_paths(tmp_path)
    build_benchmark_package(paths)
    boundary = benchmark_json(paths, "benchmark_boundary_check")
    boundary["broker_connected"] = True
    path = paths.data_dir / "equity_benchmarks" / "daily" / "2026-06-26" / "benchmark_boundary_check.json"
    path.write_text(json.dumps(boundary, ensure_ascii=False), encoding="utf-8")
    audit = audit_benchmark_package(paths)
    assert audit["overall_passed"] is False
