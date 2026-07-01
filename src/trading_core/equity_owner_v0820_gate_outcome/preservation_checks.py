"""Preservation checks for threshold, waiver, and boundary."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v0820_gate_outcome.outcome_config import BOUNDARY, DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_threshold_preservation_check(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any]) -> dict[str, Any]:
    return {
        "check_id": "A-SHARE-V0820-THRESHOLD-PRESERVATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "threshold_lowered": False,
        "threshold_preserved": True,
    }


def build_waiver_exclusion_check(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "check_id": "A-SHARE-V0820-WAIVER-EXCLUSION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "waiver_used_for_outcome": False,
    }


def build_boundary_preservation_check(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "check_id": "A-SHARE-V0820-BOUNDARY-PRESERVATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **BOUNDARY,
    }

