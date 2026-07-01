"""Unresolved owner-readiness blocker register."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_unresolved_blocker_register(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any]) -> dict[str, Any]:
    previous = availability.get("previous_readiness_score")
    minimum = availability.get("minimum_owner_readiness_score")
    blockers = [
        _blocker("B001", "readiness_score_gap", "v0.8.13", "a_share_owner_readiness_gate_audit.json", f"Owner-readiness score remains {previous} against threshold {minimum}.", True, True, False, False, "Improve audited readiness inputs before a future gate reevaluation."),
        _blocker("B002", "missing_recovery_evidence", "v0.8.18", "a_share_owner_recovery_evidence_audit.json", "Recovery evidence is not sufficient to justify a new gate evaluation.", True, True, False, False, "Collect real evidence and rerun the evidence-backed prep in a later version."),
        _blocker("B003", "missing_audit_verified_evidence", "v0.8.19", "a_share_owner_evidence_backed_reevaluation_prep_audit.json", "Audit-verified evidence did not support controlled reevaluation.", True, True, False, False, "Add audit-verifiable evidence before reopening the gate."),
        _blocker("B004", "remaining_evidence_gaps", "v0.8.20", "final_blocked_closeout.json", f"Remaining gap count is {availability.get('remaining_gap_count')}.", True, True, False, False, "Resolve remaining blockers with source-backed artifacts."),
        _blocker("B005", "owner_readiness_not_acceptable", "v0.8.20", "v0820_owner_outcome_summary.json", "Owner operational acceptability is false.", True, True, False, False, "Do not describe the state as owner-ready until a future gate passes."),
        _blocker("B006", "insufficient_history_if_present", "v0.8.20", "v0820_input_availability.json", "Historical sufficiency remains a review item if upstream audits expose it.", True, True, False, False, "Keep the v0.9.0 audit sweep checking history and trace coverage."),
        _blocker("B007", "v090_rc_known_blocked_state", "v0.8.21", "v090_release_candidate_readiness_decision.json", "v0.9.0 RC may proceed only as a documented research closeout RC with known blocked owner-readiness state.", True, False, False, False, "Keep the blocked state explicit in RC scope, docs, audit, and owner-facing reports."),
    ]
    return {
        "register_id": "A-SHARE-OWNER-CLOSEOUT-UNRESOLVED-BLOCKER-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
        "unresolved_blocker_count": len(blockers),
        "blockers_that_block_owner_readiness_acceptance": sum(1 for item in blockers if item["blocks_owner_readiness_acceptance"]),
        "blockers_that_block_v090_rc": sum(1 for item in blockers if item["blocks_v090_rc"]),
        "blockers": blockers,
    }


def _blocker(
    blocker_id: str,
    category: str,
    source_version: str,
    source_artifact: str,
    description: str,
    owner_visible: bool,
    blocks_owner_readiness_acceptance: bool,
    blocks_v090_rc: bool,
    requires_resolution_before_v090: bool,
    recommended_resolution: str,
) -> dict[str, Any]:
    return {
        "blocker_id": blocker_id,
        "category": category,
        "source_version": source_version,
        "source_artifact": source_artifact,
        "description": description,
        "owner_visible": owner_visible,
        "blocks_owner_readiness_acceptance": blocks_owner_readiness_acceptance,
        "blocks_v090_rc": blocks_v090_rc,
        "requires_resolution_before_v090": requires_resolution_before_v090,
        "recommended_resolution": recommended_resolution,
    }
