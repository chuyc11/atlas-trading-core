from __future__ import annotations

from pathlib import Path

from a_share_daily_workflow_test_utils import build_workflow_package, make_workflow_paths


def test_daily_workflow_stage_manifest_ordering(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    result = build_workflow_package(paths)
    stages = result["workflow_stage_manifest"]["stages"]

    assert [stage["stage_id"] for stage in stages] == [
        "stage_00_preflight",
        "stage_01_data_readiness",
        "stage_02_tradable_universe",
        "stage_03_feature_engineering",
        "stage_04_scoring",
        "stage_05_candidate_generation",
        "stage_06_virtual_portfolio_construction",
        "stage_07_daily_briefing",
        "stage_08_virtual_portfolio_tracking",
        "stage_09_workflow_audit",
        "stage_10_owner_summary",
    ]
    assert [stage["stage_order"] for stage in stages] == list(range(11))
    assert all(stage["status"] == "passed" for stage in stages)
    assert all("boundary_flags" in stage for stage in stages)
