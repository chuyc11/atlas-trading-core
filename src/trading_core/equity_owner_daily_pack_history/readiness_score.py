"""Owner readiness score."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION


def build_owner_readiness_score(*, as_of_date: str, payloads: dict[str, Any], daily_pack_manifest_sha256: str | None = None) -> dict[str, Any]:
    audit = payloads["owner_daily_pack_audit"]
    status = payloads["owner_daily_status_brief"]
    warning = payloads["warning_issue_digest"]
    safe = payloads["safe_action_digest"]
    boundary = payloads["daily_pack_boundary_check"]
    source_trace = payloads["daily_pack_source_trace"]
    resolution = payloads["daily_pack_source_resolution"]
    blocking_count = int(status.get("blocking_count", 0) or 0)
    warning_count = int(status.get("warning_count", warning.get("warning_count", 0)) or 0)
    safe_action_count = int(status.get("safe_action_count", safe.get("safe_action_count", 0)) or 0)
    score = 100
    explanation: list[str] = ["base_score=100"]
    if blocking_count > 0:
        score -= 40
        explanation.append("minus_40_blocking_count")
    if audit.get("overall_passed") is not True:
        score -= 30
        explanation.append("minus_30_daily_pack_audit_failed")
    if payloads.get("input_availability", {}).get("overall_passed") is False:
        score -= 25
        explanation.append("minus_25_required_source_missing")
    if boundary.get("overall_passed") is not True:
        score -= 20
        explanation.append("minus_20_boundary_not_clean")
    if status.get("protected_path_modifications_detected") is True:
        score -= 20
        explanation.append("minus_20_protected_path_modified")
    if int(status.get("business_output_drift_count", 0) or 0) > 0:
        score -= 15
        explanation.append("minus_15_business_output_drift")
    if source_trace.get("source_trace_complete") is not True:
        score -= 10
        explanation.append("minus_10_source_trace_incomplete")
    warning_penalty = min(warning_count * 3, 30)
    safe_penalty = min(safe_action_count * 2, 20)
    score -= warning_penalty + safe_penalty
    explanation.append(f"minus_{warning_penalty}_warnings")
    explanation.append(f"minus_{safe_penalty}_manual_safe_actions")
    if resolution.get("fallback_used") is True:
        score -= 5
        explanation.append("minus_5_fallback_source_used")
    score = max(0, min(100, int(score)))
    return {
        "score_id": "A-SHARE-OWNER-READINESS-SCORE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "daily_pack_manifest_sha256": daily_pack_manifest_sha256,
        "score": score,
        "grade": grade_for_score(score),
        "overall_status": status.get("overall_status"),
        "blocking_count": blocking_count,
        "warning_count": warning_count,
        "safe_action_count": safe_action_count,
        "automatic_action_count": int(status.get("automatic_action_count", 0) or 0),
        "business_output_drift_count": int(status.get("business_output_drift_count", 0) or 0),
        "protected_path_modifications_detected": status.get("protected_path_modifications_detected") is True,
        "boundary_clean": boundary.get("overall_passed") is True and not boundary.get("blocking_reasons"),
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "score_explanation": explanation,
        "not_trade_instruction": True,
        "owner_readiness_used_as_trade_instruction": False,
    }


def grade_for_score(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"
