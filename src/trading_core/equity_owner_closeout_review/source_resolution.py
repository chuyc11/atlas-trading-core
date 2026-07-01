"""Source resolution for v0.8.21 closeout review."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.equity_owner_closeout_review.input_availability import input_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_source_resolution(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    input_availability: dict[str, Any],
) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    blocking: list[str] = []
    if input_availability.get("overall_passed") is not True:
        blocking.append("input_availability_not_passed")
    if input_availability.get("preferred_source") != "v0.8.20_gate_outcome_artifacts":
        blocking.append("preferred_source_not_v0820_gate_outcome")
    return {
        "resolution_id": "A-SHARE-OWNER-CLOSEOUT-SOURCE-RESOLUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "preferred_source": "v0.8.20_gate_outcome_artifacts",
        "supporting_sources": [
            "v0.8.19_evidence_backed_reevaluation_prep_audit",
            "v0.8.18_recovery_evidence_audit",
            "v0.8.17_controlled_reevaluation_audit",
            "v0.8.16_recovery_execution_audit",
            "v0.8.15_recovery_plan_audit",
            "v0.8.14_quality_exception_workflow_audit",
            "v0.8.13_owner_readiness_gate_audit",
        ],
        "no_real_account_inputs": True,
        "no_broker_inputs": True,
        "no_network_refresh_inputs": True,
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }
