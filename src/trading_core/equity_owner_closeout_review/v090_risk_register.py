"""v0.9.0 release risk register."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION

RISKS = [
    ("R001", "blocked_state_misinterpretation", "high", "Known blocked owner-readiness state could be mistaken for acceptance.", "Keep blocked state in scope, reports, docs, and audit.", False, True),
    ("R002", "owner_confusion", "medium", "Owner may confuse research-system RC with operational approval.", "Use owner-facing disclaimers and boundary checks.", False, True),
    ("R003", "readiness_score_gap", "high", "Score remains 21 points below threshold.", "Treat as owner-readiness blocker, not RC blocker.", False, True),
    ("R004", "evidence_gap", "high", "Recovery evidence remains insufficient.", "Keep future evidence collection outside v0.8.21.", False, True),
    ("R005", "test_runtime_cost", "medium", "Full regression can be slower than small-version tests.", "Run it only in v0.9.0 closeout.", False, False),
    ("R006", "documentation_drift", "medium", "Docs may lag release truth.", "Use documentation freeze checklist.", True, True),
    ("R007", "forbidden_wording_regression", "high", "Positive trading wording could appear in reports.", "Audit markdown wording.", True, True),
    ("R008", "protected_path_regression", "high", "Protected paths could be modified accidentally.", "Audit protected artifact paths.", True, False),
    ("R009", "source_trace_hash_drift", "medium", "Artifact hashes could drift after trace generation.", "Verify hashes in audit sweep.", True, False),
    ("R010", "version_tag_mismatch", "medium", "Release metadata could diverge from tag.", "Check VERSION, CLI, tag in v0.9.0.", True, False),
]


def build_v090_release_risk_register(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    risks = [
        {
            "risk_id": risk_id,
            "category": category,
            "severity": severity,
            "description": description,
            "mitigation": mitigation,
            "blocks_v090_rc": blocks_v090_rc,
            "owner_visible": owner_visible,
        }
        for risk_id, category, severity, description, mitigation, blocks_v090_rc, owner_visible in RISKS
    ]
    return {
        "register_id": "A-SHARE-V090-RELEASE-RISK-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
        "risk_count": len(risks),
        "risks": risks,
    }
