from __future__ import annotations

from pathlib import Path

from daily_workflow_test_utils import build_daily_workflow_stack, make_daily_workflow_paths


def make_authorization_paths(tmp_path: Path):
    paths = make_daily_workflow_paths(tmp_path)
    from trading_core.planning.plan_alignment_audit import audit_plan_alignment

    audit_plan_alignment(paths=paths)
    build_daily_workflow_stack(paths)
    return paths


def build_authorization_pack(paths) -> None:
    from trading_core.forward_dry_run.current_daily_workflow_readiness_snapshot import build_current_daily_workflow_readiness_snapshot
    from trading_core.forward_dry_run.day1_prompt_eligibility_report import build_forward_dry_run_day1_prompt_eligibility
    from trading_core.forward_dry_run.manual_confirmation_checklist_v2 import build_forward_dry_run_manual_confirmation_checklist_v2
    from trading_core.forward_dry_run.owner_authorization_packet import build_forward_dry_run_owner_authorization_packet
    from trading_core.forward_dry_run.run_daily_command_preview_metadata import build_forward_dry_run_run_daily_command_preview
    from trading_core.forward_dry_run.start_authorization_audit import audit_forward_dry_run_start_authorization
    from trading_core.forward_dry_run.start_authorization_scope_plan import build_forward_dry_run_authorization_scope_plan
    from trading_core.forward_dry_run.start_gate_validator import validate_forward_dry_run_start_gate_v062
    from trading_core.forward_dry_run.start_prerequisite_inventory import build_forward_dry_run_start_prerequisite_inventory

    build_forward_dry_run_authorization_scope_plan(paths=paths)
    build_forward_dry_run_start_prerequisite_inventory(paths=paths)
    build_current_daily_workflow_readiness_snapshot(paths=paths)
    build_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
    build_forward_dry_run_owner_authorization_packet(paths=paths)
    validate_forward_dry_run_start_gate_v062(paths=paths)
    build_forward_dry_run_run_daily_command_preview(paths=paths)
    build_forward_dry_run_day1_prompt_eligibility(paths=paths)
    audit_forward_dry_run_start_authorization(paths=paths)
