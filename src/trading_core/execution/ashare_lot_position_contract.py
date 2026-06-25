"""Lot, cash, position, and available-share contract artifact."""

from __future__ import annotations

from typing import Any

from trading_core.execution.ashare_lot_rules import validate_order_quantity
from trading_core.execution.cash_position_invariants import check_cash_position_invariants
from trading_core.execution.common import HARDENING_NOTICE, paths_or_default, standard_boundary
from trading_core.execution.position_availability import AvailabilityBook
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_lot_position_contract(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    contract_id, created_at = timestamp_id("ASHARE-LOT-POSITION-CONTRACT")
    book = AvailabilityBook()
    settle = book.buy(100, "2024-01-02")
    same_day_available = book.available
    book.settle(settle)
    scenarios = {
        "buy_100_allowed": validate_order_quantity("BUY", 100),
        "buy_50_rejected": validate_order_quantity("BUY", 50),
        "buy_150_rejected": validate_order_quantity("BUY", 150),
        "sell_odd_lot_allowed": validate_order_quantity("SELL", 50, position_quantity=150, available_quantity=150),
        "sell_more_than_position_rejected": validate_order_quantity("SELL", 200, position_quantity=150, available_quantity=150),
        "sell_more_than_available_rejected": validate_order_quantity("SELL", 100, position_quantity=150, available_quantity=50),
    }
    payload: dict[str, Any] = {
        "contract_id": contract_id,
        "created_at": created_at,
        "default_board_lot": 100,
        "buy_must_satisfy_board_lot": True,
        "sell_odd_lot_allowed_when_position_exists": True,
        "sell_more_than_position_allowed": False,
        "sell_more_than_available_allowed": False,
        "t_day_buy_available_same_day": False,
        "t_plus_1_available_date": settle,
        "t_plus_1_available_after_settlement": book.available == 100 and same_day_available == 0,
        "insufficient_cash_policy": "reject",
        "negative_cash_allowed": False,
        "negative_position_allowed": False,
        "silent_partial_fill_allowed": False,
        "reject_or_downsize_requires_reason": True,
        "scenarios": scenarios,
        "invariant_example": check_cash_position_invariants({"cash": 100.0, "positions": [{"symbol": "510300.SH", "quantity": 100, "available_quantity": 100}]}),
        "boundary": standard_boundary("lot_position_contract_only"),
    }
    json_path = paths.data_dir / "system" / "ashare_lot_position_contract.json"
    md_path = paths.outputs_dir / "system" / "ASHARE_LOT_POSITION_CONTRACT.md"
    write_json_markdown(json_path, payload, md_path, build_lot_position_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_lot_position_markdown(payload: dict[str, Any]) -> str:
    lines = ["# A-Share Lot Position Contract", "", "## Scope", "This contract defines board lot, odd lot, cash, position, and available-share rules.", HARDENING_NOTICE, "", "## Rules"]
    for key in ["buy_must_satisfy_board_lot", "sell_odd_lot_allowed_when_position_exists", "t_day_buy_available_same_day", "negative_cash_allowed", "negative_position_allowed"]:
        lines.append(f"- {key}: {payload[key]}")
    lines.extend(["", "## Boundary", "- lot position contract only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

