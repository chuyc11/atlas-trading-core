from __future__ import annotations

import json
from pathlib import Path

from a_share_daily_workflow_test_utils import build_workflow_package, make_workflow_paths, workflow_data_dir
from trading_core.equity_workflows.workflow_audit import audit_a_share_daily_research_workflow


def test_daily_workflow_source_trace_complete(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    result = build_workflow_package(paths)
    trace = result["workflow_source_trace"]

    assert trace["source_trace_complete"] is True
    assert trace["forbidden_path_hits"] == []
    assert trace["benchmark_placeholder_deferred_to_v0_7_10"] is True
    assert len(trace["stage_commands"]) == 11


def test_daily_workflow_source_trace_blocks_forbidden_paths(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    build_workflow_package(paths)
    trace_path = workflow_data_dir(paths) / "workflow_source_trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["sources"].append({"path": "external_research/mock/day_002/orders.json", "exists": True, "sha256": "x"})
    trace_path.write_text(json.dumps(trace, ensure_ascii=False), encoding="utf-8")

    audit = audit_a_share_daily_research_workflow(paths=paths)

    assert audit["overall_passed"] is False
    assert "source_trace_has_no_forbidden_paths=false" in audit["blocking_reasons"]
