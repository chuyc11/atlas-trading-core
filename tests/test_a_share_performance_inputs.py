from __future__ import annotations
import pytest

import json
from pathlib import Path

from a_share_performance_test_utils import make_performance_paths
from trading_core.equity_performance.performance_inputs import load_performance_inputs


def test_performance_inputs_validate_v0710_baseline(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    inputs = load_performance_inputs(paths=paths, as_of_date="2026-06-26")
    assert inputs.audits["benchmark_audit"]["overall_passed"] is True
    assert inputs.benchmark_artifacts["benchmark_data_availability"]["placeholder_benchmarks_used"] == []


def test_performance_inputs_fail_closed_when_benchmark_audit_blocks(tmp_path: Path) -> None:
    paths = make_performance_paths(tmp_path)
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_benchmark_comparison_audit.json"
    payload = json.loads(audit_path.read_text(encoding="utf-8"))
    payload["overall_passed"] = False
    audit_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="benchmark audit overall_passed"):
        load_performance_inputs(paths=paths, as_of_date="2026-06-26")
