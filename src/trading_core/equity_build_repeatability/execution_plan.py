"""Repeat build execution plan."""

from __future__ import annotations

from trading_core.equity_build_repeatability.repeatability_config import (
    FORBIDDEN_COMMAND_FRAGMENTS,
    REPEATABILITY_BOUNDARY,
    TARGET_VERSION,
    WORKFLOW_COMMAND_TEMPLATE,
)


def build_repeat_build_execution_plan(*, as_of_date: str) -> dict:
    command = WORKFLOW_COMMAND_TEMPLATE.format(as_of_date=as_of_date)
    normalized = command.lower()
    hits = [frag for frag in FORBIDDEN_COMMAND_FRAGMENTS if frag in normalized]
    return {
        "plan_id": "A-SHARE-REPEAT-BUILD-FROM-EXISTING-DATA-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "workflow_mode": "build_from_existing_data",
        "command": command,
        "workflow_command": command,
        "command_allowed": not hits,
        "forbidden_command_fragments_present": hits,
        "expected_boundary": dict(REPEATABILITY_BOUNDARY),
        "expected_outputs": [
            "repeat_build_execution_record",
            "repeat_build_workflow_result",
            "second_build_artifact_snapshot",
            "build_vs_build_comparison",
        ],
        "expected_audits": ["a_share_current_day_research_run_audit", "a_share_build_repeatability_audit"],
    }

