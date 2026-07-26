"""Pre-execution gate for virtual forward dry-run day 1."""

from __future__ import annotations

from typing import Any

from trading_core.forward_dry_run.day1_common import (
    DAY_INDEX,
    day1_already_executed,
    day_json,
    day_report,
    eligible_as_of_date,
    git_status_clean,
    no_broker_live_config,
    non_claim_lines,
    paths_or_default,
    read_system,
    write_artifact,
)
from trading_core.forward_dry_run.start_authorization_common import passed_without_blockers
from trading_core.storage.file_paths import ProjectPaths


def build_day1_pre_execution_gate(
    *,
    paths: ProjectPaths | None = None,
    allow_rerun: bool = False,
    git_status_clean_override: bool | None = None,
    main_ledger_write_guard_active: bool = True,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    owner_record = read_system(paths, "forward_dry_run_owner_manual_confirmation_record.json")
    completed = read_system(paths, "forward_dry_run_manual_confirmation_checklist_v2_completed.json")
    authorized = read_system(paths, "forward_dry_run_owner_authorization_packet_authorized.json")
    gate = read_system(paths, "forward_dry_run_start_gate_v0621.json")
    eligibility = read_system(paths, "forward_dry_run_day1_prompt_eligibility_v0621.json")
    materialization_audit = read_system(paths, "forward_dry_run_authorization_materialization_audit.json")
    reclass = read_system(paths, "day1_blocker_reclassification_v0621.json")
    daily = read_system(paths, "daily_workflow_audit.json")
    strategy = read_system(paths, "baseline_strategy_pack_audit.json")
    rules = read_system(paths, "ashare_execution_rules_audit.json")
    residue = read_system(paths, "protected_path_residue_scan.json")
    _, data_details = eligible_as_of_date(paths)

    clean = git_status_clean_override if git_status_clean_override is not None else git_status_clean(paths)
    checks = {
        "owner_confirmation_recorded": owner_record.get("owner_confirmation_recorded") is True,
        "manual_confirmation_complete": completed.get("manual_confirmation_complete") is True,
        "forward_dry_run_start_authorized": authorized.get("forward_dry_run_start_authorized") is True,
        "day1_prompt_eligible": eligibility.get("day1_prompt_eligible") is True and gate.get("day1_prompt_eligible") is True,
        "authorization_materialization_audit_passed": passed_without_blockers(materialization_audit),
        "updated_day1_blocker_count=0": int(reclass.get("updated_day1_blocker_count", 1) or 0) == 0,
        "git_status_clean_before_execution": clean is True,
        "daily_workflow_audit_passed": passed_without_blockers(daily),
        "baseline_strategy_pack_audit_passed": passed_without_blockers(strategy),
        "ashare_execution_rules_audit_passed": passed_without_blockers(rules),
        "protected_path_blocker_count=0": int(residue.get("blocker_count", 1) or 0) == 0,
        "forward_dry_run_not_already_started": not read_system(paths, "forward_dry_run_status.json").get("forward_dry_run_started", False),
        "day_001_not_already_executed": allow_rerun or not day1_already_executed(paths),
        "run_daily_mode_forward_dry_run": True,
        "main_ledger_write_guard_active": main_ledger_write_guard_active,
        "broker_live_config_absent": no_broker_live_config(),
        "ml_llm_rl_promotion_disabled": True,
        "day1_data_eligible": data_details["eligible"],
    }
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    warnings: list[dict[str, Any]] = []
    payload: dict[str, Any] = {
        "gate_id": "FORWARD-DRY-RUN-DAY1-PRE-EXECUTION-GATE",
        "day_index": DAY_INDEX,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "checks": checks,
        "data_eligibility": data_details,
        "authorization": {
            "manual_confirmation_complete": completed.get("manual_confirmation_complete") is True,
            "forward_dry_run_start_authorized": authorized.get("forward_dry_run_start_authorized") is True,
            "day1_prompt_eligible": eligibility.get("day1_prompt_eligible") is True,
        },
        "boundary": {
            "pre_execution_gate_only": True,
            "broker_connected": False,
            "real_orders_enabled": False,
            "main_ledger_write_guard_active": main_ledger_write_guard_active,
            "ml_shadow_used_as_authorization": False,
            "llm_trading_decision": False,
            "rl_used": False,
            "promotion_triggered": False,
        },
    }
    return write_artifact(day_json(paths, "day1_pre_execution_gate.json"), payload, day_report(paths, "DAY1_PRE_EXECUTION_GATE.md"), build_markdown(payload))


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Day 1 Pre-Execution Gate",
        "",
        "## Verdict",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        "",
        "## Authorization",
        f"- manual_confirmation_complete: {str(payload['authorization']['manual_confirmation_complete']).lower()}",
        f"- forward_dry_run_start_authorized: {str(payload['authorization']['forward_dry_run_start_authorized']).lower()}",
        f"- day1_prompt_eligible: {str(payload['authorization']['day1_prompt_eligible']).lower()}",
        "",
        "## Boundary",
        *non_claim_lines(),
        "",
    ]
    return "\n".join(lines)

