"""Price status and tradability contract artifact."""

from __future__ import annotations

from typing import Any

from trading_core.execution.ashare_tradability import SUPPORTED_STATUSES, evaluate_tradability
from trading_core.execution.common import HARDENING_NOTICE, paths_or_default, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_price_status_contract(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    contract_id, created_at = timestamp_id("ASHARE-PRICE-STATUS-CONTRACT")
    scenarios = {
        "tradable_buy": evaluate_tradability("tradable", "BUY").to_dict(),
        "tradable_sell": evaluate_tradability("tradable", "SELL").to_dict(),
        "suspended_buy": evaluate_tradability("suspended", "BUY").to_dict(),
        "suspended_sell": evaluate_tradability("suspended", "SELL").to_dict(),
        "missing_price": evaluate_tradability("missing_price", "BUY", price_available=False).to_dict(),
        "limit_up_buy": evaluate_tradability("limit_up", "BUY").to_dict(),
        "limit_up_sell": evaluate_tradability("limit_up", "SELL").to_dict(),
        "limit_down_sell": evaluate_tradability("limit_down", "SELL").to_dict(),
        "limit_down_buy": evaluate_tradability("limit_down", "BUY").to_dict(),
        "st_flagged": evaluate_tradability("st_flagged", "BUY").to_dict(),
        "new_listing_restricted": evaluate_tradability("new_listing_restricted", "BUY").to_dict(),
        "unknown_status": evaluate_tradability("unknown_status", "BUY").to_dict(),
        "future_status": evaluate_tradability("tradable", "BUY", status_date="2024-01-04", execution_date="2024-01-03").to_dict(),
    }
    payload: dict[str, Any] = {
        "contract_id": contract_id,
        "created_at": created_at,
        "supported_statuses": SUPPORTED_STATUSES,
        "default_fail_closed": True,
        "blocked_order_requires_reject_reason": True,
        "silent_fill_allowed": False,
        "future_status_allowed": False,
        "scenarios": scenarios,
        "suspension_missing_limit_handled": True,
        "st_new_listing_handled": True,
        "boundary": standard_boundary("price_status_contract_only"),
    }
    json_path = paths.data_dir / "system" / "ashare_price_status_contract.json"
    md_path = paths.outputs_dir / "system" / "ASHARE_PRICE_STATUS_CONTRACT.md"
    write_json_markdown(json_path, payload, md_path, build_price_status_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_price_status_markdown(payload: dict[str, Any]) -> str:
    lines = ["# A-Share Price Status Contract", "", "## Scope", "This contract defines fail-closed tradability rules for A-share and ETF virtual execution.", HARDENING_NOTICE, "", "## Statuses"]
    lines.extend(f"- {item}" for item in payload["supported_statuses"])
    lines.extend(["", "## Boundary", "- price status contract only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

