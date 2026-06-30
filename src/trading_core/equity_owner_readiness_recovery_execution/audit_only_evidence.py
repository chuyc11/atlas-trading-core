"""Audit-only verification evidence."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery_execution.execution_config import DEFAULT_AS_OF_DATE, FORBIDDEN_COMMAND_FRAGMENTS, TARGET_VERSION


def build_audit_only_verification_evidence(*, as_of_date: str = DEFAULT_AS_OF_DATE, verification_plan: dict[str, Any]) -> dict[str, Any]:
    commands = list(verification_plan.get("audit_only_commands", []))
    forbidden = forbidden_verification_commands(commands)
    items = [
        {
            "command": command,
            "executed_by_recovery_execution": False,
            "evidence_available": False,
            "verification_result": "not_run_in_v0.8.16",
        }
        for command in commands
    ]
    return {
        "evidence_id": "A-SHARE-AUDIT-ONLY-VERIFICATION-EVIDENCE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "audit_only_command_count": len(commands),
        "items": items,
        "forbidden_verification_commands_detected": forbidden,
        "audit_only_verification_passed": False,
        "does_not_execute_commands": True,
    }


def forbidden_verification_commands(commands: list[str]) -> list[str]:
    hits = []
    for command in commands:
        lower = command.lower()
        for fragment in FORBIDDEN_COMMAND_FRAGMENTS:
            frag = fragment.lower()
            if frag == "trade" and "trading_core" in lower:
                continue
            if frag == "order" and "owner" in lower:
                continue
            if frag in lower:
                hits.append(command)
                break
    return hits
