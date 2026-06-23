"""Load macro signals from global-briefing or local trading-core data."""

from __future__ import annotations

from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_jsonl, write_jsonl
from trading_core.universe.universe_loader import universe_symbols


def macro_signal_path(date: str, paths: ProjectPaths | None = None):
    paths = paths or project_paths()
    local = paths.data_dir / "macro_signals" / f"macro_signals-{date}.jsonl"
    global_path = paths.global_briefing_data_dir / f"macro_signals-{date}.jsonl"
    if local.exists():
        return local
    return global_path


def load_macro_signals(date: str, paths: ProjectPaths | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    paths = paths or project_paths()
    path = macro_signal_path(date, paths)
    if not path.exists():
        return [], [f"missing macro_signals for {date}"]
    rows = read_jsonl(path)
    local_path = paths.data_dir / "macro_signals" / f"macro_signals-{date}.jsonl"
    if path != local_path:
        write_jsonl(local_path, rows)
    return rows, []


def filter_china_macro_signals(
    macro_signals: list[dict[str, Any]],
    universe: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    allowed = set(universe_symbols(universe))
    filtered = []
    for signal in macro_signals:
        if signal.get("region") != "CHINA":
            continue
        assets = [asset for asset in signal.get("affected_assets", []) if asset in allowed]
        if not assets:
            continue
        copy = dict(signal)
        copy["affected_assets"] = assets
        filtered.append(copy)
    return filtered
