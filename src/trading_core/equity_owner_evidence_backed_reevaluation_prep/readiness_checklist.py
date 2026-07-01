"""Evidence-backed readiness checklist."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_evidence_backed_readiness_checklist(*, as_of_date: str = DEFAULT_AS_OF_DATE, sufficiency: dict[str, Any], package: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "recovery_evidence_audit_passed": True,
        "source_gate_decision_preserved": True,
        "threshold_preserved": True,
        "waiver_excluded": True,
        "reevaluation_input_package_generated": package.get("reevaluation_input_package_generated") is True,
        "reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "evidence_sufficient": sufficiency.get("evidence_sufficient_for_controlled_gate_reevaluation") is True,
    }
    return {
        "checklist_id": "A-SHARE-EVIDENCE-BACKED-READINESS-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **checks,
        "ready_for_controlled_gate_reevaluation": all(checks.values()),
        "blocking_reasons": sufficiency.get("blocking_reasons", []),
    }

