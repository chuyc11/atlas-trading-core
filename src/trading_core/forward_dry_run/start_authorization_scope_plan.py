"""Build the v0.6.2 forward dry-run start authorization scope plan."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import (
    AUTHORIZATION_NOTICE,
    BASELINE_FROM,
    RELEASE_CANDIDATE,
    authorization_boundary,
    non_claim_markdown,
    paths_or_default,
    read_system,
    system_json,
    system_report,
    write_artifact,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id


SCOPE_COMPONENTS = [
    "start_prerequisite_inventory",
    "current_daily_workflow_readiness_snapshot",
    "manual_confirmation_checklist_v2",
    "owner_authorization_packet",
    "start_gate_validator",
    "run_daily_command_preview_metadata",
    "day1_prompt_eligibility_report",
    "start_authorization_audit",
]


def build_forward_dry_run_authorization_scope_plan(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    plan_id, created_at = timestamp_id("FORWARD-DRY-RUN-AUTHORIZATION-SCOPE-PLAN")
    daily_audit = read_system(paths, "daily_workflow_audit.json")
    v061 = read_system(paths, "day1_blocker_reclassification_v061.json")
    payload: dict[str, Any] = {
        "plan_id": plan_id,
        "created_at": created_at,
        "target_version": RELEASE_CANDIDATE,
        "baseline_from": BASELINE_FROM,
        "daily_workflow_audit_passed": daily_audit.get("overall_passed") is True and not daily_audit.get("blocking_reasons"),
        "known_day1_blockers_closed": int(v061.get("updated_day1_blocker_count", 1) or 0) == 0,
        "start_authorization_pack_required": True,
        "forward_dry_run_day1_allowed": False,
        "scope_components": SCOPE_COMPONENTS,
        "input_artifacts": {
            "daily_workflow_audit": "data/system/daily_workflow_audit.json",
            "day1_blocker_reclassification_v061": "data/system/day1_blocker_reclassification_v061.json",
            "protected_path_residue_scan": "data/system/protected_path_residue_scan.json",
            "baseline_strategy_pack_audit": "data/system/baseline_strategy_pack_audit.json",
            "ashare_execution_rules_audit": "data/system/ashare_execution_rules_audit.json",
            "plan_alignment_audit": "data/system/plan_alignment_audit.json",
        },
        "boundary": authorization_boundary("scope_plan_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_authorization_scope_plan.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_AUTHORIZATION_SCOPE_PLAN.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Authorization Scope Plan",
        "",
        AUTHORIZATION_NOTICE,
        "",
        "## Summary",
        f"- target_version: {payload['target_version']}",
        f"- baseline_from: {payload['baseline_from']}",
        f"- daily_workflow_audit_passed: {str(payload['daily_workflow_audit_passed']).lower()}",
        f"- known_day1_blockers_closed: {str(payload['known_day1_blockers_closed']).lower()}",
        "- forward_dry_run_day1_allowed: false",
        "",
        "## Scope Components",
    ]
    lines.extend(f"- {item}" for item in payload["scope_components"])
    lines.extend(["", "## Boundary", *non_claim_markdown(), ""])
    return "\n".join(lines)

