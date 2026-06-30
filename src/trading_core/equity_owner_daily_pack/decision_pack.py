"""Owner operations decision pack."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import (
    ALLOWED_OPERATIONAL_DECISION_CATEGORIES,
    FORBIDDEN_DECISION_CATEGORIES,
    TARGET_VERSION,
)


def build_decision_pack(*, as_of_date: str, payloads: dict) -> dict:
    status = payloads["owner_daily_status_brief"]
    warning = payloads["warning_issue_digest"]
    safe = payloads["safe_action_digest"]
    category = _decision_category(warning, safe)
    forbidden = [category] if category in FORBIDDEN_DECISION_CATEGORIES else []
    if category not in ALLOWED_OPERATIONAL_DECISION_CATEGORIES:
        forbidden.append(category)
    return {
        "pack_id": "A-SHARE-OWNER-OPERATIONS-DECISION-PACK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "decision_pack_type": "owner_operations_decision_pack",
        "not_investment_decision_pack": True,
        "today_status": status.get("overall_status"),
        "what_changed_today": ["daily pack generated from build-output ops refresh"],
        "what_owner_should_review_first": status.get("top_next_step_zh"),
        "research_output_digest": payloads["research_output_digest"],
        "warning_issue_digest": warning,
        "safe_action_digest": safe,
        "protected_path_digest": payloads["protected_path_digest"],
        "boundary_digest": payloads["boundary_digest"],
        "artifact_navigation": payloads.get("daily_pack_artifact_navigation", {}),
        "next_operational_decision": category,
        "not_trade_instruction": True,
        "forbidden_decision_categories_detected": forbidden,
        "overall_passed": not forbidden,
        "blocking_reasons": ["forbidden_decision_category_present"] if forbidden else [],
    }


def _decision_category(warning: dict, safe: dict) -> str:
    if warning.get("blocking_count", 0):
        return "hold_release"
    if safe.get("safe_action_count", 0):
        return "review_safe_actions"
    if warning.get("warning_count", 0):
        return "review_warnings"
    return "no_action_required"

