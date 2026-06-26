"""Audit v0.6.2.1 owner authorization materialization artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.start_authorization_common import (
    MATERIALIZATION_NEXT_REQUIRED_ACTION,
    MATERIALIZATION_NOTICE,
    MATERIALIZATION_RELEASE_CANDIDATE,
    audit_report,
    materialization_boundary,
    materialization_non_claim_markdown,
    paths_or_default,
    read_system,
    system_json,
    system_report,
    write_artifact,
)
from trading_core.storage.file_paths import ProjectPaths


FORBIDDEN_POSITIVE_PHRASES = [
    "forward dry-run started",
    "forward dry-run validated",
    "run-daily executed",
    "day1 executed",
    "strategy effectiveness proven",
    "live trading ready",
    "broker connected",
    "real orders supported",
    "promotion approved",
    "ML approved for trading",
    "LLM approved for trading",
    "RL approved for trading",
]
NEGATION_MARKERS = ["not ", "does not ", "no ", "without ", "false", "pending", "not_", "not-"]


def audit_forward_dry_run_authorization_materialization(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    artifacts = {
        "owner_manual_confirmation_record": read_system(paths, "forward_dry_run_owner_manual_confirmation_record.json"),
        "completed_manual_confirmation": read_system(paths, "forward_dry_run_manual_confirmation_checklist_v2_completed.json"),
        "updated_owner_authorization": read_system(paths, "forward_dry_run_owner_authorization_packet_authorized.json"),
        "start_gate_revalidation": read_system(paths, "forward_dry_run_start_gate_v0621.json"),
        "day1_prompt_eligibility_revalidation": read_system(paths, "forward_dry_run_day1_prompt_eligibility_v0621.json"),
        "run_daily_preview": read_system(paths, "forward_dry_run_run_daily_command_preview.json"),
    }
    blocking: list[str] = []
    for key, payload in artifacts.items():
        if not payload:
            blocking.append(f"missing {key}")

    record = artifacts["owner_manual_confirmation_record"]
    completed = artifacts["completed_manual_confirmation"]
    authorized = artifacts["updated_owner_authorization"]
    gate = artifacts["start_gate_revalidation"]
    eligibility = artifacts["day1_prompt_eligibility_revalidation"]
    preview = artifacts["run_daily_preview"]

    _block_if(blocking, record.get("owner_confirmation_recorded") is not True, "owner manual confirmation record missing confirmation")
    _block_if(blocking, completed.get("manual_confirmation_complete") is not True, "manual_confirmation_complete not true")
    _block_if(blocking, authorized.get("forward_dry_run_start_authorized") is not True, "forward_dry_run_start_authorized not true")
    _block_if(blocking, gate.get("day1_prompt_eligible") is not True, "day1_prompt_eligible not true in start gate")
    _block_if(blocking, gate.get("day1_start_allowed") is True, "day1_start_allowed=true")
    _block_if(blocking, gate.get("day1_execution_requires_separate_prompt") is not True, "day1_execution_requires_separate_prompt not true")
    _block_if(blocking, eligibility.get("day1_prompt_eligible") is not True, "day1_prompt_eligible not true")
    _block_if(blocking, eligibility.get("day1_prompt_generated") is True, "day1_prompt_generated=true")
    _block_if(blocking, preview.get("executed") is True, "run-daily command preview executed=true")
    _block_if(blocking, preview.get("run_daily_called") is True, "run_daily_called=true")

    for name, payload in artifacts.items():
        boundary = payload.get("boundary", {})
        for field in ["run_daily_called", "forward_dry_run_started", "main_ledger_written"]:
            if payload.get(field) is True or boundary.get(field) is True:
                blocking.append(f"{name}.{field}=true")
    blocking.extend(_forbidden_wording_issues(paths))

    payload: dict[str, Any] = {
        "release_candidate": MATERIALIZATION_RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "summary": {
            "manual_confirmation_complete": True,
            "forward_dry_run_start_authorized": True,
            "day1_prompt_eligible": True,
            "day1_prompt_generated": False,
            "day1_start_allowed": False,
            "recommended_next_action": MATERIALIZATION_NEXT_REQUIRED_ACTION,
        },
        "boundary": materialization_boundary("authorization_materialization_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_authorization_materialization_audit.json"),
        payload,
        audit_report(paths, "FORWARD_DRY_RUN_AUTHORIZATION_MATERIALIZATION_AUDIT.md"),
        build_markdown(payload),
    )


def _block_if(blocking: list[str], condition: bool, reason: str) -> None:
    if condition:
        blocking.append(reason)


def _forbidden_wording_issues(paths: ProjectPaths) -> list[str]:
    issues: list[str] = []
    candidates = [
        system_report(paths, "FORWARD_DRY_RUN_OWNER_MANUAL_CONFIRMATION_RECORD.md"),
        system_report(paths, "FORWARD_DRY_RUN_MANUAL_CONFIRMATION_CHECKLIST_V2_COMPLETED.md"),
        system_report(paths, "FORWARD_DRY_RUN_OWNER_AUTHORIZATION_PACKET_AUTHORIZED.md"),
        system_report(paths, "FORWARD_DRY_RUN_START_GATE_V0621.md"),
        system_report(paths, "FORWARD_DRY_RUN_DAY1_PROMPT_ELIGIBILITY_V0621.md"),
        paths.project_root / "docs" / "OWNER_MANUAL_CONFIRMATION_MATERIALIZATION.md",
        paths.project_root / "docs" / "FORWARD_DRY_RUN_START_AUTHORIZATION.md",
        paths.project_root / "docs" / "FORWARD_DRY_RUN_START_GATE.md",
        paths.project_root / "docs" / "FORWARD_DRY_RUN_DAY1_ELIGIBILITY.md",
    ]
    for path in candidates:
        if not path.exists():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            lower = line.lower()
            for phrase in FORBIDDEN_POSITIVE_PHRASES:
                if phrase.lower() in lower and not _is_negated(lower, phrase.lower()):
                    issues.append(f"forbidden positive wording: {path.name}:{number}:{phrase}")
    return issues


def _is_negated(line: str, phrase: str) -> bool:
    idx = line.find(phrase)
    prefix = line[max(0, idx - 24) : idx]
    return any(marker in prefix for marker in NEGATION_MARKERS) or any(marker in line for marker in ["=false", ": false"])


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Authorization Materialization Audit",
        "",
        MATERIALIZATION_NOTICE,
        "",
        "## Summary",
        f"- release_candidate: {payload['release_candidate']}",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        "- recommended_next_action: owner_requests_day1_prompt",
        "",
        "## Boundary",
        *materialization_non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

