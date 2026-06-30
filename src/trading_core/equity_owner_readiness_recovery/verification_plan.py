"""Recovery verification plan."""

from __future__ import annotations

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, FORBIDDEN_COMMAND_FRAGMENTS, TARGET_VERSION
from trading_core.equity_owner_readiness_recovery.task_backlog import SAFE_AUDIT_COMMANDS


def build_recovery_verification_plan(*, as_of_date: str = DEFAULT_AS_OF_DATE, backlog: dict | None = None) -> dict:
    tasks = (backlog or {}).get("tasks", [])
    commands = list(SAFE_AUDIT_COMMANDS)
    return {
        "plan_id": "A-SHARE-RECOVERY-VERIFICATION-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "audit_only_commands": commands,
        "forbidden_command_fragments": FORBIDDEN_COMMAND_FRAGMENTS,
        "forbidden_verification_commands_detected": _forbidden_commands(commands),
        "required_evidence_per_task": {task["task_id"]: task["evidence_required"] for task in tasks},
        "expected_audit_artifacts": [
            "a_share_owner_quality_exception_workflow_audit.json",
            "a_share_owner_readiness_gate_audit.json",
            "a_share_owner_daily_pack_history_audit.json",
            "a_share_owner_daily_pack_audit.json",
        ],
        "expected_quality_improvements": ["warnings mapped", "developer follow-up evidence captured", "source explanations clarified"],
        "criteria_for_reevaluation_readiness": ["tasks have completion evidence", "audit-only verification passes", "no threshold lowering", "no auto waiver"],
        "criteria_for_not_ready": ["tasks remain planned", "developer follow-up unresolved", "insufficient evidence"],
        "no_waiver_constraint": True,
        "no_threshold_lowering_constraint": True,
    }


def _forbidden_commands(commands: list[str]) -> list[str]:
    hits = []
    for command in commands:
        lower = command.lower()
        for fragment in FORBIDDEN_COMMAND_FRAGMENTS:
            if fragment == "order":
                continue
            if fragment.lower() in lower:
                hits.append(command)
                break
    return hits
