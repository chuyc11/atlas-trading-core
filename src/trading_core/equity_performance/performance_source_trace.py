"""Source trace for A-share multi-day performance tracking."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_performance.performance_config import FORBIDDEN_SOURCE_PATH_TOKENS, PERFORMANCE_FLAGS, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


MAX_HASH_BYTES = 100 * 1024 * 1024


def build_performance_source_trace(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    generated_at: str,
    input_paths: dict[str, Path],
    price_panel_paths: dict[str, Path],
    output_artifacts: dict[str, Path],
    limitations: dict[str, Any],
    assumptions: list[str],
) -> dict[str, Any]:
    source_records = [_record(paths, path) for path in input_paths.values()]
    price_panel_records = {key: _record(paths, path, allow_missing=True) for key, path in price_panel_paths.items()}
    output_records = {
        key: _record(
            paths,
            path,
            allow_missing=key in {"performance_source_trace", "performance_audit_json", "performance_audit_report"},
        )
        for key, path in output_artifacts.items()
    }
    forbidden_hits = forbidden_source_path_hits(source_records + list(output_records.values()))
    return {
        "trace_id": "A-SHARE-MULTI-DAY-PERFORMANCE-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "source_artifacts": source_records,
        "price_panel_artifacts": price_panel_records,
        "output_artifacts": output_records,
        "limitations_traced": {
            "limitations_id": limitations.get("limitations_id"),
            "insufficient_history": limitations.get("insufficient_history"),
            "performance_not_yet_observed": limitations.get("performance_not_yet_observed"),
        },
        "assumptions": assumptions,
        "forbidden_source_path_hits": forbidden_hits,
        "source_trace_complete": not forbidden_hits and all(row["exists"] for row in source_records),
        **PERFORMANCE_FLAGS,
    }


def update_trace_with_audit_artifacts(*, paths: ProjectPaths, trace: dict[str, Any], audit_json: Path, audit_report: Path) -> dict[str, Any]:
    trace = dict(trace)
    outputs = dict(trace.get("output_artifacts", {}))
    outputs["performance_audit_json"] = _record(paths, audit_json)
    outputs["performance_audit_report"] = _record(paths, audit_report)
    trace["output_artifacts"] = outputs
    trace["forbidden_source_path_hits"] = forbidden_source_path_hits(list(trace.get("source_artifacts", [])) + list(outputs.values()))
    trace["source_trace_complete"] = not trace["forbidden_source_path_hits"] and all(row.get("exists") for row in trace.get("source_artifacts", []))
    return trace


def forbidden_source_path_hits(records: list[dict[str, Any]]) -> list[str]:
    hits = []
    for row in records:
        text = str(row.get("path") or "").replace("\\", "/").lower()
        for token in FORBIDDEN_SOURCE_PATH_TOKENS:
            if token.lower() in text:
                hits.append(f"{row.get('path')}:{token}")
    return sorted(set(hits))


def _record(paths: ProjectPaths, path: Path, *, allow_missing: bool = False) -> dict[str, Any]:
    display = relative(path, paths.project_root)
    exists = path.exists()
    size = path.stat().st_size if exists and path.is_file() else None
    hash_skipped_reason = "large_file" if size is not None and size > MAX_HASH_BYTES else None
    return {
        "path": display,
        "exists": exists or allow_missing,
        "sha256": sha256_file(path) if exists and path.is_file() and hash_skipped_reason is None else None,
        "size_bytes": size,
        "hash_skipped_reason": hash_skipped_reason,
    }
