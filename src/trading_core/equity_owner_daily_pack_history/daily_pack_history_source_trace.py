"""Source trace for daily pack history."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_source_trace(*, paths: ProjectPaths | None, as_of_date: str, generated_at: str, source_paths: dict[str, Path], output_paths: dict[str, Path], command_policy_decisions: dict[str, Any]) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = [_record(paths, key, path, True) for key, path in source_paths.items()]
    outputs = [_record(paths, key, path, False) for key, path in output_paths.items()]
    return {
        "trace_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-SOURCE-TRACE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "source_artifacts": sources,
        "output_artifacts": outputs,
        "boundary_assumptions": [
            "daily_pack_history_only",
            "append_only_history",
            "no_synthetic_history",
            "no_future_dates",
            "no_daily_pack_rerun",
            "no_build_from_existing_data_rerun",
            "no_broker",
            "no_order_preview",
            "no_trade_signal",
        ],
        "command_policy_decisions": command_policy_decisions,
        "source_trace_complete": all(row["exists"] for row in sources if row["required"]),
    }


def _record(paths: ProjectPaths, artifact_id: str, path: Path, required: bool) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "required": required,
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }
