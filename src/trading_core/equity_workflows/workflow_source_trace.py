"""Source trace for A-share daily research workflow orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_workflows.workflow_config import (
    FORBIDDEN_SOURCE_PATH_TOKENS,
    TARGET_VERSION,
    WORKFLOW_BOUNDARY,
    WORKFLOW_FLAGS,
    required_input_artifacts,
    upstream_audit_artifacts,
)
from trading_core.equity_workflows.workflow_manifest import artifact_record
from trading_core.storage.file_paths import ProjectPaths


def build_workflow_source_trace(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    mode: str,
    stages: list[dict[str, Any]],
    workflow_artifacts: dict[str, Path],
    generated_at: str,
) -> dict[str, Any]:
    input_artifacts = required_input_artifacts(paths, as_of_date)
    audit_artifacts = upstream_audit_artifacts(paths)
    stage_commands = [
        {
            "stage_id": stage["stage_id"],
            "stage_order": stage["stage_order"],
            "command": stage["command"],
            "status": stage["status"],
        }
        for stage in stages
    ]
    source_records = [
        artifact_record(paths, path)
        for path in [
            *input_artifacts.values(),
            *audit_artifacts.values(),
            workflow_artifacts["workflow_config"],
            workflow_artifacts["workflow_preflight"],
            workflow_artifacts["workflow_stage_manifest"],
            workflow_artifacts["workflow_run_manifest"],
            workflow_artifacts["workflow_boundary_check"],
        ]
    ]
    forbidden_hits = _forbidden_path_hits(source_records)
    return {
        "trace_id": "A-SHARE-DAILY-WORKFLOW-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "generated_at": generated_at,
        "tradable_universe_source": artifact_record(paths, input_artifacts["tradable_universe_manifest"]),
        "features_source": artifact_record(paths, input_artifacts["feature_manifest"]),
        "scores_source": artifact_record(paths, input_artifacts["score_manifest"]),
        "candidates_source": artifact_record(paths, input_artifacts["candidate_manifest"]),
        "virtual_portfolios_source": artifact_record(paths, input_artifacts["portfolio_manifest"]),
        "briefing_source": artifact_record(paths, input_artifacts["briefing_manifest"]),
        "tracking_source": artifact_record(paths, input_artifacts["tracking_manifest"]),
        "audit_sources": {key: artifact_record(paths, path) for key, path in audit_artifacts.items()},
        "stage_manifest_source": artifact_record(paths, workflow_artifacts["workflow_stage_manifest"]),
        "run_manifest_source": artifact_record(paths, workflow_artifacts["workflow_run_manifest"]),
        "stage_commands": stage_commands,
        "sources": source_records,
        "source_trace_complete": all(record["exists"] for record in source_records),
        "forbidden_path_hits": forbidden_hits,
        "benchmark_placeholder_deferred_to_v0_7_10": True,
        **WORKFLOW_FLAGS,
        "boundary": dict(WORKFLOW_BOUNDARY),
    }


def source_trace_has_forbidden_paths(source_trace: dict[str, Any]) -> list[str]:
    recorded = list(source_trace.get("forbidden_path_hits", []))
    rescanned = _forbidden_path_hits([record for record in source_trace.get("sources", []) if isinstance(record, dict)])
    return sorted({*recorded, *rescanned})


def _forbidden_path_hits(records: list[dict[str, Any]]) -> list[str]:
    hits = []
    for record in records:
        path = str(record.get("path") or "")
        lower = path.lower().replace("\\", "/")
        for token in FORBIDDEN_SOURCE_PATH_TOKENS:
            if token in lower:
                hits.append(f"{path}:{token}")
    return sorted(set(hits))
