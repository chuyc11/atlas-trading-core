"""Data quality checks for first-stage virtual trading."""

from __future__ import annotations

from typing import Any


def normalize_quality(item: dict[str, Any] | None) -> str:
    if not item:
        return "missing"
    if item.get("price") is None and item.get("last_close") is None:
        return "missing"
    status = str(item.get("data_status") or item.get("quality") or "").lower()
    source = str(item.get("provider") or item.get("source") or "").lower()
    if "stale" in status:
        return "stale"
    if "fallback" in status or "fallback" in source:
        return "fallback"
    return "fresh"


def trade_action_for_quality(quality: str, side: str) -> tuple[str, str]:
    quality = quality.lower()
    side = side.upper()
    if quality == "fresh":
        return "ALLOW", "fresh data"
    if quality == "fallback":
        return ("REJECT", "fallback data blocks new buy") if side == "BUY" else ("ALLOW", "fallback sell allowed")
    if quality == "stale":
        return ("REJECT", "stale data blocks new buy") if side == "BUY" else ("ALLOW", "stale sell allowed")
    return "REJECT", "missing price blocks trade"


def limitation_for_quality(symbol: str, quality: str) -> str | None:
    if quality == "fresh":
        return None
    return f"{symbol}: price quality is {quality}; trading may be held or rejected"
