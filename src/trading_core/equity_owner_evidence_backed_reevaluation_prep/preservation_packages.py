"""Threshold, waiver, and boundary preservation packages."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import BOUNDARY, DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_gate_threshold_preservation_package(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any]) -> dict[str, Any]:
    return {
        "package_id": "A-SHARE-GATE-THRESHOLD-PRESERVATION-PACKAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "threshold_lowered": False,
        "threshold_preserved": True,
    }


def build_waiver_exclusion_package(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "package_id": "A-SHARE-WAIVER-EXCLUSION-PACKAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "waiver_used_to_change_gate_status": False,
    }


def build_boundary_preservation_package(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "package_id": "A-SHARE-BOUNDARY-PRESERVATION-PACKAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **BOUNDARY,
    }

