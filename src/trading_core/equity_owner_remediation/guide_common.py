"""Shared remediation guide helpers."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_remediation.remediation_mapping import DISALLOWED_ACTIONS
from trading_core.equity_owner_remediation.remediation_config import TARGET_VERSION


DISCLAIMER_LINES = [
    "This guide is not an investment recommendation.",
    "This guide does not authorize trades.",
    "This guide does not connect broker.",
    "This guide does not place orders.",
]


def build_guide(guide_id: str, as_of_date: str, categories: list[str], steps: list[str], artifacts: list[str], cli_checks: list[str]) -> dict[str, Any]:
    return {
        "guide_id": guide_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "applicable_issue_categories": categories,
        "safe_diagnostic_steps": steps,
        "safe_artifacts_to_open": [item.format(as_of_date=as_of_date) for item in artifacts],
        "safe_cli_checks": [item.format(as_of_date=as_of_date) for item in cli_checks],
        "manual_review_required": True,
        "owner_decision_points": ["Decide whether the issue is understood.", "Decide whether developer escalation is required."],
        "disallowed_actions": list(DISALLOWED_ACTIONS),
        "success_criteria": ["Relevant audit is passing.", "Boundary remains clean.", "Source trace is complete."],
        "failure_escalation": "Escalate to developer if validation remains failing or any boundary field is unsafe.",
        "disclaimer": list(DISCLAIMER_LINES),
    }
