"""Execution cost contract artifact."""

from __future__ import annotations

from typing import Any

from trading_core.broker.cost_model import calculate_trade_cost, slippage_price
from trading_core.broker.market_rules import get_market_rule
from trading_core.execution.common import HARDENING_NOTICE, paths_or_default, standard_boundary
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_execution_cost_contract(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    contract_id, created_at = timestamp_id("ASHARE-EXECUTION-COST-CONTRACT")
    rule = get_market_rule("A_SHARE")
    buy = calculate_trade_cost(10.0, 100, "BUY", "A_SHARE", rule)
    sell = calculate_trade_cost(10.0, 100, "SELL", "A_SHARE", rule)
    payload: dict[str, Any] = {
        "contract_id": contract_id,
        "created_at": created_at,
        "commission_bps": rule.commission_rate * 10000,
        "minimum_commission": rule.min_commission,
        "stamp_duty_bps_sell": rule.stamp_tax_sell_rate * 10000,
        "transfer_fee_defined": False,
        "slippage_bps": rule.default_slippage_bps,
        "buy_sell_fee_difference": True,
        "fill_price_source": "next_day_open_or_configured_execution_price",
        "pit_safe_fill_price_required": True,
        "future_close_as_t_plus_1_price_allowed": False,
        "costs_enter_cash_accounting": True,
        "costs_enter_trade_record": True,
        "costs_enter_replay_evaluation": True,
        "examples": {
            "buy": buy.__dict__,
            "sell": sell.__dict__,
            "buy_fill_price": slippage_price(10.0, "BUY", rule),
            "sell_fill_price": slippage_price(10.0, "SELL", rule),
        },
        "boundary": standard_boundary("execution_cost_contract_only"),
    }
    json_path = paths.data_dir / "system" / "ashare_execution_cost_contract.json"
    md_path = paths.outputs_dir / "system" / "ASHARE_EXECUTION_COST_CONTRACT.md"
    write_json_markdown(json_path, payload, md_path, build_execution_cost_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_execution_cost_markdown(payload: dict[str, Any]) -> str:
    lines = ["# A-Share Execution Cost Contract", "", "## Scope", "This contract defines fee, tax, slippage, and PIT-safe fill price rules.", HARDENING_NOTICE, "", "## Defaults"]
    for key in ["commission_bps", "minimum_commission", "stamp_duty_bps_sell", "slippage_bps"]:
        lines.append(f"- {key}: {payload[key]}")
    lines.extend(["", "## Boundary", "- execution cost contract only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

