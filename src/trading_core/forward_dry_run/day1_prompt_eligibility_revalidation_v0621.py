"""Revalidate day1 prompt eligibility without generating a day1 prompt."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import MATERIALIZATION_NEXT_REQUIRED_ACTION, MATERIALIZATION_NOTICE, materialization_boundary, materialization_non_claim_markdown, paths_or_default, read_system, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def revalidate_forward_dry_run_day1_prompt_eligibility(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    gate = read_system(paths, "forward_dry_run_start_gate_v0621.json")
    payload: dict[str, Any] = {
        "eligibility_id": "FORWARD-DRY-RUN-DAY1-PROMPT-ELIGIBILITY-V0621",
        "day1_prompt_eligible": gate.get("day1_prompt_eligible") is True,
        "day1_prompt_generated": False,
        "day1_execution_requires_separate_prompt": True,
        "next_required_action": MATERIALIZATION_NEXT_REQUIRED_ACTION,
        "boundary": materialization_boundary("eligibility_revalidation_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_day1_prompt_eligibility_v0621.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_DAY1_PROMPT_ELIGIBILITY_V0621.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day1 Prompt Eligibility V0621",
        "",
        MATERIALIZATION_NOTICE,
        "",
        "## Eligibility",
        f"- day1_prompt_eligible: {str(payload['day1_prompt_eligible']).lower()}",
        "- day1_prompt_generated: false",
        "- day1_execution_requires_separate_prompt: true",
        "- next_required_action: owner_requests_day1_prompt",
        "",
        "## Boundary",
        *materialization_non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

