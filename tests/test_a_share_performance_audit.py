from __future__ import annotations

import json
from pathlib import Path

from a_share_performance_test_utils import audit_performance_package, build_performance_package, make_performance_paths, performance_data_dir


def test_performance_audit_passes_after_build(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    build_performance_package(paths)
    audit = audit_performance_package(paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["observation_checks"]["long_virtual_portfolio"] == 1


def test_performance_audit_fails_for_boundary_violation(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    build_performance_package(paths)
    path = performance_data_dir(paths) / "performance_boundary_check.json"
    boundary = json.loads(path.read_text(encoding="utf-8"))
    boundary["real_orders_placed"] = True
    path.write_text(json.dumps(boundary, ensure_ascii=False), encoding="utf-8")
    audit = audit_performance_package(paths)
    assert audit["overall_passed"] is False
    assert any("boundary_fields_clean" in reason for reason in audit["blocking_reasons"])
