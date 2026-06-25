"""Convert daily baseline signals into preview-only order proposals."""

from __future__ import annotations

from typing import Any

from trading_core.broker.cost_model import calculate_trade_cost
from trading_core.execution.ashare_lot_rules import validate_order_quantity
from trading_core.execution.ashare_tradability import evaluate_tradability
from trading_core.storage.file_paths import ProjectPaths
from trading_core.strategies.common import market_for_symbol

from .common import DEFAULT_AS_OF_DATE, NOTICE, boundary_markdown, daily_order_preview_path, daily_order_preview_report_path, daily_signals_path, market_rows_for_date, paths_or_default, price_for_symbol, read_json_file, workflow_boundary, write_artifact
from .daily_baseline_signal_binding import build_daily_baseline_signals


def build_daily_order_preview(*, as_of_date: str = DEFAULT_AS_OF_DATE, strategy: str = "all", execution_mode: str = "isolated", paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    if execution_mode != "isolated":
        raise ValueError("daily order preview only supports execution_mode=isolated")
    if not daily_signals_path(paths, as_of_date).exists():
        build_daily_baseline_signals(as_of_date=as_of_date, strategy=strategy, paths=paths)
    signal_payload = read_json_file(daily_signals_path(paths, as_of_date))
    market_rows = market_rows_for_date(paths, as_of_date)
    proposals = []
    for signal_index, signal in enumerate(signal_payload.get("signals", []), 1):
        if strategy != "all" and signal.get("strategy_id") != strategy:
            continue
        for symbol, target_weight in sorted(signal.get("target_weights", {}).items()):
            price = price_for_symbol(market_rows, symbol)
            raw_quantity = int((1_000_000.0 * float(target_weight)) / float(price or 1.0))
            quantity = (raw_quantity // 100) * 100
            side = "BUY"
            market = "A_SHARE" if market_for_symbol(symbol) in {"SSE", "SZSE"} else "HK"
            decision = evaluate_tradability("tradable", side, price_available=price is not None, status_date=as_of_date, execution_date=signal["execution_earliest_date"])
            lot = validate_order_quantity(side, quantity)
            reject_reason = None
            if not decision.allowed:
                reject_reason = decision.reason
            elif not lot["accepted"]:
                reject_reason = lot["reason"]
            cost = calculate_trade_cost(float(price or 0.0), quantity, side, market) if price and quantity > 0 else None
            proposals.append(
                {
                    "order_id": f"ORD-DW-{signal['strategy_id'][:3].upper()}-{signal_index:02d}-{symbol.replace('.', '')}",
                    "strategy_id": signal["strategy_id"],
                    "strategy_version": signal["strategy_version"],
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "estimated_price": price,
                    "estimated_cost": cost.net_amount if cost else 0.0,
                    "estimated_commission": cost.commission if cost else 0.0,
                    "estimated_tax": cost.tax if cost else 0.0,
                    "estimated_slippage": cost.slippage if cost else 0.0,
                    "execution_earliest_date": signal["execution_earliest_date"],
                    "target_weight": float(target_weight),
                    "cash_weight": float(signal["cash_weight"]),
                    "cash_buffer_applied": float(signal["cash_weight"]) >= 0,
                    "board_lot_applied": quantity % 100 == 0,
                    "preview_only": True,
                    "executed": False,
                    "reject_reason": reject_reason,
                    "downsize_reason": "board_lot_rounding" if quantity != raw_quantity else None,
                    "execution_mode": "isolated",
                }
            )
    payload: dict[str, Any] = {
        "as_of_date": as_of_date,
        "strategy": strategy,
        "execution_mode": execution_mode,
        "proposals": proposals,
        "proposal_count": len(proposals),
        "rejected_count": sum(1 for item in proposals if item["reject_reason"]),
        "preview_only": all(item["preview_only"] is True for item in proposals),
        "executed": any(item["executed"] is True for item in proposals),
        "boundary": workflow_boundary("daily_order_preview_binding_only"),
    }
    return write_artifact(daily_order_preview_path(paths, as_of_date), payload, daily_order_preview_report_path(paths, as_of_date), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Daily Order Preview - {payload['as_of_date']}",
        "",
        NOTICE,
        "",
        "## Summary",
        f"- proposal_count: {payload['proposal_count']}",
        f"- rejected_count: {payload['rejected_count']}",
        "- preview_only=true",
        "- executed=false",
        "",
        "## Boundary",
    ]
    lines.extend(boundary_markdown("daily order preview binding only"))
    lines.append("")
    return "\n".join(lines)

