"""Build the v0.6.2 start prerequisite inventory."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import (
    AUTHORIZATION_NOTICE,
    authorization_boundary,
    non_claim_markdown,
    passed_without_blockers,
    paths_or_default,
    read_system,
    system_json,
    system_report,
    write_artifact,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id


def _status_for(payload: dict[str, Any], *, count_key: str | None = None) -> str:
    if count_key is not None:
        return "passed" if int(payload.get(count_key, 1) or 0) == 0 else "blocked"
    return "passed" if passed_without_blockers(payload) else "missing_or_blocked"


def build_forward_dry_run_start_prerequisite_inventory(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    inventory_id, created_at = timestamp_id("FORWARD-DRY-RUN-START-PREREQUISITE-INVENTORY")
    prerequisites = [
        _prerequisite("plan_alignment", _status_for(read_system(paths, "plan_alignment_audit.json")), ["data/system/plan_alignment_audit.json"]),
        _prerequisite("ashare_execution_rules", _status_for(read_system(paths, "ashare_execution_rules_audit.json")), ["data/system/ashare_execution_rules_audit.json"]),
        _prerequisite("baseline_strategy_pack", _status_for(read_system(paths, "baseline_strategy_pack_audit.json")), ["data/system/baseline_strategy_pack_audit.json"]),
        _prerequisite("daily_workflow_binding", _status_for(read_system(paths, "daily_workflow_audit.json")), ["data/system/daily_workflow_audit.json"]),
        _prerequisite("data_quality", _status_for(read_system(paths, "daily_workflow_audit.json")), ["data/daily_workflow/audits/daily_data_quality_audit-2024-12-31.json"]),
        _prerequisite("protected_path_residue", _status_for(read_system(paths, "protected_path_residue_scan.json"), count_key="blocker_count"), ["data/system/protected_path_residue_scan.json"]),
        _prerequisite("manual_confirmation", "pending", ["data/system/forward_dry_run_manual_confirmation_checklist_v2.json"]),
        _prerequisite("owner_authorization", "pending", ["data/system/forward_dry_run_owner_authorization_packet.json"]),
        _prerequisite("run_daily_preview", "pending", ["data/system/forward_dry_run_run_daily_command_preview.json"]),
        _prerequisite("day1_prompt_eligibility", "not_eligible", ["data/system/forward_dry_run_day1_prompt_eligibility.json"]),
    ]
    payload: dict[str, Any] = {
        "inventory_id": inventory_id,
        "created_at": created_at,
        "prerequisites": prerequisites,
        "overall_day1_allowed": False,
        "manual_confirmation_complete": False,
        "forward_dry_run_start_authorized": False,
        "run_daily_called": False,
        "forward_dry_run_started": False,
        "main_ledger_written": False,
        "boundary": authorization_boundary("start_prerequisite_inventory_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_start_prerequisite_inventory.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_START_PREREQUISITE_INVENTORY.md"),
        build_markdown(payload),
    )


def _prerequisite(prerequisite_id: str, status: str, evidence_artifacts: list[str]) -> dict[str, Any]:
    return {
        "prerequisite_id": prerequisite_id,
        "required_before_day1": True,
        "status": status,
        "evidence_artifacts": evidence_artifacts,
        "blocking_if_missing": True,
        "notes": [],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Forward Dry-Run Start Prerequisite Inventory", "", AUTHORIZATION_NOTICE, "", "## Prerequisites"]
    lines.extend(f"- {item['prerequisite_id']}: {item['status']}" for item in payload["prerequisites"])
    lines.extend(["", "## Summary", "- overall_day1_allowed: false", "- authorization remains pending", "", "## Boundary", *non_claim_markdown(), ""])
    return "\n".join(lines)

