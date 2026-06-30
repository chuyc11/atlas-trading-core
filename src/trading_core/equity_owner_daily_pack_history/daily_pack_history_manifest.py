"""Manifest and summary for owner daily pack history."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.system.common import relative


def build_manifest(*, paths, as_of_date: str, mode: str, generated_at: str, output_artifacts: dict, source_artifacts: dict, append_result: dict, snapshot: dict, score: dict, sufficiency: dict, boundary: dict, source_trace: dict) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "generated_at": generated_at,
        "source_workflow_mode": "build_from_existing_data",
        "append_only_history": True,
        "allow_synthetic_history": False,
        "synthetic_history_used": False,
        "future_dates_used": False,
        "daily_pack_history_observation_count": snapshot.get("daily_pack_history_observation_count"),
        "trend_analysis_available": sufficiency.get("trend_analysis_available"),
        "readiness_trend_status": sufficiency.get("readiness_trend_status"),
        "owner_readiness_score": score.get("score"),
        "owner_readiness_grade": score.get("grade"),
        "append_result": append_result,
        "source_trace_complete": source_trace.get("source_trace_complete"),
        "boundary": boundary,
        "output_artifacts": {key: relative(path, paths.project_root) for key, path in output_artifacts.items()},
        "source_artifacts": {key: relative(path, paths.project_root) for key, path in source_artifacts.items()},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_summary(*, as_of_date: str, mode: str, availability: dict, append_result: dict, snapshot: dict, score: dict, sufficiency: dict, boundary: dict) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "source_workflow_mode": "build_from_existing_data",
        "overall_passed": availability.get("overall_passed") is True and boundary.get("overall_passed") is True,
        "blocking_reasons": sorted(set(availability.get("blocking_reasons", []) + boundary.get("blocking_reasons", []))),
        "warnings": sorted(set(availability.get("warnings", []) + append_result.get("warnings", []) + boundary.get("warnings", []))),
        "owner_daily_pack_audit_passed": availability.get("owner_daily_pack_audit_passed") is True,
        "daily_pack_history_observation_count": snapshot.get("daily_pack_history_observation_count"),
        "minimum_required_observations": sufficiency.get("minimum_required_observations"),
        "trend_analysis_available": sufficiency.get("trend_analysis_available"),
        "readiness_trend_status": sufficiency.get("readiness_trend_status"),
        "insufficient_history_correctly_flagged": sufficiency.get("insufficient_history_correctly_flagged"),
        "owner_readiness_score": score.get("score"),
        "owner_readiness_grade": score.get("grade"),
        "append_only_history": True,
        "idempotent_append": append_result.get("idempotent_append"),
        "duplicate_detected": append_result.get("duplicate_detected"),
        "same_date_changed_content_warning": append_result.get("same_date_changed_content_warning"),
        "synthetic_history_used": False,
        "future_dates_used": False,
        "owner_readiness_used_as_trade_instruction": False,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
