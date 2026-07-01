"""Boundary check for v0.9.0 RC."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v090_rc.v090_config import BOUNDARY, DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_boundary_check(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any], full_pytest: dict[str, Any], audit_sweep: dict[str, Any], boundary_sweep: dict[str, Any]) -> dict[str, Any]:
    blocking = list(boundary_sweep.get("blocking_reasons", []))
    return {
        "boundary_id": "A-SHARE-OWNER-V090-RC-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": availability.get("source_gate_decision"),
        "owner_operationally_acceptable": availability.get("owner_operationally_acceptable"),
        "full_pytest_run": full_pytest.get("full_pytest_run"),
        "audit_sweep_run": audit_sweep.get("audit_sweep_run"),
        **BOUNDARY,
        "forbidden_artifacts_present": boundary_sweep.get("forbidden_artifacts_present", []),
        "forbidden_wording_positive_hits": boundary_sweep.get("forbidden_wording_positive_hits", []),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": list(boundary_sweep.get("warnings", [])),
    }
