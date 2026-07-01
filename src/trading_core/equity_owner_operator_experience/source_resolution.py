"""Source resolution for owner/operator experience."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_operator_experience.input_availability import input_paths
from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, SOURCE_RELEASE_CANDIDATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_source_resolution(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE, input_availability: dict[str, Any] | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = input_availability or {}
    sources = input_paths(paths, as_of_date)
    supporting = [
        {"source_key": "v090_rc_audit", "role": "primary_release_evidence", "path": str(sources["v090_rc_audit"])},
        {"source_key": "v090_owner_release_summary", "role": "owner_readiness_truth", "path": str(sources["v090_owner_release_summary"])},
        {"source_key": "v090_known_blocked_state_disclosure", "role": "blocked_state_truth", "path": str(sources["v090_known_blocked_state_disclosure"])},
        {"source_key": "v0821_unresolved_blocker_register", "role": "blocker_digest_source", "path": str(sources["v0821_unresolved_blocker_register"])},
        {"source_key": "v0820_gate_outcome_audit", "role": "final_blocked_closeout_source", "path": str(sources["v0820_gate_outcome_audit"])},
    ]
    blocking = [] if availability.get("overall_passed") is True else ["input_availability_not_passed"]
    return {
        "resolution_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-SOURCE-RESOLUTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "preferred_source": "v0.9.0_rc_artifacts",
        "source_release_candidate": SOURCE_RELEASE_CANDIDATE,
        "supporting_sources": supporting,
        "source_resolution_prefers_v090_rc": True,
        "no_real_account_inputs": True,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }
