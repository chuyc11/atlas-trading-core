"""Operator capability matrix."""

from __future__ import annotations

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


ALLOWED_CAPABILITIES = [
    "view_rc_report",
    "view_full_regression_result",
    "view_audit_sweep_result",
    "view_known_blocked_state",
    "view_unresolved_blockers",
    "view_artifact_index",
    "view_owner_daily_status",
    "prepare_future_evidence_review",
]

FORBIDDEN_CAPABILITIES = [
    "connect_broker",
    "read_real_account",
    "place_real_order",
    "generate_order_preview",
    "generate_buy_signal",
    "generate_sell_signal",
    "execute_old_run_daily",
    "execute_forward_dry_run_day2",
    "claim_live_trading_ready",
    "claim_owner_readiness_acceptable",
]


def build_operator_capability_matrix(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    rows = []
    rows.extend(
        {
            "capability_id": capability,
            "label": capability.replace("_", " "),
            "allowed": True,
            "reason": "Safe read-only operator experience capability.",
            "source_artifact": "v0.9.0 RC and v0.8.21 closeout artifacts",
            "owner_visible": True,
            "risk_level": "low",
        }
        for capability in ALLOWED_CAPABILITIES
    )
    rows.extend(
        {
            "capability_id": capability,
            "label": capability.replace("_", " "),
            "allowed": False,
            "reason": "Outside v0.9.1 research-only operator experience boundary.",
            "source_artifact": "operator_boundary_check.json",
            "owner_visible": True,
            "risk_level": "blocked",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )
    return {
        "matrix_id": "A-SHARE-OPERATOR-CAPABILITY-MATRIX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "capabilities": rows,
        "forbidden_capabilities_disallowed": all(not row["allowed"] for row in rows if row["capability_id"] in FORBIDDEN_CAPABILITIES),
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
    }
