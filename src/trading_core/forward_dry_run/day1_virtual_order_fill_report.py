"""Build the day1 virtual order and fill report."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_owner_report_common import build_simple_markdown, load_day1_owner_report_context, order_side_summary, paths_or_default, report_boundary, symbol_summary, write_report_artifact
from trading_core.storage.file_paths import ProjectPaths


def build_day1_virtual_order_fill_report(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    context = load_day1_owner_report_context(paths)
    preview = context["payloads"].get("day1_virtual_order_preview", {})
    execution = context["payloads"].get("day1_virtual_execution_result", {})
    orders = preview.get("orders", [])
    fills = execution.get("fills", [])
    rejects = execution.get("rejects", [])
    costs = execution.get("costs", {})
    payload: dict[str, Any] = {
        "report_id": "FORWARD-DRY-RUN-DAY1-VIRTUAL-ORDER-FILL-REPORT",
        "day_index": 1,
        "orders_total": len(orders),
        "fills_total": len(fills),
        "rejects_total": len(rejects),
        "order_side_summary": order_side_summary(orders),
        "symbol_summary": symbol_summary(fills),
        "estimated_cost_summary": {"orders_estimated_cost": round(sum(float(order.get("estimated_cost", 0.0) or 0.0) for order in orders), 6), "fills_net_amount": costs.get("net", 0.0)},
        "fee_tax_slippage_summary": {"commission": costs.get("commission", 0.0), "tax": costs.get("tax", 0.0), "slippage": costs.get("slippage", 0.0)},
        "no_trade_fallback": execution.get("no_trade_fallback", False),
        "t_plus_1_execution_notes": "Orders use the earliest execution date from the day1 signal preview; A-share available shares remain zero on fill day.",
        "tradability_notes": "All filled orders passed the day1 tradability checks.",
        "board_lot_odd_lot_notes": "Preview quantities apply board-lot rounding where required; no odd-lot real order was placed.",
        "real_orders_placed": False,
        "broker_orders_placed": False,
        "main_orders_written": False,
        "main_trades_written": False,
        "boundary": {
            **report_boundary("virtual_orders_only"),
            "virtual_orders_only": True,
            "real_execution": False,
            "broker_execution": False,
            "main_ledger_written": False,
        },
    }
    lines = [
        f"- orders_total: {payload['orders_total']}",
        f"- fills_total: {payload['fills_total']}",
        f"- rejects_total: {payload['rejects_total']}",
        f"- order_side_summary: {payload['order_side_summary']}",
        f"- estimated_cost_summary: {payload['estimated_cost_summary']}",
        f"- fee_tax_slippage_summary: {payload['fee_tax_slippage_summary']}",
        f"- no_trade_fallback: {str(payload['no_trade_fallback']).lower()}",
        "- real_orders_placed: false",
        "- broker_orders_placed: false",
        "- main_orders_written: false",
        "- main_trades_written: false",
    ]
    return write_report_artifact(paths, "day1_virtual_order_fill_report.json", payload, "DAY1_VIRTUAL_ORDER_FILL_REPORT.md", build_simple_markdown("Day1 Virtual Order And Fill Report", lines, payload))
