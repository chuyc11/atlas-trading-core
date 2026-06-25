"""Normalize local real global-briefing packages to the v1 signal contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.global_briefing.real_package_manifest import read_local_package_rows
from trading_core.global_briefing.signal_schema import REQUIRED_FIELDS, resolve_project_path, validate_signal_row
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import write_jsonl
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


ALIASES = {
    "as_of_date": ["as_of_date", "date", "signal_date", "briefing_date", "report_date"],
    "generated_at": ["generated_at", "generated_time", "published_at", "created_at", "timestamp"],
    "region": ["region", "market", "geography"],
    "signals": ["signals", "signal_values", "macro_signals", "factors", "scores"],
    "source": ["source", "provider", "system"],
    "version": ["version", "schema_version"],
}
METADATA_COLUMNS = set(sum(ALIASES.values(), [])) | {"package_id"}


def normalize_global_briefing_package(
    input_path: str,
    *,
    package_id: str | None = None,
    region: str | None = None,
    source: str | None = None,
    version: str | None = None,
    output: str | None = None,
    strict: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    normalization_id, created_at = timestamp_id("GB-NORMALIZE")
    input_file = resolve_project_path(input_path, paths)
    blocking: list[str] = []
    warnings: list[str] = []
    rows_in: list[dict[str, Any]] = []
    try:
        rows_in = read_local_package_rows(input_file)
    except ValueError as exc:
        blocking.append(str(exc))

    normalized_rows: list[dict[str, Any]] = []
    dropped = 0
    field_mapping: dict[str, str] = {}
    for index, row in enumerate(rows_in, 1):
        normalized, row_mapping, row_warnings, row_blocking = _normalize_row(
            row,
            index,
            region=region,
            source=source,
            version=version,
            strict=strict,
        )
        field_mapping.update(row_mapping)
        warnings.extend(row_warnings)
        if row_blocking:
            blocking.extend(row_blocking)
            dropped += 1
            continue
        if normalized is None:
            dropped += 1
            continue
        clean, validation_blocking, validation_warnings = validate_signal_row(normalized, index, check_point_in_time=False)
        warnings.extend(validation_warnings)
        if validation_blocking:
            blocking.extend(validation_blocking)
            dropped += 1
            continue
        normalized_rows.append(clean or normalized)

    package_name = package_id or input_file.stem.upper().replace("-", "_")
    output_path = resolve_project_path(output, paths) if output else paths.data_dir / "global_briefing" / "normalized" / f"{package_name}.normalized.jsonl"
    if normalized_rows:
        write_jsonl(output_path, normalized_rows)
    payload: dict[str, Any] = {
        "normalization_id": normalization_id,
        "created_at": created_at,
        "input": str(input_file),
        "output": str(output_path),
        "package_id": package_name,
        "overall_passed": not blocking and bool(normalized_rows),
        "blocking_reasons": blocking if blocking or normalized_rows else ["no rows normalized"],
        "rows_in": len(rows_in),
        "rows_out": len(normalized_rows),
        "dropped_rows": dropped,
        "field_mapping": field_mapping,
        "warnings": warnings,
        "boundary": {
            "normalization_only": True,
            "network_access": False,
            "replay_started": False,
            "main_ledger_written": False,
            "write_main_ledger": False,
            "run_daily_called": False,
        },
    }
    json_path = paths.data_dir / "system" / "global_briefing_normalization_summary.json"
    report_path = paths.outputs_dir / "system" / "GLOBAL_BRIEFING_NORMALIZATION_REPORT.md"
    write_json_markdown(json_path, payload, report_path, build_normalization_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _normalize_row(
    row: dict[str, Any],
    index: int,
    *,
    region: str | None,
    source: str | None,
    version: str | None,
    strict: bool,
) -> tuple[dict[str, Any] | None, dict[str, str], list[str], list[str]]:
    mapping: dict[str, str] = {}
    warnings: list[str] = []
    blocking: list[str] = []
    canonical: dict[str, Any] = {}
    for target in ["as_of_date", "generated_at", "region", "signals", "source", "version"]:
        source_key, value = _first_alias(row, ALIASES[target])
        if source_key:
            mapping[source_key] = target
        if value not in (None, ""):
            canonical[target] = value
    if "generated_at" not in canonical:
        if strict:
            blocking.append(f"row {index} missing generated_at in strict mode")
        elif canonical.get("as_of_date"):
            canonical["generated_at"] = f"{canonical['as_of_date']}T00:00:00Z"
            warnings.append(f"row {index} generated_at missing; defaulted to as_of_date at 00:00:00Z")
    if "region" not in canonical and region:
        canonical["region"] = region
    if "source" not in canonical and source:
        canonical["source"] = source
    if "version" not in canonical and version:
        canonical["version"] = version
    signals = canonical.get("signals")
    if isinstance(signals, str):
        signals = _parse_signal_string(signals)
    if not isinstance(signals, dict):
        signals = {
            key: _coerce_value(value, warnings, index, key)
            for key, value in row.items()
            if key not in METADATA_COLUMNS and value != ""
        }
    if not signals:
        blocking.append(f"row {index} signals empty")
    canonical["signals"] = signals
    for field in REQUIRED_FIELDS:
        if field not in canonical or canonical[field] in (None, ""):
            blocking.append(f"row {index} missing {field}")
    return (canonical if not blocking else None), mapping, warnings, blocking


def _first_alias(row: dict[str, Any], aliases: list[str]) -> tuple[str | None, Any | None]:
    for alias in aliases:
        if alias in row:
            return alias, row.get(alias)
    return None, None


def _parse_signal_string(value: str) -> dict[str, Any]:
    import json

    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _coerce_value(value: Any, warnings: list[str], row_index: int, key: str) -> Any:
    if value == "":
        return None
    if not isinstance(value, str):
        return value
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        number = float(value)
    except ValueError:
        warnings.append(f"row {row_index} signal {key} kept as string")
        return value
    return int(number) if number.is_integer() else number


def build_normalization_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Normalization Report",
            "",
            "## Overall Verdict",
            f"- overall_passed={str(payload['overall_passed']).lower()}",
            f"- blocking_reasons={payload['blocking_reasons']}",
            "",
            "## Input",
            f"- {payload['input']}",
            "",
            "## Output",
            f"- {payload['output']}",
            "",
            "## Rows",
            f"- rows_in={payload['rows_in']}",
            f"- rows_out={payload['rows_out']}",
            f"- dropped_rows={payload['dropped_rows']}",
            "",
            "## Warnings",
            *([f"- {item}" for item in payload["warnings"]] if payload["warnings"] else ["- none"]),
            "",
            "## Boundary",
            "- normalization only",
            "- no network access",
            "- replay not started",
            "- run-daily not called",
            "- no orders/trades/portfolio/accounts written",
            "",
        ]
    )
