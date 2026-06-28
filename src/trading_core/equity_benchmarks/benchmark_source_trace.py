"""Source trace for A-share benchmark comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_benchmarks.benchmark_config import BENCHMARK_FLAGS, FORBIDDEN_SOURCE_PATH_TOKENS, TARGET_VERSION
from trading_core.equity_data_quality.common import sha256_file
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


MAX_HASH_BYTES = 100 * 1024 * 1024


def build_benchmark_source_trace(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    generated_at: str,
    input_paths: dict[str, Path],
    output_artifacts: dict[str, Path],
    index_source_meta: dict[str, Any],
) -> dict[str, Any]:
    source_records = [_record(paths, path) for path in input_paths.values()]
    index_path = index_source_meta.get("source_path")
    if index_path:
        source_records.append(_record(paths, Path(index_path)))
    output_records = {key: _record(paths, path, allow_missing=key in {"benchmark_source_trace", "benchmark_audit_json", "benchmark_audit_report"}) for key, path in output_artifacts.items()}
    forbidden_hits = forbidden_source_path_hits(source_records)
    return {
        "trace_id": "A-SHARE-BENCHMARK-COMPARISON-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "source_artifacts": source_records,
        "index_benchmark_source": index_source_meta,
        "cash_benchmark_assumption": {"source_type": "cash_assumption_zero_return", "daily_return": 0.0},
        "equal_weight_universe_construction": {
            "strict_tradable": "as_of_date filter_passed symbols with adjusted close preferred",
            "candidate_pool": "deduplicated long, mid, short, and multi-horizon candidate symbols",
        },
        "output_artifacts": output_records,
        "forbidden_source_path_hits": forbidden_hits,
        "source_trace_complete": not forbidden_hits and all(row["exists"] for row in source_records),
        **BENCHMARK_FLAGS,
    }


def update_trace_with_audit_artifacts(*, paths: ProjectPaths, trace: dict[str, Any], audit_json: Path, audit_report: Path) -> dict[str, Any]:
    outputs = dict(trace.get("output_artifacts", {}))
    outputs["benchmark_audit_json"] = _record(paths, audit_json)
    outputs["benchmark_audit_report"] = _record(paths, audit_report)
    trace = dict(trace)
    trace["output_artifacts"] = outputs
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
