"""Merge historical price CSV packages with source-priority auditing."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from trading_core.config_loader import load_config
from trading_core.data.data_package_validator import REQUIRED_COLUMNS, validate_data_package
from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import write_json, write_jsonl


def merge_price_data(
    inputs: list[Path],
    output_path: Path,
    paths: ProjectPaths | None = None,
    source_priority: dict[str, int] | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    source_priority = source_priority or load_config("source_priority.yaml")
    output_path = _resolve_output_path(output_path, paths)
    output_path.mkdir(parents=True, exist_ok=True)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    errors: list[str] = []
    total_input_rows = 0

    for input_path in inputs:
        for csv_path in _csv_files(_resolve_output_path(input_path, paths)):
            rows, row_errors = _read_rows(csv_path)
            errors.extend(row_errors)
            for row in rows:
                total_input_rows += 1
                grouped[(row["symbol"], row["date"])].append(row)

    selected_by_symbol: dict[str, list[dict[str, Any]]] = defaultdict(list)
    duplicate_records = []
    discarded = []
    if not errors:
        for (symbol, date), rows in sorted(grouped.items()):
            selected = _select_row(rows, source_priority)
            selected_by_symbol[symbol].append({column: selected[column] for column in REQUIRED_COLUMNS})
            if len(rows) > 1:
                duplicate_records.append(
                    {
                        "symbol": symbol,
                        "date": date,
                        "selected_source": selected["source"],
                        "sources": [row["source"] for row in rows],
                    }
                )
                for row in rows:
                    if row is not selected:
                        discarded.append({**row, "discard_reason": "duplicate_lower_priority"})

        for symbol, rows in selected_by_symbol.items():
            _write_symbol_csv(output_path / f"{symbol}.csv", sorted(rows, key=lambda row: row["date"]))

    discarded_path = output_path / "discarded_records.jsonl"
    write_jsonl(discarded_path, discarded)
    validation = validate_data_package(output_path, paths)
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "inputs": [str(path) for path in inputs],
        "output_path": str(output_path),
        "source_priority": source_priority,
        "total_input_rows": total_input_rows,
        "total_output_rows": sum(len(rows) for rows in selected_by_symbol.values()),
        "duplicate_records_count": len(duplicate_records),
        "discarded_records_count": len(discarded),
        "duplicate_records": duplicate_records,
        "discarded_records_path": str(discarded_path),
        "errors": errors,
        "validation": validation,
        "passed": not errors and validation["passed"],
    }
    manifest_path = output_path / "merge_manifest.json"
    write_json(manifest_path, manifest)
    return {"manifest_path": str(manifest_path), "manifest": manifest, "validation": validation}


def _csv_files(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(item for item in path.glob("*.csv") if item.is_file())
    return [path]


def _read_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            return [], [f"{path.name}: missing columns {missing}"]
        for row in reader:
            rows.append({column: row[column] for column in REQUIRED_COLUMNS})
    return rows, errors


def _select_row(rows: list[dict[str, Any]], source_priority: dict[str, int]) -> dict[str, Any]:
    return sorted(
        rows,
        key=lambda row: (
            int(source_priority.get(str(row.get("source")), 999)),
            str(row.get("source")),
        ),
    )[0]


def _write_symbol_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _resolve_output_path(path: Path, paths: ProjectPaths) -> Path:
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return path.resolve()
