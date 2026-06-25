"""Virtual execution contract artifact."""

from __future__ import annotations

from typing import Any

from trading_core.execution.common import HARDENING_NOTICE, paths_or_default, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_virtual_execution_contract(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    contract_id, created_at = timestamp_id("VIRTUAL-EXECUTION-CONTRACT")
    payload: dict[str, Any] = {
        "contract_id": contract_id,
        "created_at": created_at,
        "integrates": ["calendar", "T+1", "tradability", "lot rules", "cash/position/available shares", "fees/taxes/slippage", "reject reason", "fill reason", "isolated output path", "protected path guard"],
        "calendar_required": True,
        "t_plus_1_required": True,
        "tradability_required": True,
        "lot_rules_required": True,
        "cash_position_available_required": True,
        "costs_required": True,
        "rejected_orders_require_reason": True,
        "fills_require_reason": True,
        "isolated_output_path": "data/replays/global_briefing/execution_aware_smoke",
        "protected_path_guard": True,
        "boundary": standard_boundary("virtual_execution_contract_only"),
    }
    json_path = paths.data_dir / "system" / "virtual_execution_contract.json"
    md_path = paths.outputs_dir / "system" / "VIRTUAL_EXECUTION_CONTRACT.md"
    write_json_markdown(json_path, payload, md_path, build_virtual_execution_contract_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_virtual_execution_contract_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Virtual Execution Contract", "", "## Scope", "This contract integrates A-share execution hardening rules for isolated virtual execution.", HARDENING_NOTICE, "", "## Integrated Rules"]
    lines.extend(f"- {item}" for item in payload["integrates"])
    lines.extend(["", "## Boundary", "- virtual execution contract only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

