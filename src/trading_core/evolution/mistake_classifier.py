"""Classify signal mistakes into a small fixed taxonomy."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_jsonl


MISTAKE_TYPES = {
    "asset_mapping_error",
    "already_priced_in",
    "data_quality_or_stale_price",
    "benchmark_underperformance",
    "weak_signal",
}


def classify_mistake(item: dict[str, Any]) -> str | None:
    if item.get("status") not in {"wrong", "partial"}:
        return None
    flags = set(item.get("risk_flags") or [])
    if "asset_mapping_error" in flags:
        return "asset_mapping_error"
    if "already_priced_in" in flags:
        return "already_priced_in"
    if "data_fallback_used" in flags or "stale" in flags:
        return "data_quality_or_stale_price"
    if float(item.get("confidence") or 0.0) < 0.55:
        return "weak_signal"
    return "benchmark_underperformance"


def classify_mistakes(
    date: str,
    scorecard: dict[str, Any],
    paths: ProjectPaths | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for item in scorecard.get("items", []):
        mistake_type = classify_mistake(item)
        if not mistake_type:
            continue
        rows.append(
            {
                "date": date,
                "signal_id": item.get("signal_id"),
                "strategy_id": item.get("strategy_id"),
                "symbol": item.get("symbol"),
                "mistake_type": mistake_type,
                "excess_return": item.get("excess_return"),
                "status": item.get("status"),
            }
        )
    paths = paths or project_paths()
    write_jsonl(paths.dated_jsonl("evolution", "mistakes", date), rows)
    return rows
