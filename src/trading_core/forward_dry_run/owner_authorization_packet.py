"""Build a fail-closed owner authorization packet."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import AUTHORIZATION_NOTICE, REQUIRED_PHRASE, authorization_boundary, non_claim_markdown, paths_or_default, system_json, system_report, write_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_forward_dry_run_owner_authorization_packet(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    payload: dict[str, Any] = {
        "authorization_packet_id": "FORWARD-DRY-RUN-OWNER-AUTHORIZATION-PACKET",
        "authorization_status": "not_authorized",
        "forward_dry_run_start_authorized": False,
        "owner_must_edit_or_confirm": True,
        "authorized_by": None,
        "authorized_at": None,
        "authorization_phrase_required": REQUIRED_PHRASE,
        "day1_start_allowed": False,
        "boundary": authorization_boundary("authorization_packet_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_owner_authorization_packet.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_OWNER_AUTHORIZATION_PACKET.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Owner Authorization Packet",
        "",
        AUTHORIZATION_NOTICE,
        "",
        "## Authorization",
        "- authorization_status: not_authorized",
        "- forward_dry_run_start_authorized=false",
        "- day1_start_allowed=false",
        f"- future required phrase: {payload['authorization_phrase_required']}",
        "",
        "## Boundary",
        *non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

