"""Revalidate the forward dry-run start gate after owner materialization."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import MATERIALIZATION_NOTICE, materialization_boundary, materialization_non_claim_markdown, passed_without_blockers, paths_or_default, read_system, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def revalidate_forward_dry_run_start_gate_v0621(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    audit = read_system(paths, "forward_dry_run_start_authorization_audit.json")
    completed = read_system(paths, "forward_dry_run_manual_confirmation_checklist_v2_completed.json")
    authorized = read_system(paths, "forward_dry_run_owner_authorization_packet_authorized.json")
    preview = read_system(paths, "forward_dry_run_run_daily_command_preview.json")
    technical_passed = passed_without_blockers(audit)
    manual_complete = completed.get("manual_confirmation_complete") is True
    start_authorized = authorized.get("forward_dry_run_start_authorized") is True
    prompt_eligible = technical_passed and manual_complete and start_authorized
    payload: dict[str, Any] = {
        "gate_id": "FORWARD-DRY-RUN-START-GATE-V0621",
        "technical_prerequisites_passed": technical_passed,
        "manual_confirmation_complete": manual_complete,
        "forward_dry_run_start_authorized": start_authorized,
        "day1_start_allowed": False,
        "day1_prompt_eligible": prompt_eligible,
        "day1_execution_requires_separate_prompt": True,
        "deny_reasons": ["day1_execution_requires_separate_prompt"],
        "run_daily_command_preview": {
            "exists": bool(preview),
            "preview_only": preview.get("preview_only") is True,
            "executed": preview.get("executed") is True,
        },
        "boundary": materialization_boundary("start_gate_revalidation_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_start_gate_v0621.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_START_GATE_V0621.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Start Gate V0621",
        "",
        MATERIALIZATION_NOTICE,
        "",
        "## Gate",
        f"- technical_prerequisites_passed: {str(payload['technical_prerequisites_passed']).lower()}",
        f"- manual_confirmation_complete: {str(payload['manual_confirmation_complete']).lower()}",
        f"- forward_dry_run_start_authorized: {str(payload['forward_dry_run_start_authorized']).lower()}",
        f"- day1_prompt_eligible: {str(payload['day1_prompt_eligible']).lower()}",
        "- day1_start_allowed: false",
        "- deny_reasons: day1_execution_requires_separate_prompt",
        "",
        "## Boundary",
        *materialization_non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

