"""Source trace for A-share data refresh."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_data_refresh.data_refresh_config import FORBIDDEN_SOURCE_TOKENS, REFRESH_FLAGS, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


MAX_HASH_BYTES = 100 * 1024 * 1024


def build_data_refresh_source_trace(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    generated_at: str,
    input_paths: dict[str, Path],
    output_artifacts: dict[str, Path],
    provider_registry: dict[str, Any],
    fallback_report: dict[str, Any],
    stale_decisions: list[dict[str, Any]],
    schema_fallback_decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    source_records = [_record(paths, path) for path in input_paths.values()]
    output_records = {
        key: _record(paths, path, allow_missing=key in {"data_refresh_source_trace", "data_refresh_audit_json", "data_refresh_audit_report"})
        for key, path in output_artifacts.items()
    }
    provider_records = [
        {
            "provider_id": provider["provider_id"],
            "provider_type": provider["provider_type"],
            "requires_network": provider["requires_network"],
            "enabled": provider["enabled"],
        }
        for provider in provider_registry.get("providers", [])
    ]
    forbidden = forbidden_source_path_hits(source_records + list(output_records.values()))
    return {
        "trace_id": "A-SHARE-DAILY-DATA-REFRESH-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "source_artifacts": source_records,
        "provider_artifacts": provider_records,
        "output_artifacts": output_records,
        "fallback_decisions": fallback_report.get("fallbacks", []),
        "stale_data_decisions": stale_decisions,
        "schema_fallback_decisions": schema_fallback_decisions,
        "forbidden_source_path_hits": forbidden,
        "source_trace_complete": not forbidden and all(row["exists"] for row in source_records),
        **REFRESH_FLAGS,
    }


def update_trace_with_audit_artifacts(*, paths: ProjectPaths, trace: dict[str, Any], audit_json: Path, audit_report: Path) -> dict[str, Any]:
    updated = dict(trace)
    outputs = dict(updated.get("output_artifacts", {}))
    outputs["data_refresh_audit_json"] = _record(paths, audit_json, allow_missing=True)
    outputs["data_refresh_audit_report"] = _record(paths, audit_report, allow_missing=True)
    updated["output_artifacts"] = outputs
    updated["forbidden_source_path_hits"] = forbidden_source_path_hits(list(updated.get("source_artifacts", [])) + list(outputs.values()))
    updated["source_trace_complete"] = not updated["forbidden_source_path_hits"] and all(row.get("exists") for row in updated.get("source_artifacts", []))
    return updated


def forbidden_source_path_hits(records: list[dict[str, Any]]) -> list[str]:
    hits = []
    for row in records:
        text = str(row.get("path") or "").replace("\\", "/").lower()
        for token in FORBIDDEN_SOURCE_TOKENS:
            if token in text:
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
