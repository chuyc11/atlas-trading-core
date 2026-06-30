"""Threshold policy artifacts for owner readiness gate."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_gate.gate_config import DEFAULT_AS_OF_DATE, DEFAULT_MINIMUM_OWNER_READINESS_SCORE, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_owner_readiness_threshold_policy(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    minimum_owner_readiness_score: int = DEFAULT_MINIMUM_OWNER_READINESS_SCORE,
    allow_known_non_blocking_warnings: bool = True,
    allow_insufficient_history_if_correctly_flagged: bool = True,
) -> dict[str, Any]:
    return _policy(
        "A-SHARE-OWNER-READINESS-THRESHOLD-POLICY",
        as_of_date,
        minimum_owner_readiness_score,
        allow_known_non_blocking_warnings,
        allow_insufficient_history_if_correctly_flagged,
    )


def build_daily_pack_quality_threshold_policy(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    minimum_owner_readiness_score: int = DEFAULT_MINIMUM_OWNER_READINESS_SCORE,
    allow_known_non_blocking_warnings: bool = True,
    allow_insufficient_history_if_correctly_flagged: bool = True,
) -> dict[str, Any]:
    return _policy(
        "A-SHARE-DAILY-PACK-QUALITY-THRESHOLD-POLICY",
        as_of_date,
        minimum_owner_readiness_score,
        allow_known_non_blocking_warnings,
        allow_insufficient_history_if_correctly_flagged,
    )


def _policy(
    policy_id: str,
    as_of_date: str,
    minimum_owner_readiness_score: int,
    allow_known_non_blocking_warnings: bool,
    allow_insufficient_history_if_correctly_flagged: bool,
) -> dict[str, Any]:
    return {
        "policy_id": policy_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "minimum_owner_readiness_score": minimum_owner_readiness_score,
        "minimum_required_artifact_completeness": 1.0,
        "minimum_markdown_report_completeness": 1.0,
        "required_source_trace_complete": True,
        "required_boundary_clean": True,
        "allow_insufficient_history_if_correctly_flagged": allow_insufficient_history_if_correctly_flagged,
        "allow_known_non_blocking_warnings": allow_known_non_blocking_warnings,
        "allow_timestamp_hash_metadata_drift": True,
        "allow_business_output_drift": False,
        "allow_protected_path_modifications": False,
        "allow_automatic_actions": False,
        "allow_external_notifications": False,
        "allow_remediation_execution": False,
        "allow_forbidden_wording": False,
        "not_investment_decision_pack_required": True,
        "owner_readiness_used_as_trade_instruction_required": False,
    }
