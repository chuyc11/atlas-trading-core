from __future__ import annotations

from pathlib import Path

from a_share_daily_workflow_test_utils import build_workflow_package, make_workflow_paths, workflow_output_dir
from trading_core.equity_workflows.workflow_audit import audit_a_share_daily_research_workflow


def test_daily_workflow_audit_passes_complete_validate_run(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    build_workflow_package(paths)

    audit = audit_a_share_daily_research_workflow(paths=paths)

    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["stage_counts"]["total"] == 11
    assert audit["stage_counts"]["passed"] == 11
    assert audit["checks"]["upstream_audits_passed"] is True
    assert audit["checks"]["build_timestamp_non_strict_idempotency_recorded"] is True
    assert audit["recommended_next_version"] == "v0.7.10-a-share-benchmark-data-and-performance-comparison"


def test_daily_workflow_audit_blocks_forbidden_positive_wording(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    build_workflow_package(paths)
    report = workflow_output_dir(paths) / "A_SHARE_DAILY_WORKFLOW_SUMMARY.md"
    report.write_text(report.read_text(encoding="utf-8") + "\n推荐买入\n", encoding="utf-8")

    audit = audit_a_share_daily_research_workflow(paths=paths)

    assert audit["overall_passed"] is False
    assert "no_forbidden_positive_wording=false" in audit["blocking_reasons"]
