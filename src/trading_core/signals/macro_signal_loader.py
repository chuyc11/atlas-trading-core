"""Load macro signals from global-briefing or local trading-core data."""

from __future__ import annotations

import json
from uuid import uuid4
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_jsonl
from trading_core.universe.universe_loader import universe_symbols


VALID_CONFIDENCE = {"high", "medium", "low"}


def macro_signal_path(date: str, paths: ProjectPaths | None = None):
    paths = paths or project_paths()
    local = paths.data_dir / "macro_signals" / f"macro_signals-{date}.jsonl"
    global_path = paths.global_briefing_data_dir / f"macro_signals-{date}.jsonl"
    if local.exists():
        return local
    return global_path


def sync_macro_signals(
    date: str,
    paths: ProjectPaths | None = None,
    *,
    write_local: bool = True,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Validate the global-briefing source and atomically refresh the local copy.

    Unlike ``load_macro_signals``, this function never prefers an existing local
    snapshot. It is the bridge/import operation used by ATLAS sync.
    """
    paths = paths or project_paths()
    source_path = paths.global_briefing_data_dir / f"macro_signals-{date}.jsonl"
    if not source_path.exists():
        return [], [f"missing global macro_signals for {date}"]
    rows, limitations = _read_macro_jsonl(source_path)
    if not rows:
        limitations.append(f"empty global macro_signals for {date}")
    rows, validation_limitations = _validate_macro_rows(rows)
    limitations.extend(validation_limitations)
    if limitations or not write_local:
        return rows, limitations

    local_path = paths.data_dir / "macro_signals" / f"macro_signals-{date}.jsonl"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = local_path.with_name(f".{local_path.name}.{uuid4().hex}.tmp")
    temporary.write_bytes(source_path.read_bytes())
    temporary.replace(local_path)
    return rows, []


def load_macro_signals(
    date: str,
    paths: ProjectPaths | None = None,
    *,
    write_local: bool = True,
) -> tuple[list[dict[str, Any]], list[str]]:
    paths = paths or project_paths()
    path = macro_signal_path(date, paths)
    if not path.exists():
        return [], [f"missing macro_signals for {date}"]
    rows, limitations = _read_macro_jsonl(path)
    if not rows:
        limitations.append(f"empty macro_signals for {date}")
    rows, validation_limitations = _validate_macro_rows(rows)
    limitations.extend(validation_limitations)
    local_path = paths.data_dir / "macro_signals" / f"macro_signals-{date}.jsonl"
    if write_local and path != local_path:
        write_jsonl(local_path, rows)
    return rows, limitations


def _read_macro_jsonl(path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    limitations: list[str] = []
    text = path.read_text(encoding="utf-8")
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            limitations.append(f"bad macro_signals JSONL line {line_number}")
            continue
        if not isinstance(row, dict):
            limitations.append(f"non-object macro_signals row {line_number}")
            continue
        rows.append(row)
    return rows, limitations


def _validate_macro_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    validated = []
    limitations = []
    for index, row in enumerate(rows, 1):
        copy = dict(row)
        assets = copy.get("affected_assets")
        if not isinstance(assets, list):
            limitations.append(f"macro_signal row {index} missing affected_assets")
            copy["affected_assets"] = []
        elif not assets:
            limitations.append(f"macro_signal row {index} empty affected_assets")
        confidence = copy.get("confidence")
        if not _valid_confidence(confidence):
            limitations.append(f"macro_signal row {index} invalid confidence")
            flags = list(copy.get("risk_flags", [])) if isinstance(copy.get("risk_flags", []), list) else []
            copy["risk_flags"] = [*flags, "invalid_confidence"]
            copy["confidence"] = "low"
        validated.append(copy)
    return validated, limitations


def _valid_confidence(value: Any) -> bool:
    if isinstance(value, (int, float)):
        return 0.0 <= float(value) <= 1.0
    return str(value or "").lower() in VALID_CONFIDENCE


def filter_china_macro_signals(
    macro_signals: list[dict[str, Any]],
    universe: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    allowed = set(universe_symbols(universe))
    filtered = []
    for signal in macro_signals:
        if signal.get("region") != "CHINA":
            continue
        raw_assets = signal.get("affected_assets", [])
        if not isinstance(raw_assets, list):
            raw_assets = []
        assets = [asset for asset in raw_assets if asset in allowed]
        if not assets:
            continue
        copy = dict(signal)
        copy["affected_assets"] = assets
        filtered.append(copy)
    return filtered
