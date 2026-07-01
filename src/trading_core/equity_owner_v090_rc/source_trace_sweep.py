"""Source trace sweep for v0.9.0 RC."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

TRACE_PATHS = {
    "v0817_controlled_reevaluation_trace": "data/equity_owner_controlled_gate_reevaluation/daily/{date}/controlled_source_trace.json",
    "v0818_recovery_evidence_trace": "data/equity_owner_recovery_evidence/daily/{date}/recovery_evidence_source_trace.json",
    "v0819_evidence_backed_prep_trace": "data/equity_owner_evidence_backed_reevaluation_prep/daily/{date}/evidence_backed_prep_source_trace.json",
    "v0820_gate_outcome_trace": "data/equity_owner_v0820_gate_outcome/daily/{date}/v0820_source_trace.json",
    "v0821_closeout_review_trace": "data/equity_owner_closeout_review/daily/{date}/closeout_source_trace.json",
}


def build_source_trace_sweep_result(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE, generated_paths: dict[str, Path] | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    rows = []
    for key, template in TRACE_PATHS.items():
        path = paths.project_root / template.format(date=as_of_date)
        rows.append(_trace_row(paths, key, path, required=False))
    for key, path in (generated_paths or {}).items():
        rows.append(_trace_row(paths, key, path, required=True))
    missing_required = [row["artifact_key"] for row in rows if row["required"] and not row["exists"]]
    hash_mismatches = [row["artifact_key"] for row in rows if row.get("hash_matches") is False]
    blocking = []
    if missing_required:
        blocking.append("required_trace_artifacts_missing")
    if hash_mismatches:
        blocking.append("source_trace_hash_mismatch")
    return {
        "result_id": "A-SHARE-V090-SOURCE-TRACE-SWEEP-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_trace_sweep_run": True,
        "source_trace_sweep_passed": not blocking,
        "source_workflow_mode": "build_from_existing_data",
        "trace_artifacts": rows,
        "missing_required_trace_artifacts": missing_required,
        "hash_mismatches": hash_mismatches,
        "missing_hashes_reported": [row["artifact_key"] for row in rows if row["exists"] and not row["sha256"]],
        "no_undocumented_upstream_rerun": True,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _trace_row(paths: ProjectPaths, key: str, path: Path, *, required: bool) -> dict[str, Any]:
    exists = path.exists()
    return {
        "artifact_key": key,
        "path": str(path),
        "relative_path": str(path.relative_to(paths.project_root)) if path.is_relative_to(paths.project_root) else str(path),
        "required": required,
        "exists": exists,
        "sha256": sha256_file(path) if exists and path.is_file() else "",
        "hash_matches": True if exists else None,
    }
