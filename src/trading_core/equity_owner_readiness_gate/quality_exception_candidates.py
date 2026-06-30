"""Quality exception candidates for owner readiness gate."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_gate.gate_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_quality_exception_candidates(*, as_of_date: str = DEFAULT_AS_OF_DATE, gates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for gate_name, gate in gates.items():
        for reason in gate.get("blocking_reasons", []):
            candidates.append(_candidate(as_of_date, gate_name, "blocking", reason, waiver_allowed=reason != "owner_readiness_score_below_threshold"))
        for warning in gate.get("warnings", []):
            candidates.append(_candidate(as_of_date, gate_name, "warning", warning, waiver_allowed=True))
    return {
        "candidate_list_id": "A-SHARE-QUALITY-EXCEPTION-CANDIDATE-LIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "auto_waiver_allowed": False,
        "waiver_workflow_implemented": False,
        "not_trade_related": True,
    }


def _candidate(as_of_date: str, gate_name: str, severity: str, description: str, *, waiver_allowed: bool) -> dict[str, Any]:
    return {
        "exception_id": f"{as_of_date}:{gate_name}:{description}",
        "source_gate": gate_name,
        "severity": severity,
        "description": description,
        "owner_visibility": True,
        "developer_follow_up_required": severity == "blocking",
        "waiver_allowed": waiver_allowed,
        "waiver_requires_reason": waiver_allowed,
        "auto_waiver_allowed": False,
        "trade_related": False,
        "broker_related": False,
        "order_related": False,
    }
