"""Manual waiver policy artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_manual_waiver_policy(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "policy_id": "A-SHARE-MANUAL-WAIVER-POLICY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "auto_waiver_allowed": False,
        "manual_waiver_supported": True,
        "manual_waiver_approval_recorded": False,
        "waiver_changes_gate_decision": False,
        "waiver_scope": "owner_review_only",
        "cannot_override": ["broker/order/boundary violations", "protected path modifications", "investment or trading outputs"],
        "cannot_authorize_trading": True,
    }


def build_manual_waiver_request_template(*, as_of_date: str = DEFAULT_AS_OF_DATE, evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "template_id": "A-SHARE-MANUAL-WAIVER-REQUEST-TEMPLATE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "request_status": "not_requested",
        "eligible_exception_ids": [row["exception_id"] for row in evaluation.get("waiver_candidates", []) if row.get("waiver_allowed")],
        "required_reason_fields": ["exception_id", "owner_review_reason", "risk_acknowledgement", "expiration"],
        "auto_submission_enabled": False,
        "approved_for_trading": False,
    }


def build_manual_waiver_decision_record(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "waiver_record_id": "A-SHARE-MANUAL-WAIVER-DECISION-RECORD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "manual_waiver_decision_status": "not_requested",
        "manual_waiver_approval_recorded": False,
        "approved_for_owner_review_only": False,
        "approved_for_trading": False,
        "waiver_changes_gate_decision": False,
        "auto_waiver_allowed": False,
        "waiver_reason": "",
        "waiver_scope": [],
        "waiver_expiration": None,
        "blocking_reasons": [],
        "warnings": [],
    }
