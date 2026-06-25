"""Audit v0.6.2 forward dry-run start authorization artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.forward_dry_run.start_authorization_common import (
    AUTHORIZATION_NOTICE,
    NEXT_REQUIRED_ACTION,
    RELEASE_CANDIDATE,
    authorization_boundary,
    audit_report,
    non_claim_markdown,
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
    "day1 authorized",
    "day1 prompt generated",
    "run-daily executed",
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


def audit_forward_dry_run_start_authorization(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    artifacts = {
        "scope_plan": read_system(paths, "forward_dry_run_authorization_scope_plan.json"),
        "inventory": read_system(paths, "forward_dry_run_start_prerequisite_inventory.json"),
        "readiness_snapshot": read_system(paths, "current_daily_workflow_readiness_snapshot.json"),
        "manual_confirmation": read_system(paths, "forward_dry_run_manual_confirmation_checklist_v2.json"),
        "owner_authorization": read_system(paths, "forward_dry_run_owner_authorization_packet.json"),
        "start_gate": read_system(paths, "forward_dry_run_start_gate_v062.json"),
        "run_daily_preview": read_system(paths, "forward_dry_run_run_daily_command_preview.json"),
        "day1_eligibility": read_system(paths, "forward_dry_run_day1_prompt_eligibility.json"),
        "protected_residue": read_system(paths, "protected_path_residue_scan.json"),
    }
    blocking: list[str] = []
    for key, payload in artifacts.items():
        if not payload:
            blocking.append(f"missing {key}")
    manual = artifacts["manual_confirmation"]
    owner = artifacts["owner_authorization"]
    gate = artifacts["start_gate"]
    preview = artifacts["run_daily_preview"]
    eligibility = artifacts["day1_eligibility"]
    residue = artifacts["protected_residue"]
    _block_if(blocking, manual.get("manual_confirmation_complete") is True, "manual_confirmation_complete=true in release-default artifact")
    _block_if(blocking, owner.get("forward_dry_run_start_authorized") is True, "forward_dry_run_start_authorized=true in release-default artifact")
    _block_if(blocking, gate.get("day1_start_allowed") is True, "day1_start_allowed=true")
    _block_if(blocking, eligibility.get("day1_prompt_generated") is True, "day1_prompt_generated=true")
    _block_if(blocking, eligibility.get("day1_prompt_eligible") is True, "day1_prompt_eligible=true in release-default artifact")
    _block_if(blocking, preview.get("preview_only") is not True, "run_daily_command_preview.preview_only not true")
    _block_if(blocking, preview.get("executed") is True, "run_daily_command_preview.executed=true")
    _block_if(blocking, preview.get("run_daily_called") is True, "run_daily_called=true")
    _block_if(blocking, int(residue.get("blocker_count", 1) or 0) != 0, "protected path blocker count not zero")
    for name, payload in artifacts.items():
        boundary = payload.get("boundary", {})
        for field in ["run_daily_called", "forward_dry_run_started", "main_ledger_written"]:
            if payload.get(field) is True or boundary.get(field) is True:
                blocking.append(f"{name}.{field}=true")
    blocking.extend(_forbidden_wording_issues(paths))
    payload: dict[str, Any] = {
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "summary": {
            "technical_prerequisites_passed": True,
            "manual_confirmation_complete": False,
            "forward_dry_run_start_authorized": False,
            "day1_start_allowed": False,
            "day1_prompt_eligible": False,
            "day1_prompt_generated": False,
            "recommended_next_action": NEXT_REQUIRED_ACTION,
        },
        "boundary": authorization_boundary("start_authorization_pack_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_start_authorization_audit.json"),
        payload,
        audit_report(paths, "FORWARD_DRY_RUN_START_AUTHORIZATION_AUDIT.md"),
        build_markdown(payload),
    )


def _block_if(blocking: list[str], condition: bool, reason: str) -> None:
    if condition:
        blocking.append(reason)


def _forbidden_wording_issues(paths: ProjectPaths) -> list[str]:
    issues: list[str] = []
    candidates = [
        system_report(paths, "FORWARD_DRY_RUN_AUTHORIZATION_SCOPE_PLAN.md"),
        system_report(paths, "FORWARD_DRY_RUN_START_PREREQUISITE_INVENTORY.md"),
        system_report(paths, "CURRENT_DAILY_WORKFLOW_READINESS_SNAPSHOT.md"),
        system_report(paths, "FORWARD_DRY_RUN_MANUAL_CONFIRMATION_CHECKLIST_V2.md"),
        system_report(paths, "FORWARD_DRY_RUN_OWNER_AUTHORIZATION_PACKET.md"),
        system_report(paths, "FORWARD_DRY_RUN_START_GATE_V062.md"),
        system_report(paths, "FORWARD_DRY_RUN_RUN_DAILY_COMMAND_PREVIEW.md"),
        system_report(paths, "FORWARD_DRY_RUN_DAY1_PROMPT_ELIGIBILITY.md"),
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
        "# Forward Dry-Run Start Authorization Audit",
        "",
        AUTHORIZATION_NOTICE,
        "",
        "## Summary",
        f"- release_candidate: {payload['release_candidate']}",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        "- recommended_next_action: owner_manual_confirmation",
        "",
        "## Boundary",
        *non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

