"""Report day1 prompt eligibility without generating a day1 prompt."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import AUTHORIZATION_NOTICE, authorization_boundary, non_claim_markdown, paths_or_default, read_system, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_forward_dry_run_day1_prompt_eligibility(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    gate = read_system(paths, "forward_dry_run_start_gate_v062.json")
    manual_complete = gate.get("manual_confirmation_complete") is True
    owner_authorized = gate.get("forward_dry_run_start_authorized") is True
    gate_allowed = gate.get("day1_start_allowed") is True
    deny_reasons: list[str] = []
    if not manual_complete:
        deny_reasons.append("manual_confirmation_complete=false")
    if not owner_authorized:
        deny_reasons.append("forward_dry_run_start_authorized=false")
    if not gate_allowed:
        deny_reasons.append("start_gate_day1_start_allowed=false")
    payload: dict[str, Any] = {
        "eligibility_id": "FORWARD-DRY-RUN-DAY1-PROMPT-ELIGIBILITY",
        "day1_prompt_eligible": False if deny_reasons else True,
        "day1_prompt_generated": False,
        "deny_reasons": deny_reasons,
        "next_required_action": "owner_manual_confirmation_and_start_authorization",
        "boundary": authorization_boundary("eligibility_report_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_day1_prompt_eligibility.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_DAY1_PROMPT_ELIGIBILITY.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day1 Prompt Eligibility",
        "",
        AUTHORIZATION_NOTICE,
        "",
        "## Eligibility",
        f"- day1_prompt_eligible: {str(payload['day1_prompt_eligible']).lower()}",
        "- day1_prompt_generated: false",
        f"- deny_reasons: {', '.join(payload['deny_reasons']) if payload['deny_reasons'] else '[]'}",
        "- no day1 prompt file generated",
        "",
        "## Boundary",
        *non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

