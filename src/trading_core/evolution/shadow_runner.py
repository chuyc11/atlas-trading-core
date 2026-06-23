"""Shadow strategy runner."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_jsonl
from trading_core.strategy.momentum_strategy import generate_momentum_shadow_signals


def run_shadow(
    date: str,
    account_id: str,
    prices: dict[str, dict[str, Any]],
    paths: ProjectPaths | None = None,
) -> list[dict[str, Any]]:
    rows = generate_momentum_shadow_signals(prices, date, account_id)
    paths = paths or project_paths()
    write_jsonl(paths.data_dir / "experiments" / f"shadow_signals-{date}.jsonl", rows)
    return rows
