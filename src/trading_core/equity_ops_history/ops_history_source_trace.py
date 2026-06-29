"""Source trace for v0.8.6 ops history baselines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_ops_history.ops_history_config import FORBIDDEN_PATH_TOKENS, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_ops_history_source_trace(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    generated_at: str,
    source_paths: dict[str, Path],
    output_paths: dict[str, Path],
    command_policy_decisions: dict[str, Any],
) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = [_record(paths, key, path) for key, path in source_paths.items()]
    outputs = [_record(paths, key, path) for key, path in output_paths.items()]
    hits = forbidden_source_path_hits(sources + outputs)
    return {
        "trace_id": "A-SHARE-OPS-HISTORY-BASELINE-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "source_artifacts": sources,
        "output_artifacts": outputs,
        "boundary_assumptions": [
            "ops_history_only",
            "append_only_history",
            "trend_baseline_only",
            "research_only",
            "virtual_only",
            "no_synthetic_history",
            "no_future_dates",
            "no_upstream_build_rerun",
            "no_broker",
            "no_order_preview",
            "no_trade_signal",
        ],
        "command_policy_decisions": command_policy_decisions,
        "forbidden_path_hits": hits,
        "source_trace_complete": not hits and all(row["exists"] for row in sources if row["required"]),
    }


def forbidden_source_path_hits(records: list[dict[str, Any]]) -> list[str]:
    hits: list[str] = []
    for row in records:
        path = str(row.get("path") or "").lower().replace("\\", "/")
        for token in FORBIDDEN_PATH_TOKENS:
            if token in path:
                hits.append(f"{row.get('path')}:{token}")
    return sorted(set(hits))


def _record(paths: ProjectPaths, artifact_id: str, path: Path) -> dict[str, Any]:
    required = not artifact_id.startswith("monitoring_")
    return {
        "artifact_id": artifact_id,
        "required": required,
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }

