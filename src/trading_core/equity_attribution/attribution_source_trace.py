"""Source trace for attribution diagnostics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, FORBIDDEN_PATH_TOKENS, TARGET_VERSION
from trading_core.equity_data_quality.common import sha256_file
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


MAX_HASH_BYTES = 100 * 1024 * 1024


def build_attribution_source_trace(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    generated_at: str,
    input_paths: dict[str, Path],
    output_artifacts: dict[str, Path],
    limitations: dict[str, Any],
    assumptions: list[str],
) -> dict[str, Any]:
    source_records = [_record(paths, path) for path in input_paths.values()]
    output_records = {
        key: _record(paths, path, allow_missing=key in {"attribution_source_trace", "attribution_audit_json", "attribution_audit_report"})
        for key, path in output_artifacts.items()
    }
    hits = forbidden_source_path_hits(source_records + list(output_records.values()))
    return {
        "trace_id": "A-SHARE-PERFORMANCE-ATTRIBUTION-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "source_artifacts": source_records,
        "output_artifacts": output_records,
        "limitations_traced": {
            "limitations_id": limitations.get("limitations_id"),
            "limited_history": limitations.get("limited_history"),
            "realized_performance_attribution_available": limitations.get("realized_performance_attribution_available"),
        },
        "assumptions": assumptions,
        "forbidden_source_path_hits": hits,
        "source_trace_complete": not hits and all(row["exists"] for row in source_records),
        **ATTRIBUTION_FLAGS,
    }


def update_trace_with_audit_artifacts(*, paths: ProjectPaths, trace: dict[str, Any], audit_json: Path, audit_report: Path) -> dict[str, Any]:
    updated = dict(trace)
    outputs = dict(updated.get("output_artifacts", {}))
    outputs["attribution_audit_json"] = _record(paths, audit_json)
    outputs["attribution_audit_report"] = _record(paths, audit_report)
    updated["output_artifacts"] = outputs
    updated["forbidden_source_path_hits"] = forbidden_source_path_hits(list(updated.get("source_artifacts", [])) + list(outputs.values()))
    updated["source_trace_complete"] = not updated["forbidden_source_path_hits"] and all(row.get("exists") for row in updated.get("source_artifacts", []))
    return updated


def forbidden_source_path_hits(records: list[dict[str, Any]]) -> list[str]:
    hits = []
    for row in records:
        text = str(row.get("path") or "").replace("\\", "/").lower()
        for token in FORBIDDEN_PATH_TOKENS:
            if token.lower() in text:
                hits.append(f"{row.get('path')}:{token}")
    return sorted(set(hits))


def _record(paths: ProjectPaths, path: Path, *, allow_missing: bool = False) -> dict[str, Any]:
    display = relative(path, paths.project_root)
    exists = path.exists()
    size = path.stat().st_size if exists and path.is_file() else None
    hash_skipped_reason = "self_or_pending_artifact" if allow_missing else ("large_file" if size is not None and size > MAX_HASH_BYTES else None)
    return {
        "path": display,
        "exists": exists or allow_missing,
        "sha256": sha256_file(path) if exists and path.is_file() and hash_skipped_reason is None else None,
        "size_bytes": size,
        "hash_skipped_reason": hash_skipped_reason,
    }
