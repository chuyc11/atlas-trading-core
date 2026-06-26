"""Create the v0.6.2.1 authorized owner packet for day1 prompt generation."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import MATERIALIZATION_NOTICE, materialization_non_claim_markdown, paths_or_default, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def update_forward_dry_run_owner_authorization_packet(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    payload: dict[str, Any] = {
        "authorization_packet_id": "FORWARD-DRY-RUN-OWNER-AUTHORIZATION-PACKET-AUTHORIZED",
        "source_packet": "data/system/forward_dry_run_owner_authorization_packet.json",
        "authorization_status": "authorized_for_day1_prompt_generation",
        "forward_dry_run_start_authorized": True,
        "day1_execution_authorized": False,
        "day1_execution_requires_separate_prompt": True,
        "authorized_scope": "day1_prompt_generation_only",
        "boundary": {
            "authorization_packet_only": True,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "main_ledger_written": False,
        },
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_owner_authorization_packet_authorized.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_OWNER_AUTHORIZATION_PACKET_AUTHORIZED.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Owner Authorization Packet Authorized",
        "",
        MATERIALIZATION_NOTICE,
        "",
        "## Authorization",
        "- authorization_status: authorized_for_day1_prompt_generation",
        "- forward_dry_run_start_authorized: true",
        "- day1_execution_authorized: false",
        "- day1_execution_requires_separate_prompt: true",
        "- authorized_scope: day1_prompt_generation_only",
        "",
        "## Boundary",
        *materialization_non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

