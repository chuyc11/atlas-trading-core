"""Manifest and summary for ops history baselines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_ops_history.ops_history_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_ops_history_manifest(
    *,
    as_of_date: str,
    generated_at: str,
    mode: str,
    run_record: dict[str, Any],
    append_result: dict[str, Any],
    snapshot: dict[str, Any],
    trend_sufficiency: dict[str, Any],
    boundary: dict[str, Any],
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OPS-HISTORY-BASELINE-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "mode": mode,
        "source_version": run_record.get("source_version"),
        "ops_health_score": run_record.get("ops_health_score"),
        "ops_health_grade": run_record.get("ops_health_grade"),
        "overall_status": run_record.get("overall_status"),
        "run_history_observation_count": snapshot.get("run_history_observation_count"),
        "trend_analysis_available": trend_sufficiency.get("trend_analysis_available"),
        "baseline_status": trend_sufficiency.get("baseline_status"),
        "append_only_history": append_result.get("append_completed") is True,
        "synthetic_history_used": trend_sufficiency.get("synthetic_history_used") is True,
        "future_dates_used": trend_sufficiency.get("future_dates_used") is True,
        "commands_executed": boundary.get("commands_executed", []),
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_ops_history_summary(*, as_of_date: str, mode: str, manifest: dict[str, Any], append_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OPS-HISTORY-BASELINE-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "source_version": manifest.get("source_version"),
        "ops_health_score": manifest.get("ops_health_score"),
        "ops_health_grade": manifest.get("ops_health_grade"),
        "overall_status": manifest.get("overall_status"),
        "run_history_observation_count": manifest.get("run_history_observation_count"),
        "trend_analysis_available": manifest.get("trend_analysis_available"),
        "baseline_status": manifest.get("baseline_status"),
        "append_completed": append_result.get("append_completed"),
        "idempotent_append": append_result.get("idempotent_append"),
        "synthetic_history_used": manifest.get("synthetic_history_used"),
        "future_dates_used": manifest.get("future_dates_used"),
        "commands_executed": manifest.get("commands_executed", []),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

