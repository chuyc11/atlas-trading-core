"""Safe operator action menu."""

from __future__ import annotations

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, FORBIDDEN_ACTION_TYPES, TARGET_VERSION


ALLOWED_ACTIONS = [
    ("view_status", "View owner daily status", "Open the current owner/operator status card.", "A_SHARE_OWNER_DAILY_OPERATOR_STATUS.md"),
    ("view_rc_report", "View v0.9.0 RC report", "Open release-candidate evidence.", "A_SHARE_V090_RC_REPORT.md"),
    ("view_known_blocked_state", "View known blocked state", "Open blocked-state guide.", "A_SHARE_KNOWN_BLOCKED_STATE_GUIDE.md"),
    ("view_full_regression_result", "View full regression result", "Open v0.9.0 full pytest result.", "A_SHARE_V090_FULL_REGRESSION_RESULT.md"),
    ("view_audit_sweep_result", "View audit sweep result", "Open v0.9.0 audit sweep result.", "A_SHARE_V090_AUDIT_SWEEP_RESULT.md"),
    ("view_closeout_review", "View closeout review", "Open v0.8.21 closeout review.", "A_SHARE_OWNER_READINESS_CLOSEOUT_REVIEW.md"),
    ("view_final_blocked_closeout", "View final blocked closeout", "Open v0.8.20 final blocked closeout audit.", "a_share_owner_v0820_gate_outcome_audit.json"),
    ("view_unresolved_blockers", "View unresolved blockers", "Open unresolved blocker digest.", "unresolved_blocker_digest.json"),
    ("view_artifact_navigation_index", "View artifact index", "Open artifact navigation index.", "A_SHARE_ARTIFACT_NAVIGATION_INDEX.md"),
]


def build_operator_action_menu(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    actions = [
        {
            "action_id": action_type,
            "label": label,
            "description": description,
            "action_type": action_type,
            "allowed": True,
            "safe_command_if_any": "",
            "source_artifact": artifact,
            "expected_output": "read-only artifact view",
            "owner_visible": True,
            "forbidden_reason_if_not_allowed": "",
        }
        for action_type, label, description, artifact in ALLOWED_ACTIONS
    ]
    forbidden = sorted({str(row["action_type"]) for row in actions}.intersection(FORBIDDEN_ACTION_TYPES))
    return {
        "menu_id": "A-SHARE-OPERATOR-ACTION-MENU",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "actions": actions,
        "forbidden_operator_actions_present": bool(forbidden),
        "forbidden_action_types_present": forbidden,
        "upstream_workflow_actions_present": False,
        "overall_passed": not forbidden,
        "blocking_reasons": ["forbidden_operator_actions_present"] if forbidden else [],
        "warnings": [],
    }
