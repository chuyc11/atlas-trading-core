"""Source resolution for owner recovery evidence."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.equity_owner_recovery_evidence.input_availability import input_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_source_resolution(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE, input_availability: dict[str, Any] | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    blocking = []
    if input_availability and not input_availability.get("overall_passed"):
        blocking.extend(input_availability.get("blocking_reasons", []))
    return {
        "resolution_id": "A-SHARE-OWNER-RECOVERY-EVIDENCE-SOURCE-RESOLUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "preferred_source": "v0.8.17_controlled_gate_reevaluation_artifacts",
        "supporting_sources": [
            "v0.8.16_recovery_execution_artifacts",
            "v0.8.15_recovery_plan_artifacts",
            "v0.8.14_quality_exception_artifacts",
            "v0.8.13_owner_readiness_gate_artifacts",
        ],
        "resolved_sources": {key: str(path) for key, path in input_paths(paths, as_of_date).items()},
        "no_real_account_inputs": True,
        "no_broker_inputs": True,
        "no_order_inputs": True,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
    }

