"""Known blocked state banner and explanation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_known_blocked_state_banner(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any]) -> dict[str, Any]:
    score = availability.get("previous_readiness_score")
    threshold = availability.get("minimum_owner_readiness_score")
    return {
        "banner_id": "A-SHARE-KNOWN-BLOCKED-STATE-BANNER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "severity": "blocked",
        "headline": "Owner-readiness is BLOCKED.",
        "messages": [
            f"Score {score} is below threshold {threshold}.",
            "This is intentional and audited.",
            "This is not a live-trading-ready state.",
            "This is not an order instruction.",
        ],
        "owner_operationally_acceptable": availability.get("owner_operationally_acceptable"),
        "owner_visible": True,
        "overall_passed": availability.get("owner_operationally_acceptable") is False,
        "blocking_reasons": [],
        "warnings": [],
    }


def build_known_blocked_state_explanation(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any]) -> dict[str, Any]:
    return {
        "explanation_id": "A-SHARE-KNOWN-BLOCKED-STATE-EXPLANATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": availability.get("owner_operationally_acceptable"),
        "what_blocked_means": "The research system RC passed, but owner operational acceptability did not pass.",
        "why_blocked_is_not_system_failure": "The blocked state is expected because score and evidence thresholds are not met.",
        "what_is_safe_to_view": ["status card", "RC report", "full regression result", "audit sweep result", "known blocked state disclosure", "unresolved blockers"],
        "what_is_not_allowed": ["broker connection", "real account read", "real orders", "order preview", "trading signals", "old run-daily", "official day2"],
        "what_needs_future_work": "Future evidence collection and operator usability work before any controlled reevaluation can be considered.",
        "owner_misunderstanding_prevention": [
            "Do not describe blocked as acceptable.",
            "Do not describe the RC as live-ready.",
            "Do not treat operator status as an order instruction.",
        ],
        "overall_passed": availability.get("blocked_state_misrepresented_as_acceptable") is False,
        "blocking_reasons": [],
        "warnings": [],
    }
