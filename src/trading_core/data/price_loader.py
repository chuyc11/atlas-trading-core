"""Price loading and normalization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.data.data_quality import normalize_quality
from trading_core.data.snapshot_loader import load_snapshot, snapshot_items
from trading_core.storage.file_paths import ProjectPaths, project_paths


def _symbol_from_item(item: dict[str, Any]) -> str | None:
    return item.get("symbol") or item.get("ticker")


def _price_from_item(item: dict[str, Any]) -> float | None:
    value = item.get("price", item.get("last_close"))
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_price_item(item: dict[str, Any], date: str) -> dict[str, Any]:
    symbol = _symbol_from_item(item)
    price = _price_from_item(item)
    return {
        "symbol": symbol,
        "date": date,
        "price": price,
        "previous_close": item.get("previous_close"),
        "change_pct": item.get("change_pct"),
        "source": item.get("provider") or item.get("source"),
        "source_detail": item.get("source_detail"),
        "fetched_at": item.get("fetched_at") or item.get("generated_at"),
        "quality": normalize_quality({"price": price, **item}),
        "raw": item,
    }


def prices_by_symbol_from_snapshot(path: Path, date: str) -> dict[str, dict[str, Any]]:
    payload = load_snapshot(path)
    result: dict[str, dict[str, Any]] = {}
    for item in snapshot_items(payload):
        normalized = normalize_price_item(item, date)
        if normalized["symbol"]:
            result[str(normalized["symbol"])] = normalized
    return result


def load_china_prices(date: str, paths: ProjectPaths | None = None) -> tuple[dict[str, dict[str, Any]], list[str]]:
    paths = paths or project_paths()
    candidates = [
        paths.data_dir / "snapshots" / f"china-market-snapshot-{date}.json",
        paths.global_briefing_data_dir / f"china-market-snapshot-{date}.json",
    ]
    limitations: list[str] = []
    for candidate in candidates:
        if candidate.exists():
            return prices_by_symbol_from_snapshot(candidate, date), limitations
    limitations.append(f"missing China market snapshot for {date}")
    return {}, limitations


def simple_price_map(price_rows: dict[str, dict[str, Any]]) -> dict[str, float]:
    return {
        symbol: float(row["price"])
        for symbol, row in price_rows.items()
        if row.get("price") is not None
    }
