"""Global-briefing macro signal contract artifact generation."""

from __future__ import annotations

from typing import Any

from trading_core.global_briefing.signal_schema import CONTRACT_ID, CONTRACT_VERSION, REQUIRED_FIELDS, SUPPORTED_FORMATS
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


def build_signal_contract(paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    payload: dict[str, Any] = {
        "contract_id": CONTRACT_ID,
        "version": CONTRACT_VERSION,
        "required_fields": list(REQUIRED_FIELDS),
        "supported_formats": list(SUPPORTED_FORMATS),
        "point_in_time_rules": [
            "Only signals generated at or before the replay decision timestamp may be used.",
            "Future macro signals must be rejected.",
        ],
        "boundary": {
            "contract_only": True,
            "network_access": False,
            "write_main_ledger": False,
            "run_daily_called": False,
        },
    }
    json_path = paths.data_dir / "system" / "global_briefing_signal_contract.json"
    report_path = paths.outputs_dir / "system" / "GLOBAL_BRIEFING_SIGNAL_CONTRACT.md"
    write_json_markdown(json_path, payload, report_path, build_contract_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_contract_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Signal Contract",
            "",
            "## Scope",
            "This contract defines historical macro signal packages accepted by trading-core.",
            "",
            "## Required Fields",
            *[f"- {field}" for field in payload["required_fields"]],
            "",
            "## Point-in-Time Rules",
            *[f"- {rule}" for rule in payload["point_in_time_rules"]],
            "",
            "## What This Is Not",
            "- not a live global-briefing integration",
            "- not live trading",
            "- not forward dry-run",
            "- not strategy effectiveness proof",
            "",
            "## Boundary",
            "- contract only",
            "- no network access",
            "- no main ledger writes",
            "- run-daily not called",
            "",
        ]
    )
