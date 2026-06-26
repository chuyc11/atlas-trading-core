"""Reclassify day-1 blockers after v0.6.2.1 authorization materialization."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import MATERIALIZATION_NEXT_REQUIRED_ACTION, MATERIALIZATION_NOTICE, materialization_boundary, materialization_non_claim_markdown, paths_or_default, read_system, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def reclassify_day1_blockers_after_authorization_materialization(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    audit = read_system(paths, "forward_dry_run_authorization_materialization_audit.json")
    passed = audit.get("overall_passed") is True and not audit.get("blocking_reasons")
    technical_count = 0 if passed else 1
    authorization_count = 0 if passed else 1
    payload: dict[str, Any] = {
        "reclassification_id": "DAY1-BLOCKER-RECLASSIFICATION-V0621",
        "technical_day1_blocker_count": technical_count,
        "authorization_blocker_count": authorization_count,
        "updated_day1_blocker_count": technical_count + authorization_count,
        "day1_prompt_eligible": passed,
        "day1_start_allowed": False,
        "recommended_next_action": MATERIALIZATION_NEXT_REQUIRED_ACTION,
        "boundary": materialization_boundary("reclassification_only"),
    }
    return write_artifact(
        system_json(paths, "day1_blocker_reclassification_v0621.json"),
        payload,
        system_report(paths, "DAY1_BLOCKER_RECLASSIFICATION_V0621.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day-1 Blocker Reclassification V0621",
        "",
        MATERIALIZATION_NOTICE,
        "",
        "## Summary",
        f"- technical_day1_blocker_count: {payload['technical_day1_blocker_count']}",
        f"- authorization_blocker_count: {payload['authorization_blocker_count']}",
        f"- updated_day1_blocker_count: {payload['updated_day1_blocker_count']}",
        f"- day1_prompt_eligible: {str(payload['day1_prompt_eligible']).lower()}",
        "- day1_start_allowed: false",
        "- recommended_next_action: owner_requests_day1_prompt",
        "",
        "## Boundary",
        *materialization_non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

