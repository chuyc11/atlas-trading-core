"""Build research-only baseline strategy order previews."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.execution.ashare_lot_rules import validate_order_quantity
from trading_core.execution.ashare_tradability import evaluate_tradability
from trading_core.storage.file_paths import ProjectPaths

from .baseline_signal_engine import generate_baseline_strategy_signals
from .common import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    RESEARCH_NOTICE,
    latest_signal_file,
    load_price_history,
    market_for_symbol,
    parse_dates_from_signal_file,
    paths_or_default,
    preview_path,
    preview_report_path,
    price_on_or_before,
    read_rows,
    rel,
    research_boundary,
    rows_and_paths,
    selected_strategies,
    simulated_price_status,
)


def build_baseline_order_preview(
    *,
    strategy: str = "all",
    signals: str | None = None,
    execution_mode: str = "isolated",
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    if execution_mode != "isolated":
        raise ValueError("baseline order preview only supports execution_mode=isolated")
    outputs = {}
    for strategy_id in selected_strategies(strategy):
        signal_file = _resolve_signal_file(paths, strategy_id, signals)
        if signal_file is None:
            generate_baseline_strategy_signals(strategy=strategy_id, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE, paths=paths)
            signal_file = _resolve_signal_file(paths, strategy_id, signals)
        if signal_file is None:
            raise FileNotFoundError(f"Missing signals for {strategy_id}")
        start_date, end_date = parse_dates_from_signal_file(signal_file, strategy_id)
        signals_rows = read_rows(signal_file)
        prices, _ = load_price_history(paths, start_date=start_date, end_date=end_date)
        preview_rows = _preview_rows(strategy_id, signals_rows, prices)
        jsonl_path = preview_path(paths, strategy_id, start_date, end_date)
        rows_and_paths(jsonl_path, preview_rows)
        md_path = preview_report_path(paths, strategy_id, start_date, end_date)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(_build_markdown(strategy_id, jsonl_path, preview_rows, paths), encoding="utf-8")
        outputs[strategy_id] = {
            "preview_path": str(jsonl_path),
            "report_path": str(md_path),
            "orders": len(preview_rows),
            "rejected": len([row for row in preview_rows if row["status"] == "rejected"]),
            "preview_only": all(row["preview_only"] is True for row in preview_rows),
            "executed": any(row["executed"] is True for row in preview_rows),
        }
    return {
        "strategy": strategy,
        "execution_mode": execution_mode,
        "paths": outputs,
        "preview_only": all(item["preview_only"] for item in outputs.values()),
        "executed": any(item["executed"] for item in outputs.values()),
        "boundary": research_boundary("order_preview_only"),
    }


def _resolve_signal_file(paths: ProjectPaths, strategy_id: str, raw: str | None) -> Path | None:
    if raw:
        path = Path(raw)
        if not path.is_absolute():
            path = paths.project_root / path
        return path if path.exists() else None
    return latest_signal_file(paths, strategy_id)


def _preview_rows(strategy_id: str, signal_rows: list[dict[str, Any]], prices: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    rows = []
    portfolio_value = 1_000_000.0
    for signal_index, signal in enumerate(signal_rows):
        execution_date = str(signal["execution_earliest_date"])
        for symbol, weight in sorted(signal.get("target_weights", {}).items()):
            price_date, price = price_on_or_before(prices, symbol, execution_date)
            raw_quantity = int((portfolio_value * float(weight)) / float(price or 1))
            quantity = (raw_quantity // 100) * 100
            status = simulated_price_status(symbol, execution_date)
            decision = evaluate_tradability(
                status,
                "BUY",
                price_available=price is not None,
                status_date=execution_date,
                execution_date=execution_date,
            )
            lot = validate_order_quantity("BUY", quantity)
            reject_reason = None
            order_status = "proposed"
            if not decision.allowed:
                order_status = "rejected"
                reject_reason = decision.reason
            elif not lot["accepted"]:
                order_status = "rejected"
                reject_reason = lot["reason"]
            rows.append(
                {
                    "order_id": f"ORD-BSP-{strategy_id[:3].upper()}-{signal_index + 1:04d}-{symbol.replace('.', '')}",
                    "strategy_id": strategy_id,
                    "strategy_version": signal["strategy_version"],
                    "signal_date": signal["signal_date"],
                    "execution_date": execution_date,
                    "symbol": symbol,
                    "market": "A_SHARE" if market_for_symbol(symbol) in {"SSE", "SZSE"} else "HK",
                    "side": "BUY",
                    "target_weight": float(weight),
                    "cash_weight": float(signal["cash_weight"]),
                    "cash_buffer_applied": float(signal["cash_weight"]) >= 0.0,
                    "price": price,
                    "price_data_as_of": price_date,
                    "raw_quantity": raw_quantity,
                    "quantity": quantity,
                    "board_lot_applied": quantity % 100 == 0,
                    "downsize_reason": "board_lot_rounding" if quantity != raw_quantity else None,
                    "status": order_status,
                    "reject_reason": reject_reason,
                    "preview_only": True,
                    "executed": False,
                    "execution_mode": "isolated",
                    "uses_ml_shadow": False,
                    "uses_llm": False,
                    "uses_rl": False,
                    "uses_promotion_outputs": False,
                }
            )
    return rows


def _build_markdown(strategy_id: str, path: Path, rows: list[dict[str, Any]], paths: ProjectPaths) -> str:
    rejected = len([row for row in rows if row["status"] == "rejected"])
    lines = [
        f"# Order Preview - {strategy_id}",
        "",
        RESEARCH_NOTICE,
        "",
        "## Summary",
        f"- path: {rel(path, paths)}",
        f"- proposals: {len(rows)}",
        f"- rejected: {rejected}",
        "- preview_only=true",
        "- executed=false",
        "",
        "## Boundary",
        "- order preview only",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "- ML shadow not used as authorization",
        "- LLM not used for trading decision",
        "- RL not used",
        "- promotion not triggered",
        "",
    ]
    return "\n".join(lines)
