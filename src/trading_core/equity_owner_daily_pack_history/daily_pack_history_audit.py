"""Audit for v0.8.12 owner daily pack history."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file, write_report
from trading_core.equity_owner_daily_pack_history.daily_pack_history_boundary import _forbidden_artifacts, _forbidden_wording_hits
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import (
    BOUNDARY,
    DEFAULT_AS_OF_DATE,
    FILES,
    INDEX_FILES,
    RECOMMENDED_NEXT_VERSION,
    REPORTS,
    TARGET_VERSION,
    artifact_paths,
)
from trading_core.equity_owner_daily_pack_history.daily_pack_history_report import render_audit
from trading_core.equity_owner_daily_pack_history.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_owner_daily_pack_history(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = artifact_paths(paths, as_of_date)
    payloads = {
        key: load_json(path)
        for key, path in artifacts.items()
        if key in FILES or key in INDEX_FILES
    }
    checks = _checks(paths=paths, as_of_date=as_of_date, artifacts=artifacts, payloads=payloads)
    blocking = sorted(key for key, passed in checks.items() if not passed)
    availability = payloads.get("daily_pack_history_input_availability", {})
    snapshot = payloads.get("daily_pack_history_snapshot", {})
    suff = payloads.get("owner_readiness_trend_sufficiency", {})
    score = payloads.get("owner_readiness_score", {})
    append = payloads.get("daily_pack_history_append_result", {})
    boundary = payloads.get("daily_pack_history_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("daily_pack_history_config", {}).get("mode", "build_owner_readiness_trends"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "input_checks": {
            "owner_daily_pack_audit_passed": availability.get("owner_daily_pack_audit_passed", False),
        },
        "history_checks": {
            "append_only_history": append.get("append_completed") is True,
            "daily_pack_history_observation_count": snapshot.get("daily_pack_history_observation_count"),
            "minimum_required_observations": suff.get("minimum_required_observations"),
            "trend_analysis_available": suff.get("trend_analysis_available"),
            "insufficient_history_correctly_flagged": suff.get("insufficient_history_correctly_flagged"),
            "synthetic_history_used": suff.get("synthetic_history_used"),
            "future_dates_used": suff.get("future_dates_used"),
        },
        "readiness_checks": {
            "owner_readiness_score_valid": isinstance(score.get("score"), int) and 0 <= score.get("score") <= 100,
            "owner_readiness_score_min": 0,
            "owner_readiness_score_max": 100,
            "owner_readiness_used_as_trade_instruction": score.get("owner_readiness_used_as_trade_instruction") is True,
            "no_fabricated_trends": suff.get("no_fabricated_trends") is True,
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY},
        "append_result": {
            "idempotent_append": append.get("idempotent_append"),
            "duplicate_detected": append.get("duplicate_detected"),
            "same_date_changed_content_warning": append.get("same_date_changed_content_warning"),
            "records_before": append.get("records_before"),
            "records_after": append.get("records_after"),
        },
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    result = write_report(
        artifacts["daily_pack_history_audit_json"],
        audit,
        artifacts["daily_pack_history_audit_report"],
        render_audit(audit),
    )
    return {
        "audit_id": result["audit_id"],
        "overall_passed": result["overall_passed"],
        "blocking_reasons": result["blocking_reasons"],
        "warnings": len(result["warnings"]),
        "input_checks": result["input_checks"],
        "history_checks": result["history_checks"],
        "readiness_checks": result["readiness_checks"],
        "boundary": result["boundary"],
        "append_result": result["append_result"],
        "recommended_next_version": result["recommended_next_version"],
        "json_path": str(artifacts["daily_pack_history_audit_json"]),
        "report_path": str(artifacts["daily_pack_history_audit_report"]),
    }


def _checks(*, paths: ProjectPaths, as_of_date: str, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    availability = payloads.get("daily_pack_history_input_availability", {})
    append = payloads.get("daily_pack_history_append_result", {})
    snapshot = payloads.get("daily_pack_history_snapshot", {})
    suff = payloads.get("owner_readiness_trend_sufficiency", {})
    score = payloads.get("owner_readiness_score", {})
    safe = payloads.get("safe_action_trend_baseline", {})
    protected = payloads.get("protected_path_trend_baseline", {})
    boundary_trend = payloads.get("boundary_trend_baseline", {})
    trace = payloads.get("daily_pack_history_source_trace", {})
    boundary = payloads.get("daily_pack_history_boundary_check", {})
    manifest = payloads.get("daily_pack_history_manifest", {})
    summary = payloads.get("daily_pack_history_summary", {})
    records = payloads.get("daily_pack_history_index", {}).get("records", [])
    current_forbidden_artifacts = _forbidden_artifacts(paths, as_of_date)
    current_forbidden_wording = _forbidden_wording_hits(paths, as_of_date)
    return {
        "json_artifacts_present": all(artifacts[key].exists() for key in FILES),
        "history_indexes_present": all(artifacts[key].exists() for key in INDEX_FILES),
        "markdown_reports_present": all(artifacts[key].exists() for key in REPORTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload and "target_version" in payload),
        "owner_daily_pack_audit_passed": availability.get("owner_daily_pack_audit_passed") is True,
        "append_only_rules_respected": append.get("append_completed") is True and manifest.get("append_only_history") is True,
        "duplicate_handling_recorded": "duplicate_detected" in append and "idempotent_append" in append,
        "history_observation_count_matches": snapshot.get("daily_pack_history_observation_count") == len(records),
        "trend_insufficiency_consistent": _trend_sufficiency_consistent(suff),
        "synthetic_history_false": suff.get("synthetic_history_used") is False and summary.get("synthetic_history_used") is False,
        "future_dates_false": suff.get("future_dates_used") is False and summary.get("future_dates_used") is False,
        "owner_readiness_score_valid": isinstance(score.get("score"), int) and 0 <= score.get("score") <= 100,
        "owner_readiness_not_trade_instruction": score.get("owner_readiness_used_as_trade_instruction") is False and summary.get("owner_readiness_used_as_trade_instruction") is False,
        "no_fabricated_trends": suff.get("no_fabricated_trends") is True,
        "safe_action_trend_clean": safe.get("safe_actions_not_trade_related") is True and not safe.get("forbidden_safe_action_hits"),
        "protected_path_trend_clean": protected.get("protected_path_trend_clean") is True,
        "boundary_trend_clean": boundary_trend.get("boundary_trend_clean") is True,
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_clean": boundary.get("overall_passed") is True and _boundary_fields_clean(boundary),
        "no_forbidden_artifacts": not boundary.get("forbidden_artifacts_present") and not current_forbidden_artifacts,
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits") and not current_forbidden_wording,
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-DAILY-PACK-HISTORY-MANIFEST",
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-DAILY-PACK-HISTORY-SUMMARY",
    }


def _trend_sufficiency_consistent(suff: dict[str, Any]) -> bool:
    count = suff.get("daily_pack_history_observation_count")
    minimum = suff.get("minimum_required_observations")
    if not isinstance(count, int) or not isinstance(minimum, int):
        return False
    available = count >= minimum
    return suff.get("trend_analysis_available") is available and suff.get("readiness_trend_status") == ("available" if available else "insufficient_history")


def _boundary_fields_clean(boundary: dict[str, Any]) -> bool:
    for key, expected in BOUNDARY.items():
        if boundary.get(key) is not expected:
            return False
    return True


def _source_hashes_match(paths: ProjectPaths, trace: dict[str, Any]) -> bool:
    for row in trace.get("source_artifacts", []):
        path = Path(row.get("path", ""))
        if not path.is_absolute():
            path = paths.project_root / path
        if row.get("required") is True and (not path.exists() or not row.get("sha256")):
            return False
        if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
            return False
    return True
