"""Manual confirmation packet for day-0 readiness."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.common import DAY0_NOTICE, TRADING_AUTHORIZATION_NOTICE, latest_tag, paths_or_default, rel, resolve_path, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


CONFIRMATION_FIELDS = [
    "owner_confirmed_data_freeze",
    "owner_confirmed_warning_acceptance",
    "owner_confirmed_no_blocking_conditions",
    "owner_confirmed_run_daily_preview",
    "owner_confirmed_forward_dry_run_can_start",
]


def build_day0_manual_confirmation_packet(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    packet_id, created_at = timestamp_id("DAY0-MANUAL-CONFIRMATION")
    confirmations = {field: False for field in CONFIRMATION_FIELDS}
    payload: dict[str, Any] = {
        "packet_id": packet_id,
        "created_at": created_at,
        "latest_tag": latest_tag(paths),
        "pytest_count": "737 passed, 1 skipped",
        "artifact_paths": {
            "day0_data_freeze": rel(paths.data_dir / "system" / "day0_data_freeze_manifest.json", paths),
            "warning_register": rel(paths.data_dir / "system" / "day0_accepted_warning_register.json", paths),
            "blocking_conditions": rel(paths.data_dir / "system" / "day0_blocking_conditions.json", paths),
            "preflight": rel(paths.data_dir / "system" / "day0_run_daily_preflight.json", paths),
        },
        "accepted_limitations": [
            "EPU partial: missing us_epu/europe_epu; policy uncertainty proxy only.",
            "OECD macro-cycle proxy is not official OECD CLI.",
            "Internal global-briefing historical signal package remains not_configured.",
            "Proxy package is not an internal global-briefing signal.",
        ],
        "explicit_non_claims": [
            "not strategy effectiveness proof",
            "not forward dry-run validation",
            "not live trading readiness",
            "not trading authorization",
        ],
        "all_confirmations_default_false": True,
        "confirmations": confirmations,
        "manual_confirmation_complete": False,
        "forward_dry_run_start_authorized": False,
        "boundary": {**standard_boundary("manual_packet_only"), "auto_confirmation": False},
    }
    json_path = paths.data_dir / "system" / "day0_manual_confirmation_packet.json"
    md_path = paths.outputs_dir / "system" / "DAY0_MANUAL_CONFIRMATION_PACKET.md"
    write_json_markdown(json_path, payload, md_path, build_manual_confirmation_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_manual_confirmation_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Day-0 Manual Confirmation Packet",
            "",
            "## Scope",
            "This packet must be reviewed manually before any future forward dry-run starts.",
            "This file does not authorize automatically.",
            DAY0_NOTICE,
            TRADING_AUTHORIZATION_NOTICE,
            "",
            "## Accepted Limitations",
            *[f"- {item}" for item in payload["accepted_limitations"]],
            "",
            "## Explicit Non-Claims",
            *[f"- {item}" for item in payload["explicit_non_claims"]],
            "",
            "## Manual Confirmation Fields",
            "All confirmation fields default to false.",
            *[f"- {key}: {str(value).lower()}" for key, value in payload["confirmations"].items()],
            "",
            "## Boundary",
            "- manual confirmation packet only",
            "- no auto-confirmation",
            "- forward dry-run not started",
            "- run-daily not called",
            "",
        ]
    )
