"""Recovery risk register."""

from __future__ import annotations

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_recovery_risk_register(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    risks = [
        "threshold_weakening_risk",
        "waiver_misuse_risk",
        "history_insufficiency_misinterpretation_risk",
        "owner_confusion_between_ops_and_trading_risk",
        "source_trace_regression_risk",
        "protected_path_regression_risk",
        "boundary_regression_risk",
    ]
    return {
        "register_id": "A-SHARE-RECOVERY-RISK-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "risks": [
            {
                "risk_id": risk,
                "severity": "high" if "threshold" in risk or "boundary" in risk else "medium",
                "description": risk,
                "mitigation": "keep recovery as non-trading planned workflow with audit-only verification",
                "owner_visible": True,
                "blocking_if_triggered": True,
            }
            for risk in risks
        ],
    }
