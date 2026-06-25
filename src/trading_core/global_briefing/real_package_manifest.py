"""Local historical global-briefing package manifest generation."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.global_briefing.signal_schema import parse_date, resolve_project_path
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


DEFAULT_PACKAGE_ROOTS = [
    "data/global_briefing",
    "data/global_briefing/packages",
    "data/global_briefing/signals",
    "external/global_briefing",
]
SUPPORTED_SUFFIXES = {".json": "json", ".jsonl": "jsonl", ".csv": "csv", ".parquet": "parquet"}
DATE_KEYS = ["as_of_date", "date", "signal_date", "briefing_date", "report_date"]
REGION_KEYS = ["region", "market", "geography"]
SOURCE_KEYS = ["source", "provider", "system"]


def build_global_briefing_package_manifest(
    *,
    root: str | None = None,
    include: list[str] | None = None,
    output: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    manifest_id, created_at = timestamp_id("GB-PACKAGE-MANIFEST")
    roots = [root] if root else list(DEFAULT_PACKAGE_ROOTS)
    roots.extend(include or [])
    warnings: list[str] = []
    packages: list[dict[str, Any]] = []

    for root_text in roots:
        root_path = resolve_project_path(root_text, paths)
        if not root_path.exists():
            warnings.append(f"root missing: {root_text}")
            continue
        for file_path in sorted(path for path in root_path.rglob("*") if path.is_file()):
            suffix = file_path.suffix.lower()
            if suffix not in SUPPORTED_SUFFIXES:
                warnings.append(f"unsupported package file skipped: {file_path}")
                continue
            packages.append(_inspect_package(file_path, paths))

    counts = {fmt: 0 for fmt in ["json", "jsonl", "csv", "parquet"]}
    for package in packages:
        counts[str(package["format"])] += 1
    payload: dict[str, Any] = {
        "manifest_id": manifest_id,
        "created_at": created_at,
        "roots_scanned": [str(resolve_project_path(item, paths)) for item in roots],
        "packages": packages,
        "counts": {"packages": len(packages), **counts},
        "warnings": warnings,
        "boundary": {
            "local_files_only": True,
            "network_access": False,
            "replay_started": False,
            "run_daily_called": False,
            "main_ledger_written": False,
            "write_main_ledger": False,
        },
    }
    json_path = resolve_project_path(output, paths) if output else paths.data_dir / "system" / "global_briefing_package_manifest.json"
    report_path = paths.outputs_dir / "system" / "GLOBAL_BRIEFING_PACKAGE_MANIFEST.md"
    write_json_markdown(json_path, payload, report_path, build_manifest_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _inspect_package(path: Path, paths: ProjectPaths) -> dict[str, Any]:
    warnings: list[str] = []
    fmt = SUPPORTED_SUFFIXES[path.suffix.lower()]
    rows: list[dict[str, Any]] = []
    if fmt == "parquet":
        warnings.append("parquet support is optional; pyarrow/pandas reader not required for manifest")
    else:
        try:
            rows = read_local_package_rows(path)
        except ValueError as exc:
            warnings.append(str(exc))
    dates = sorted({str(value) for row in rows if (value := _first_value(row, DATE_KEYS)) and parse_date(str(value))})
    regions = sorted({str(value) for row in rows if (value := _first_value(row, REGION_KEYS))})
    sources = sorted({str(value) for row in rows if (value := _first_value(row, SOURCE_KEYS))})
    stat = path.stat()
    return {
        "package_id": path.stem.upper().replace("-", "_"),
        "path": str(path),
        "format": fmt,
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat().replace("+00:00", "Z"),
        "detected_rows": len(rows) if fmt != "parquet" else None,
        "date_min": dates[0] if dates else None,
        "date_max": dates[-1] if dates else None,
        "region_values": regions,
        "source_values": sources,
        "warnings": warnings,
    }


def read_local_package_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        rows = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"malformed JSONL row {line_number}: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"JSONL row {line_number} is not an object")
            rows.append(value)
        return rows
    if suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed JSON: {exc.msg}") from exc
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict) and isinstance(payload.get("signals"), list):
            return [row for row in payload["signals"] if isinstance(row, dict)]
        if isinstance(payload, dict):
            return [payload]
        return []
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix == ".parquet":
        raise ValueError("parquet support is optional and unavailable in this lightweight reader")
    raise ValueError(f"unsupported package format: {path.suffix}")


def _first_value(row: dict[str, Any], keys: list[str]) -> Any | None:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def build_manifest_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Global Briefing Package Manifest",
        "",
        "## Scope",
        "This manifest scans local historical global-briefing packages only.",
        "",
        "## Roots Scanned",
        *[f"- {root}" for root in payload["roots_scanned"]],
        "",
        "## Packages",
    ]
    if payload["packages"]:
        lines.extend(f"- {item['package_id']}: {item['path']} rows={item['detected_rows']}" for item in payload["packages"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Warnings",
            *([f"- {item}" for item in payload["warnings"]] if payload["warnings"] else ["- none"]),
            "",
            "## Boundary",
            "- local files only",
            "- no network access",
            "- replay not started",
            "- run-daily not called",
            "- no orders/trades/portfolio/accounts written",
            "",
        ]
    )
    return "\n".join(lines)
