"""State-free isolated execution preview for the daily workflow."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths

from .common import DEFAULT_AS_OF_DATE, NOTICE, boundary_markdown, daily_order_preview_path, execution_preview_path, execution_preview_report_path, paths_or_default, read_json_file, workflow_boundary, write_artifact
from .daily_order_preview_binding import build_daily_order_preview


def build_daily_isolated_execution_preview(*, as_of_date: str = DEFAULT_AS_OF_DATE, execution_mode: str = "isolated", paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    if execution_mode != "isolated":
        raise ValueError("daily isolated execution preview only supports execution_mode=isolated")
    if not daily_order_preview_path(paths, as_of_date).exists():
        build_daily_order_preview(as_of_date=as_of_date, strategy="all", execution_mode="isolated", paths=paths)
    order_preview = read_json_file(daily_order_preview_path(paths, as_of_date))
    fills = []
    rejects = []
    for proposal in order_preview.get("proposals", []):
        if proposal.get("reject_reason"):
            rejects.append({**proposal, "preview_only": True, "executed": False})
            continue
        fills.append(
            {
                "order_id": proposal["order_id"],
                "strategy_id": proposal["strategy_id"],
                "symbol": proposal["symbol"],
                "side": proposal["side"],
                "quantity": proposal["quantity"],
                "estimated_price": proposal["estimated_price"],
                "estimated_cost": proposal["estimated_cost"],
                "estimated_commission": proposal["estimated_commission"],
                "estimated_tax": proposal["estimated_tax"],
                "estimated_slippage": proposal["estimated_slippage"],
                "execution_earliest_date": proposal["execution_earliest_date"],
                "preview_only": True,
                "executed": False,
            }
        )
    cost_summary = {
        "estimated_cost": round(sum(float(fill.get("estimated_cost", 0.0)) for fill in fills), 6),
        "estimated_commission": round(sum(float(fill.get("estimated_commission", 0.0)) for fill in fills), 6),
        "estimated_tax": round(sum(float(fill.get("estimated_tax", 0.0)) for fill in fills), 6),
        "estimated_slippage": round(sum(float(fill.get("estimated_slippage", 0.0)) for fill in fills), 6),
    }
    strategy_count = max(len({fill["strategy_id"] for fill in fills}), 1)
    initial_cash = 1_000_000.0 * strategy_count
    valuation_estimate = {
        "initial_cash": initial_cash,
        "estimated_cash_after_preview": round(initial_cash - cost_summary["estimated_cost"], 6),
        "estimated_market_value": round(cost_summary["estimated_cost"], 6),
        "state_updated": False,
    }
    payload: dict[str, Any] = {
        "as_of_date": as_of_date,
        "execution_mode": "isolated_preview",
        "preview_only": True,
        "executed": False,
        "state_updated": False,
        "fills": fills,
        "rejects": rejects,
        "cost_summary": cost_summary,
        "valuation_estimate": valuation_estimate,
        "ledger_invariants": {
            "cash_non_negative_preview": valuation_estimate["estimated_cash_after_preview"] >= 0,
            "positions_non_negative_preview": True,
            "available_lte_position_preview": True,
            "passed": valuation_estimate["estimated_cash_after_preview"] >= 0,
        },
        "no_trade_fallback": len(fills) == 0,
        "forward_dry_run_started": False,
        "forward_dry_run_validated": False,
        "main_ledger_written": False,
        "boundary": workflow_boundary("daily_isolated_execution_preview_only"),
    }
    return write_artifact(execution_preview_path(paths, as_of_date), payload, execution_preview_report_path(paths, as_of_date), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Daily Isolated Execution Preview - {payload['as_of_date']}",
        "",
        NOTICE,
        "",
        "## Summary",
        "- execution_mode=isolated_preview",
        "- preview_only=true",
        "- executed=false",
        f"- fills: {len(payload['fills'])}",
        f"- rejects: {len(payload['rejects'])}",
        f"- state_updated={str(payload['state_updated']).lower()}",
        "",
        "## Boundary",
    ]
    lines.extend(boundary_markdown("daily isolated execution preview only"))
    lines.append("")
    return "\n".join(lines)
