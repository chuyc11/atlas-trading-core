"""Full audit sweep for v0.9.0 RC."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_closeout_review.closeout_review_audit import audit_a_share_owner_closeout_review
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_reevaluation_audit import audit_a_share_owner_controlled_gate_reevaluation
from trading_core.equity_owner_evidence_backed_reevaluation_prep.evidence_backed_prep_audit import audit_a_share_owner_evidence_backed_reevaluation_prep
from trading_core.equity_owner_quality_exceptions.quality_exception_audit import audit_a_share_owner_quality_exceptions
from trading_core.equity_owner_readiness_gate.owner_readiness_gate_audit import audit_a_share_owner_readiness_gate
from trading_core.equity_owner_readiness_recovery.recovery_audit import audit_a_share_owner_readiness_recovery
from trading_core.equity_owner_readiness_recovery_execution.recovery_execution_audit import audit_a_share_owner_readiness_recovery_execution
from trading_core.equity_owner_recovery_evidence.recovery_evidence_audit import audit_a_share_owner_recovery_evidence
from trading_core.equity_owner_v0820_gate_outcome.v0820_outcome_audit import audit_a_share_owner_v0820_gate_outcome
from trading_core.equity_owner_v090_rc.io import load_json
from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

AUDIT_SPECS = [
    ("a_share_owner_readiness_gate_audit", audit_a_share_owner_readiness_gate, "a_share_owner_readiness_gate_audit.json"),
    ("a_share_owner_quality_exception_workflow_audit", audit_a_share_owner_quality_exceptions, "a_share_owner_quality_exception_workflow_audit.json"),
    ("a_share_owner_readiness_recovery_audit", audit_a_share_owner_readiness_recovery, "a_share_owner_readiness_recovery_audit.json"),
    ("a_share_owner_readiness_recovery_execution_audit", audit_a_share_owner_readiness_recovery_execution, "a_share_owner_readiness_recovery_execution_audit.json"),
    ("a_share_owner_controlled_gate_reevaluation_audit", audit_a_share_owner_controlled_gate_reevaluation, "a_share_owner_controlled_gate_reevaluation_audit.json"),
    ("a_share_owner_recovery_evidence_audit", audit_a_share_owner_recovery_evidence, "a_share_owner_recovery_evidence_audit.json"),
    ("a_share_owner_evidence_backed_reevaluation_prep_audit", audit_a_share_owner_evidence_backed_reevaluation_prep, "a_share_owner_evidence_backed_reevaluation_prep_audit.json"),
    ("a_share_owner_v0820_gate_outcome_audit", audit_a_share_owner_v0820_gate_outcome, "a_share_owner_v0820_gate_outcome_audit.json"),
    ("a_share_owner_closeout_review_audit", audit_a_share_owner_closeout_review, "a_share_owner_closeout_review_audit.json"),
]


def run_audit_sweep(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    items = []
    for audit_name, fn, file_name in AUDIT_SPECS:
        result = fn(as_of_date=as_of_date, paths=paths)
        artifact_path = paths.data_dir / "equity_data_quality" / file_name
        payload = load_json(artifact_path)
        items.append(_item(audit_name, artifact_path, payload, result))
    self_path = paths.data_dir / "equity_data_quality" / "a_share_owner_v090_rc_audit.json"
    self_payload = load_json(self_path)
    items.append(
        {
            "audit_name": "a_share_owner_v090_rc_audit",
            "audit_artifact_path": str(self_path),
            "audit_exists": self_path.exists(),
            "overall_passed": self_payload.get("overall_passed"),
            "blocking_reasons": self_payload.get("blocking_reasons", []),
            "warnings_count": len(self_payload.get("warnings", [])) if isinstance(self_payload.get("warnings"), list) else self_payload.get("warnings", 0),
            "required_for_v090_rc": False,
            "sweep_passed": True,
            "self_audit_generated_after_sweep": True,
        }
    )
    required_items = [item for item in items if item["required_for_v090_rc"]]
    blocking = [] if all(item["sweep_passed"] for item in required_items) else ["audit_sweep_failed"]
    return {
        "result_id": "A-SHARE-V090-AUDIT-SWEEP-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "audit_sweep_run": True,
        "audit_sweep_passed": not blocking,
        "audit_sweep_item_count": len(items),
        "failed_audit_sweep_items": [item["audit_name"] for item in required_items if not item["sweep_passed"]],
        "items": items,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _item(audit_name: str, path: Path, payload: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    passed = payload.get("overall_passed", result.get("overall_passed")) is True
    return {
        "audit_name": audit_name,
        "audit_artifact_path": str(path),
        "audit_exists": path.exists(),
        "overall_passed": payload.get("overall_passed", result.get("overall_passed")),
        "blocking_reasons": payload.get("blocking_reasons", result.get("blocking_reasons", [])),
        "warnings_count": len(payload.get("warnings", [])) if isinstance(payload.get("warnings"), list) else result.get("warnings", 0),
        "required_for_v090_rc": True,
        "boundary_summary": payload.get("boundary", result.get("boundary", {})),
        "source_trace_summary": payload.get("checks", {}),
        "sweep_passed": path.exists() and passed and payload.get("blocking_reasons", []) in ([], None),
    }
