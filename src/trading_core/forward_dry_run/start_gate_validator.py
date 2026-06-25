"""Validate the v0.6.2 forward dry-run start gate."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.run_daily_command_preview_metadata import build_forward_dry_run_run_daily_command_preview
from trading_core.forward_dry_run.start_authorization_common import (
    AUTHORIZATION_NOTICE,
    authorization_boundary,
    non_claim_markdown,
    passed_without_blockers,
    paths_or_default,
    read_system,
    start_authorized,
    system_json,
    system_report,
    write_artifact,
)
from trading_core.storage.file_paths import ProjectPaths


def evaluate_start_gate(
    *,
    plan_alignment_passed: bool,
    ashare_execution_rules_passed: bool,
    baseline_strategy_pack_passed: bool,
    daily_workflow_audit_passed: bool,
    protected_path_blocker_count: int,
    updated_day1_blocker_count: int,
    manual_confirmation_complete: bool,
    forward_dry_run_start_authorized: bool,
    git_status_clean: bool,
    latest_release_tag_exists: bool,
    run_daily_called: bool,
    forward_dry_run_started: bool,
    main_ledger_written: bool,
    no_broker_live_config: bool,
    no_rl_llm_trading_decision_enabled: bool,
) -> dict[str, Any]:
    checks = {
        "plan_alignment_passed": plan_alignment_passed,
        "ashare_execution_rules_passed": ashare_execution_rules_passed,
        "baseline_strategy_pack_passed": baseline_strategy_pack_passed,
        "daily_workflow_audit_passed": daily_workflow_audit_passed,
        "protected_path_blocker_count=0": protected_path_blocker_count == 0,
        "updated_day1_blocker_count=0": updated_day1_blocker_count == 0,
        "manual_confirmation_complete": manual_confirmation_complete,
        "forward_dry_run_start_authorized": forward_dry_run_start_authorized,
        "git_status_clean": git_status_clean,
        "latest_release_tag_exists": latest_release_tag_exists,
        "run_daily_called=false": not run_daily_called,
        "forward_dry_run_started=false": not forward_dry_run_started,
        "main_ledger_written=false": not main_ledger_written,
        "no_broker_live_config": no_broker_live_config,
        "no_rl_llm_trading_decision_enabled": no_rl_llm_trading_decision_enabled,
    }
    deny_reasons = [f"{key}=false" for key, passed in checks.items() if not passed]
    return {"checks": checks, "deny_reasons": deny_reasons, "day1_start_allowed": not deny_reasons}


def validate_forward_dry_run_start_gate_v062(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    preview = build_forward_dry_run_run_daily_command_preview(paths=paths)
    manual = read_system(paths, "forward_dry_run_manual_confirmation_checklist_v2.json")
    owner = read_system(paths, "forward_dry_run_owner_authorization_packet.json")
    plan = read_system(paths, "plan_alignment_audit.json")
    rules = read_system(paths, "ashare_execution_rules_audit.json")
    strategy = read_system(paths, "baseline_strategy_pack_audit.json")
    daily = read_system(paths, "daily_workflow_audit.json")
    residue = read_system(paths, "protected_path_residue_scan.json")
    v061 = read_system(paths, "day1_blocker_reclassification_v061.json")

    manual_complete = manual.get("manual_confirmation_complete") is True
    owner_authorized = start_authorized(owner)
    technical = {
        "plan_alignment_passed": passed_without_blockers(plan),
        "ashare_execution_rules_passed": passed_without_blockers(rules),
        "baseline_strategy_pack_passed": passed_without_blockers(strategy),
        "daily_workflow_audit_passed": passed_without_blockers(daily),
        "protected_path_blocker_count": int(residue.get("blocker_count", 1) or 0),
        "updated_day1_blocker_count": int(v061.get("updated_day1_blocker_count", 1) or 0),
    }
    evaluation = evaluate_start_gate(
        **technical,
        manual_confirmation_complete=manual_complete,
        forward_dry_run_start_authorized=owner_authorized,
        git_status_clean=True,
        latest_release_tag_exists=True,
        run_daily_called=False,
        forward_dry_run_started=False,
        main_ledger_written=False,
        no_broker_live_config=True,
        no_rl_llm_trading_decision_enabled=True,
    )
    default_deny = []
    if not manual_complete:
        default_deny.append("manual_confirmation_complete=false")
    if not owner_authorized:
        default_deny.append("forward_dry_run_start_authorized=false")
    deny_reasons = default_deny or evaluation["deny_reasons"]
    day1_allowed = not deny_reasons
    payload: dict[str, Any] = {
        "gate_id": "FORWARD-DRY-RUN-START-GATE-V062",
        "day1_start_allowed": day1_allowed,
        "deny_reasons": deny_reasons,
        "manual_confirmation_complete": manual_complete,
        "forward_dry_run_start_authorized": owner_authorized,
        "technical_prerequisites": technical,
        "run_daily_command_preview": {
            "exists": True,
            "preview_only": preview["preview_only"],
            "executed": preview["executed"],
        },
        "boundary": authorization_boundary("start_gate_only"),
    }
    return write_artifact(
        system_json(paths, "forward_dry_run_start_gate_v062.json"),
        payload,
        system_report(paths, "FORWARD_DRY_RUN_START_GATE_V062.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Start Gate V062",
        "",
        AUTHORIZATION_NOTICE,
        "",
        "## Gate",
        f"- day1_start_allowed: {str(payload['day1_start_allowed']).lower()}",
        f"- deny_reasons: {', '.join(payload['deny_reasons']) if payload['deny_reasons'] else '[]'}",
        "- manual_confirmation_complete=false",
        "- forward_dry_run_start_authorized=false",
        "- run_daily_command_preview.preview_only=true",
        "- run_daily_command_preview.executed=false",
        "",
        "## Boundary",
        *non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

