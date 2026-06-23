"""Load local and global-briefing snapshot files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.storage.jsonl_store import read_json


def load_snapshot(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def snapshot_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("items", [])
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []
