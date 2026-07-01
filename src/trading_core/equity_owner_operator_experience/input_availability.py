"""Input availability for v0.9.1 operator experience."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_operator_experience.io import load_json
from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, SOURCE_RELEASE_CANDIDATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


V090_FILES = [
    "v090_rc_config",
    "v090_input_availability",
    "v090_source_resolution",
    "v090_date_alignment",
    "v090_full_pytest_result",
    "v090_audit_sweep_result",
    "v090_boundary_sweep_result",
    "v090_source_trace_sweep_result",
    "v090_documentation_freeze_result",
    "v090_known_blocked_state_disclosure",
    "v090_release_candidate_decision",
    "v090_owner_release_summary",
    "v090_source_trace",
    "v090_boundary_check",
    "v090_manifest",
]


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    v090_root = paths.data_dir / "equity_owner_v090_rc" / "daily" / as_of_date
    return {
        **{key: v090_root / f"{key}.json" for key in V090_FILES},
        "v090_rc_audit": paths.data_dir / "equity_data_quality" / "a_share_owner_v090_rc_audit.json",
        "v0821_closeout_review_audit": paths.data_dir / "equity_data_quality" / "a_share_owner_closeout_review_audit.json",
        "v0820_gate_outcome_audit": paths.data_dir / "equity_data_quality" / "a_share_owner_v0820_gate_outcome_audit.json",
        "v0821_unresolved_blocker_register": paths.data_dir / "equity_owner_closeout_review" / "daily" / as_of_date / "unresolved_blocker_register.json",
        "v0821_closeout_review_report": paths.outputs_dir / "equity_owner_closeout_review" / "daily" / as_of_date / "A_SHARE_OWNER_READINESS_CLOSEOUT_REVIEW.md",
    }


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    missing = sorted(key for key, path in sources.items() if not path.exists() and key not in {"v0821_closeout_review_report", "v0820_final_blocked_closeout_report"})
    rc_audit = load_json(sources["v090_rc_audit"])
    full_pytest = load_json(sources["v090_full_pytest_result"])
    decision = load_json(sources["v090_release_candidate_decision"])
    disclosure = load_json(sources["v090_known_blocked_state_disclosure"])
    summary = load_json(sources["v090_owner_release_summary"])
    boundary = load_json(sources["v090_boundary_check"])
    checks = {
        "v090_rc_audit_passed": rc_audit.get("overall_passed") is True,
        "v090_rc_audit_blocking_reasons_empty": rc_audit.get("blocking_reasons") == [],
        "v090_full_pytest_passed": full_pytest.get("overall_passed") is True and full_pytest.get("full_pytest_run") is True,
        "release_candidate_decision_passed": decision.get("decision") == "v090_rc_passed_with_known_blocked_owner_readiness",
        "owner_readiness_state_blocked": disclosure.get("owner_readiness_state") == "blocked",
        "owner_operationally_acceptable_false": disclosure.get("owner_operationally_acceptable") is False,
        "blocked_state_not_misrepresented": disclosure.get("blocked_state_misrepresented_as_acceptable") is False,
        "boundary_clean": boundary.get("overall_passed") is True,
        "source_release_candidate_matches": summary.get("target_version") == SOURCE_RELEASE_CANDIDATE,
    }
    blocking = missing + sorted(key for key, passed in checks.items() if not passed)
    return {
        "availability_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_release_candidate": SOURCE_RELEASE_CANDIDATE,
        "required_sources": {key: str(path) for key, path in sources.items()},
        "missing_required_sources": missing,
        "checks": checks,
        "source_gate_decision": summary.get("source_gate_decision", "blocked"),
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": disclosure.get("owner_operationally_acceptable"),
        "previous_readiness_score": disclosure.get("previous_readiness_score"),
        "minimum_owner_readiness_score": disclosure.get("minimum_owner_readiness_score"),
        "score_gap": disclosure.get("score_gap"),
        "blocked_state_intentional": disclosure.get("blocked_state_intentional"),
        "blocked_state_audited": disclosure.get("blocked_state_audited"),
        "blocked_state_misrepresented_as_acceptable": disclosure.get("blocked_state_misrepresented_as_acceptable"),
        "v090_full_pytest_passed": checks["v090_full_pytest_passed"],
        "v090_audit_sweep_passed": summary.get("audit_sweep_passed") is True,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }
