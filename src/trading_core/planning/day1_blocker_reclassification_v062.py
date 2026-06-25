"""Reclassify day-1 blockers after v0.6.2 start authorization pack creation."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import AUTHORIZATION_NOTICE, NEXT_REQUIRED_ACTION, authorization_boundary, non_claim_markdown, paths_or_default, read_system, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def reclassify_day1_blockers_after_start_authorization(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    audit = read_system(paths, "forward_dry_run_start_authorization_audit.json")
    technical_count = 0 if audit.get("overall_passed") is True and not audit.get("blocking_reasons") else 1
    authorization_blockers = ["manual_confirmation_complete=false", "forward_dry_run_start_authorized=false"]
    payload: dict[str, Any] = {
        "reclassification_id": "DAY1-BLOCKER-RECLASSIFICATION-V062",
        "technical_day1_blocker_count": technical_count,
        "authorization_blocker_count": len(authorization_blockers),
        "authorization_blockers": authorization_blockers,
        "updated_day1_blocker_count": technical_count + len(authorization_blockers),
        "day1_start_allowed": False,
        "recommended_next_action": NEXT_REQUIRED_ACTION,
        "boundary": authorization_boundary("reclassification_only"),
    }
    return write_artifact(
        system_json(paths, "day1_blocker_reclassification_v062.json"),
        payload,
        system_report(paths, "DAY1_BLOCKER_RECLASSIFICATION_V062.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Day-1 Blocker Reclassification V062",
        "",
        AUTHORIZATION_NOTICE,
        "",
        "## Summary",
        f"- technical_day1_blocker_count: {payload['technical_day1_blocker_count']}",
        f"- authorization_blocker_count: {payload['authorization_blocker_count']}",
        f"- updated_day1_blocker_count: {payload['updated_day1_blocker_count']}",
        "- day1_start_allowed=false",
        "- recommended_next_action: owner_manual_confirmation",
        "",
        "## Authorization Blockers",
    ]
    lines.extend(f"- {item}" for item in payload["authorization_blockers"])
    lines.extend(["", "## Boundary", *non_claim_markdown(), ""])
    return "\n".join(lines)

